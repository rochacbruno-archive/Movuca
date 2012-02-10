# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
# original by http://groups.google.com/group/web2py/browse_frm/thread/d1ec3ded48839071#

# MODIFIED CODE

from gluon import *
from gluon.storage import Messages


class Paginator(UL):
    def __init__(self,
                 paginate=10,
                 records=100,
                 renderstyle=False,
                 page_var='page',
                 anchor="",
                 extra_vars={},
                 **attributes):
        UL.__init__(self, **attributes)
        self.attributes['_class'] = 'paginator'
        self.paginate, self.records, self.page_var, self.anchor, self.extra_vars = (
            paginate, records, page_var, anchor, extra_vars
        )
        self.page = int(current.request.get_vars.get(self.page_var) or 1)

        self.messages = Messages(current.T)
        self.messages.prev = 'Prev'
        self.messages.next = 'Next'

        if renderstyle:
            _url = URL('static', 'plugin_paginator/paginator.css')
            if _url not in current.response.files:
                current.response.files.append(_url)

    def _url(self, page):
        vars = current.request.get_vars.copy()
        vars[self.page_var] = page
        vars.update(self.extra_vars)
        return URL(args=current.request.args, vars=vars, anchor=self.anchor)

    def limitby(self):
        return (self.paginate * (self.page - 1), self.paginate * self.page)

    def xml(self):
        pages = (self.records - 1) / self.paginate + 1
        if (self.records > self.paginate and
            pages == 1 and pages * self.paginate != self.records):
            pages = 2
        elif pages == 0 and self.records != 0:
            pages = 1

        if pages > 1:
            def _get_page_el(page):
                if self.page == page:
                    return LI(A(page, _href="#"), _class="active")
                else:
                    return LI(A(page,
                            _title=page,
                            _href=self._url(page),
                            _class='w2p_trap'))

            if self.page != 1:
                self.append(
                    LI(A(self.messages.prev, _href=self._url(self.page - 1),
                         _title=(self.page - 1), _class='previous_page w2p_trap')))

            _pad_prev = 2
            _pad_next = 3 if self.page > 3 else 7 - self.page
            if self.page - _pad_prev > 1:
                self.append(_get_page_el(1))
                if self.page - _pad_prev > 2:
                    self.append(LI(A('... ', _href="#"), _class="disabled"))
                elif self.page - _pad_prev == 1:
                    self.append(_get_page_el(2))
            for page in range(max(self.page - _pad_prev, 1),
                                   min(self.page + _pad_next, pages + 1)):
                self.append(_get_page_el(page))
            if self.page + _pad_next <= pages:
                if self.page + _pad_next <= pages - 2:
                    self.append(LI(A('... ', _href="#"), _class="disabled"))
                elif self.page + _pad_next == pages - 1:
                    self.append(_get_page_el(pages - 1))
                self.append(_get_page_el(pages))

            if pages > self.page:
                self.append(
                    LI(A(self.messages.next, _href=self._url(self.page + 1),
                         _title=(self.page + 1), _class='next_page w2p_trap')))

        return DIV.xml(self)


class PaginateSelector(SPAN):
    def __init__(self,
                 paginates=(10, 25, 50, 100),
                 paginate_var='paginate',
                 page_var='page',
                 anchor=None,
                 style='text',
                 **attributes):
        SPAN.__init__(self, **attributes)
        self.attributes['_class'] = 'paginate_selector'
        self.paginates, self.paginate_var, self.page_var, self.anchor, self.style = (
            paginates, paginate_var, page_var, anchor, style
        )
        self.paginate = int(current.request.get_vars.get(self.paginate_var, paginates[0]))

        self.messages = Messages(current.T)
        self.messages.paginate = 'Per page: '
        self.messages.option = ''

    def _url(self, paginate):
        vars = current.request.get_vars.copy()
        vars[self.page_var] = 1
        vars[self.paginate_var] = paginate
        return URL(args=current.request.args, vars=vars, anchor=self.anchor)

    def xml(self):
        if self.style == 'text':
            def _get_paginate_link(_paginate):
                if _paginate == self.paginate:
                    return str(_paginate)
                else:
                    return A(_paginate, _href=self._url(_paginate), _class='w2p_trap').xml()
            inner = XML(self.messages.paginate +
                     ', '.join([_get_paginate_link(_paginate) for _paginate in self.paginates]))
            return SPAN(inner, **self.attributes).xml()
        elif self.style == 'select':
            options = [OPTION(self.messages.option % _paginate if self.messages.option else _paginate,
                              _value=_paginate) for _paginate in self.paginates]
            return SPAN(self.messages.paginate,
                        SELECT(options, value=self.paginate,
                               _onchange='location.href="%s".replace("__paginate__", this.value)' % self._url('__paginate__')

                               ), **self.attributes).xml()
        else:
            raise RuntimeError


class PaginateInfo(SPAN):
    def __init__(self, page, paginate, records, **attributes):
        SPAN.__init__(self, **attributes)
        self.attributes['_class'] = 'paginate_info'
        self.page, self.paginate, self.records = (
            page, paginate, records
        )

        self.messages = Messages(current.T)
        self.messages.display_without_span = 'Results: <b>%(total)s</b>'
        self.messages.display_with_span = 'Results: <b>%(start)s - %(end)s</b> of <b>%(total)s</b>'

    def xml(self):
        if self.records <= self.paginate:
            inner = XML(self.messages.display_without_span %
                        dict(total=self.records))
        else:
            inner = XML(self.messages.display_with_span %
                  dict(start=(self.page - 1) * self.paginate + 1, end=self.page * self.paginate,
                       total=self.records))
        return SPAN(inner, **self.attributes).xml()
