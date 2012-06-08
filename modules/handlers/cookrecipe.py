# -*- coding: utf-8 -*-

from handlers.base import Base
from gluon import BUTTON, URL, TAG


class CookRecipe(Base):
    def start(self):
        from movuca import DataBase, User
        from datamodel.article import Category, ContentType, Article
        from datamodel.contenttypes import CookRecipeBook
        from datamodel.contenttypes import CookRecipe as CookRecipeModel

        self.db = DataBase([User, ContentType, Category, Article, CookRecipeModel,CookRecipeBook])

    def pre_render(self):
        # obrigatorio ter um config, um self.response|request, que tenha um render self.response.render
        self.response = self.db.response
        self.request = self.db.request
        self.config = self.db.config
        self.session = self.db.session
        self.T = self.db.T
        self.CURL = self.db.CURL
        #self.view = "app/home.html"
        self.context.content_types = self.context.content_types or self.allowed_content_types()
        self.context.categories = self.context.categories = self.allowed_categories()


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
                    return "alert('Error')"
                else:
                    self.db.commit()
                    if not 'show' in self.request.args:
                        return "jQuery('#article_%s').remove();" % str(article_id)
                    else:
                        return BUTTON(TAG.I(_class="icon-plus", _style="margin-right:5px"), self.T("Add to my book"),
                            _class="button button not-on-book btn btn-success addtobookbutton",
                            _onclick="ajax('%s', [], 'addtobookbutton');" % URL('cookrecipe', 'addtobook', args=[self.request.args(0), 'show']))

    def add_to_book_button(self):
        user = self.session.auth.user if self.session.auth else None
        if user:
            already = self.db.CookRecipeBook(article_id=int(self.request.args(0)), user_id=user.id)
            if already:
                bt = BUTTON(TAG.I(_class="icon-minus", _style="margin-right:5px"), self.T("Remove from book!"),
                            _class="button already-on-book btn btn-danger addtobookbutton",
                            _onclick="ajax('%s', [], 'addtobookbutton');" % URL('cookrecipe', 'removefrombook', args=[self.request.args(0), 'show']))
            else:
                bt = BUTTON(TAG.I(_class="icon-plus", _style="margin-right:5px"), self.T("Add to my book"),
                            _class="button button not-on-book btn btn-success addtobookbutton",
                            _onclick="ajax('%s', [], 'addtobookbutton');" % URL('cookrecipe', 'addtobook', args=[self.request.args(0), 'show']))
        else:
            bt = BUTTON(TAG.I(_class="icon-plus", _style="margin-right:5px"), self.T("Add to my book"),
                            _class="button button not-on-book btn btn-success addtobookbutton",
                            _onclick="window.location = '%s';" % URL('person', 'account',
                                 args='login', vars=dict(_next=self.CURL('article', 'show', args=[self.request.args(0), 'show']))))
        return bt

    def book(self):
        user_id = self.request.args(0) or self.db.auth.user_id
        if user_id:
            query = (self.db.CookRecipeBook.user_id == user_id) & (self.db.CookRecipeBook.article_id == self.db.article.id)
            if "q" in self.request.vars:
                query &= self.db.article.search_index.like("%%%s%%" % self.request.vars.q)  
            self.context.book = self.db(query).select()
            self.context.user = self.db.auth_user[user_id]
            self.response.meta.title = "%s | %s" % (
               self.db.T("%s's cook book", self.context.user.nickname.title() or self.context.user.first_name.title()),
               self.db.config.meta.title,
              )
        else:
            redirect(self.CURL('home','index'))

