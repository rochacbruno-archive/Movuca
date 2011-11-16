# -*- coding: utf-8 -*-

from gluon.storage import Storage


class Base(object):
    def __init__(
        self,
        theme="%(name)s/",
        view="generic.html",
        meta=Storage(),
        context={},
        ):
        self.meta = meta
        self.context = context
        self.theme = theme
        self.view = view

        # hooks call
        self.start()
        self.build()
        self.pre_render()

    def start(self):
        pass

    def build(self):
        pass

    def pre_render(self):
        from gluon import current
        from config import Config
        self.config = Config()
        self.response = current.response

    def render(self):
        # lançar erro caso nao tenha config e response e render
        theme = self.theme % self.config.theme
        filename = theme + self.view
        return self.response.render(filename, self.context)
