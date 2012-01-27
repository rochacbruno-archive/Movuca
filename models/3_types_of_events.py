# events

event_info = dict(

new_article={'url_to': CURL('article', 'show', extension=False, scheme=True, host=True),
             'url': CURL('person', 'show', extension=False, scheme=True, host=True),
             'icon': "attach_round.24.png",
             'title': T(" added a new %(event_to)s"),
             'smalltitle': T("added a new content"),
             },

update_article={'url_to': CURL('article', 'show', extension=False, scheme=True, host=True),
                'url': CURL('person', 'show', extension=False, scheme=True, host=True),
                'icon': "pen_rounded.24.png",
                'title': T(" updated an %(event_to)s"),
                'smalltitle': T("updated"),
                },

new_contact={'url_to': CURL('person', 'show', extension=False, scheme=True, host=True),
             'url': CURL('person', 'show', extension=False, scheme=True, host=True),
             'icon': "edge_arrow_right.24.png",
             'title': T(" followed %(event_to)s"),
             'smalltitle': T("followed"),
             },

new_article_comment={'url_to': CURL('article', 'show', extension=False, scheme=True, host=True),
                     'url': CURL('person', 'show', extension=False, scheme=True, host=True),
                     'icon': "black_board.24.png",
                     'title': T(" commented on %(event_to)s")},

liked={'url_to': CURL('article', 'show', extension=False, scheme=True, host=True),
       'url': CURL('person', 'show', extension=False, scheme=True, host=True),
       'icon': "like_rounded.24.png",
       'title': T(" liked the %(event_to)s")},

subscribed={'url_to': CURL('article', 'show', extension=False, scheme=True, host=True),
            'url': CURL('person', 'show', extension=False, scheme=True, host=True),
            'icon': "subscribe.png",
            'title': T(" subscribed to %(event_to)s updates")},

favorited={'url_to': CURL('article', 'show', extension=False, scheme=True, host=True),
           'url': CURL('person', 'show', extension=False, scheme=True, host=True),
           'icon': "favorite.png",
           'title': T(" favorited the %(event_to)s")},

disliked={'url_to': CURL('article', 'show', extension=False, scheme=True, host=True),
          'url': CURL('person', 'show', extension=False, scheme=True, host=True),
          'icon': "dislike.png",
          'title': T(" disliked the %(event_to)s")},

new_picture={'url': CURL(),
             'url_to': CURL('article', 'show', extension=False, scheme=True, host=True),
             'title': ""},

new_picture_comment={'url': CURL(),
                     'url_to': CURL('article', 'show', extension=False, scheme=True, host=True),
                     'title': ""},

wrote_on_wall={'url': CURL('person', 'show', extension=False, scheme=True, host=True),
               'url_to': CURL('person', 'show', extension=False, scheme=True, host=True),
               'icon': "board.24.png",
               'title': T(" wrote on %(event_to)s board")},
new_article_comment_subscribers={'url_to': CURL('article', 'show', extension=False, scheme=True, host=True)},
update_article_subscribers={'url_to': CURL('article', 'show', extension=False, scheme=True, host=True)},

               )

current.event_info = event_info
