# -*- coding: utf-8 -*-


from gluon import *


def contact_box(row,
                kind='contact',
                ajax=False,
                where=None,
                action=None,
                follows_you=None,
                css={"main": "six columns", "img": "two columns", "div": "four columns"},
                themename="basic"):
    T = current.T
    CURL = current.CURL
    if kind in ['contact', 'search']:
        uid = row.id
        # thumbnail = row.thumbnail
        name = row.nickname or row.first_name
        text = row.tagline or row.website or ''
        if not action:
            action = 'unfollow'
        if not where:
            where = 'follower'
        user_record = row
    else:
        if not ajax:
            uid = row[kind].id
            # thumbnail = row[kind].thumbnail
            name = row[kind].nickname or row[kind].first_name
            text = row[kind].tagline or row[kind].website or ''
            user_record = row[kind]
        else:
            uid = row.id
            # thumbnail = row.thumbnail
            name = row.nickname or row.first_name
            text = row.tagline or row.website or ''
            user_record = row
        if not action:
            action = 'unfollow' if kind == 'followed' else 'follow'
        if not where:
            where = 'contact' if kind == 'follower' else 'following'

    ret = DIV(_class="%s contact-item %s" % (css.get("main", ""), current.getclass(2)),
              _id="item_%s" % uid)
    ret.append(IMG(_style="margin:0 10px 0;height:92px;width:92px;max-height:92px;max-width:92px;", _class="%s alpha thumbnail" % css.get("img", ""), _src=current.get_image(None, 'user', themename=themename, user=user_record)))
    infodiv = DIV(_class="%s omega" % css.get("div", ""))
    infodiv.append(TAG.STRONG(name))
    if follows_you:
        infodiv.append(BR())
        infodiv.append(SPAN(T("Follows you!"), _class="label label-info"))
    infodiv.append(BR())
    infodiv.append(text)
    infodiv.append(BR())
    buttondiv = DIV(_class="btn-group")

    if kind != 'search':
        buttondiv.append(TAG.BUTTON(T(action), _class="button %s" % "btn btn-danger" if action == 'unfollow' else 'btn btn-success',
            _onclick="jQuery(this).parent().parent().parent().hide();append_ajax('%s',[],'%s-wrapper')" % (URL('person', action, args=uid), where)))
    else:
        buttondiv.append(TAG.BUTTON(T(action), _class="button %s" % "btn btn-danger" if action == 'unfollow' else 'btn btn-success',
            _onclick="jQuery(this).text('%s');ajax('%s',[],'%s-wrapper')" % (T("Done"), URL('person', action, args=uid), where)))

    buttondiv.append(A(T("View Profile"), _class="button btn", _href=CURL('person', 'show', args=uid)))
    infodiv.append(buttondiv)
    ret.append(infodiv)
    return ret
