# coding: utf-8

from gluon.dal import Field
from basemodel import BaseModel
from helpers.customvalidators import COMMA_SEPARATED_LIST
from helpers.widgets import StringListWidget
from gluon.validators import IS_SLUG, IS_NOT_EMPTY, IS_EMPTY_OR, IS_IMAGE, IS_IN_SET, IS_NOT_IN_DB
from helpers.images import THUMB2
from plugin_ckeditor import CKEditor


class Page(BaseModel):
    tablename = "internal_page"

    def set_properties(self):
        ckeditor = CKEditor()
        self.fields = [
            Field("title", unique=True),
            Field("description", "text"),
            Field("page_content", "text"),
            Field("picture", "upload"),
            Field("thumbnail", "upload"),
            Field("tags", "list:string"),
            Field("slug"),
            Field("page_scope", "list:string", default=["public", "sitemap"]),
            Field("visibility"),
            Field("text_language", default="pt-br"),
        ]

        self.widgets = {
            "tags": StringListWidget.widget,
            "page_content": ckeditor.widget
        }

        self.comments = {
          "page_scope": "public, sitemap, members"
        }

        self.computations = {
            "slug": lambda r: IS_SLUG()(r.title)[0],
            "thumbnail": lambda r: THUMB2(r.picture, 200, 200)
        }

        self.validators = {
            "title": [IS_NOT_EMPTY(), IS_NOT_IN_DB(self.db, "internal_page.title")],
            "description": IS_NOT_EMPTY(),
            "picture": IS_EMPTY_OR(IS_IMAGE()),
            "tags": COMMA_SEPARATED_LIST(),
            "text_language": IS_IN_SET(["en", "pt-br", "es"])
        }
