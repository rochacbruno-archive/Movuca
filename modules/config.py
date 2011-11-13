# -*- coding: utf-8 -*-


class Config(object):
    """Build and read config on GAE or config.cfg file"""
    def __init__(self):
        from gluon import current
        self.request = current.request
        self.ongae = self.request.env.web2py_runtime_gae
        self.T = current.T
        from gluon import DAL
        if self.ongae:
            self._db = DAL("google:datastore")
        else:
            self._db = DAL("sqlite://movucaconfig.sqlite")

        self.define_tables()
        self.get_config()

    def define_tables(self):
        from datamodel.setup import Setup
        setup = Setup()
        self.tables = filter(lambda item: not item.startswith("_"), dir(setup))
        for table in self.tables:
            entity = self._db.define_table(table,
                *setup.__getattribute__(table),
                **dict(migrate="config_%s.table" % table)
            )
            self.__setattr__(table, entity)

    def set_default_config(self):
        now = self.request.now
        for table in self.tables:
            self.__getattribute__(table).insert(setuptime=now)
            self._db.commit()

    def get_config(self):
        for table in self.tables:
            self.__setattr__(table.split("_")[0],
                             self._db(self._db[table]).select().last())

    def get_list(self, table, option):
        options = self._db(self._db["%s_options" % table]).select().last()[option]
        assert isinstance(options, list)
        return [(option.split(":")[0], str(self.T(option.split(":")[1]))) for option in options]

        # database
        #self.db_migrate = True
        #self.db_pool_size = 10
        #self.db_uri = "sqlite://config101.sqlite"
        #self.db_uri = 'postgres://tutor:302010@localhost/movuca1'
        # self.db_gaeuri = "google:datastore"
        # self.db_migrate_enabled = True
        # self.mail_server = 'logging'
        # self.mail_sender = 'teste@teste.com'
        # self.mail_login = 'teste:1234'

        # # auth
        # from gluon import current
        # T = current.T
        # self.auth_formstyle = 'divs'
        # self.auth_photo_source = [
        #                           (1, T("upload")),
        #                           (2, "gravatar"),
        #                           (3, "facebook"),
        #                           (4, "twitter"),
        #                           (5, T("no photo")),
        #                          ]
        # self.auth_gender = [
        #                    ("Male", T("Male")),
        #                    ("Female", T("Female")),
        #                    ("Not specified", T("Not specified")),
        #                    ]

        # self.auth_privacy = [
        #                     (1, T("Public")),
        #                     (2, T("Visible only for contacts")),
        #                     (3, T("Private")),
        #                     ]
        # mail
