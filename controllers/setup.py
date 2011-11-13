# -*- coding: utf-8 -*-


def install():
    from config import Config
    config = Config()
    config.set_default_config()
    config.get_config()
    return (str(type(config.db)),
            config.db.uri,
            str(type(config.db_options)))


def getlist():
    from config import Config
    config = Config()
    return str(config.get_list('auth', 'privacy'))
    #return config.auth.privacy


def test():
    from config import Config
    config = Config()
    return config.mail.sender
