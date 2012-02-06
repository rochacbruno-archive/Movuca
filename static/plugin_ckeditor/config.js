/*
Copyright (c) 2003-2011, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

// CKEDITOR.editorConfig = function( config )
// {
// 	// Define changes to default configuration here. For example:
// 	// config.language = 'fr';
// 	// config.uiColor = '#AADC6E';
// };

CKEDITOR.editorConfig = function(config) {

    config.extraPlugins = 'insertcode';

    config.keystrokes = [
        [CKEDITOR.CTRL + 68 /*D*/, 'insertcode'],
    ];

    config.toolbar = 'Basic';

    config.toolbar_Basic = ['InsertCode'/* Other buttons ... */];
};

CKEDITOR.on('instanceReady', function(ev) {
    ev.editor.dataProcessor.writer.setRules('pre', {
        breakBeforeOpen : true,
        breakAfterOpen : false,
        breakBeforeClose : false,
        breakAfterClose : true
    });
});
