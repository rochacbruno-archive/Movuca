# -*- coding: utf-8 -*-


class Config(object):
    """Build and read config on GAE or config.cfg file"""
    def __init__(self):
        self.write_tries = 0
        from gluon import current
        self.request = current.request
        self.ongae = self.request.env.web2py_runtime_gae
        if self.ongae:
            from gluon import DAL, Field
            self.db = DAL("google:datastore://config")
            self.db.define_table('application_setup',
                                 Field("appname"))
        else:
            from ConfigParser import RawConfigParser
            self.parser = RawConfigParser()

        self.get_config()  # testing for gae

    def set_config(self, sections):
        self.sections = sections
        for section, options in sections.items():
            self.parser.add_section(section)
            for option, value in options.items():
                self.parser.set(section, option, value)

    def parsed_sections(self):
        # parse to store on gae
        return self.sections

    def write_to(self):
        self.write_tries += 1
        try:
            if self.ongae:
                #self.config.entity.insert(**self.parsed_sections())
                #self.config.entity._db.commit()
                #self.config.entity.insert(appname="testando")
                self.db.application_setup.insert(appname="testando")
                self.db.commit()
            else:
                import os
                filename = os.path.join(self.request.folder, 'private', 'config.cfg')
                configfile = open(filename, 'wb')
                self.parser.write(configfile)
                configfile.flush()
                configfile.close()
            return True
        except Exception:
            if self.write_tries < 6:
                self.write_to()
            else:
                self.write_tries = 0
                return False

    def get_config(self):
        # config = {}
        # self.config.parser.get('db', 'uri')
        # self.config.parser.getboolean('db', 'migrate')
        # return config

        # database
        self.db_migrate = True
        self.db_pool_size = 10
        self.db_uri = "sqlite://config101.sqlite"
        #self.db_uri = 'postgres://tutor:302010@localhost/movuca1'
        self.db_gaeuri = "google:datastore"
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
