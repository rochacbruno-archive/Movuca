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
        view="app/generic",
        meta=None,
        context=None
        ):
        from gluon.storage import Storage
        self.meta = meta or Storage()
        self.context = context or Storage()
        self.context.alerts = []
        self.context.content_types = []
        self.context.categories = []
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

    def allowed_content_types(self):
        if self.db.auth:
            allowed_types = self.db.auth.user_groups.values()
            query = (self.db.ContentType.access_control.contains("public"))
            for content_type in allowed_types:
                query |= (self.db.ContentType.access_control.contains(content_type))
            return self.db(query).select(orderby=self.db.ContentType.id)
        else:
            return []

    def allowed_categories(self):
        qry = (self.db.Article.is_active == True) & (self.db.Article.draft == False)
        articles_categories = self.db(qry).select(self.db.article.category_id, cache=(self.db.cache.ram, 300))
        used_categories = []
        for cat in articles_categories:
            if cat.category_id:
                used_categories += cat.category_id
        used_categories = list(set(used_categories))

        allowed_cats = []
        categories = self.db(self.db.Category.id.belongs(used_categories)).select()
        for content in self.context.content_types:
            this_categories = categories.exclude(lambda row: row.content_type == content.id)
            if this_categories:
                allowed_cats.append({"content_type": content.title,
                                     "id": content.id,
                                     "categories": this_categories
                                    })
        return allowed_cats

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
