#!/usr/bin/python
# -*- coding: utf-8 -*-

from handlers.person import Person


def usertimeline():
    person = Person('usertimeline')
    return person.render()


def publictimeline():
    person = Person('publictimeline')
    return person.render()
