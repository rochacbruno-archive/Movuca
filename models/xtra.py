# -*- coding: utf-8 -*-


def tagfy(tags):
    links = [A(" %s " % tag.strip(), _href=CURL('article', 'tag', args=tag)) for tag in tags[:5]]
    return CAT(*links)


TIMEFORMAT = T("%Y-%m-%d")


def ftime(value):
    return value.strftime(str(TIMEFORMAT))


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


def get_image(image, placeholder="image"):
    if image:
        return URL('default', 'download', args=image)
    else:
        return URL('static', 'basic/images', args='%s.png' % placeholder)


def has_permission_to_edit(record):
    userid = session.auth.user.id if session.auth else 0
    return record.author == userid
