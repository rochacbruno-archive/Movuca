# -*- coding: utf-8 -*-


response.generic_patterns = ['*']
from gluon.custom_import import track_changes
track_changes(True)

from config import Config
config = Config()
#db = DAL(config.db_uri)
