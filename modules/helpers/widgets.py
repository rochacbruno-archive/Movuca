# -*- coding: utf-8 -*-

from gluon.sqlhtml import OptionsWidget, FormWidget, StringWidget
from gluon import *
from gluon import current


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


class StringListWidget(FormWidget):
    _class = 'string'

    @classmethod
    def widget(cls, field, value, **attributes):
        """
        generates an INPUT text tag.

        see also: :meth:`FormWidget.widget`
        """
        if value:
            value = ','.join(value)
        else:
            value = None
        default = dict(
            _type='text',
            value=(not value is None and str(value)) or '',
            )
        attr = cls._attributes(field, default, **attributes)

        return INPUT(**attr)


class ListWidget(StringWidget):

    @classmethod
    def widget(cls, field, value, **attributes):
        _id = '%s_%s' % (field._tablename, field.name)
        _name = field.name
        if field.type == 'list:integer':
            _class = 'integer'
        else:
            _class = 'string'
        requires = field.requires if isinstance(field.requires, (IS_NOT_EMPTY, IS_LIST_OF)) else None
        items = [LI(INPUT(_id=_id, _class=_class, _name=_name, value=v, hideerror=True, requires=requires)) \
                   for v in value or ['']]
        buttons = UL()
        buttons.append(TAG.BUTTON(TAG.I(_class="icon-plus", _style="margin-right:10px;"), current.T("add new"), _class="btn", _id=_id + '_add'))
        script = SCRIPT("""
// from http://refactormycode.com/codes/694-expanding-input-list-using-jquery
(function(){
jQuery.fn.grow_input = function() {
  return this.each(function() {
    var ul = this;
    jQuery(ul).find(":text").after('<a href="javascript:void(0)>+</a>').keypress(function (e) { return (e.which == 13) ? pe(ul) : true; }).next().click(function(){ pe(ul) });
    jQuery('#%(id)s_add').click(function(){
        pe(ul);
        return false;
    });

  });
};
function pe(ul) {
  var new_line = ml(ul);
  rel(ul);
  new_line.appendTo(ul);
  new_line.find(":text").focus();
  return false;
}
function ml(ul) {
  var line = jQuery(ul).find("li:first").clone(true);
  line.find(':text').val('');
  return line;
}
function rel(ul) {
  jQuery(ul).find("li").each(function() {
    var trimmed = jQuery.trim(jQuery(this.firstChild).val());
    if (trimmed=='') jQuery(this).remove(); else jQuery(this.firstChild).val(trimmed);
  });
}
})();
jQuery(document).ready(function(){jQuery('#%(id)s_grow_input').grow_input();});
""" % dict(id=_id))
        attributes['_id'] = _id + '_grow_input'
        return TAG[''](UL(*items, **attributes), buttons, script)


# class TagsWidget(StringWidget):

#     @classmethod
#     def widget(cls, field, value, **attributes):
#         _id = '%s_%s' % (field._tablename, field.name)
#         _name = field.name
#         attributes['_name'] = _name
#         if field.type == 'list:integer':
#             _class = 'integer'
#         else:
#             _class = 'string'
#         requires = field.requires  # if isinstance(field.requires, (IS_NOT_EMPTY, IS_LIST_OF)) else None
#         attributes['requires'] = requires
#         attributes['hideerror'] = True
#         items = [LI(v) for v in value or ['']]
#         script = SCRIPT("""
# // from http://webspirited.com/tagit/?theme=simple-grey#demos
# $(function() {

#             var availableTags = %s;

#             $('#%s_tagit').tagit({tagSource: availableTags, select: true});
#             });
# """ % (str(value or '[]'), _id))
#         attributes['_id'] = _id + '_tagit'
#         return TAG[''](UL(*items, **attributes), script)
