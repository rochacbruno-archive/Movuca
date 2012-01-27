# -*- coding: utf-8 -*-

###############################################################################
# Movuca - The Social CMS
# Copyright (C) 2012  Bruno Cezar Rocha <rochacbruno@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
