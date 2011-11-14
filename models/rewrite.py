# -*- coding: utf-8 -*-

controller_routes = {
    "inicio": "default",
    "principal": "default",
}

function_routes = {
    "artigos": "articles",
    "articulos": "articles",
    "home": "index",
    "usuario": "user",
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
