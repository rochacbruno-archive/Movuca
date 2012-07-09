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

from urllib2 import urlopen, build_opener
import json
import time
import datetime

#URL = "https://graph.facebook.com/fql?q=SELECT url, normalized_url, share_count, like_count, comment_count, total_count,commentsbox_count, comments_fbid, click_count FROM link_stat WHERE url= 'http://www.menuvegano.com.br/article/show/%(id)s/%(slug)s'"
URL = "https://graph.facebook.com/fql?q=SELECT%20url,%20normalized_url,%20share_count,%20like_count,%20comment_count,%20total_count,commentsbox_count,%20comments_fbid,%20click_count%20FROM%20link_stat%20WHERE%20url=%20%27http://www.menuvegano.com.br/article/show/{{ID}}/{{SLUG}}%27"
from movuca import DataBase, User
from datamodel.article import Article, Category, ContentType
db = DataBase([User, ContentType, Category, Article])

opener = build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
#response = opener.open('wwww.stackoverflow.com')

while True:
    articles = db((db.article.draft == False) & (db.article.is_active == True)).select()
    for article in articles:
        #print URL.replace("{{ID}}", str(article.id)).replace("{{SLUG}}", article.slug)
        try:
            #data = urlopen(URL % article).read()
            data = opener.open(URL.replace("{{ID}}", str(article.id)).replace("{{SLUG}}", article.slug)).read()
            jsondata = json.loads(data)
            likes = jsondata['data'][0]['total_count']
            #print likes
            #print bool(likes)
            #message = ["Likes not updated", "null", article.id, article.slug, datetime.datetime.now(), "\n"]
            message = None
            if likes and int(likes) != int(article.likes):
                article.update_record(likes=likes)
                message = ["Likes updated", likes, article.id, article.slug, datetime.datetime.now(), "\n"]
        except Exception, e:
            #print str(e)
            db.rollback()
            message = ["Exception: %s" % str(e), "null", article.id, article.slug, datetime.datetime.now(), "\n"]
        else:
            db.commit()
        if message:
            try:
                with open("update_likes.log", "a") as log:
                    log.write(",".join([str(item) for item in message]))
            except Exception, e:
                print str(e)

    time.sleep(300)  # check every 5 minutes
