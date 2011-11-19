# -*- coding: utf-8 -*-

from fbappauth import CLIENT_ID, CLIENT_SECRET
from pyfacebook import GraphAPI, GraphAPIError
from gluon.contrib.login_methods.oauth20_account import OAuthAccount
from gluon import current
from gluon import HTTP


class FaceBookAccount(OAuthAccount):
    """OAuth impl for FaceBook"""
    AUTH_URL = "https://graph.facebook.com/oauth/authorize"
    TOKEN_URL = "https://graph.facebook.com/oauth/access_token"

    def __init__(self):
        g = dict(GraphAPI=GraphAPI,
                 GraphAPIError=GraphAPIError,
                 request=current.request,
                 response=current.response,
                 session=current.session,
                 HTTP=HTTP)
        OAuthAccount.__init__(self, g, CLIENT_ID, CLIENT_SECRET,
                              self.AUTH_URL, self.TOKEN_URL,
                              scope='email,user_about_me,user_location,user_photos,user_relationships,user_birthday,user_website,create_event,user_events,publish_stream')
        self.graph = None

    def get_user(self):
        session = current.session
        '''Returns the user using the Graph API.
        '''

        if not self.accessToken():
            return None

        if not self.graph:
            self.graph = GraphAPI((self.accessToken()))

        user = None
        try:
            user = self.graph.get_object_c("me")
        except GraphAPIError:
            self.session.token = None
            self.graph = None

        if user:
            b = user["birthday"]
            birthday = "%s-%s-%s" % (b[-4:], b[0:2], b[-7:-5])
            if 'location' in user:
                session.flocation = user['location']
            return dict(name=user.get('name', ""),
                        facebookid=user['id'],
                        facebook=user.get('username', user['id']),
                        email=user['email'],
                        birthdate=birthday,
                        bio=user.get("bio", ""),
                        homepage=user.get("website", ""),
                        gender=user.get("gender", "M")[0].upper(),
                        photo_source=4
                        )

#location,albums,family,friends,picture

# if ('fb' in request.vars) or ('code' in request.vars) or ('token' in session):
#     auth.settings.login_url = URL('default','user', args='login',vars={'fb':'true'})
#     auth.settings.login_next = URL('default','index',vars={'fb':'true'})
#     auth.settings.register_next = URL('default','user', args='login')
#     auth.settings.login_form=FaceBookAccount(globals())

#auth.settings.login_form = FaceBookAccount(globals())


# def getGraph():
#     a_token = auth.settings.login_form.accessToken()
#     return GraphAPI(a_token)