# coding: utf-8

from gluon.dal import Field
from basemodel import BaseModel


class ProductOrder(BaseModel):
    tablename = "product_order"

    def set_properties(self):
        self.fields = [
            Field("buyer","reference auth_user"),
            Field("seller", "reference auth_user"),
            Field("total_items", "integer"),
            Field("total_value", "double"),
            Field("ship_address", "reference product_address"),
            Field("notes", "text"),
            Field("coupom"),
            Field("discount"),
            Field("discount_type"),
            Field("status"),
        ]


class ProductOrderItems(BaseModel):
    tablename = "product_orderitems"

    def set_properties(self):
        self.fields = [
            Field("order_id", "reference product_order"),
            Field("product_id", "integer"),
            Field("quantity", "integer"),
            Field("current_price", "double"),
            Field("product_options")
        ]

