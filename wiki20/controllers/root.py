# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, lurl, request, redirect
from tg.i18n import ugettext as _, lazy_ugettext as l_
from wiki20 import model
from repoze.what import predicates
from wiki20.controllers.secure import SecureController
from tgext.admin.mongo import TGMongoAdminConfig
from tgext.admin.controller import AdminController

from wiki20.lib.base import BaseController
from wiki20.controllers.error import ErrorController

from wiki20.model.page import Page
import re
from docutils.core import publish_parts

__all__ = ['RootController']

wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

class RootController(BaseController):
    """
    The root controller for the Wiki-20 application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    secc = SecureController()
    admin = AdminController(model, None, config_type=TGMongoAdminConfig)

    error = ErrorController()

    def get_page_name(self, pagename):
        #SQL ALCHEMY
        #page = DBSession.query(Page).filter_by(pagename=pagename).one()
        
        #MING
        page = Page.query.get(pagename=pagename)
        
        return dict(wikipage=page)

    @expose('wiki20.templates.page')
    def _default(self, pagename="FrontPage"):
        page = Page.query.get(pagename=pagename)
        if page == None:
            raise redirect("notfound", pagename=pagename)
        content = publish_parts(page.data, writer_name="html")["html_body"]
        root = url('/')
        content = wikiwords.sub(r'<a href="%s\1">\1</a>' % root, content)
        return dict(content=content, wikipage=page)
    
    @expose('wiki20.templates.edit')
    def notfound(self,pagename):
        page = Page(pagename,'')
        
        return dict(wikipage=page)       

    @expose('wiki20.templates.edit')
    def edit(self,pagename):
        return self.get_page_name(pagename)
            
    @expose()
    def save(self,pagename,data,submit):
        page = Page.query.get(pagename=pagename)
        page.data = data
        redirect("/" + pagename)

    @expose('wiki20.templates.pagelist')
    def pagelist(self):
        #Sql Alchemy
        #pages = [page.pagename for page in DBSession.query(Page).order_by(Page.pagename)]
        
        #Ming
        pages = [page.pagename for page in Page.query.find().sort('pagename')]
        return dict(pages=pages)

    @expose('wiki20.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    @expose('wiki20.templates.environ')
    def environ(self):
        """This method showcases TG's access to the wsgi environment."""
        return dict(environment=request.environ)

    @expose('wiki20.templates.data')
    @expose('json')
    def data(self, **kw):
        """This method showcases how you can use the same controller for a data page and a display page"""
        return dict(params=kw)
    @expose('wiki20.templates.authentication')
    def auth(self):
        """Display some information about auth* on this application."""
        return dict(page='auth')

    @expose('wiki20.templates.index')
    @require(predicates.has_permission('manage', msg=l_('Only for managers')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff')

    @expose('wiki20.templates.index')
    @require(predicates.is_user('editor', msg=l_('Only for the editor')))
    def editor_user_only(self, **kw):
        """Illustrate how a page exclusive for the editor works."""
        return dict(page='editor stuff')

    @expose('wiki20.templates.login')
    def login(self, came_from=lurl('/')):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)

    @expose()
    def post_login(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect('/login',
                params=dict(came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        redirect(came_from)

