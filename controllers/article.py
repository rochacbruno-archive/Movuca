#!/usr/bin/python
# -*- coding: utf-8 -*-
from handlers.article import Article


def show():
    article = Article('show')
    article.context.left_sidebar_enabled = True
    return article.render("app/article/show/%s" % article.context.article.content_type_id.viewname)


def edit():
    article = Article('edit')
    return article.render("app/article/edit/%s" % article.context.article.content_type_id.viewname)


def new():
    article = Article('new')
    #article.context.right_sidebar_enabled = True
    return article.render("app/article/new/%s" % article.context.viewname)


def delete():
    article = Article('delete')
    article.context.left_sidebar_enabled = True
    return article.render("app/article/delete")


def list():
    article = Article('list')
    article.context.left_sidebar_enabled = True
    return article.render("app/article/list")


def search():
    article = Article('search')
    article.context.left_sidebar_enabled = True
    return article.render("app/article/search")


def favorite():
    article = Article('favorite')
    if not article.context.error:
        return article.action_links()
    else:
        return article.context.error


def like():
    article = Article('like')
    if not article.context.error:
        return article.action_links()
    else:
        return article.context.error


def dislike():
    article = Article('dislike')
    if not article.context.error:
        return article.action_links()
    else:
        return article.context.error


def subscribe():
    article = Article('subscribe')
    if not article.context.error:
        return article.action_links()
    else:
        return article.context.error


def unfavorite():
    article = Article('unfavorite')
    if not article.context.error:
        return article.action_links()
    else:
        return article.context.error


def unlike():
    article = Article('unlike')
    if not article.context.error:
        return article.action_links()
    else:
        return article.context.error


def unsubscribe():
    article = Article('unsubscribe')
    if not article.context.error:
        return article.action_links()
    else:
        return article.context.error


def undislike():
    article = Article('undislike')
    if not article.context.error:
        return article.action_links()
    else:
        return article.context.error


def showcomment():
    article = Article('showcomment')
    article.context.left_sidebar_enabled = True
    return article.render("app/article/showcomment")


def isanswer():
    article = Article('isanswer')
    return article.render()


def isnotanswer():
    article = Article('isnotanswer')
    return article.render()


def editcomment():
    article = Article('editcomment')
    return ''


def removecomment():
    article = Article('removecomment')
    return ''


def addreply():
    article = Article("addreply")
    return article.context.replies


def removereply():
    article = Article('removereply')
    return ''

def removeevent():
    return "alert('ok')"


def votecomment():
    article = Article('vote_comment')
    return article.context.voted


def book():
    pass


def tag():
    article = Article('tag')
    return article.render("app/article/tag")


def category():
    article = Article('category')
    return article.render("app/article/category")


def tagcloud():
    article = Article('tagcloud')
    return article.render("app/article/tagcloud")
