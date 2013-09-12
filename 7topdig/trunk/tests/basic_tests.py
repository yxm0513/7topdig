# -*- coding: utf-8 -*-
from flaskext.testing import TestCase

def create_app():
    from app import app
    return app 

class TestSetup(TestCase):

    def create_app(self):
        return create_app()

    def test_setup(self):
        self.assertTrue(self.app is not None)
        self.assertTrue(self.client is not None)
        self.assertTrue(self._ctx is not None)


class BasicTestCase(TestCase):

    def create_app(self):
        return create_app()

    def login(self, username, password):
        return self.client.post('/account/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_index(self):
        response = self.client.get("/")
        self.assert200(response)
        
#    def test_login_logout(self):
#        """Make sure login and logout works"""
#        '''
#        rv = self.login(flaskr.app.config['USERNAME'],
#                        flaskr.app.config['PASSWORD'])
#        assert 'You were logged in' in rv.data
#        rv = self.logout()
#        assert 'You were logged out' in rv.data
#        rv = self.login(flaskr.app.config['USERNAME'] + 'x',
#                        flaskr.app.config['PASSWORD'])
#        assert 'Invalid username' in rv.data
#        rv = self.login(flaskr.app.config['USERNAME'],
#                        flaskr.app.config['PASSWORD'] + 'x')
#        assert 'Invalid password' in rv.data
#        '''
#        response = self.client.get("/account/login")
#        rv = self.login("admin", "111111")
#        #assert u'成功' in rv.data
#        rv = self.logout()


#    def test_register(self):
#        pass
