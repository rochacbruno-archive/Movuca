#!/usr/bin/python
# -*- coding: utf-8 -*-

from movuca import DataBase, User, UserTimeLine
db = DataBase()
auth = User(db)
timeline = UserTimeLine(db)


def usertimeline():
    user = request.args(0)
    events = db(timeline.entity.user_id == user).select()
    event_types = timeline.entity._event_types
    ret = DIV(
       UL(
          *[LI(XML(str(event_types[event.event_type]) % event)) for event in events]
       )
    )
    return dict(ret=ret)
