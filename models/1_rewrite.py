# -*- coding: utf-8 -*-

controller_routes = {
    "inicio": "home",
    "principal": "home",
    "artigo": "article",
    "articulo": "article"
}

function_routes = {
    "artigo": "article",
    "articulo": "article",
    "home": "index",
    "usuario": "user",
    "ver": "show",
    "editar": "edit"
}

args_router = {
    "['cadastro']": ['register'],
    "['entrar']": ['login'],
    "['sair']": ['logout'],
    "['perfil']": ['profile'],
}

request.controller = controller_routes.get(request.controller, request.controller)
request.function = function_routes.get(request.function, request.function)
#print request.args
request.args = args_router.get(str(request.args), request.args)


CURL = URL
from gluon import current
current.CURL = CURL
