# -*- coding: utf-8 -*-

#from fbappauth import CLIENT_ID, CLIENT_SECRET
from pyfacebook import GraphAPI, GraphAPIError
from gluon.contrib.login_methods.oauth20_account import OAuthAccount
from gluon import HTTP
from gluon.validators import IS_SLUG
from gluon import current


class FaceBookAccount(OAuthAccount):
    """OAuth impl for FaceBook"""
    AUTH_URL = "https://graph.facebook.com/oauth/authorize"
    TOKEN_URL = "https://graph.facebook.com/oauth/access_token"

    def __init__(self, db):
        self.db = db
        g = dict(GraphAPI=GraphAPI,
                 GraphAPIError=GraphAPIError,
                 request=current.request,
                 response=current.response,
                 session=current.session,
                 HTTP=HTTP)
        client = dict(db.config.get_list('auth', 'facebook'))
        OAuthAccount.__init__(self, g, client['id'], client['secret'],
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
            current.session.facebooklogin = True
            existent = self.db(self.db.auth_user.email == user["email"]).select().first()
            if existent:
                current.session["%s_setpassword" % existent.id] = existent.password
                return dict(first_name=user.get('first_name', ""),
                            last_name=user.get('last_name', ""),
                            facebookid=user['id'],
                            facebook=user.get('username', user['id']),
                            email=user['email'],
                            password=existent.password
                            )
            else:
                # b = user["birthday"]
                # birthday = "%s-%s-%s" % (b[-4:], b[0:2], b[-7:-5])
                # if 'location' in user:
                #     session.flocation = user['location']
                current.session["is_new_from"] = "facebook"
                self.db.auth.send_welcome_email(user)
                # self.db.auth.initial_user_permission(user)  # Called on profile page
                return dict(first_name=user.get('first_name', ""),
                            last_name=user.get('last_name', ""),
                            facebookid=user['id'],
                            facebook=user.get('username', user['id']),
                            nickname=IS_SLUG()(user.get('username', "%(first_name)s-%(last_name)s" % user) + "-" + user['id'][:5])[0],
                            email=user['email'],
                            # birthdate=birthday,
                            about=user.get("bio", ""),
                            website=user.get("website", ""),
                            # gender=user.get("gender", "Not specified").title(),
                            photo_source=3,
                            tagline=user.get("link", ""),
                            registration_type=2,
                            )


# def getGraph():
#     a_token = auth.settings.login_form.accessToken()
#     return GraphAPI(a_token)
