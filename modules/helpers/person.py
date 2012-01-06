# -*- coding: utf-8 -*-


from gluon import *


def contact_box(row,
                kind='contact',
                ajax=False,
                where=None,
                action=None,
                follows_you=None):
    T = current.T
    CURL = current.CURL
    if kind in ['contact', 'search']:
        uid = row.id
        thumbnail = row.thumbnail
        name = row.nickname or row.first_name
        text = row.tagline or row.website or ''
        if not action:
            action = 'unfollow'
        if not where:
            where = 'follower'
    else:
        if not ajax:
            uid = row[kind].id
            thumbnail = row[kind].thumbnail
            name = row[kind].nickname or row[kind].first_name
            text = row[kind].tagline or row[kind].website or ''
        else:
            uid = row.id
            thumbnail = row.thumbnail
            name = row.nickname or row.first_name
            text = row.tagline or row.website or ''
        if not action:
            action = 'unfollow' if kind == 'followed' else 'follow'
        if not where:
            where = 'contact' if kind == 'follower' else 'following'

    ret = DIV(_class="five columns contact-item %s" % current.getclass(2),
              _id="item_%s" % uid)
    ret.append(IMG(_class="two columns alpha thumbnail", _src=current.get_image(thumbnail, 'user')))
    infodiv = DIV(_class="three columns omega")
    infodiv.append(TAG.STRONG(name))
    if follows_you:
        infodiv.append(BR())
        infodiv.append(EM(T("Follows you!")))
    infodiv.append(BR())
    infodiv.append(text)
    infodiv.append(BR())

    if kind != 'search':
        infodiv.append(TAG.BUTTON(T(action),
            _onclick="jQuery(this).parent().parent().hide();append_ajax('%s',[],'%s-wrapper')" % (URL('person', action, args=uid), where)))
    else:
        infodiv.append(TAG.BUTTON(T(action),
            _onclick="jQuery(this).text('%s');append_ajax('%s',[],'%s-wrapper')" % (T("Done"), URL('person', action, args=uid), where)))

    infodiv.append(A(T("View Profile"), _class="button", _href=CURL('person', 'show', args=uid)))
    ret.append(infodiv)
    return ret
