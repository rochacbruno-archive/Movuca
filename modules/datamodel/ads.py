# -*- coding: utf-8 -*-

from gluon.dal import Field
from basemodel import BaseModel
from gluon.validators import *
from helpers.images import THUMB2


class Ads(BaseModel):
    tablename = "ads"

    def set_properties(self):
        T = self.db.T
        self.fields = [
                      # main
                      Field("title", "string"),
                      Field("description", "text"),
                      Field("picture", "upload"),
                      Field("thumbnail", "upload"),
                      Field("link", "string"),
                      Field("place", "string")
                     ]

        self.computations = {
            "thumbnail": lambda r: THUMB2(r['picture'], gae=self.db.request.env.web2py_runtime_gae)
        }

        self.validators = {
          "title": IS_NOT_EMPTY(),
          "description": IS_LENGTH(255, 10),
          "picture": IS_IMAGE(),
          "place": IS_IN_SET(["top_slider", "top_banner", "bottom_banner", "left_sidebar", "right_sidebar", "inside_article", "user_profile"], zero=None)
        }
