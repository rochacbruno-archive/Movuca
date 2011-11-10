# -*- coding: utf-8 -*-


class Config(object):
    def __init__(self):
        # database
        self.db_migrate = True
        self.db_pool_size = 10
        self.db_uri = "sqlite://config100.sqlite"#'postgres://tutor:302010@localhost/movuca1'#"sqlite://config100.sqlite"
        self.db_migrate_enabled = True
        self.mail_server = 'logging'
        self.mail_sender = 'teste@teste.com'
        self.mail_login = 'teste:1234'

        # auth
        from gluon import current
        T = current.T
        self.auth_formstyle = 'divs'
        self.auth_photo_source = [
                                  (1, T("upload")),
                                  (2, "gravatar"),
                                  (3, "facebook"),
                                  (4, "twitter"),
                                  (5, T("no photo")),
                                 ]
        self.auth_gender = [
                           ("Male", T("Male")),
                           ("Female", T("Female")),
                           ("Not specified", T("Not specified")),
                           ]

        self.auth_privacy = [
                            (1, T("Public")),
                            (2, T("Visible only for contacts")),
                            (3, T("Private")),
                            ]
        # mail
