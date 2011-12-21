# -*- coding: utf-8 -*-


from gluon import *


def contact_box(row, kind='contact', ajax=False, where=None):
    T = current.T
    if kind == 'contact':
        uid = row.id
        thumbnail = row.thumbnail
        name = row.nickname or row.first_name
        text = row.tagline or row.website or ''
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

        action = 'unfollow' if kind == 'followed' else 'follow'
        if not where:
            where = 'contact' if kind == 'follower' else 'following'

    ret = DIV(_class="six columns contact-item %s" % current.getclass(2),
              _id="item_%s" % uid)
    ret.append(IMG(_class="two columns alpha", _src=current.get_image(thumbnail, 'user')))
    infodiv = DIV(_class="four columns omega")
    infodiv.append(name)
    infodiv.append(text)
    infodiv.append(BR())
    infodiv.append(TAG.BUTTON(T(action),
        _onclick="jQuery(this).parent().parent().hide();append_ajax('%s',[],'%s-wrapper')" % (URL('person', action, args=uid), where)))
    ret.append(infodiv)
    return ret
