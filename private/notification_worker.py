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
from movuca import DataBase, User, Mailer
from handlers.notification import Notifier
db = DataBase([User])
notifier = Notifier(db)
mail = Mailer(db)

while True:
    rows = db(db.notification.mail_sent == False).select()
    for row in rows:
        s_to_parse = row.kwargs or "{}"
        kwargs = eval(s_to_parse.strip())  # from str to dict (can user json?)

        notifier.send_email(row.user_id.email, row.event_type, **kwargs)
        row.update_record(mail_sent=True)
        db.commit()
    time.sleep(60)  # check every minute
