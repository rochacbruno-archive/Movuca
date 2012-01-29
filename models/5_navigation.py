response.menu = []

if session.auth:

    logout_url = (T('Logout'), False, CURL('person', 'account', args='logout'), [])
    if session.facebooklogin:
        logout_url = (T('Logout'), False, CURL('person', 'facebook', args='logout'), [])
    elif session.googlelogin:
        logout_url = (T('Logout'), False, CURL('person', 'google', args='logout'), [])

    response.menu.append(
        (T('Create'), False, False, [
                                  (T('Content'), False, False, [
                                          (T('Article'), False, CURL('article', 'new', args='Article'), []),
                                          (T('Cook Recipe'), False, CURL('article', 'new', args='CookRecipe'), []),
                                          (T('Product'), False, CURL('article', 'new', args='Product'), []),
                                  ]),
                                  (T('Group'), False, False, [
                                
                                  ]),
                                  (T('Page'), False, False, [
                                          
                                  ])
                                  ]
                            )
                        )

    # CURL = ''

    response.menu.append(
         (T('Explore'), False, False, [
                                          (T('Find articles'), False, CURL('article', 'search'), []),
                                          (T('All articles'), False, CURL('article', 'list'), []),
                                          (T('Find members'), False, CURL('person', 'search'), []),
                                          (T('All members'), False, CURL('person', 'search', vars=dict(q='@')), []),
                                  ])
    )
    response.menu.append(
         (T('Me'), False, False, [
                                          (T('My profile'), False, CURL('person', 'show'), []),
                                          (T('My Settings'), False, CURL('person', 'account', args='profile'), []),
                                          (T('My content'), False, False, [
                                                 (T('My articles'), False, CURL('article', 'list', vars={'author': session.auth.user.id, 'limitby': '0,50'}), []),
                                                 (T('My drafts'), False, CURL('article', 'list', vars={'author': session.auth.user.id, 'limitby': '0,50'}), []),
                                                 (T('My pictures'), False, CURL('article', 'list', vars={'author': session.auth.user.id, 'limitby': '0,50'}), []),
                                                 (T('My favorited'), False, CURL('article', 'list', vars={'author': session.auth.user.id, 'limitby': '0,50'}), []),
                                                 (T('My liked'), False, CURL('article', 'list', vars={'author': session.auth.user.id, 'limitby': '0,50'}), []),
                                                 (T('My disliked'), False, CURL('article', 'list', vars={'author': session.auth.user.id, 'limitby': '0,50'}), []),
                                                 (T('My subscriptions'), False, CURL('article', 'list', vars={'author': session.auth.user.id, 'limitby': '0,50'}), []),
                                                 (T('My comments'), False, CURL('article', 'list', vars={'author': session.auth.user.id, 'limitby': '0,50'}), []),
                                                 (T('My Recipe Book'), False, CURL('article', 'list', vars={'author': session.auth.user.id, 'limitby': '0,50'}), []),
                                          ]),
                                          (T('My contacts'), False, CURL('person', 'contacts'), []),
                                          (T('My pages'), False, False, []),
                                          (T('My groups'), False, False, []),
                                          (T('My Activities'), False, CURL('person', 'usertimeline'), []),
                                          (T('My Board'), False, CURL('person', 'usertimeline'), []),
                                          (T('My Messages'), False, False, []),
                                          logout_url,
                                  ])
    )
    response.menu.append((DIV(IMG(_src=URL('static', 'images', args='alert.18.png'), alt=T("Alert"), title=T("Notifications")),
                                  " (", SPAN(_id="notification-counter"), ")",
                                  _id="notification-opener",
                                  ), False, False, []))
else:
    response.menu.append((T('Login'), False, CURL('person', 'account', args='login'), []))
    response.menu.append((T('Join'), False, CURL('person', 'account', args='register'), []))

response.menu.append((T('GitHub'), False, "http://github.com/rochacbruno/Movuca", []))
