#!/usr/bin/python
# -*- coding: utf-8 -*-

from handlers.person import Person


def usertimeline():
    person = Person('usertimeline')
    return person.render()


def publictimeline():
    person = Person('publictimeline')
    return person.render()


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


def follow():
    person = Person()
    return person.follow()


def unfollow():
    person = Person('unfollow')
    return person.render()
