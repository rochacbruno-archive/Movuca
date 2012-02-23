# -*- coding: utf-8 -*-

from gluon.tools import prettydate
from datetime import datetime


def tagfy(tags, extension='html'):
    links = [A(" %s " % tag.strip(), _href=CURL('article', 'list', vars=dict(tag=tag), extension=extension)) for tag in tags]
    return CAT(*links)


DATEFORMAT = T("%Y-%m-%d")
TIMEFORMAT = T("%H:%M:%S")
current.TIMEFORMAT = TIMEFORMAT
current.DATEFORMAT = DATEFORMAT


def ftime(value):
    return value.strftime(str(DATEFORMAT))


def pdate(value):
    if isinstance(value, str):
        value = datetime.strptime(value, "%s %s" % (DATEFORMAT, TIMEFORMAT))
    return prettydate(value, T=T)

current.pdate = pdate
current.ftime = ftime


def ICONBUTTON(icon, text, action):
    bt = BUTTON(_class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-icon-primary",
                _role="button",
                _onclick=action)
    bt.append(SPAN(_class="ui-button-icon-primary ui-icon ui-icon-%s" % icon))
    bt.append(SPAN(text, _class="ui-button-text"))

    return bt


def ICONLINK(icon, text, action=None):
    bt = A(_class="icon-link",
              _onclick=action,
              _style="cursor:pointer;")
    bt.append(CAT(
        IMG(_src=URL('static', 'basic/images/icons', args="%s.png" % icon), _width=16),
        SPAN(text, _style="line-height:16px;")
    ))

    return bt


def get_image(image, placeholder="image", themename='basic', user=None, host=False, scheme=False):
    if user:
        if user.photo_source == 1:
            if user.thumbnail:
                return URL('default', 'download', args=user.thumbnail, extension=False, host=host, scheme=scheme)
            # pass and let go to return default placeholder
        # elif user.photo_source == 6:
        #     return user.googlepicture
        elif user.photo_source == 5:
            pass  # pass and let go to return default placeholder
        else:
            # try to get the image from the source
            from helpers.images import GetImages
            return GetImages.getphoto(user=user)

    if image and image.startswith("http://"):
        return image
    if image:
        return URL('default', 'download', args=image, extension=False, host=host, scheme=scheme)
    else:
        return URL('static', '%s/images' % themename, args='%s.png' % placeholder, extension=False, host=host, scheme=scheme)

current.get_image = get_image


def has_permission_to_edit(record):
    userid = session.auth.user.id if session.auth else 0
    return record.author == userid


c = 1


def getclass(columns=2):
    global c
    if c % columns == 0:
        c += 1
        return 'omega'
    else:
        c += 1
        return 'alpha'


current.getclass = getclass


def get_name_of(user):
    return "%(first_name)s %(last_name)s (%(nickname)s)" % user

search_form = FORM(
    DIV(
        SELECT(*[OPTION(option, _value=value) for value, option in [("article", T("Articles")), ("user", T("Users"))]], _name="kind", _id="kind"),
       _class="two columns alpha search-select"),
    DIV(
        INPUT(_type="search", _placeholder=T("Type word or name to find"), _name="q", _id="q"),
        BUTTON(IMG(_src=URL('static', 'images', args='search_button.png'))),
        _class="four columns omega search-input"
    ),
    _class="search-form",
    _method="GET",
    _action=CURL("home", "search")
)


def iicon(iconname):
    return TAG['i'](_class="icon-%s" % iconname, _style="margin-right:5px;")
