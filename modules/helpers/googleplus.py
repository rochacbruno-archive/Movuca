# -*- coding: utf-8 -*-

from oauth20_account_google import OAuthAccount
from gluon import HTTP
from gluon import current
import urllib
# import urllib2
from gluon.contrib import simplejson as json


class GooglePlusAccount(OAuthAccount):
    """OAuth impl for FaceBook"""
    AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    TOKEN_URL = "https://accounts.google.com/o/oauth2/token"
    API_URL = "https://www.googleapis.com/oauth2/v1/userinfo"

    def __init__(self, db):
        self.db = db
        g = dict(request=current.request,
                 response=current.response,
                 session=current.session,
                 HTTP=HTTP)
        client = dict(db.config.get_list('auth', 'google'))
        "https://code.google.com/apis/console/"
        OAuthAccount.__init__(self, g, client,
                              self.AUTH_URL, self.TOKEN_URL,
                              scope='https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
                              user_agent='google-api-client-python-plus-cmdline/1.0',
                              xoauth_displayname=client["xoauth_displayname"],
                              response_type='code',
                              redirect_uri="%(redirect_scheme)s://%(redirect_uri)s" % client,
                              approval_prompt=client['approval_prompt'],
                              state='google'
                             )
        self.graph = None

    def get_user(self):
        self.session = current.session
        '''Returns the user using the Graph API.
        '''

        if not self.accessToken():
            return None

        user = None
        try:
            user = self.call_api()
        except Exception, e:
            print str(e)
            self.session.token = None

        if user:
            current.session.googlelogin = True
            existent = self.db(self.db.auth_user.email == user["email"]).select().first()
            if existent:
                current.session["%s_setpassword" % existent.id] = existent.password
                return dict(
                            #first_name=user.get('given_name', user["name"]),
                            #last_name=user.get('family_name', user["name"]),
                            googleid=user['id'],
                            email=user['email'],
                            password=existent.password
                            )
            else:
                # b = user["birthday"]
                # birthday = "%s-%s-%s" % (b[-4:], b[0:2], b[-7:-5])
                # if 'location' in user:
                #     session.flocation = user['location']
                current.session["is_new_from"] = "google"
                self.db.auth.send_welcome_email(user)
                return dict(
                            first_name=user.get('given_name', user["name"].split()[0]),
                            last_name=user.get('family_name', user["name"].split()[-1]),
                            googleid=user['id'],
                            nickname="%(first_name)s-%(last_name)s-%(id)s" % dict(first_name=user["name"].split()[0].lower(), last_name=user["name"].split()[-1].lower(), id=user['id'][:5]),
                            email=user['email'],
                            # birthdate=birthday,
                            website=user.get("link", ""),
                            # gender=user.get("gender", "Not specified").title(),
                            photo_source=6 if user.get('picture', None) else 2,
                            googlepicture=user.get('picture', ''),
                            registration_type=3,
                            )

    def call_api(self):
        api_return = urllib.urlopen("https://www.googleapis.com/oauth2/v1/userinfo?access_token=%s" % self.accessToken())
        user = json.loads(api_return.read())
        if user:
            return user
        else:
            self.session.token = None
            return None
