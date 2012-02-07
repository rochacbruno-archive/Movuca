# -*- coding: utf-8 -*-


def clean_object(d=None, T=lambda x, y: (x, y)):
    """
    Takes a Row object and clean unpickeable objects
    """

    from gluon.dal import Row, Set, Field
    from gluon.storage import Storage
    from gluon.languages import lazyT
    import datetime
    # print type(datetime.date(2012, 01, 01))
    if not d:
        d = {"nome": "BRuno", "field": Field("test"), "row": Row(), "sto": Storage(),
                "data": {"birthdate": datetime.date(2012, 01, 01), "nome": "bla", "T": lazyT("aaaa %s", "bbbb"), "l": lambda: 1, "st": Storage(), "set": Set(None, None), "valor": 1.4},
             "numero": 7}

    for item, value in d.items():
        if isinstance(value, (Row, Storage)):
            d[item] = dict(value)
        if isinstance(value, lazyT):
            d[item] = str(T(value.m, value.s))
        if isinstance(value, (Set, Field, type(lambda: 1))):
            d[item] = ""

    for item, value in d.items():
        if isinstance(value, dict):
            for iitem, ivalue in value.items():
                    if isinstance(ivalue, (Row, Storage)):
                        value[iitem] = dict(ivalue)
                    if isinstance(ivalue, lazyT):
                        value[iitem] = str(T(ivalue.m, ivalue.s))
                    if isinstance(ivalue, (Set, Field, type(lambda: 1))):
                        value[iitem] = ""

    return d


if __name__ == "__main__":
    import datetime
    d = clean_object()
    s = str(d)
    print eval(s)
