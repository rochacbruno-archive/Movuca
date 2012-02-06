(function() {

var pluginName = "insertcode";

CKEDITOR.dialog.add(pluginName, function(editor) {
    return {
        title: editor.lang[pluginName].label,
        resizable: CKEDITOR.DIALOG_RESIZE_BOTH,
        minWidth: 500,
        minHeight: 400,
        onShow: function() {
            var editor = this.getParentEditor(),
                selection = editor.getSelection(),
                startElement = selection && selection.getStartElement(),
                preElement = startElement && startElement.getAscendant("pre", true),
                className = "",
                options = null;
            if (preElement) {
                options = getOptions(preElement.getAttribute("class"));
                options.code = unescapeHTML(preElement.getHtml());
            } else {
                options = defaults();
            }
            this.setupContent(options);
        },
        onOk: function() {
            var editor = this.getParentEditor(),
                selection = editor.getSelection(),
                startElement = selection && selection.getStartElement(),
                preElement = startElement && startElement.getAscendant("pre", true),
                options = defaults();
            this.commitContent(options);
            var className = getClassName(options);
            if (preElement) {
                preElement.setAttribute("class", className);
                preElement.setText(options.code || "");
            } else {
                preElement = new CKEDITOR.dom.element("pre", editor.document);
                preElement.setAttribute("class", className);
                preElement.setText(options.code);
                editor.insertElement(preElement);
            }
        },
        contents: [
            {
                id: "source",
                label: editor.lang[pluginName].sourceTab,
                elements: [
                    {
                        type: "textarea",
                        id: "insertcode_textarea",
                        className: "insertcode_textarea",
                        rows: 30,
                        style: "width: 100%",
                        setup: function(editor) {
                            this.setValue(editor.code || "");
                        },
                        commit: function(editor) {
                            editor.code = this.getValue();
                        }
                    }
                ]
            }
        ]
    };
});

var defaults = function() {
    return {
        linenums: 1,
        lang: null,
        code: ""
    };
};

function unescapeHTML(html) {
    return html.replace(/&amp;/gi, "&")
              .replace(/&lt;/gi, "<")
              .replace(/&gt;/gi, ">")
              .replace(/&nbsp;/gi, " ")
              .replace(/&apos;/gi, "'")
              .replace(/&quot;/gi, '"')
              .replace(/<br(\s*\/)?>/gi, "\n");
}

function getClassName(options) {
    var className = "prettyprint";
    if (options.lang) className += " lang-" + options.lang.toLowerCase();
    if (options.linenums) className += " linenums";//" linenums:" + options.linenums;
    return className;
}

function getOptions(className) {
    var options = defaults();
    if (!className) return options;
    var match = className.match(/lang-([a-z]+)/);
    if (match) options.lang = match[1].toLowerCase();
    var match = className.match(/linenums:([0-9]+)/);
    if (match) options.linenums = match[1];
    return options;
}

})();
