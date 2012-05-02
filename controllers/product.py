# coding: utf-8

from handlers.product import ProductHandler

session.cart = session.cart or {}

def cart():
	pass

def addtocart():
    product = ProductHandler("addtocart")
    return product.context.js

def clearcart():
    product = ProductHandler("clearcart")
    return str(session.cart)

def removefromcart():
	pass

def countcart():
	pid = request.args(0) or None
	if pid:
		pass