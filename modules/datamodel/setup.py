# -*- coding: utf-8 -*-

from gluon.dal import Field


class Setup(object):

    def __init__(self):
        self.db_options = [
            Field("uri", "string", notnull=True, default="sqlite://movuca.sqlite"),
            Field("migrate", "boolean", notnull=True, default=True),
            Field("migrate_enabled", "boolean", notnull=True, default=True),
            Field("pool_size", "integer", notnull=True, default=10),
            Field("gaeuri", "string", notnull=True, default="google:datastore"),
            Field("setuptime", "datetime", notnull=True),
        ]

        self.mail_options = [
            Field("server", "string", notnull=True, default="logging"),
            Field("sender", "string", notnull=True, default="mail@domain.com"),
            Field("login", "string", notnull=True, default="teste:1234"),
            Field("setuptime", "datetime", notnull=True),
        ]

        self.auth_options = [
            Field("formstyle", "string", notnull=True, default="divs"),
            Field("photo_source", "list:string", notnull=True, default=["1:upload", "2:gravatar", "3:facebook", "4:twitter", "5:no photo"]),
            Field("gender", "list:string", notnull=True, default=["Male:Male", "Female:Female", "Not specified:Not specified"]),
            Field("privacy", "list:string", notnull=True, default=["1:Public", "2:Visible only for contacts", "3:Private"]),
            Field("setuptime", "datetime", notnull=True),
        ]

        self.crud_options = [
            Field("formstyle", "string", notnull=True, default="divs"),
            Field("setuptime", "datetime", notnull=True),
        ]

        self.theme_options = [
            Field("name", "string", notnull=True, default="basic"),
            Field("setuptime", "datetime", notnull=True),
        ]
