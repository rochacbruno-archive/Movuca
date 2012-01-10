# -*- coding: utf-8 -*-

from fbappauth import CLIENT_ID, CLIENT_SECRET
from pyfacebook import GraphAPI, GraphAPIError
from gluon.contrib.login_methods.oauth20_account import OAuthAccount
from gluon import HTTP
from gluon import current

# ## extend the OAUthAccount class
# class FaceBookAccount(OAuthAccount):
#     """OAuth impl for Facebook"""
#     AUTH_URL = "https://graph.facebook.com/oauth/authorize"
#     TOKEN_URL = "https://graph.facebook.com/oauth/access_token"

#     def __init__(self):
#         print 'initing'
#         from gluon import current
#         g = dict(GraphAPI=GraphAPI,
#                  GraphAPIError=GraphAPIError,
#                  request=current.request,
#                  response=current.response,
#                  session=current.session,
#                  HTTP=HTTP)
#         OAuthAccount.__init__(self, g,
#                               CLIENT_ID,
#                               CLIENT_SECRET,
#                               self.AUTH_URL,
#                               self.TOKEN_URL)
#         self.graph = None
#     # override function that fetches user info

#     def get_user(self):
#         print 'get user'
#         "Returns the user using the Graph API"
#         if not self.accessToken():
#             print 'at'
#             return None
#         if not self.graph:
#             print 'not graph'
#             self.graph = GraphAPI((self.accessToken()))
#         try:
#             print 'fetch user'
#             user = self.graph.get_object("me")
#             return dict(first_name=user['first_name'],
#                         last_name=user['last_name'],
#                         username=user['id'])
#         except GraphAPIError:
#             print 'graph error'
#             self.session.token = None
#             self.graph = None
#             return None
# ## use the above class to build a new login form
# #auth.settings.login_form = FaceBookAccount()


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
        print 'facebook iniciali'

    def get_user(self):
        print 'getting user'
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
            print 'use getted'
            print user
        except GraphAPIError:
            self.session.token = None
            self.graph = None
            print 'no'

        if user:
            b = user["birthday"]
            birthday = "%s-%s-%s" % (b[-4:], b[0:2], b[-7:-5])
            # if 'location' in user:
            #     session.flocation = user['location']
            return dict(first_name=user.get('first_name', ""),
                        last_name=user.get('last_name', ""),
                        facebookid=user['id'],
                        facebook=user.get('username', user['id']),
                        nickname=str(user['id']) + str(user.get('username', '')),
                        email=user['email'],
                        birthdate=birthday,
                        about=user.get("bio", ""),
                        website=user.get("website", ""),
                        gender=user.get("gender", "Not specified").title(),
                        photo_source=3,
                        tagline=user.get("link", ""),
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