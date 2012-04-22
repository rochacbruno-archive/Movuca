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


    def cart(self):
        pass

    def addtocart(self):
        pid = self.request.vars.id
        quantity = self.request.vars.quant
        options = self.request.vars.options or {}
        cart_item = self.build_item_to_cart(pid, quantity, options)
        if cart_item:
            self.session.cart[pid] = cart_item

        self.context.js = """alert("%s");""" % str(self.session.cart)

    def removefromcart(self):
        pass

    def countcart(self):
        pass

    def build_item_to_cart(self, pid, quantity, options={}):
        query = (self.db.Article.id == pid) & (self.db.Product.article_id == self.db.Article.id)
        product = self.db(query).select().first()
        print product
        return {"quantity": quantity, "id": pid, "options": options}
