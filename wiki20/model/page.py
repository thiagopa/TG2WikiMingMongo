from ming import schema as s
from ming.orm import FieldProperty, ForeignIdProperty, RelationProperty
from ming.orm import Mapper
from ming.orm.declarative import MappedClass
from tgming import SynonymProperty, ProgrammaticRelationProperty
import os
from session import DBSession


class Page(MappedClass):
    class __mongometa__:
        session = DBSession
        name = 'page'
        unique_indexes = [('pagename',),]
    
    _id = FieldProperty(s.ObjectId)
    
    pagename = FieldProperty(s.String)
    
    data = FieldProperty(s.String)
    
    def __init__(self, pagename, data):
        self.pagename = pagename
        self.data = data