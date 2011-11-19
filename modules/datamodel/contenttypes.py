# -*- coding: utf-8 -*-

from gluon.dal import Field
from basemodel import ContentModel
from gluon.validators import IS_NOT_EMPTY, IS_IN_SET
from gluon import current


class Article(ContentModel):
    tablename = "article_data"

    def set_properties(self):
        self.fields = [
            Field("markup"),
            Field("body", "text", notnull=True),
        ]

        self.validators = {
            "body": IS_NOT_EMPTY(),
            "markup": IS_IN_SET(["html", "markmin"]),
        }


class CookRecipe(ContentModel):
    tablename = "cookrecipe_data"

    def set_properties(self):
        T = current.T
        self.fields = [
            Field("prep_time", "string"),
            Field("cook_time", "string"),
            Field("difficulty", "string"),
            Field("servings", "double"),
            Field("ingredients", "list:string"),
            Field("instructions", "text"),
            Field("credits", "text"),
        ]

        self.validators = {
            "ingredients": IS_NOT_EMPTY(),
            "instructions": IS_NOT_EMPTY(),
            "difficulty": IS_IN_SET([("1", T("Easy")), ("2", T("Medium")), ("3", T("Hard"))], zero=None)
        }


class CodeRecipe(ContentModel):
    tablename = "coderecipe_data"

    def set_properties(self):
        self.fields = [
            Field("code", "text"),
        ]
