# -*- coding: utf-8 -*-

from movuca import Access, DataBase
from datamodel.article import Article, ContentType
db = DataBase()
auth = Access(db)
content_type = ContentType(db)
article = Article(db)


class Setup(object):
    def run(self):
        pass
