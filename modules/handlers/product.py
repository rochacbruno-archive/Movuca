# coding: utf-8

from handlers.base import Base

class ProductHandler(Base):
    def start(self):
        from movuca import DataBase, User
        from datamodel.article import Category, ContentType, Article
        from datamodel.contenttypes import Product
        from datamodel.product import ProductOrder, ProductOrderItems

        self.db = DataBase([User, ContentType, Category, Article, Product, ProductOrder, ProductOrderItems])

    def pre_render(self):
        self.response = self.db.response
        self.request = self.db.request
        self.config = self.db.config
        self.session = self.db.session
        self.T = self.db.T
        self.CURL = self.db.CURL
        self.context.content_types = self.context.content_types or self.allowed_content_types()
        self.context.categories = self.context.categories = self.allowed_categories()


    def cart(self):
        pass

    def addtocart(self):
        pid = self.request.vars.id
        quantity = self.request.vars.quant
        if int(quantity) < 0:
            quantity = 0
        options = self.request.vars.options or {}
        cart_item = self.build_item_to_cart(int(pid), int(quantity), options)
        if cart_item:
            self.session.cart[int(pid)] = cart_item

        if int(quantity):
            js = """$('.incartinfo').show();$('.addtext').text('update cart');$('#quant').val('%s');""" % int(quantity) or 1
        else:
            js = """$('.incartinfo').hide();$('.addtext').text('add to cart');$('#quant').val('1');"""

        self.context.js = js

    def removefromcart(self):
        pass

    def clearcart(self):
        self.session.cart = {}

    def countcart(self):
        pass

    def build_item_to_cart(self, pid, quantity, options={}):
        query = (self.db.Article.id == pid) & (self.db.Product.article_id == self.db.Article.id)
        product = self.db(query).select().first()
        return {"quantity": int(quantity), "id": int(pid), "options": options}
