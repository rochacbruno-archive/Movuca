# -*- coding: utf-8 -*-


def install():
    from config import Config
    config = Config()
    config.write_to()
    config.get_config()
    return config.db_uri
