# -*- coding: utf-8 -*-

#from fbappauth import CLIENT_ID, CLIENT_SECRET
#from pyfacebook import GraphAPI, GraphAPIError
from oauth20_account_google import OAuthAccount
from gluon import HTTP
from gluon import current


class GooglePlusAccount(OAuthAccount):
    """OAuth impl for FaceBook"""
    AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    TOKEN_URL = "https://accounts.google.com/o/oauth2/token"

    def __init__(self, db):
        self.db = db
        g = dict(request=current.request,
                 response=current.response,
                 session=current.session,
                 HTTP=HTTP)
        client = dict(db.config.get_list('auth', 'facebook'))
        kid = '908928538602.apps.googleusercontent.com'
        secret = 'HH6ITKRWOkhS-prHliD21weA'
        OAuthAccount.__init__(self, g, kid, secret,
                              self.AUTH_URL, self.TOKEN_URL,
                              scope='https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/userinfo.profile',
                              user_agent='google-api-client-python-plus-cmdline/1.0',
                              xoauth_displayname='Google Plus Client Example App',
                              response_type='code',
                              redirect_uri="http://movu.ca/demo/person/google/login",
                              approval_prompt='force',
                              state='google'
                             )
        self.graph = None

    def get_user(self):
        session = current.session
        '''Returns the user using the Graph API.
        '''

        if not self.accessToken():
            return None
        else:
            return self.accessToken()

        # # if not self.graph:
        # #     self.graph = GraphAPI((self.accessToken()))

        # user = None
        # try:
        #     user = self.graph.get_object_c("me")
        # except GraphAPIError:
        #     self.session.token = None
        #     self.graph = None

        # if user:
        #     current.session.facebooklogin = True
        #     existent = self.db(self.db.auth_user.email == user["email"]).select().first()
        #     if existent:
        #         current.session["%s_setpassword" % existent.id] = existent.password
        #         return dict(first_name=user.get('first_name', ""),
        #                     last_name=user.get('last_name', ""),
        #                     facebookid=user['id'],
        #                     facebook=user.get('username', user['id']),
        #                     email=user['email'],
        #                     password=existent.password
        #                     )
        #     else:
        #         # b = user["birthday"]
        #         # birthday = "%s-%s-%s" % (b[-4:], b[0:2], b[-7:-5])
        #         # if 'location' in user:
        #         #     session.flocation = user['location']
        #         current.session["%s_is_new_from_facebook" % user['id']] = True
        #         return dict(first_name=user.get('first_name', ""),
        #                     last_name=user.get('last_name', ""),
        #                     facebookid=user['id'],
        #                     facebook=user.get('username', user['id']),
        #                     nickname=str(user.get('username', '')) + str(user['id']),
        #                     email=user['email'],
        #                     # birthdate=birthday,
        #                     about=user.get("bio", ""),
        #                     website=user.get("website", ""),
        #                     # gender=user.get("gender", "Not specified").title(),
        #                     photo_source=3,
        #                     tagline=user.get("link", ""),
        #                     registration_type=2,
        #                     )


# def getGraph():
#     a_token = auth.settings.login_form.accessToken()
#     return GraphAPI(a_token)
