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
        pass

    def render(self):
        # lançar erro caso nao tenha response e render
        return self.response.render(self.view, self.context)

    def start(self):
        pass

    def build(self):
        pass

    def pre_render(self):
        from gluon import current
        self.response = current.response
