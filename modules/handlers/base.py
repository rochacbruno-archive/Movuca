# -*- coding: utf-8 -*-


class Base(object):
    def __init__(
        self,
        hooks=[],
        theme="%(name)s/",
        view="generic/generic",
        meta=None,
        context=None
        ):
        from gluon.storage import Storage
        self.meta = meta or Storage()
        self.context = context or Storage()
        self.context.alerts = []
        self.theme = theme
        self.view = view

        # hooks call
        self.start()
        self.build()
        self.pre_render()

        # aditional hooks
        if not isinstance(hooks, list):
            hooks = [hooks]

        for hook in hooks:
            self.__getattribute__(hook)()

    def start(self):
        pass

    def build(self):
        pass

    def pre_render(self):
        from gluon import current
        from config import Config
        self.config = Config()
        self.response = current.response
        self.request = current.request
        self.context.theme_name = self.config.theme.name

    def render(self, view=None, theme=None):
        if theme:
            self.theme = theme
            self.context.theme_name = theme
        if view:
            self.view = view
        # lançar erro caso nao tenha config e response e render
        theme = self.theme % self.config.theme
        viewfile = "%s.%s" % (self.view, self.request.extension)
        filename = theme + viewfile
        return self.response.render(filename, self.context)
