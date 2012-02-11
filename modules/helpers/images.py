# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Custom methods
#########################################################################
from gluon import *
# request = current.request
# if 'auth' in current.session:
#     user = current.session.auth.user
# else:
#     user = None

########################################################################
# IMAGE METHODS
########################################################################


class RESIZE(object):
    def __init__(self, nx=160, ny=80, error_message=' image resize'):
        (self.nx, self.ny, self.error_message) = (nx, ny, error_message)

    def __call__(self, value):
        if isinstance(value, str) and len(value) == 0:
            return (value, None)
        from PIL import Image
        import cStringIO
        try:
            img = Image.open(value.file)
            img.thumbnail((self.nx, self.ny), Image.ANTIALIAS)
            s = cStringIO.StringIO()
            img.save(s, 'JPEG', quality=100)
            s.seek(0)
            value.file = s
        except:
            return (value, self.error_message)
        else:
            return (value, None)


def THUMB(image, nx=120, ny=120):
    if image:
        request = current.request
        from PIL import Image
        import os
        img = Image.open(request.folder + 'static/uploads/userprofile/' + image)
        img.thumbnail((nx, ny), Image.ANTIALIAS)
        root, ext = os.path.splitext(image)
        thumb = '%s_thumb%s' % (root, ext)
        img.save(request.folder + 'static/uploads/userprofile/' + thumb)
        return thumb


def THUMB2(image, nx=120, ny=120, gae=False, name='thumb'):
    if image:
        if not gae:
            request = current.request
            from PIL import Image
            import os
            img = Image.open(request.folder + 'uploads/' + image)
            img.thumbnail((nx, ny), Image.ANTIALIAS)
            root, ext = os.path.splitext(image)
            thumb = '%s_%s%s' % (root, name, ext)
            img.save(request.folder + 'uploads/' + thumb)
            return thumb
        else:
            return image


class GetImages(object):
########################################################################
# TWITTER IMAGE
########################################################################
    @staticmethod
    def get_twitter_image(username):
        api = "http://api.twitter.com/1/users/profile_image?screen_name=%s&size=reasonably_small" % username.split('/')[-1].strip()  # bigger
        return api

    @staticmethod
    def get_gravatar_image(email):
        import urllib
        import hashlib

        default = "mm"  # "http://www.example.com/default.jpg"
        size = 128

        # construct the url
        gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'d': default, 's': str(size)})

        return gravatar_url

    @staticmethod
    def get_url_image(url):
        return URL('static', 'images', args='people.png', extension=False)

    @staticmethod
    def get_no_image(nothing):
        return URL('static', 'images', args='people.png', extension=False)

    @staticmethod
    def get_upload_image(image):
        if image and image != "None":
            import os
            root, ext = os.path.splitext(image)
            thumb = '%s_thumb%s' % (root, ext)
            return URL('static', 'uploads', args=['userprofile', thumb])
        else:
            return GetImages.get_no_image(None)

    @staticmethod
    def get_facebook_image(user):
        return "http://graph.facebook.com/%s/picture?type=large" % user.split('/')[-1].strip()

    @staticmethod
    def get_google_image(image):
        if image and image.startswith("http"):
            return image
        else:
            return GetImages.get_no_image(image)

    @staticmethod
    def getphoto(user=None, img=False):
        if not user:
            if 'auth' in current.session:
                user = current.session.auth.user

        action = {
        '1': GetImages.get_upload_image,
        '2': GetImages.get_gravatar_image,
        '3': GetImages.get_facebook_image,
        '4': GetImages.get_twitter_image,
        '5': GetImages.get_no_image,
        '6': GetImages.get_google_image
        }

        value = {
        '1': 'thumbnail',
        '2': 'email',
        '3': 'facebook',
        '4': 'twitter',
        '5': 'id',
        '6': 'googlepicture'
        }

        photo_source = action[str(user.photo_source)]
        val = user[value[str(user.photo_source)]] or None

        if not img:
            return photo_source(str(val))
        else:
            return IMG(_src=photo_source(str(val)), _width='100')


########################################################################
# FLICKR METHODS
########################################################################
APIKEY = '7f42deecc225d70db85467a335170ae6'
APISECRET = '3c1a8f7223e7b597'


def get_flickerset(pset=None, per_page=15, page=1):
    from urllib2 import urlopen
    from xml.dom.minidom import parse as domparse
    apiurl = 'http://api.flickr.com/services/rest/?method=flickr.photosets.getPhotos&api_key=%(apikey)s&photoset_id=%(pset)s&privacy_filter=1&per_page=%(per_page)s&page=%(page)s&extras=url_t,url_m,url_o,url_sq,url_s'
    dom = domparse(urlopen(apiurl % dict(pset=pset, per_page=per_page, page=page, apikey=APIKEY)))

    photos = []

    for node in dom.getElementsByTagName('photo'):
        photos.append({
        'id': node.getAttribute('id'),
        'title': node.getAttribute('title'),
        'thumb': node.getAttribute('url_t'),
        'small': node.getAttribute('url_s'),
        'medio': node.getAttribute('url_m'),
        'original': node.getAttribute('url_o'),
        'square': node.getAttribute('url_sq'),
        })

    return photos


def get_flickerphoto(photoid):
    from urllib2 import urlopen
    from xml.dom.minidom import parse as domparse
    apiurl = 'http://api.flickr.com/services/rest/?method=flickr.photosets.getPhotos&api_key=%(apikey)s&photoset_id=%(pset)s&privacy_filter=1&per_page=%(per_page)s&page=%(page)s&extras=url_t,url_m,url_o,url_sq,url_s'
    dom = domparse(urlopen(apiurl % dict(pset=pset, per_page=per_page, page=page, apikey=APIKEY)))

    photos = []

    for node in dom.getElementsByTagName('photo'):
        photos.append({
        'id': node.getAttribute('id'),
        'title': node.getAttribute('title'),
        'thumb': node.getAttribute('url_t'),
        'small': node.getAttribute('url_s'),
        'medio': node.getAttribute('url_m'),
        'original': node.getAttribute('url_o'),
        'square': node.getAttribute('url_sq'),
        })

    return photos

#######################################################################
# User Profile Methods
#######################################################################


def get_user_photo_url(photo_source=None,
                       user=None,
                       user_id=None,
                       user_mail=None
                       ):

    if not user:
        if 'auth' in current.session:
            user = current.session.auth.user
    #print user
    if (not user.photo_source and not user.photo):
        return URL('static', 'images', args='people.png')
    elif (not user.photo_source and user.photo) or\
        (user.photo_source == '1' and user.photo):
        return URL('static', 'uploads/userprofile', args=auth.user.photo_thumb)
    elif user.photo_source == '2':
        from gravatar import Gravatar
        return Gravatar(user.email).thumb
    elif user.photo_source == '3' and user.twitter:
        return get_twitter_image(user.twitter)
    elif user.photo_source == '4':
        return user.photo_url
    elif user.photo_source == '5':
        return 'photo do facebook'
    else:
        return URL('static', 'images', args='people.png')
