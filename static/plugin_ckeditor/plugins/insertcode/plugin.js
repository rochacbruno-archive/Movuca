(function() {

var pluginName = 'insertcode';

CKEDITOR.plugins.add(pluginName, {
    requires: ['dialog'],
    lang: ['en', 'zh-cn'],
    init: function(editor) {
        var command = editor.addCommand(pluginName, new CKEDITOR.dialogCommand(pluginName));
        command.modes = {wysiwyg: 1, source: 0};
        command.canUndo = false;
        editor.ui.addButton('InsertCode', {
            label: editor.lang[pluginName].label,
            command: pluginName,
            icon: this.path + 'images/icon.gif'
        });
        CKEDITOR.dialog.add(pluginName, this.path + "dialogs/" + pluginName + ".js")
        editor.on('doubleclick', function(e) {
            var element = e.data.element;
            if (element.getAscendant('pre', true)) {
                e.data.dialog = 'insertcode';
            }
        });
    }
});

})();
