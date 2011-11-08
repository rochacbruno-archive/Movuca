# -*- coding: utf-8 -*-


class Config(object):
    def __init__(self):
        # database
        self.db_migrate = True
        self.db_pool_size = 10
        self.db_uri = "sqlite://config.sqlite"
        self.db_migrate_enabled = True
        self.mail_server = 'logging'
        self.mail_sender = 'teste@teste.com'
        self.mail_login = 'teste:1234'

        # auth

        # mail
