# -*- coding: utf-8 -*-

from gluon.sqlhtml import OptionsWidget, FormWidget
from gluon import *


class Radio(OptionsWidget):

    @staticmethod
    def widget(field, value, **attributes):
        """
        generates a TABLE tag, including INPUT radios (only 1 option allowed)

        see also: :meth:`FormWidget.widget`
        """

        attr = OptionsWidget._attributes(field, {}, **attributes)

        requires = field.requires
        if not isinstance(requires, (list, tuple)):
            requires = [requires]
        if requires:
            if hasattr(requires[0], 'options'):
                options = requires[0].options()
            else:
                raise SyntaxError('widget cannot determine options of %s' % field)

        options = [(k, v) for k, v in options if str(v)]
        opts = []
        cols = attributes.get('cols', 1)
        totals = len(options)
        mods = totals % cols
        rows = totals / cols
        if mods:
            rows += 1

        for r_index in range(rows):
            tds = []
            for k, v in options[r_index * cols:(r_index + 1) * cols]:

                checked = {'_checked': 'checked'} if k == value else {}
                tds.append(LI(INPUT(_type='radio',
                                    _id='%s%s' % (field.name, k),
                                    _name=field.name,
                                    requires=attr.get('requires', None),
                                    hideerror=True, _value=k,
                                    value=value,
                                    **checked
                                    ),
                                    LABEL(v, _for='%s%s' % (field.name, k))))
            opts.append(UL(tds, _style='list-style-type: none;'))

        if opts:
            opts[-1][0][0]['hideerror'] = False
        return DIV(*opts, **attr)


class Checkbox(OptionsWidget):

    @staticmethod
    def widget(field, value, **attributes):
        """
        generates a TABLE tag, including INPUT checkboxes (multiple allowed)

        see also: :meth:`FormWidget.widget`
        """

        # was values = re.compile('[\w\-:]+').findall(str(value))
        if isinstance(value, (list, tuple)):
            values = [str(v) for v in value]
        else:
            values = [str(value)]

        attr = OptionsWidget._attributes(field, {}, **attributes)

        requires = field.requires
        if not isinstance(requires, (list, tuple)):
            requires = [requires]
        if requires:
            if hasattr(requires[0], 'options'):
                options = requires[0].options()
            else:
                raise SyntaxError('widget cannot determine options of %s' % field)

        options = [(k, v) for k, v in options if k != '']
        opts = []
        cols = attributes.get('cols', 1)
        totals = len(options)
        mods = totals % cols
        rows = totals / cols
        if mods:
            rows += 1

        for r_index in range(rows):
            tds = []
            for k, v in options[r_index * cols:(r_index + 1) * cols]:
                if k in values:
                    r_value = k
                else:
                    r_value = []
                tds.append(LI(INPUT(_type='checkbox', _id='%s%s' % (field.name, k), _name=field.name,
                         requires=attr.get('requires', None),
                         hideerror=True, _value=k,
                         value=r_value), LABEL(v, _for='%s%s' % (field.name, k))))
            opts.append(UL(tds, _style='list-style-type: none;'))

        if opts:
            opts[-1][0][0]['hideerror'] = False
        return DIV(*opts, **attr)


class Upload(FormWidget):

    DEFAULT_WIDTH = '100px'
    ID_DELETE_SUFFIX = '__delete'
    GENERIC_DESCRIPTION = 'file'
    DELETE_FILE = 'delete'

    @staticmethod
    def widget(field, value, download_url=None, show=False, **attributes):
        """
        generates a INPUT file tag.

        Optionally provides an A link to the file, including a checkbox so
        the file can be deleted.
        All is wrapped in a DIV.

        see also: :meth:`FormWidget.widget`

        :param download_url: Optional URL to link to the file (default = None)
        """

        default = dict(
            _type='file',
            )
        attr = Upload._attributes(field, default, **attributes)

        inp = DIV(
                  DIV(INPUT(**attr), _id='uploadinput'),
                  BR(),
                  DIV(_id='photopicture'),
                  )

        if download_url and value:
            if callable(download_url):
                url = download_url(value)
            else:
                url = download_url + '/' + value
            (br, image) = ('', DIV(_id='photopicture'))
            if Upload.is_image(value) and show:
                br = BR()
                image = DIV(IMG(_src=url, _width=Upload.DEFAULT_WIDTH),
                               _id='photopicture',
                               _class='ui-corner-all'
                            )

            requires = attr["requires"]
            if requires == [] or isinstance(requires, IS_EMPTY_OR):
                inp.elements()[0][0].append(CAT(
                     INPUT(_type='checkbox',
                                _name=field.name + Upload.ID_DELETE_SUFFIX,
                                _id=field.name + Upload.ID_DELETE_SUFFIX),
                          LABEL(Upload.DELETE_FILE, _for=field.name + Upload.ID_DELETE_SUFFIX)
                ))
                inp = DIV(
                        inp, br, image
                        )
            else:
                inp = DIV(inp, '[',
                          A(Upload.GENERIC_DESCRIPTION, _href=url),
                          ']', br, image)
        return inp

    @staticmethod
    def represent(field, value, download_url=None):
        """
        how to represent the file:

        - with download url and if it is an image: <A href=...><IMG ...></A>
        - otherwise with download url: <A href=...>file</A>
        - otherwise: file

        :param field: the field
        :param value: the field value
        :param download_url: url for the file download (default = None)
        """

        inp = UploadWidget.GENERIC_DESCRIPTION

        if download_url and value:
            if callable(download_url):
                url = download_url(value)
            else:
                url = download_url + '/' + value
            if UploadWidget.is_image(value):
                inp = IMG(_src=url, _width=UploadWidget.DEFAULT_WIDTH)
            inp = A(inp, _href=url)

        return inp

    @staticmethod
    def is_image(value):
        """
        Tries to check if the filename provided references to an image

        Checking is based on filename extension. Currently recognized:
           gif, png, jp(e)g, bmp

        :param value: filename
        """

        extension = value.split('.')[-1].lower()
        if extension in ['gif', 'png', 'jpg', 'jpeg', 'bmp']:
            return True
        return False
