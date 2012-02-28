# -*- coding: utf-8 -*-

from gluon.dal import Field
from basemodel import BaseModel, ContentModel
from gluon.validators import IS_NOT_EMPTY, IS_IN_SET, IS_LENGTH, IS_EMPTY_OR
from gluon import current
from plugin_ckeditor import CKEditor
from helpers.widgets import ListWidget


class Article(ContentModel):
    tablename = "article_data"

    def set_properties(self):
        ckeditor = CKEditor()
        T = self.db.T
        self.fields = [
            Field("markup", default="html"),
            Field("body", "text", notnull=True),
        ]

        self.validators = {
            "body": IS_NOT_EMPTY(),
            #"markup": IS_IN_SET(["html", "markmin"], zero=None),
        }

        self.labels = {
            "body": T("Article Text")
        }

        self.visibility = {
            "markup": (False, False)
        }

        self.widgets = {
            "body": ckeditor.widget
        }


class Question(ContentModel):
    tablename = "question_data"

    def set_properties(self):
        self.fields = [
            Field("answer", "integer"),
        ]

        self.visibility = {
            "answer": (False, False)
        }

    def set_fixtures(self):
        ckeditor = CKEditor()
        self.db.article.description.widget = ckeditor.widget


class CookRecipe(ContentModel):
    tablename = "cookrecipe_data"

    def set_properties(self):
        ckeditor = CKEditor()
        T = current.T
        self.fields = [
            Field("prep_time", "string", notnull=True),
            Field("cook_time", "string", notnull=True),
            Field("difficulty", "string", notnull=True),
            Field("servings", "double", notnull=True),
            Field("ingredients", "list:string", notnull=True),
            Field("instructions", "text", notnull=True),
            Field("credits", "text"),
        ]

        self.validators = {
            "ingredients": IS_NOT_EMPTY(),
            "instructions": IS_NOT_EMPTY(),
            "difficulty": IS_IN_SET([("1", T("Easy")), ("2", T("Medium")), ("3", T("Hard"))], zero=None),
            "prep_time": IS_NOT_EMPTY(),
            "cook_time": IS_NOT_EMPTY(),
            "servings": IS_NOT_EMPTY(),
        }

        self.widgets = {
            "instructions": ckeditor.widget,
            "ingredients": ListWidget.widget
        }

        self.labels = {
            "instructions": T("Preparation instructions"),
            "ingredients": T("Ingredients"),
            "prep_time": T("Preparation time"),
            "cook_time": T("Cooking time"),
            "difficulty": T("Difficulty"),
            "servings": T("Servings"),
            "credits": T("credits"),
        }

        self.comments = {
            "ingredients": T("Include one item then press enter or click in 'add new' to include more"),
            "instructions": T("You can include pictures."),
            "prep_time": T("The whole time considering ingredients preparation."),
            "cook_time": T("The time needed after all ingredients are ready."),
            "servings": T("How many portions, plates, cups etc?"),
            "credits": T("Include links, names, books etc."),
            "difficulty": T("Easy, Medium or hard to cook?"),
        }


class CookRecipeBook(BaseModel):
    tablename = "cookrecipe_book"

    def set_properties(self):
        self.fields = [
            Field("article_id", "reference article", notnull=True),
            Field("user_id", "reference auth_user", notnull=True),
        ]


class CodeRecipe(ContentModel):
    tablename = "coderecipe_data"

    def set_properties(self):
        self.fields = [
            Field("code", "text"),
        ]


class Product(ContentModel):
    tablename = "product_data"

    def set_properties(self):
        ckeditor = CKEditor()
        T = current.T
        self.fields = [
            Field("price", "double", notnull=True, default=0),
            Field("manufacturer", "string", notnull=True),
            Field("in_stock", "boolean", notnull=True, default=True),
            Field("info", "text", notnull=True),
            Field("product_size", "string"),
        ]

        self.validators = {
            "info": IS_NOT_EMPTY(),
            "manufacturer": IS_NOT_EMPTY(),
            "product_size": IS_EMPTY_OR(IS_IN_SET([("L", T("Large")),
                                           ("M", T("Medium")),
                                           ("S", T("Small"))],
                                           zero=None)),
        }

        self.widgets = {
            "info": ckeditor.widget
        }

        self.labels = {
            "price": T("Product Price"),
            "manufacturer": T("Manufacturer name or brand"),
            "in_stock": T("Available?"),
            "info": T("Product specs"),
            "product_size": T("Product size"),
        }
