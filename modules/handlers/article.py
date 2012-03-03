# -*- coding: utf-8 -*-

from handlers.base import Base
from gluon import SQLFORM, redirect, A, IMG, SPAN, URL, CAT, UL, LI, DIV, XML, H4, H5, LABEL, FORM, INPUT, BR, TAG, MARKMIN
from gluon.validators import IS_SLUG, IS_IN_DB, IS_EMAIL
from helpers.images import THUMB2
from plugin_paginator import Paginator, PaginateSelector, PaginateInfo
import os


class Article(Base):
    def start(self):
        from movuca import DataBase, User, UserTimeLine
        from datamodel.article import Category, Article, ContentType, Favoriters, Subscribers, Likers, Dislikers, Comments, CommentVotes
        self.db = DataBase([User, UserTimeLine, ContentType, Category, Article, Favoriters, Subscribers, Likers, Dislikers, Comments, CommentVotes])
        from handlers.notification import Notifier
        self.notifier = Notifier(self.db)
        self.count_votes_results = {}

    def pre_render(self):
        # obrigatorio ter um config, um self.response|request, que tenha um render self.response.render
        self.response = self.db.response
        self.request = self.db.request
        self.config = self.db.config
        self.session = self.db.session
        self.T = self.db.T
        self.CURL = self.db.CURL
        self.get_image = self.db.get_image
        self.context.theme_name = self.config.theme.name
        #self.view = "app/home.html"
        self.context.content_types = self.context.content_types or self.db(self.db.ContentType).select()

    def lastest_articles(self):
        from helpers.article import latest_articles
        self.context.latest_articles = latest_articles(self.db)

    def related_articles(self):
        from helpers.article import related_articles
        related_articles = related_articles(self.db, self.context.article.tags, self.context.article.category_id, self.context.article.id)
        if related_articles:
            self.context.related_articles = UL(*[LI(
                                              DIV(
                                                IMG(_src=self.get_image(related.thumbnail, related.content_type_id.identifier), _width=100, _height=100, _style="max-height:100px;"),
                                              A(related.title, _href=self.CURL('article', 'show', args=[related.id, related.slug])), _class="thumbnail"),
                                              **{'_class': "span2", '_data-url': self.CURL('article', 'show', args=[related.id, related.slug])}
                                              ) for related in related_articles],
                                              **dict(_class="related-articles thumbnails"))
        else:
            self.context.related_articles = False

    def count_votes(self, comment_id):
        if comment_id not in self.count_votes_results:
            rows = self.context.commentvotes.find(lambda row: row.article_comment_votes.comment_id == comment_id)
            up = []
            down = []
            for row in rows:
                if row.article_comment_votes.vote == 0:
                    down.append(row.article_comment_votes.user_id)
                else:
                    up.append(row.article_comment_votes.user_id)
            lenup = len(up)
            lendown = len(down)
            count = lenup - lendown
            self.count_votes_results[comment_id] = dict(up=up, down=down, lenup=lenup, lendown=lendown, count=count)
        return self.count_votes_results[comment_id]

    def showcomment(self):
        comment_id = self.request.args(0) or redirect(self.CURL('home', 'index'))
        comment = self.db.Comments[comment_id]
        self.context.commentvotes = self.db((self.db.CommentVotes.comment_id == self.db.Comments.id) & \
                                            (self.db.Comments.id == comment.id)).select()
        self.context.article = comment.article_id
        self.context.comments = DIV(
                  UL(BR(),
                      *[LI(
                          DIV(
                          DIV(
                            A(iicon('arrow-up'), _class="vote" if self.db.auth.user_id not in self.count_votes(comment.id)["up"] else "vote votedisabled", **{"_data-url": URL('article', 'votecomment', vars=dict(comment=comment.id, vote=1))}),
                            BR(),
                            SPAN(self.count_votes(comment.id)["count"], _id="countvote_%s" % comment.id, _class="countvote label label-success" if self.count_votes(comment.id)["count"] > 0 else "countvote label label-important" if self.count_votes(comment.id)["count"] < 0 else  "countvote label label-info"),
                            BR(),
                            A(iicon('arrow-down'), _class="vote" if self.db.auth.user_id not in self.count_votes(comment.id)["down"] else "vote votedisabled", **{"_data-url": URL('article', 'votecomment', vars=dict(comment=comment.id, vote=0))}),
                            _class="comment_vote_buttons span1"
                            ),
                          DIV(
                           H5(
                              A(
                                comment.nickname or comment.user_id,
                               _href=self.CURL('person', 'show', args=comment.nickname or comment.user_id, extension=False),
                               _class="link_to_user",
                               **{"_data-id": comment.user_id}
                               ),
                              XML("&nbsp; "),
                              A(
                                self.db.pdate(comment.commenttime),
                               _href=self.CURL('article', 'showcomment', args=comment.id, extension=False))
                             ),
                            DIV(
                               XML(comment.comment_text),
                               **{'_class': 'editable commentitem',
                                  '_data-object': 'comment',
                                  '_data-id': comment.id,
                                  '_id': "comment_%s" % comment.id}
                             ),
                            DIV(
                               A(iicon("share-alt"), self.T("reply")),
                               _class="pull-right reply-button",
                               **{"_data-url": URL('article', 'addreply')}
                              ) if self.db.auth.user else DIV(),
                            _class="comment_div span10"
                            ),
                            _class="row"
                            ),
                            self.get_comment_replies(comment),
                            _class="comment_li",
                            **{"_data-cid": comment.id}
                          ) for comment in [comment]],
                  **dict(_class="comment_ul")),
                  _class="internal-comments article-box",
                  _id="internal-comments"

                  )

    def comments(self):
        if not self.context.article:
            self.get()
            self.context.content_types = [""]
            self.context.menus = [""]

        comment_system = {
            "internal": self.comment_internal,
            "disqus": self.comment_disqus,
            "intense": self.comment_intense,
            "facebook": self.comment_facebook,
            "disabled": self.comment_disabled
        }

        self.context.comments = comment_system[self.config.comment.system]()

    def comment_disabled(self):
        return " "

    def isanswer(self):
        empty = [""]
        self.context.alerts = empty
        self.context.menus = empty
        self.context.content_types = empty
        comment_id = self.request.args(0)
        comment = self.db.Comments[comment_id]
        self.context.article = self.db.Article[comment.article_id]
        if self.context.article and self.context.article.author == self.db.auth.user_id:
            content, self.context.article_data = self.get_content(self.context.article.content_type_id.classname, self.context.article.id)
            self.context.article_data.update_record(answer=comment_id)
        redirect(self.request.vars._next)

    def isnotanswer(self):
        empty = [""]
        self.context.alerts = empty
        self.context.menus = empty
        self.context.content_types = empty
        comment_id = self.request.args(0)
        comment = self.db.Comments[comment_id]
        self.context.article = self.db.Article[comment.article_id]
        if self.context.article and self.context.article.author == self.db.auth.user_id:
            content, self.context.article_data = self.get_content(self.context.article.content_type_id.classname, self.context.article.id)
            self.context.article_data.update_record(answer=None)
        redirect(self.request.vars._next)

    def is_lenght(self, form):
        if len(form.vars.comment_text) < 5:
            form.errors.comment_text = self.T("Comment too short")
            self.context.alerts.append(form.errors.comment_text)
        if len(form.vars.comment_text) > 1024:
            form.errors.comment_text = self.T("Comment too long")
            self.context.alerts.append(form.errors.comment_text)

    def comment_internal(self):
        is_author = False
        if self.session.auth and self.session.auth.user:
            is_author = True if self.session.auth.user.id == self.context.article.author else False
            self.db.Comments.article_id.default = self.context.article.id
            self.db.Comments.user_id.default = self.session.auth.user.id
            self.db.Comments.commenttime.default = self.request.now
            self.db.Comments.comment_text.label = self.T("Post your comment")
            self.db.Comments.comment_text.requires = IS_EMAIL()
            from plugin_ckeditor import CKEditor
            ckeditor = CKEditor()
            self.db.Comments.comment_text.widget = ckeditor.basicwidget
            form = SQLFORM(self.db.Comments, formstyle='divs')
            submit_button = form.elements(_type='submit')[0]
            submit_button['_class'] = "btn btn-info"
            submit_button['_value'] = self.T("Post comment")
            if form.process(message_onsuccess=self.T('Comment included'), onvalidation=self.is_lenght).accepted:
                self.new_article_event('new_article_comment',
                                        self.session.auth.user,
                                        data={'event_text': form.vars.comment_text,
                                              'event_link': form.vars.nickname or form.vars.user_id,
                                              'event_image': self.get_image(None, 'user', themename=self.context.theme_name, user=self.session.auth.user),
                                              'event_link_to': "%s/%s#comment_%s" % (self.context.article.id, self.context.article.slug, form.vars.id)})

        else:
            form = CAT(A(self.T("Login to post"),
                     _class="button btn",
                     _href=self.CURL('default', 'user',
                                  args='login',
                                  vars=dict(_next=self.CURL('article', 'show',
                                       args=[self.context.article.id,
                                             self.context.article.slug])))),
                       BR(),
                       BR())

        if 'commentlimitby' in self.request.vars:
            try:
                limitby = [int(item) for item in self.request.vars.commentlimitby.split(',')]
            except:
                limitby = (0, 5)
        else:
            limitby = (0, 5)

        orderby = ~self.db.Comments.created_on
        if "commentorder" in self.request.vars:
            if self.request.vars.commentorder == "oldest":
                orderby = self.db.Comments.created_on

        comment_set = self.db((self.db.Comments.article_id == self.context.article.id) & (self.db.Comments.parent_id == None))
        comments = comment_set.select(orderby=orderby, limitby=limitby)

        if comments and is_author:
            edit_in_place = ckeditor.bulk_edit_in_place(["comment_%(id)s" % comment for comment in comments], URL('editcomment'))
        elif comments and self.session.auth and self.session.auth.user:
            usercomments = comments.find(lambda row: row.user_id == self.session.auth.user.id)
            if usercomments:
                edit_in_place = ckeditor.bulk_edit_in_place(["comment_%(id)s" % comment for comment in usercomments], URL('editcomment'))
            else:
                edit_in_place = ('', '')
        else:
            edit_in_place = ('', '')

        self.context.lencomments = comment_set.count()

        def showmore(anchor, limitby=limitby, lencomments=self.context.lencomments):
            if lencomments > limitby[1]:
                # rvars = {"commentlimitby": "0,%s" % (limitby[1] + 10)}
                self.request.vars['commentlimitby'] = "0,%s" % (limitby[1] + 10)
                return A(self.T('show more comments'), _class="button btn", _style="width:97%;", _href=self.CURL(args=self.request.args, vars=self.request.vars, anchor=anchor))
            else:
                return ''

        self.context.commentvotes = self.db((self.db.CommentVotes.comment_id == self.db.Comments.id) & \
                                            (self.db.Comments.article_id == self.context.article.id)).select()

        count_votes_results = {}  # it is a cache for the list comp

        def count_votes(comment_id):
            if comment_id not in count_votes_results:
                rows = self.context.commentvotes.find(lambda row: row.article_comment_votes.comment_id == comment_id)
                up = []
                down = []
                for row in rows:
                    if row.article_comment_votes.vote == 0:
                        down.append(row.article_comment_votes.user_id)
                    else:
                        up.append(row.article_comment_votes.user_id)
                lenup = len(up)
                lendown = len(down)
                count = lenup - lendown
                count_votes_results[comment_id] = dict(up=up, down=down, lenup=lenup, lendown=lendown, count=count)
            return count_votes_results[comment_id]

        if "commentorder" in self.request.vars:
            if self.request.vars.commentorder == "upvoted":
                comments = comments.sort(lambda row: ~count_votes(row.id)["count"])
            if self.request.vars.commentorder == "downvoted":
                comments = comments.sort(lambda row: count_votes(row.id)["count"])

        return DIV(
                  H4(IMG(_src=URL('static', '%s/images/icons' % self.context.theme_name, args='board.24.png')), self.T("Comments"), " (%s)" % self.context.lencomments),
                  UL(form,
                     DIV(self.T("order by: "),
                        A(self.T("newest "), _href=self.CURL(args=self.request.args, anchor="internal-comments", vars=dict(commentorder="newest", commentlimitby=self.request.vars.commentlimitby))),
                        A(self.T("oldest "), _href=self.CURL(args=self.request.args, anchor="internal-comments", vars=dict(commentorder="oldest", commentlimitby=self.request.vars.commentlimitby))),
                         A(self.T("upvoted "), _href=self.CURL(args=self.request.args, anchor="internal-comments", vars=dict(commentorder="upvoted", commentlimitby=self.request.vars.commentlimitby))),
                         A(self.T("downvoted"), _href=self.CURL(args=self.request.args, anchor="internal-comments", vars=dict(commentorder="downvoted", commentlimitby=self.request.vars.commentlimitby))),
                        _class="pull-right",
                        _id="comment_order") if len(comments) > 1 else DIV(),
                     BR(),
                      *[LI(
                          DIV(
                          DIV(
                            A(iicon('arrow-up'), _class="vote" if self.db.auth.user_id not in count_votes(comment.id)["up"] else "vote votedisabled", **{"_data-url": URL('article', 'votecomment', vars=dict(comment=comment.id, vote=1))}),
                            BR(),
                            SPAN(count_votes(comment.id)["count"], _id="countvote_%s" % comment.id, _class="countvote label label-success" if count_votes(comment.id)["count"] > 0 else "countvote label label-important" if count_votes(comment.id)["count"] < 0 else  "countvote label label-info"),
                            BR(),
                            A(iicon('arrow-down'), _class="vote" if self.db.auth.user_id not in count_votes(comment.id)["down"] else "vote votedisabled", **{"_data-url": URL('article', 'votecomment', vars=dict(comment=comment.id, vote=0))}),
                            _class="comment_vote_buttons span1"
                            ),
                          DIV(
                           H5(
                              A(
                                comment.nickname or comment.user_id,
                               _href=self.CURL('person', 'show', args=comment.nickname or comment.user_id),
                               _class="link_to_user",
                               **{"_data-id": comment.user_id}
                               ),
                              XML("&nbsp;"),
                              A(
                                self.db.pdate(comment.commenttime),
                               _href=self.CURL('article', 'showcomment', args=comment.id))
                             ),
                            DIV(
                               XML(comment.comment_text),
                               **{'_class': 'editable commentitem',
                                  '_data-object': 'comment',
                                  '_data-id': comment.id,
                                  '_id': "comment_%s" % comment.id}
                             ),
                            DIV(
                               A(iicon("share-alt"), self.T("reply")),
                               _class="pull-right reply-button",
                               **{"_data-url": URL('article', 'addreply')}
                              ) if self.db.auth.user else DIV(),
                            _class="comment_div span10"
                            ),
                            _class="row"
                            ),
                            self.get_comment_replies(comment),
                            _class="comment_li",
                            **{"_data-cid": comment.id}
                          ) for comment in comments],
                  **dict(_class="comment_ul")),
                  edit_in_place[1],
                  showmore("comment_%s" % comment.id) if comments else '',
                  _class="internal-comments article-box",
                  _id="internal-comments"

                  )

    def get_comment_replies(self, comment):
        if comment.replies > 0:
            return DIV(
                     self.get_inner_comment_replies(comment),
                    _class="row comment_replies_wrapper",
                    _id="comment_replies_wrapper_%s" % comment.id
                    )
        else:
            return DIV(_class="row comment_replies_wrapper", _id="comment_replies_wrapper_%s" % comment.id)

    def get_inner_comment_replies(self, comment):
        replies = comment.article_comments.select(orderby=~self.db.Comments.created_on)
        if not self.context.article:
            self.context.article_id = comment.article_id
        return CAT(
                  DIV(H5(self.T("replies (%s)", comment.replies)), _class="span1 comment_replies"),
                  DIV(
                     UL(*[LI(
                             A(
                              reply.nickname or reply.user_id,
                             _href=self.CURL('person', 'show', args=reply.nickname or reply.user_id),
                             _class="link_to_user",
                             **{"_data-id": reply.user_id}
                             ),
                            XML("&nbsp;"),
                            self.db.pdate(reply.commenttime),
                            self.remove_reply_button(reply),
                            BR(),
                            TAG.blockquote(
                                XML(MARKMIN(reply.comment_text)),
                                _class="comment_reply_text"
                            ),
                            _class="lireply",
                            ) for reply in replies]),
                     _class="comment_replies span10 well",
                     _id="comment_replies_%s" % comment.id)
                   )

    def addreply(self):
        #<Storage {'reply_text_89': 'ddddddddddddddddddd', 'parent_89': '89'}>
        text = None
        parent = None
        for item, value in self.request.vars.items():
            if item.startswith("reply_text"):
                text = value
            elif item.startswith("parent"):
                parent = value

        comment = self.db.Comments[parent]
        if comment:
            self.db.Comments.validate_and_insert(article_id=comment.article_id,
                                    user_id=self.db.auth.user_id,
                                    nickname=self.db.auth.user.nickname,
                                    parent_id=parent,
                                    comment_text=text,
                                    commenttime=self.request.now)
            self.db.commit()
            replies = self.db(self.db.Comments.parent_id == comment.id).count()
            comment.update_record(replies=replies)
            self.db.commit()
            self.context.replies = self.get_inner_comment_replies(comment)

    def remove_reply_button(self, reply):
        user_id = self.db.auth.user_id
        if (user_id == reply.user_id) or ('admin' in self.db.auth.user_groups) or (user_id == self.context.article.author):
            return TAG.I(_class="icon-remove remove-reply", **{"_data-url": URL('article', 'removereply', args="reply_%s" % reply.id)})
        else:
            return ""

    def editcomment(self):
        user = self.session.auth.user if self.session.auth else None
        if user:
            data_id = self.request.vars['data[id]']
            content = self.request.vars['content']
            comment = self.db.Comments[data_id]
            if (comment and user) and (user.id == comment.user_id or user.id == comment.article_id.author):
                comment.update_record(comment_text=content)
                self.db.commit()

    def removecomment(self):
        user = self.session.auth.user if self.session.auth else None
        if user:
            comment_id = self.request.args(0).split('_')[1]
            try:
                comment = self.db.Comments[int(comment_id)]
                if (comment and user) and (user.id == comment.user_id or user.id == comment.article_id.author) or ('admin' in self.db.auth.user_groups):
                    comment.delete_record()
                    self.db.commit()
            except:
                pass

    def removereply(self):
        user = self.session.auth.user if self.session.auth else None
        if user:
            comment_id = self.request.args(0).split('_')[1]
            try:
                comment = self.db.Comments[int(comment_id)]
                parent = self.db.Comments[comment.parent_id]
                if (comment and user) and (user.id == comment.user_id or user.id == comment.article_id.author) or ('admin' in self.db.auth.user_groups):
                    comment.delete_record()
                    self.db.commit()
                    replies = self.db(self.db.Comments.parent_id == parent.id).count()
                    parent.update_record(replies=replies)
                    self.db.commit()
            except:
                pass

    def vote_comment(self):
        user = self.db.auth.user
        if user:
            try:
                comment_id = int(self.request.vars['comment'])
                vote = self.request.vars['vote']
                self.db.CommentVotes.validate_and_insert(user_id=user.id, comment_id=comment_id, vote=vote)
                if int(vote) == 0:
                    self.context.voted = """
                        current = $("#countvote_%(comment_id)s").text();
                        newv = parseInt(current) - 1;
                        $("#countvote_%(comment_id)s").text(newv);
                        if (newv > 0) {
                            $("#countvote_%(comment_id)s").removeClass("label-important");
                            $("#countvote_%(comment_id)s").removeClass("label-info");
                            $("#countvote_%(comment_id)s").addClass("label-success");
                        }
                        if (newv < 0) {
                            $("#countvote_%(comment_id)s").removeClass("label-success");
                            $("#countvote_%(comment_id)s").removeClass("label-info");
                            $("#countvote_%(comment_id)s").addClass("label-important");
                        }
                        if (newv == 0) {
                            $("#countvote_%(comment_id)s").removeClass("label-success");
                            $("#countvote_%(comment_id)s").removeClass("label-important");
                            $("#countvote_%(comment_id)s").addClass("label-info");
                        }
                    """ % dict(comment_id=comment_id)
                else:
                    self.context.voted = """
                        current = $("#countvote_%(comment_id)s").text();
                        newv = parseInt(current) + 1;
                        $("#countvote_%(comment_id)s").text(newv);
                        if (newv > 0) {
                            $("#countvote_%(comment_id)s").removeClass("label-important");
                            $("#countvote_%(comment_id)s").removeClass("label-info");
                            $("#countvote_%(comment_id)s").addClass("label-success");
                        }
                        if (newv < 0) {
                            $("#countvote_%(comment_id)s").removeClass("label-success");
                            $("#countvote_%(comment_id)s").removeClass("label-info");
                            $("#countvote_%(comment_id)s").addClass("label-important");
                        }
                        if (newv == 0) {
                            $("#countvote_%(comment_id)s").removeClass("label-success");
                            $("#countvote_%(comment_id)s").removeClass("label-important");
                            $("#countvote_%(comment_id)s").addClass("label-info");
                        }
                    """ % dict(comment_id=comment_id)
            except Exception:
                self.context.voted = """alert('You already voted for this comment');"""
        else:
            self.context.voted = """
                if (confirm("%(message)s")){
                    window.location = "%(url)s";
                }
            """ % dict(url=self.CURL("person", "account", args="login"),
                       message=self.T("You have to be logged in to vote. Click Ok to login, Cancel to return."))

    def comment_disqus(self):
        js = """
        <div id="disqus_thread"></div>
        <script type="text/javascript">
        /* * * CONFIGURATION VARIABLES: EDIT BEFORE PASTING INTO YOUR WEBPAGE * * */
        var disqus_shortname = '%(disqus_shortname)s'; // required: replace example with your forum shortname
        var disqus_identifier = '%(disqus_identifier)s';
        //var disqus_url = '%(disqus_url)s';
        var disqus_developer = %(disqus_developer)s; // developer mode is on
        /* * * DON'T EDIT BELOW THIS LINE * * */
        (function() {
            var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
            dsq.src = 'http://' + disqus_shortname + '.disqus.com/embed.js';
            (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
        })();
        </script>
        <noscript>Please enable JavaScript to view the <a href="http://disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>
        <a href="http://disqus.com" class="dsq-brlink">blog comments powered by <span class="logo-disqus">Disqus</span></a>
        """ % dict(
                   disqus_shortname=self.config.comment.disqus_shortname,
                   disqus_developer=self.config.comment.disqus_developer,
                   disqus_identifier="%s/%s" % (self.context.article.id, self.context.article.slug),
                   disqus_url=self.request.url
                  )
        return XML(js)

    def comment_intense(self):
       #  counterjs = """
       # <script>
       # var idcomments_acct = 'fe83a2e2af975dd1095a8e4e9ebe1902';
       # var idcomments_post_id;
       # var idcomments_post_url;
       # </script>
       # <script type="text/javascript" src="http://www.intensedebate.com/js/genericLinkWrapperV2.js"></script>
       # """

        js = """
        <script>
        var idcomments_acct = '%(intense_acct)s';
        var idcomments_post_id;
        var idcomments_post_url;
        </script>
        <span id="IDCommentsPostTitle" style="display:none"></span>
        <script type='text/javascript' src='http://www.intensedebate.com/js/genericCommentWrapperV2.js'></script>
        """ % dict(
                   intense_acct=self.config.comment.intense_acct,
                   idcomments_post_id="%s/%s" % (self.context.article.id, self.context.article.slug),
                   idcomments_post_url=self.request.url
                  )
        return XML(js)

    def comment_facebook(self):
        js = """
        <div id="fb-root"></div>
            <script>(function(d, s, id) {
            var js, fjs = d.getElementsByTagName(s)[0];
            if (d.getElementById(id)) {return;}
            js = d.createElement(s); js.id = id;
            js.src = "//connect.facebook.net/en_US/all.js#xfbml=1&appId=%(facebook_appid)s";
            fjs.parentNode.insertBefore(js, fjs);
            }(document, 'script', 'facebook-jssdk'));</script>
        <div class="fb-comments" data-href="%(url)s" data-num-posts="%(facebook_numposts)s" data-width="700"></div>
        """ % dict(
                   facebook_appid=self.config.comment.facebook_appid,
                   facebook_numposts=self.config.comment.facebook_numposts,
                   url=self.request.url
                  )
        return XML(js)

    def get(self, redir=True):
        article_id = self.request.args(0)
        article_slug = self.request.args(1)
        queries = [self.db.article.id == article_id]
        if article_slug:
            queries.append(self.db.article.slug == article_slug)
        query = reduce(lambda a, b: (a & b), queries)
        self.context.article = self.db(query).select().first()
        if not self.context.article and redir:
            redirect(self.CURL('home', 'index'))

    def show(self):
        self.get()
        if (self.context.article.draft == True or self.context.article.is_active == False) \
                and (self.context.article.author != self.db.auth.user_id):
            redirect(self.CURL('home', 'index'))
        self.related_articles()
        self.comments()
        content, self.context.article_data = self.get_content(self.context.article.content_type_id.classname, self.context.article.id)
        self.response.meta.title = "%s | %s | %s" % (
                                                     self.context.article.title,
                                                     self.T(self.context.article.content_type_id.title),
                                                     self.db.config.meta.title,
                                                    )
        self.response.meta.description = self.context.article.description
        self.response.meta.keywords = ",".join(self.context.article.tags)
        self.context.article.update_record(views=self.context.article.views + 1)
        self.context.action_links = self.action_links()
        self.db.commit()

    def delete(self):
        self.get()
        if not (has_permission_to_edit(self.session, self.context.article) \
                    or (self.db.auth.has_membership("admin", self.db.auth.user_id) \
                        or self.db.auth.has_membership("editor", self.db.auth.user_id))):
            redirect(self.CURL('article', 'show', args=[self.context.article.id, self.context.article.slug]))

        if "confirmation" in self.request.vars and self.request.vars.confirmation == "1":
            self.context.article.update_record(is_active=False)
            self.update_article_counter()
            self.session.flash = self.T("Article deleted!")
            redirect(self.CURL('article', 'list', vars={"author": self.db.auth.user_id}))

    def edit(self):
        self.context.customfield = customfield
        self.get()
        category_set = self.db(self.db.Category.content_type == self.context.article.content_type_id)
        self.db.article.category_id.requires = IS_IN_DB(category_set, self.db.Category.id, "%(name)s", multiple=True)
        if not (has_permission_to_edit(self.session, self.context.article) \
                    or (self.db.auth.has_membership("admin", self.db.auth.user_id) \
                        or self.db.auth.has_membership("editor", self.db.auth.user_id))):
            redirect(self.CURL('article', 'show', args=[self.context.article.id, self.context.article.slug]))

        self.db.article.thumbnail.compute = lambda r: THUMB2(r['picture'], gae=self.request.env.web2py_runtime_gae)
        self.db.article.medium_thumbnail.compute = lambda r: THUMB2(r['picture'], gae=self.request.env.web2py_runtime_gae, nx=400, ny=400, name='medium_thumb')
        self.context.article_form = SQLFORM(self.db.article, self.context.article, _id="article_form")
        content, article_data = self.get_content(self.context.article.content_type_id.classname, self.context.article.id)

        if self.context.article_form.process().accepted:
            if self.context.article.is_active == False:
                self.context.article.update_record(is_active=True)
            article_data.update_record(**content.entity._filter_fields(self.request.vars))
            self.new_article_event('update_article', data={'event_link_to': "%s/%s" % (self.context.article.id, IS_SLUG()(self.context.article_form.vars.title)[0]),
                                                           'event_text': self.context.article_form.vars.description,
                                                           'event_to': "%s (%s)" % (self.context.article.content_type_id.title, self.context.article.title),
                                                           'event_image_to': self.get_image(self.context.article.thumbnail, self.context.article.content_type_id.identifier)})
            self.session.flash = self.T("%s updated." % self.context.article.content_type_id.title)
            self.context.article.update_record(search_index="|".join(str(value) for value in self.request.vars.values()))
            self.update_article_counter()
            redirect(self.CURL('article', 'show', args=[self.context.article.id, IS_SLUG()(self.request.vars.title)[0]]))

        self.context.content_form = SQLFORM(content.entity, article_data)

    def define_content_type(self, classname):
        from datamodel import contenttypes
        return getattr(contenttypes, classname)(self.db)

    def get_content(self, classname, article_id):
        content = self.define_content_type(classname)
        row = self.db(content.entity.article_id == article_id).select().first()
        if self.request.vars:
            row.update(**content.entity._filter_fields(self.request.vars))
        return (content, row)

    def new(self):
        if not self.session.auth:
            redirect(self.CURL('default', 'user', args='login', vars=dict(_next=self.CURL('article', 'new', args=self.request.args))))
        arg = self.request.args(0)
        query = self.db.content_type.identifier == arg
        content_type = self.db(query).select().first() or redirect(self.CURL('home', 'index'))
        self.context.viewname = content_type.viewname
        content = self.define_content_type(content_type.classname)
        path = os.path.join(self.request.folder, 'uploads/')
        if not self.request.env.web2py_runtime_gae:
            self.db.article.picture.uploadfolder = path
            self.db.article.thumbnail.uploadfolder = path
        else:
            self.db.article.picture.uploadfield = "picture_blob"
            self.db.article.thumbnail.uploadfield = "thumbnail_blob"
        self.db.article.author.default = self.db.auth.user_id
        self.db.article.thumbnail.compute = lambda r: THUMB2(r['picture'], gae=self.request.env.web2py_runtime_gae)
        self.db.article.medium_thumbnail.compute = lambda r: THUMB2(r['picture'], gae=self.request.env.web2py_runtime_gae, nx=400, ny=400, name='medium_thumb')

        self.db.article.content_type_id.default = content_type.id
        category_set = self.db(self.db.Category.content_type == content_type.id)
        self.db.article.category_id.requires = IS_IN_DB(category_set, self.db.Category.id, "%(name)s", multiple=True)
        self.context.form = SQLFORM.factory(self.db.article, content.entity, table_name="article", formstyle='divs', separator='', _id="article_form")
        self.context.customfield = customfield
        if self.context.form.process().accepted:
            try:
                article_id = self.db.article.insert(**self.db.article._filter_fields(self.context.form.vars))
                self.context.form.vars.article_id = article_id
                self.context.form.vars.type_id = content_type.id
                content_id = content.entity.insert(**content.entity._filter_fields(self.context.form.vars))
                if not content_id:
                    raise Exception("Content not added")
            except Exception:
                self.db.rollback()
                self.response.flash = self.T("error including %s." % content_type.title)
            else:
                self.db.commit()
                self.session.flash = self.T("%s included." % content_type.title)
                self.context.article = self.db.article[article_id]
                self.context.article.update_record(search_index="|".join(str(value) for value in self.context.form.vars.values()))

                self.update_article_counter()

                if not self.context.article.draft:
                    self.new_article_event('new_article')

                redirect(self.CURL('article', 'show', args=[article_id, IS_SLUG()(self.context.form.vars.title)[0]]))

    def update_article_counter(self):
        user = self.context.article.author
        articles = self.db((self.db.Article.author == user) & (self.db.Article.draft == False) & (self.db.Article.is_active == True)).count()
        draft_articles = self.db((self.db.Article.author == user) & (self.db.Article.draft == True) & (self.db.Article.is_active == True)).count()
        user.update_record(articles=articles, draft_articles=draft_articles)
        self.db.commit()
        self.db.auth.user.articles = articles
        self.db.auth.user.draft_articles = draft_articles

    def tag(self):
        pass

    def category(self):
        category = None
        try:
            category = self.db.Category[int(self.request.args(0))]
        except:
            category = self.db(self.db.Category.name == self.request.args(0).replace('_', ' ')).select()
            if category:
                category = category[0]
        self.context.category = category

    def search(self):
        q = self.request.vars.q or None
        self.context.form = FORM(INPUT(_type="text", _name="q", _id="q", _value=q or ''), _method="GET")
        if q:
            query = (self.db.Article.search_index.like("%" + q + "%")) | (self.db.Article.tags.contains(q))
            #### pagination
            self.context.paginate_selector = PaginateSelector(paginates=(10, 25, 50, 100))
            self.context.paginator = Paginator(paginate=self.context.paginate_selector.paginate)
            self.context.paginator.records = self.db(query).count()
            self.context.paginate_info = PaginateInfo(self.context.paginator.page, self.context.paginator.paginate, self.context.paginator.records)
            limitby = self.context.paginator.limitby()
            #### /pagination
            query &= self.db.Article.draft == False
            query &= self.db.Article.is_active == True
            if "content_type_id" in self.request.vars:
                query &= self.db.Article.content_type_id == self.request.vars.content_type_id
            self.context.results = self.db(query).select(limitby=limitby, orderby=~self.db.Article.publish_date)
        else:
            self.context.results = []

    def list(self):
        denied_fields = ['limitby', 'orderby', 'tag', 'category', 'or',
                          'page', 'paginate', 'draft', 'favorite', 'like',
                          'dislike', 'subscribe', 'comment', 'thrash']

        self.context.title = str(self.db.T("Articles "))
        queries = []
        for field, value in self.request.vars.items():
            if field not in denied_fields:
                queries.append(self.db.Article[field] == value)
            if field == 'tag':
                queries.append(self.db.Article.tags.contains(value))
                self.context.title += str(self.db.T("tagged with %s ", value))
            if field == 'category':
                try:
                    cat_qry = self.db.Article.category_id.contains(int(value))
                except:
                    #cat_id = self.db(self.db.Category.name == value.replace('_', ' ')).select().first().id
                    cats = self.db(self.db.Category.name == value.replace('_', ' ')).select()
                    cat_ids = [cat.id for cat in cats]
                    catqueries = []
                    for catid in cat_ids:
                        catqueries.append(self.db.Article.category_id.contains(catid))
                    cat_qry = reduce(lambda a, b: (a | b), catqueries)
                queries.append((cat_qry))
                self.context.title += str(self.db.T("in %s category ", value.replace('_', ' ')))
            if field == "draft":
                queries.append(self.db.Article.draft == True)
                queries.append(self.db.Article.author == self.db.auth.user_id)
                self.context.title = self.T("Your drafts")
            if field == "thrash":
                queries.append(self.db.Article.is_active == False)
                queries.append(self.db.Article.author == self.db.auth.user_id)
                self.context.title = self.T("Your deleted articles")

            action_tables = {"favorite": self.db.Favoriters,
                             "like": self.db.Likers,
                             "dislike": self.db.Dislikers,
                             "subscribe": self.db.Subscribers}

            if field in action_tables:
                articles = self.db(action_tables[field].user_id == value).select()
                nickname = articles[0].user_id.nickname if articles else self.db.auth_user[value].nickname
                articles_ids = [article.article_id for article in articles]
                queries.append(self.db.Article.id.belongs(articles_ids))
                queries.append(self.db.Article.draft == False)
                self.context.title = self.T("%s %ss", (nickname, field))

        if not "draft" in self.request.vars:
            queries.append(self.db.Article.draft == False)
        if not "thrash" in self.request.vars:
            queries.append(self.db.Article.is_active == True)

        query = reduce(lambda a, b: (a & b), queries)

        #### pagination
        self.context.paginate_selector = PaginateSelector(paginates=(10, 25, 50, 100))
        self.context.paginator = Paginator(paginate=self.context.paginate_selector.paginate)
        self.context.paginator.records = self.db(query).count()
        self.context.paginate_info = PaginateInfo(self.context.paginator.page, self.context.paginator.paginate, self.context.paginator.records)
        limitby = self.context.paginator.limitby()
        #### /pagination
        if self.request.vars.limitby:
            limitby = [int(item) for item in self.request.vars.limitby.split(',')]
        self.context.articles = self.db(query).select(limitby=limitby, orderby=~self.db.Article.publish_date)
        if 'author' in self.request.vars and self.context.articles:
            self.context.title = str(self.db.T("Articles wrote by %s", self.context.articles[0].author.nickname))

    def new_article_event(self, event_type, user=None, data={}):
        if not user:
            user = self.session.auth.user if self.session.auth else None
        if user and (event_type not in ['update_article'] or self.request.vars.notify_subscribers):
            self.db.UserTimeLine._new_event(v=dict(
                                                user_id=user.id,
                                                nickname=user.nickname or "%(first_name)s %(last_name)s" % user,
                                                event_type=event_type,
                                                event_image=data.get('event_image', self.get_image(None, 'user', themename=self.context.theme_name, user=user)),
                                                event_to=data.get('event_to', "%s (%s)" % (self.context.article.content_type_id.title, self.context.article.title)),
                                                event_reference=data.get('event_reference', self.context.article.id),
                                                event_text=data.get('event_text', self.context.article.description),
                                                event_link=data.get('event_link', user.nickname or user.id),
                                                event_image_to=data.get('event_image_to', self.get_image(self.context.article.thumbnail, self.context.article.content_type_id.identifier)),
                                                event_link_to=data.get('event_link_to', "%s/%s" % (self.context.article.id, self.context.article.slug)),
                                            ))

            events = dict(self.notifier.permission.events)
            if event_type not in ['update_article', 'new_article'] and self.context.article.author != user.id:
                self.notifier.notify(event_type,
                    self.context.article.author,
                    event_text=self.T(events.get(event_type, "%s done something on %s"), (user.nickname, data.get('event_to', self.context.article.title))),
                    event_link=data.get('event_link_to', "%s/%s" % (self.context.article.id, self.context.article.slug)),
                    event_reference=data.get('event_reference', self.context.article.id),
                    event_image=data.get('event_image', self.get_image(None, 'user', themename=self.context.theme_name, user=user)),
                    data=data
                )

            if event_type in ['new_article_comment', 'update_article']:
                subs_query = (self.db.Subscribers.article_id == self.context.article.id) & (self.db.Subscribers.user_id != user.id)
                subscribers = self.db(subs_query).select()
                user_ids = [subscriber.user_id for subscriber in subscribers]
                rows = self.db(self.db.auth_user.id.belongs(user_ids)).select()
                emails = [row.email for row in rows]
                users = [row.id for row in rows]
                events.update({"new_article_comment_subscribers": self.T("%s commented on article %s"), "update_article_subscribers": self.T("%s updated %s")})
                if emails and users:
                    self.notifier.notify_all("%s_subscribers" % event_type,
                        emails=emails,
                        users=users,
                        event_text=self.T(events.get("%s_subscribers" % event_type, "%s done something on %s"), (user.nickname, data.get('event_to', self.context.article.title))),
                        event_link=data.get('event_link_to', "%s/%s" % (self.context.article.id, self.context.article.slug)),
                        event_reference=data.get('event_reference', self.context.article.id),
                        event_image=data.get('event_image', self.get_image(None, 'user', themename=self.context.theme_name, user=user)),
                        data=data
                    )

    def favorite(self):
        user = self.session.auth.user if self.session.auth else None
        if user:
            self.get()  # get article object
            try:
                self.context.favorited = self.db.Favoriters.update_or_insert(article_id=self.context.article.id, user_id=user.id)
            except Exception, e:
                self.context.error = str(e)
            else:
                try:
                    count = self.db(self.db.Favoriters.article_id == self.context.article.id).count()
                    self.context.article.update_record(favorited=count)

                    count = self.db(self.db.Favoriters.user_id == user.id).count()
                    self.db.auth_user[user.id] = dict(favorites=count)
                    self.new_article_event('favorited', user)
                except Exception, e:
                    print str(e)
                    self.db.rollback()
                else:
                    self.db.commit()

    def like(self):
        self.undislike()
        user = self.session.auth.user if self.session.auth else None
        if user:
            self.get()  # get article object
            try:
                self.context.liked = self.db.Likers.update_or_insert(article_id=self.context.article.id, user_id=user.id)
            except Exception, e:
                self.context.error = str(e)
            else:
                try:
                    count = self.db(self.db.Likers.article_id == self.context.article.id).count()
                    self.context.article.update_record(likes=count)

                    count = self.db(self.db.Likers.user_id == user.id).count()
                    self.db.auth_user[user.id] = dict(likes=count)
                    self.new_article_event('liked', user)
                except Exception:
                    self.db.rollback()
                else:
                    self.db.commit()

    def dislike(self):
        self.unlike()
        user = self.session.auth.user if self.session.auth else None
        if user:
            self.get()  # get article object
            try:
                self.context.disliked = self.db.Dislikers.update_or_insert(article_id=self.context.article.id, user_id=user.id)
            except Exception, e:
                self.context.error = str(e)
            else:
                try:
                    count = self.db(self.db.Dislikers.article_id == self.context.article.id).count()
                    self.context.article.update_record(dislikes=count)

                    count = self.db(self.db.Dislikers.user_id == user.id).count()
                    self.db.auth_user[user.id] = dict(dislikes=count)
                    self.new_article_event('disliked', user)
                except Exception:
                    self.db.rollback()
                else:
                    self.db.commit()

    def subscribe(self):
        user = self.session.auth.user if self.session.auth else None
        if user:
            self.get()  # get article object
            try:
                self.context.subscribed = self.db.Subscribers.update_or_insert(article_id=self.context.article.id, user_id=user.id)
            except Exception, e:
                self.context.error = str(e)
            else:
                try:
                    count = self.db(self.db.Subscribers.article_id == self.context.article.id).count()
                    self.context.article.update_record(subscriptions=count)

                    count = self.db(self.db.Subscribers.user_id == user.id).count()
                    self.db.auth_user[user.id] = dict(subscriptions=count)
                    # self.new_article_event('subscribed', user)
                except Exception:
                    self.db.rollback()
                else:
                    self.db.commit()

    def unfavorite(self):
        user = self.session.auth.user if self.session.auth else None
        if user:
            self.get()  # get article object
            try:
                query = (self.db.Favoriters.article_id == self.context.article.id) & (self.db.Favoriters.user_id == user.id)
                self.context.unfavorited = self.db(query).delete()
            except Exception, e:
                self.context.error = str(e)
            else:
                try:
                    count = self.db(self.db.Favoriters.article_id == self.context.article.id).count()
                    self.context.article.update_record(favorited=count)

                    count = self.db(self.db.Favoriters.user_id == user.id).count()
                    self.db.auth_user[user.id] = dict(favorites=count)
                except Exception:
                    self.db.rollback()
                else:
                    self.db.commit()

    def unlike(self):
        user = self.session.auth.user if self.session.auth else None
        if user:
            self.get()  # get article object
            try:
                query = (self.db.Likers.article_id == self.context.article.id) & (self.db.Likers.user_id == user.id)
                self.context.unliked = self.db(query).delete()
            except Exception, e:
                self.context.error = str(e)
            else:
                try:
                    count = self.db(self.db.Likers.article_id == self.context.article.id).count()
                    self.context.article.update_record(likes=count)

                    count = self.db(self.db.Likers.user_id == user.id).count()
                    self.db.auth_user[user.id] = dict(likes=count)
                except Exception:
                    self.db.rollback()
                else:
                    self.db.commit()

    def unsubscribe(self):
        user = self.session.auth.user if self.session.auth else None
        if user:
            self.get()  # get article object
            try:
                query = (self.db.Subscribers.article_id == self.context.article.id) & (self.db.Subscribers.user_id == user.id)
                self.context.unsubscribed = self.db(query).delete()
            except Exception, e:
                self.context.error = str(e)
            else:
                try:
                    count = self.db(self.db.Subscribers.article_id == self.context.article.id).count()
                    self.context.article.update_record(subscriptions=count)

                    count = self.db(self.db.Subscribers.user_id == user.id).count()
                    self.db.auth_user[user.id] = dict(subscriptions=count)
                except Exception:
                    self.db.rollback()
                else:
                    self.db.commit()

    def undislike(self):
        user = self.session.auth.user if self.session.auth else None
        if user:
            self.get()  # get article object
            try:
                query = (self.db.Dislikers.article_id == self.context.article.id) & (self.db.Dislikers.user_id == user.id)
                self.context.undisliked = self.db(query).delete()
            except Exception, e:
                self.context.error = str(e)
            else:
                try:
                    count = self.db(self.db.Dislikers.article_id == self.context.article.id).count()
                    self.context.article.update_record(dislikes=count)

                    count = self.db(self.db.Dislikers.user_id == user.id).count()
                    self.db.auth_user[user.id] = dict(dislikes=count)
                except Exception:
                    self.db.rollback()
                else:
                    self.db.commit()

    def action_links(self):
        CURL = self.CURL
        article = self.context.article
        request = self.request
        T = self.T
        userid = self.session.auth.user.id if self.session.auth else 0
        icons = {
            "views": ICONLINK(userid, "views", T("Views (%s)", article.views or 0), title=T("The number of times this page has been displayed"), theme_name=self.context.theme_name),
            "favorite": ICONLINK(userid, "favorite", T("Favorite (%s)", article.favorited or 0), "ajax('%s',[], 'links')" % CURL('favorite', args=request.args), T("Click to add to your favorites"), theme_name=self.context.theme_name),
            "unfavorite": ICONLINK(userid, "unfavorite", T("Favorite (%s)", article.favorited or 0), "ajax('%s',[], 'links')" % CURL('unfavorite', args=request.args), T("Click to remove from your favorites"), theme_name=self.context.theme_name),
            "like": ICONLINK(userid, "like", T("Like (%s)", article.likes or 0), "ajax('%s',[], 'links')" % CURL('like', args=request.args), T("Click to like"), theme_name=self.context.theme_name),
            "unlike": ICONLINK(userid, "unlike", T("Like (%s)", article.likes or 0), "ajax('%s',[], 'links')" % CURL('unlike', args=request.args), T("Click to remove the like"), theme_name=self.context.theme_name),
            "dislike": ICONLINK(userid, "dislike", T("Dislike (%s)", article.dislikes or 0), "ajax('%s',[], 'links')" % CURL('dislike', args=request.args), T("Click to dislike"), theme_name=self.context.theme_name),
            "undislike": ICONLINK(userid, "undislike", T("Dislike (%s)", article.dislikes or 0), "ajax('%s',[], 'links')" % CURL('undislike', args=request.args), T("Click to remove the dislike"), theme_name=self.context.theme_name),
            "subscribe": ICONLINK(userid, "subscribe", T("Subscribe (%s)", article.subscriptions or 0), "ajax('%s',[], 'links')" % CURL('subscribe', args=request.args), T("Click to subscribe to this article updates"), theme_name=self.context.theme_name),
            "unsubscribe": ICONLINK(userid, "unsubscribe", T("Subscribe (%s)", article.subscriptions or 0), "ajax('%s',[], 'links')" % CURL('unsubscribe', args=request.args), T("Click to unsubscribe from this article updates"), theme_name=self.context.theme_name),
            "edit": ICONLINK(userid, "edit", T("Edit"), "window.location = '%s'" % CURL('edit', args=request.args), T("Click to edit"), theme_name=self.context.theme_name),
            "delete": ICONLINK(userid, "delete", T("Delete"), "window.location = '%s'" % CURL('delete', args=request.args), T("Click to delete"), theme_name=self.context.theme_name),
        }

        links = ['views']

        favorited = self.db.Favoriters(article_id=self.context.article.id, user_id=userid) if userid else None
        liked = self.db.Likers(article_id=self.context.article.id, user_id=userid) if userid else None
        disliked = self.db.Dislikers(article_id=self.context.article.id, user_id=userid) if userid else None
        subscribed = self.db.Subscribers(article_id=self.context.article.id, user_id=userid) if userid else None

        links.append('unfavorite' if favorited else 'favorite')
        links.append('unlike' if liked else 'like')
        links.append('undislike' if disliked else 'dislike')
        if self.config.comment.system == "internal":
            links.append('unsubscribe' if subscribed else 'subscribe')

        if has_permission_to_edit(self.session, self.context.article):
            links.append('edit')
            if self.context.article.is_active:
                links.append('delete')
        elif self.session.auth and \
            (self.db.auth.has_membership("admin", self.db.auth.user_id) or self.db.auth.has_membership("editor", self.db.auth.user_id)):
            links.append('edit')
            if self.context.article.is_active:
                links.append('delete')

        return CAT(*[icons[link] for link in links])

    def tagcloud(self):
        articles = self.db((self.db.Article.draft == False) & (self.db.Article.is_active == True)).select()
        tags = []
        for article in articles:
            if article.tags:
                tags += [tag.lower() for tag in article.tags]
        tagset = set(tags)
        self.context.tags = {}
        for tag in tagset:
            self.context.tags[tag] = get_tag_count(tags.count(tag))
        # bypass content_types query
        self.context.content_types = True


def get_tag_count(count):
    if count <= 1:
        return 1
    elif count <= 4:
        return 2
    elif count <= 6:
        return 3
    elif count <= 15:
        return 4
    elif count <= 20:
        return 5
    else:
        return 6


def ICONLINK(user, icon, text, action=None, title="Click", theme_name="basic"):
    from gluon import current
    request = current.request
    bt = A(_class="icon_link",
              _onclick=action if user else "window.location = '%s'" % URL('default', 'user', args='login', vars=dict(_next=URL('article', 'show', args=request.args))),
              _style="cursor:pointer;",
              _title=title)
    bt.append(CAT(
        IMG(_src=URL('static', '%s/images/icons' % theme_name, args="%s.png" % icon), _width=16),
        SPAN(text, _style="line-height:16px;")
    ))

    return bt


def has_permission_to_edit(session, record):
    userid = session.auth.user.id if session.auth else 0
    return record.author == userid


def customfield(form, field, css={"main": "row", "label": "", "comment": "", "widget": "", "input": "", "error": ""}):
    tablefield = (form.table, field)
    maindiv = DIV(_id="%s_%s__row" % tablefield, _class=css.get("main", ""))
    if field in form.errors:
        maindiv["_class"] += css.get("error", "")
    labeldiv = DIV(_class="w2p_fl %s" % css.get("label", ""))
    commentdiv = DIV(_class="w2p_fc %s" % css.get("comment", ""))
    widgetdiv = DIV(_class="w2p_fw %s" % css.get("widget", ""))

    label = LABEL(form.custom.label[field], _for="%s_%s" % tablefield, _id="%s_%s__label" % tablefield)
    comment = form.custom.comment[field]
    widget = form.custom.widget[field]

    widget_class = widget.attributes.get("_class", "")
    widget_class += css.get("input", "")
    widget["_class"] = widget_class

    labeldiv.append(label)
    commentdiv.append(comment)
    widgetdiv.append(widget)

    maindiv.append(labeldiv)
    maindiv.append(commentdiv)
    maindiv.append(widgetdiv)

    return maindiv


def iicon(iconname):
    return TAG['i'](_class="icon-%s" % iconname, _style="margin-right:5px;")
