# -*- coding: utf-8 -*-
"""Unit test suite for the models of the application."""
from nose.tools import assert_equals
from tg import config
from wiki20.tests import setup_db, teardown_db

__all__ = ['ModelTest']

# Create an empty database before we start our tests for this module
def setup():
    """Function called by nose on module load"""
    setup_db()

# Tear down that database
def teardown():
    """Function called by nose after all tests in this module ran"""
    teardown_db()


class ModelTest(object):
    """Base unit test case for the models."""

    klass = None
    attrs = {}

    def setUp(self):
        """Prepare model test fixture."""
        try:
            new_attrs = {}
            new_attrs.update(self.attrs)
            new_attrs.update(self.do_get_dependencies())
            self.obj = self.klass(**new_attrs)
            self.obj.__mongometa__.session.flush()
            self.obj.__mongometa__.session.clear()
            return self.obj
        except:
            config['pylons.app_globals'].ming_datastore.conn.drop_all()
            raise

    def tearDown(self):
        """Finish model test fixture."""
        config['pylons.app_globals'].ming_datastore.conn.drop_all()

    def do_get_dependencies(self):
        """Get model test dependencies.

        Use this method to pull in other objects that need to be created
        for this object to be build properly.

        """
        return {}

    def test_create_obj(self):
        """Model objects can be created"""
        pass

    def test_query_obj(self):
        """Model objects can be queried"""
        obj = self.klass.query.find({}).first()
        for key, value in self.attrs.iteritems():
            assert_equals(getattr(obj, key), value)
