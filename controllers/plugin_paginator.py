 # -*- coding: utf-8 -*-
from plugin_paginator import Paginator, PaginateSelector, PaginateInfo
from plugin_solidtable import SOLIDTABLE
from gluon.contrib.populate import populate

db = DAL('sqlite:memory:')
db.define_table('product', Field('name'))
populate(db.product, 99)

def index():
    query = db.product.id > 0
    
################################ The core ######################################
    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate, 
                          extra_vars={'v':1}, anchor='main',
                          renderstyle=True) 
    paginator.records = db(query).count()
    paginate_info = PaginateInfo(paginator.page, paginator.paginate, paginator.records)
    
    rows = db(query).select(limitby=paginator.limitby()) 
################################################################################

    table = SOLIDTABLE(rows, renderstyle=True)
    
    return dict(table=table, paginator=paginator, 
                paginate_selector=paginate_selector, paginate_info=paginate_info) 