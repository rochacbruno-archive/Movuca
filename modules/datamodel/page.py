# coding: utf-8

from gluon.dal import Field
from basemodel import BaseModel
from helpers.customvalidators import COMMA_SEPARATED_LIST
from helpers.widgets import StringListWidget
from gluon.validators import IS_SLUG, IS_NOT_EMPTY, IS_EMPTY_OR, IS_IMAGE, IS_IN_SET, IS_NOT_IN_DB
from helpers.images import THUMB2
from plugin_ckeditor import CKEditor


class Report(BaseModel):
    tablename = "report_content"

    def set_properties(self):
        self.fields = [
            Field("content_type"),
            Field("item_id", "integer"),
            Field("slug"),
            Field("reason"),
            Field("details", "text")
        ]

        reasons = ["Publicação não é vegana",
                   "Violação de direitos autorais",
                   "Falta de referências/fontes",
                   "Conteúdo ofensivo",
                   "Publicação falsa/mentirosa",
                   "Usuário falso",
                   "Usuário ofensivo",
                   "Usuário desrespeita os termos e condições da rede",
                   "Outro motivo (Justifique abaixo)"]

        self.validators = {
            "reason": IS_IN_SET(reasons)
        }

        self.labels = {
            "content_type": self.db.T("Content Type"),
            "item_id": self.db.T("Item id"),
            "slug": self.db.T("Item url slug"),
            "reason": self.db.T("Reason"),
            "details": self.db.T("Details")
        }


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
            Field("redirect_url"),
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
