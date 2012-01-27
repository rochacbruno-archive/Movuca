# events

event_info = dict(

new_article={'url_to': CURL('article', 'show', extension=False),
             'url': CURL('person', 'show', extension=False),
             'icon': "attach_round.24.png",
             'title': T(" added a new %(event_to)s"),
             'smalltitle': T("added a new content"),
             },

update_article={'url_to': CURL('article', 'show', extension=False),
                'url': CURL('person', 'show', extension=False),
                'icon': "pen_rounded.24.png",
                'title': T(" updated an %(event_to)s"),
                'smalltitle': T("updated"),
                },

new_contact={'url_to': CURL('person', 'show', extension=False),
             'url': CURL('person', 'show', extension=False),
             'icon': "edge_arrow_right.24.png",
             'title': T(" followed %(event_to)s"),
             'smalltitle': T("followed"),
             },

new_article_comment={'url_to': CURL('article', 'show', extension=False),
                     'url': CURL('person', 'show', extension=False),
                     'icon': "black_board.24.png",
                     'title': T(" commented on %(event_to)s")},

liked={'url_to': CURL('article', 'show', extension=False),
       'url': CURL('person', 'show', extension=False),
       'icon': "like_rounded.24.png",
       'title': T(" liked the %(event_to)s")},

subscribed={'url_to': CURL('article', 'show', extension=False),
            'url': CURL('person', 'show', extension=False),
            'icon': "subscribe.png",
            'title': T(" subscribed to %(event_to)s updates")},

favorited={'url_to': CURL('article', 'show', extension=False),
           'url': CURL('person', 'show', extension=False),
           'icon': "favorite.png",
           'title': T(" favorited the %(event_to)s")},

disliked={'url_to': CURL('article', 'show', extension=False),
          'url': CURL('person', 'show', extension=False),
          'icon': "dislike.png",
          'title': T(" disliked the %(event_to)s")},

new_picture={'url': CURL(),
             'url_to': CURL('article', 'show', extension=False),
             'title': ""},

new_picture_comment={'url': CURL(),
                     'url_to': CURL('article', 'show', extension=False),
                     'title': ""},

wrote_on_wall={'url': CURL('person', 'show', extension=False),
               'url_to': CURL('person', 'show', extension=False),
               'icon': "board.24.png",
               'title': T(" wrote on %(event_to)s board")},
new_article_comment_subscribers={'url_to': CURL('article', 'show', extension=False)},
update_article_subscribers={'url_to': CURL('article', 'show', extension=False)},

               )

current.event_info = event_info
