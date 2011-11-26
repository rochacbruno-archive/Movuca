# -*- coding: utf-8 -*-

from gluon.dal import Field
from basemodel import BaseModel, ContentModel
from gluon.validators import IS_NOT_EMPTY, IS_IN_SET
from gluon import current


class Article(ContentModel):
    tablename = "article_data"

    def set_properties(self):
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
