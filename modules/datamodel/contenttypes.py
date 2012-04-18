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


class Video(ContentModel):
    tablename = "video_data"

    def set_properties(self):
        T = current.T
        self.fields = [
            Field("video_source", "string", notnull=True),
            Field("video_embed", "string", notnull=True),
            Field("video_width", "integer", default=600),
            Field("video_height", "integer", default=380),
        ]

        self.labels = {
            "video_embed": "Video embed link",
            "video_source": "Youtube or Vimeo?"
        }

        self.comments = {
            "video_embed": T("Please insert only the link or code ex: vimeo.com/video/345345435 or 345345435")
        }

    def set_validators(self):
        self.db.video_data.video_source.requires = IS_IN_SET(["youtube", "vimeo"])


    def set_fixtures(self):
        ckeditor = CKEditor()
        self.db.article.description.widget = ckeditor.widget
        # virtual field <3
        self.entity.embed_code = Field.Virtual(lambda row: self.get_embed_code(row.video_data.video_source, row.video_data.video_height, row.video_data.video_width, row.video_data.video_embed))


    def get_embed_code(self, source, height, width, video):
        embeds = {
            "youtube": """<iframe width="%(width)s" height="%(height)s" src="http://www.youtube.com/embed/%(video)s" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowfullscreen></iframe>""",
            "vimeo": """<iframe src="http://player.vimeo.com/video/%(video)s" width="%(width)s" height="%(height)s" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe>""",
        }

        if 'http' in video or 'www' in video:
            video = video.rstrip("/")
            video = video.split("/")[-1]

        return embeds.get(source, "ERROR") % locals()


class CookRecipe(ContentModel):
    tablename = "cookrecipe_data"

    def set_fixtures(self):
        self.entity.embed_code = Field.Lazy(lambda row: self.get_embed_code(row.cookrecipe_data.video_source, row.cookrecipe_data.video_embed))

    def get_embed_code(self, source="vimeo", video=""):
        width = 500
        height = 380
        video = video or ""
        source = source or "vimeo"
        embeds = {
            "youtube": """<iframe width="%(width)s" height="%(height)s" src="http://www.youtube.com/embed/%(video)s" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowfullscreen></iframe>""",
            "vimeo": """<iframe src="http://player.vimeo.com/video/%(video)s" width="%(width)s" height="%(height)s" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe>""",
        }

        if 'http' in video or 'www' in video:
            video = video.rstrip("/")
            video = video.split("/")[-1]

        return embeds.get(source, "ERROR") % locals()

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
            Field("video_source", "string"),
            Field("video_embed", "string"),
            Field("active_tab", "string", default="photo"),
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
            "video_source": T("Video source"),
            "video_embed": T("Video link or code"),
            "active_tab": T("By default show video or picture"),
        }

        self.comments = {
            "ingredients": T("Include one item then press enter or click in 'add new' to include more"),
            "instructions": T("You can include pictures."),
            "prep_time": T("The whole time considering ingredients preparation."),
            "cook_time": T("The time needed after all ingredients are ready."),
            "servings": T("How many portions, plates, cups etc?"),
            "credits": T("Include links, names, books etc."),
            "difficulty": T("Easy, Medium or hard to cook?"),
            "video_source": T("Is your video hosted at youtube or vimeo? Leave blank if you have no video."),
            "video_embed": T("Please input only the code or link to the video i.e: http://vimeo.com/454545 or only 454545"),
            "active_tab": T("Choose what to show or leave photo as default"),
        }

    def set_validators(self):
        T = current.T
        self.db.cookrecipe_data.video_source.requires = IS_IN_SET(["youtube", "vimeo"])
        self.db.cookrecipe_data.active_tab.requires = IS_IN_SET([('photo', T("Picture")),("video", T("Video"))])
        self.db.cookrecipe_data.active_tab.default = "photo"

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
