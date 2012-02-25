# -*- coding: utf-8 -*-

###############################################################################
# Movuca - The Social CMS
# Copyright (C) 2012  Bruno Cezar Rocha <rochacbruno@gmail.com>

# License: LGPLv3 (http://www.gnu.org/licenses/lgpl.html)
###############################################################################


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
        self.context.content_types = []
        self.context.menus = []
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
        self.context.use_facebook = self.db.config.auth.use_facebook
        self.context.use_google = self.db.config.auth.use_google
        self.context.theme_name = self.config.theme.name

        # define menu table if not defined
        if not "menu" in self.db.tables:
            from datamodel.menu import Menu
            Menu(self.db)
        # load menus
        if not self.context.menus:
            self.context.menus = self.db(self.db.menu.is_active == True).select(cache=(self.db.cache.ram, 300))

        if self.response.flash:
            self.context.alerts.append(self.response.flash)

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
