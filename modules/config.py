# -*- coding: utf-8 -*-

###############################################################################
# Movuca - The Social CMS
# Copyright (C) 2012  Bruno Cezar Rocha <rochacbruno@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################


class Config(object):
    """Build and read config on GAE or config.cfg file"""
    def __init__(self, autogetconfig=True):
        from gluon import current
        self.request = current.request
        self.ongae = self.request.env.web2py_runtime_gae
        self.T = current.T
        self.cache = current.cache
        from gluon import DAL
        if self.ongae:
            self._db = DAL("google:datastore")
        else:
            self._db = DAL("sqlite://config_movuca.sqlite")

        self.define_tables()
        if autogetconfig:
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

    def get_config(self, expire=300):
        for table in self.tables:
            result = self._db(self._db[table]).select(cache=(self.cache.ram, expire)).last()
            self.__setattr__(table.split("_")[0],
                             result)

    def get_list(self, table, option):
        options = self.__getattribute__(table)[option]
        assert isinstance(options, list)
        return [(option.split(":")[0], str(self.T(option.split(":")[1]))) for option in options]
