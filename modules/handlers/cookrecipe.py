# -*- coding: utf-8 -*-

from handlers.base import Base
from gluon import BUTTON, URL, TAG


class CookRecipe(Base):
    def start(self):
        from movuca import DataBase, User
        from datamodel.article import Category, ContentType, Article
        from datamodel.contenttypes import CookRecipeBook

        self.db = DataBase([User, ContentType, Category, Article, CookRecipeBook])

    def pre_render(self):
        # obrigatorio ter um config, um self.response|request, que tenha um render self.response.render
        self.response = self.db.response
        self.request = self.db.request
        self.config = self.db.config
        self.session = self.db.session
        self.T = self.db.T
        self.CURL = self.db.CURL
        #self.view = "app/home.html"

    def add_to_book(self):
        user = self.session.auth.user if self.session.auth else None
        if user:
            try:
                article_id = int(self.request.args(0))
            except Exception:
                article_id = False

            if article_id:
                try:
                    self.context.bookitem = self.db.CookRecipeBook.update_or_insert(article_id=article_id, user_id=user.id)
                except Exception, e:
                    self.context.error = str(e)
                    self.db.rollback()
                else:
                    self.db.commit()

    def remove_from_book(self):
        user = self.session.auth.user if self.session.auth else None
        if user:
            try:
                article_id = int(self.request.args(0))
            except Exception:
                article_id = False

            if article_id:
                try:
                    query = (self.db.CookRecipeBook.article_id == int(self.request.args(0))) & (self.db.CookRecipeBook.user_id == user.id)
                    self.db(query).delete()
                except Exception, e:
                    self.context.error = str(e)
                    self.db.rollback()
                else:
                    self.db.commit()

    def add_to_book_button(self):
        user = self.session.auth.user if self.session.auth else None
        if user:
            already = self.db.CookRecipeBook(article_id=int(self.request.args(0)), user_id=user.id)
            if already:
                bt = BUTTON(TAG.I(_class="icon-minus", _style="margin-right:5px"), self.T("On your book!"),
                            _class="button already-on-book btn btn-success addtobookbutton",
                            _onclick="ajax('%s', [], 'addtobookbutton');" % URL('cookrecipe', 'removefrombook', args=self.request.args(0)))
            else:
                bt = BUTTON(TAG.I(_class="icon-plus", _style="margin-right:5px"), self.T("Add to my book"),
                            _class="button button not-on-book btn btn-info addtobookbutton",
                            _onclick="ajax('%s', [], 'addtobookbutton');" % URL('cookrecipe', 'addtobook', args=self.request.args(0)))
        else:
            bt = BUTTON(TAG.I(_class="icon-plus", _style="margin-right:5px"), self.T("Add to my book"),
                            _class="button button not-on-book btn btn-info addtobookbutton",
                            _onclick="window.location = '%s';" % URL('person', 'account',
                                 args='login', vars=dict(_next=self.CURL('article', 'show', args=self.request.args(0)))))
        return bt
