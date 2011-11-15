# -*- coding: utf-8 -*-


class Config(object):
    """Build and read config on GAE or config.cfg file"""
    def __init__(self):
        from gluon import current
        self.request = current.request
        self.ongae = self.request.env.web2py_runtime_gae
        self.T = current.T
        self.cache = current.cache
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
        # from gluon.storage import Storage
        # self.results = Storage()
        for table in self.tables:
            result = self._db(self._db[table]).select(cache=(self.cache.ram, 300)).last()
            self.__setattr__(table.split("_")[0],
                             result)
            # self.results[table.split("_")[0]] = Storage(result.as_dict())

    # def get_dict(self):
    #     #self.results.get_list = lambda table, option: ['1', '2']
    #     self.results.get_list = lambda options: \
    #         [(option.split(":")[0], str(self.T(option.split(":")[1]))) for option in options]
    #     return self.results

    def get_list(self, table, option):
        options = self.__getattribute__(table)[option]
        assert isinstance(options, list)
        return [(option.split(":")[0], str(self.T(option.split(":")[1]))) for option in options]
