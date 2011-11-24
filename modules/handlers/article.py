# -*- coding: utf-8 -*-

from handlers.base import Base
from gluon import SQLFORM, redirect, A, IMG, SPAN, URL, CAT, UL, LI, DIV, XML
from helpers.images import THUMB2
import os


class Article(Base):
    def start(self):
        from movuca import DataBase, User
        from datamodel.article import Category, Article, ContentType, Favoriters, Subscribers, Likers, Dislikers
        self.db = DataBase([User, ContentType, Category, Article, Favoriters, Subscribers, Likers, Dislikers])

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
        related_articles = related_articles(self.db, self.context.article.tags, self.context.article.id)
        self.context.related_articles = UL(*[LI(
                                              DIV(
                                                IMG(_src=URL('default', 'download', args=related.thumbnail))
                                              ),
                                              A(related.title, _href=self.CURL('article', 'show', args=[related.id, related.slug])),
                                              **{'_data-url': self.CURL('article', 'show', args=[related.id, related.slug])}
                                              ) for related in related_articles],
                                              _class="related-articles")

    def comments(self):
        comment_system = {
            "internal": self.comment_internal,
            "disqus": self.comment_disqus,
            "intense": self.comment_intense,
            "facebook": self.comment_facebook
        }

        self.context.comments = comment_system[self.config.comment.system]()

    def comment_internal(self):
        pass

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
        pass

    def comment_facebook(self):
        pass

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
        self.get()
        self.db.article.thumbnail.compute = lambda r: THUMB2(r['picture'], gae=self.request.env.web2py_runtime_gae)
        self.context.article_form = SQLFORM(self.db.article, self.context.article).process()
        content, article_data = self.get_content(self.context.article.content_type_id.classname, self.context.article.id)
        self.context.content_form = SQLFORM(content.entity, article_data).process()

    def define_content_type(self, classname):
        from datamodel import contenttypes
        return getattr(contenttypes, classname)(self.db)

    def get_content(self, classname, article_id):
        content = self.define_content_type(classname)
        return (content, self.db(content.entity.article_id == article_id).select().first())

    def new(self):
        arg = self.request.args(0)
        query = self.db.content_type.identifier == arg
        content_type = self.db(query).select().first() or redirect(self.CURL('home', 'index'))
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
        self.context.form = SQLFORM.factory(self.db.article, content.entity, table_name="article")
        if self.context.form.process().accepted:
            try:
                id = self.db.article.insert(**self.db.article._filter_fields(self.context.form.vars))
                self.context.form.vars.article_id = id
                self.context.form.vars.type_id = content_type.id
                id = content.entity.insert(**content.entity._filter_fields(self.context.form.vars))
            except Exception:
                self.db.rollback()
                self.response.flash = self.T("error including %s." % content_type.title)
            else:
                self.db.commit()
                self.response.flash = self.T("%s included." % content_type.title)

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
