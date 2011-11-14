# -*- coding: utf-8 -*-

from gluon.storage import Storage


class Base(object):
    def __init__(
        self,
        path="views/",
        view="default/index.html",
        meta=Storage(),
        context={},
        ):
        self.meta = meta
        self.context = context
        self.path = path
        self.view = view

        # hooks call
        self.load()
        self.start()
        self.build()
        self.pre_render()

    def load(self):
        from gluon import current
        self.current = current
        self.response = current.response
        self.request = current.request
        self.session = current.session
        self.T = current.T
        self.cache = current.cache

    def render(self):
        return self.response.render(self.view, self.context)

    def start(self):
        pass

    def build(self):
        pass

    def pre_render(self):
        pass
