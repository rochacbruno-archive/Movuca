#!/usr/bin/python
# -*- coding: utf-8 -*-

from handlers.person import Person


def usertimeline():
    person = Person('usertimeline')
    return person.render("app/person/usertimeline")


def publictimeline():
    person = Person('publictimeline')
    return person.render("app/person/publictimeline")


def privatetimeline():
    person = Person('privatetimeline')
    return person.render("app/person/privatetimeline")


def followers():
    person = Person()
    person.followers(request.args(0))
    return person.render()


def following():
    person = Person()
    person.following(request.args(0))
    return person.render()


def contacts():
    person = Person()
    person.contacts(request.args(0))
    person.context.left_sidebar_enabled = True
    return person.render('app/person/contacts')


def search():
    person = Person()
    person.context.left_sidebar_enabled = True
    person.search(request.vars.get('q'))
    return person.render('app/person/search')


def follow():
    person = Person()
    return person.follow()


def unfollow():
    person = Person()
    return person.unfollow()

login_url = CURL('person', 'account', args='login')


def show():
    auth = session.get("auth", {})
    user = auth.get("user", None)
    if user:
        user_id = user.id
    else:
        user_id = None
    person = Person()
    person.show(request.args(0) or user_id or redirect(login_url))
    return person.render()


def board():
    auth = session.get("auth", {})
    user = auth.get("user", None)
    if user:
        user_id = user.id
    else:
        user_id = None
    person = Person()
    person.board(request.args(0) or user_id or redirect(login_url), request.vars.postid)
    return person.render()


def removeboard():
    person = Person()
    person.removeboard(request.args(0), session.auth.user.id)
    return person.context.eval


def removeevent():
    person = Person()
    person.removeevent(request.args(0), session.auth.user.id)
    return person.context.eval


def account():
    person = Person("account")
    person.context.left_sidebar_enabled = True if 'profile' in request.args else False
    return person.render('app/person/account')


def facebook():
    session.state = 'facebook'
    person = Person("facebook")
    return person.render()


def google():
    if 'state' in request.vars and request.vars.state == 'google':
        session.state = request.vars.state
    person = Person("google")
    return person.render()


def user():
    if session.state and session.state == 'google':
        redirect(CURL('person', 'google', args=request.args, vars=request.vars))
    else:
        redirect(CURL('person', 'facebook', args=request.args, vars=request.vars))


def loginbare():
    person = Person("loginbare")
    return person.render('app/person/loginbare')


def messages():
    return 'This page is under construction, feel free to contribute <-- go back and click on GitHub link'


def check_availability():
    person = Person()
    items = dict(field=request.args(0),
                  value=request.args(1))
    error = person.check_availability(items)
    if error:
        items['error'] = error[items['field']]
        items['img'] = str(IMG(_title=items['error'], _class="%(field)s_availability_img" % items, _src=URL('static', person.context.theme_name, args=['images', 'icons', 'notright.24.png'])))
        return "jQuery('.%(field)s_availability_img').hide();jQuery('#auth_user_%(field)s').css({'border': '1px solid red'});jQuery('#auth_user_%(field)s').parent().append('%(img)s');" % items
    else:
        items['img'] = str(IMG(_title=T("Available"), _class="%(field)s_availability_img" % items, _src=URL('static', person.context.theme_name, args=['images', 'icons', 'right.24.png'])))
        return "jQuery('.%(field)s_availability_img').hide();jQuery('#auth_user_%(field)s').css({'border': '1px solid green'});jQuery('#auth_user_%(field)s').parent().append('%(img)s');" % items


def notificationpermission():
    person = Person()
    pid = request.args(0)
    way = request.args(1)
    action = request.args(2)
    person.notificationpermission(pid, way, action)
    return person.context.button
