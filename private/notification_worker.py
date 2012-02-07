# -*- coding: utf-8 -*-

#####################################################################################
#
# set worker to 'queue' in config.notification_options
# in a separate terminal run
#
# python web2py.py -S demo -M -N -R applications/demo/private/notification_worker.py
#
#
######################################################################################

import time
import datetime
from movuca import DataBase, User, Mailer
from handlers.notification import Notifier
db = DataBase([User])
notifier = Notifier(db)
mail = Mailer(db)

while True:
    rows = db(db.notification.mail_sent == False).select()
    for row in rows:
        email = row.user_id.email
        try:
            s_to_parse = row.kwargs or "{}"
            kwargs = eval(s_to_parse.strip())  # from str to dict (can user json?)
            if notifier.send_email(email, row.event_type, bypass=True, **kwargs):
                row.update_record(mail_sent=True)
                message = ["success:", email, row.event_type, row.id, datetime.datetime.now(), "\n"]
            else:
                message = ["failed on send_mail", email, row.event_type, row.id, datetime.datetime.now(), "\n"]
        except Exception, e:
            db.rollback()
            message = ["Exception: %s" % str(e), email, row.event_type, row.id, datetime.datetime.now(), "\n"]
        else:
            db.commit()

        try:
            with open("notification_worker.log", "a") as log:
                log.write(",".join([str(item) for item in message]))
        except Exception, e:
            print str(e)

    time.sleep(60)  # check every minute
