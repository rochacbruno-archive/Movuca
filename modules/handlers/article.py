# -*- coding: utf-8 -*-

from handlers.base import Base
from gluon import SQLFORM, redirect, A, IMG, SPAN, URL, CAT, UL, LI, DIV, XML, H4, H5, P, MARKMIN, LABEL
from gluon.validators import IS_SLUG
from helpers.images import THUMB2
import os


class Article(Base):
    def start(self):
        from movuca import DataBase, User
        from datamodel.article import Category, Article, ContentType, Favoriters, Subscribers, Likers, Dislikers, Comments
        self.db = DataBase([User, ContentType, Category, Article, Favoriters, Subscribers, Likers, Dislikers, Comments])

    def pre_render(self):
        # obrigatorio ter um config, um self.response|request, que tenha um render self.response.render
        self.response = self.db.response
        self.request = self.db.request
        self.config = self.db.config
        self.session = self.db.session
        self.T = self.db.T
        self.CURL = self.db.CURL
        #self.view = "app/home.html"

    def lastest_articles(self):
        from helpers.article import latest_articles
        self.context.latest_articles = latest_articles(self.db)

    def related_articles(self):
        from helpers.article import related_articles
        related_articles = related_articles(self.db, self.context.article.tags, self.context.article.category_id, self.context.article.id)
        if related_articles:
            self.context.related_articles = UL(*[LI(
                                              DIV(
                                                IMG(_src=self.get_image(related.thumbnail, related.content_type_id.identifier), _width=120)
                                              ),
                                              A(related.title, _href=self.CURL('article', 'show', args=[related.id, related.slug])),
                                              **{'_data-url': self.CURL('article', 'show', args=[related.id, related.slug])}
                                              ) for related in related_articles],
                                              **dict(_class="related-articles"))
        else:
            self.context.related_articles = False

    def get_image(self, image, placeholder="image"):
        if image:
            return URL('default', 'download', args=image)
        else:
            return URL('static', 'basic/images', args='%s.png' % placeholder)

    def comments(self):
        comment_system = {
            "internal": self.comment_internal,
            "disqus": self.comment_disqus,
            "intense": self.comment_intense,
            "facebook": self.comment_facebook
        }

        self.context.comments = comment_system[self.config.comment.system]()

    def comment_internal(self):
        if self.session.auth and self.session.auth.user:
            self.db.Comments.article_id.default = self.context.article.id
            self.db.Comments.user_id.default = self.session.auth.user.id
            self.db.Comments.commenttime.default = self.request.now
            self.db.Comments.comment_text.label = self.T("Post your comment")
            form = SQLFORM(self.db.Comments, formstyle='divs').process()
        else:
            form = A(self.T("Login to post comments"),
                     _class="button",
                     _href=self.CURL('default', 'user',
                                  args='login',
                                  vars=dict(_next=self.CURL('article', 'show',
                                       args=[self.context.article.id,
                                             self.context.article.slug]))))

        comments = self.db(self.db.Comments.article_id == self.context.article.id).select()
        return DIV(
                  H4(self.T("Comments")),
                  UL(
                      *[LI(
                           H5(
                              A(
                                 self.T("%s on %s" % (comment.user_id.nickname or comment.user_id.first_name,
                                                   comment.commenttime.strftime("%s %s" % (self.db.DATEFORMAT, self.db.TIMEFORMAT)))),
                               _href=self.CURL('person', 'show', args=comment.user_id.nickname or comment.user_id))
                             ),
                            P(
                               MARKMIN(comment.comment_text)
                             ),
                            _class="comment_li"
                          ) for comment in comments],
                  **dict(_class="comment_ul")),
                  form,
                  _class="internal-comments"
                  )

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

    def edit(self):
        self.context.customfield = customfield
        self.get()
        self.db.article.thumbnail.compute = lambda r: THUMB2(r['picture'], gae=self.request.env.web2py_runtime_gae)
        self.context.article_form = SQLFORM(self.db.article, self.context.article)
        content, article_data = self.get_content(self.context.article.content_type_id.classname, self.context.article.id)
        if self.context.article_form.process().accepted:
            article_data.update_record(**content.entity._filter_fields(self.request.vars))
            redirect(self.CURL('article', 'show', args=[self.context.article.id, IS_SLUG()(self.request.vars.title)[0]]))
        self.context.content_form = SQLFORM(content.entity, article_data)

    def define_content_type(self, classname):
        from datamodel import contenttypes
        return getattr(contenttypes, classname)(self.db)

    def get_content(self, classname, article_id):
        content = self.define_content_type(classname)
        return (content, self.db(content.entity.article_id == article_id).select().first())

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
        self.db.article.author.default = self.session.auth.user.id
        self.db.article.thumbnail.compute = lambda r: THUMB2(r['picture'], gae=self.request.env.web2py_runtime_gae)
        self.db.article.content_type_id.default = content_type.id
        self.context.form = SQLFORM.factory(self.db.article, content.entity, table_name="article", formstyle='divs', separator='')
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
                self.response.flash = self.T("%s included." % content_type.title)
                redirect(self.CURL('article', 'show', args=[article_id, IS_SLUG()(self.context.form.vars.title)[0]]))

    def list(self):
        from helpers.article import latest_articles
        try:
            self.context.latest_articles = latest_articles(self.db, **self.request.vars)
        except:
            self.context.latest_articles = latest_articles(self.db)

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
                except Exception:
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
            "views": ICONLINK(userid, "views", T("Views (%s)" % article.views or 0), title=T("The number of times this page has been displayed")),
            "favorite": ICONLINK(userid, "favorite", T("Favorite (%s)" % article.favorited or 0), "ajax('%s',[], 'links')" % CURL('favorite', args=request.args), T("Click to add to your favorites")),
            "unfavorite": ICONLINK(userid, "unfavorite", T("Favorite (%s)" % article.favorited or 0), "ajax('%s',[], 'links')" % CURL('unfavorite', args=request.args), T("Click to remove from your favorites")),
            "like": ICONLINK(userid, "like", T("Like (%s)" % article.likes or 0), "ajax('%s',[], 'links')" % CURL('like', args=request.args), T("Click to like")),
            "unlike": ICONLINK(userid, "unlike", T("Like (%s)" % article.likes or 0), "ajax('%s',[], 'links')" % CURL('unlike', args=request.args), T("Click to remove the like")),
            "dislike": ICONLINK(userid, "dislike", T("Dislike (%s)" % article.dislikes or 0), "ajax('%s',[], 'links')" % CURL('dislike', args=request.args), T("Click to dislike")),
            "undislike": ICONLINK(userid, "undislike", T("Dislike (%s)" % article.dislikes or 0), "ajax('%s',[], 'links')" % CURL('undislike', args=request.args), T("Click to remove the dislike")),
            "subscribe": ICONLINK(userid, "subscribe", T("Subscribe (%s)" % article.subscriptions or 0), "ajax('%s',[], 'links')" % CURL('subscribe', args=request.args), T("Click to subscribe to this article updates")),
            "unsubscribe": ICONLINK(userid, "unsubscribe", T("Subscribe (%s)" % article.subscriptions or 0), "ajax('%s',[], 'links')" % CURL('unsubscribe', args=request.args), T("Click to unsubscribe from this article updates")),
            "edit": ICONLINK(userid, "edit", T("Edit"), "window.location = '%s'" % CURL('edit', args=request.args), T("Click to edit"))
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

        return CAT(*[icons[link] for link in links])


def ICONLINK(user, icon, text, action=None, title="Click"):
    from gluon import current
    request = current.request
    bt = A(_class="icon-link",
              _onclick=action if user else "window.location = '%s'" % URL('default', 'user', args='login', vars=dict(_next=URL('article', 'show', args=request.args))),
              _style="cursor:pointer;",
              _title=title)
    bt.append(CAT(
        IMG(_src=URL('static', 'basic/images/icons', args="%s.png" % icon), _width=16),
        SPAN(text, _style="line-height:16px;")
    ))

    return bt


def has_permission_to_edit(session, record):
    userid = session.auth.user.id if session.auth else 0
    return record.author == userid


def customfield(form, field):
    tablefield = (form.table, field)
    maindiv = DIV(_id="%s_%s__row" % tablefield, _class="row")
    labeldiv = DIV(_class="w2p_fl")
    commentdiv = DIV(_class="w2p_fc")
    widgetdiv = DIV(_class="w2p_fw")

    label = LABEL(form.custom.label[field], _for="%s_%s" % tablefield, _id="%s_%s__label" % tablefield)
    comment = form.custom.comment[field]
    widget = form.custom.widget[field]

    labeldiv.append(label)
    commentdiv.append(comment)
    widgetdiv.append(widget)

    maindiv.append(labeldiv)
    maindiv.append(commentdiv)
    maindiv.append(widgetdiv)

    return maindiv