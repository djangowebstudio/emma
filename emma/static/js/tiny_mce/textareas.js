tinyMCE.init({
  mode : "exact",
  elements : "id_content",
  theme : "advanced",
  width: 800,
  height: 420,
  theme_advanced_toolbar_location : "top",
  theme_advanced_toolbar_align : "left",
  theme_advanced_buttons1 : "fullscreen,separator,bold,italic,underline,strikethrough,separator,bullist,numlist,outdent,indent,separator,undo,redo,separator,link,unlink,anchor,separator,table, separator, cleanup,help,separator,code, separator, pastetext,pasteword,selectall",
  theme_advanced_buttons2 : "",
  theme_advanced_buttons3 : "pastetext,pasteword,selectall",
  paste_auto_cleanup_on_paste : true,
          // paste_preprocess : function(pl, o) {
          //     // Content string containing the HTML from the clipboard
          //     alert(o.content);
          // },
          // paste_postprocess : function(pl, o) {
          //     // Content DOM node containing the DOM structure of the clipboard
          //     alert(o.node.innerHTML);
          // },
  paste_remove_styles_if_webkit: true,
  auto_cleanup_word : true,
  plugins : "table,save,advhr,advimage,advlink,emotions,iespell,insertdatetime,preview,searchreplace,print,contextmenu,fullscreen, safari, paste",
  plugin_insertdate_dateFormat : "%m/%d/%Y",
  plugin_insertdate_timeFormat : "%H:%M:%S",
  extended_valid_elements : "a[name|href|target=_blank|title|onclick],img[class|src|border=0|alt|title|hspace|vspace|width|height|align|onmouseover|onmouseout|name|style],hr[class|width|size|noshade],font[face|size|color|style],span[class|align|style]",
  fullscreen_settings : {
    theme_advanced_path_location : "top",
    theme_advanced_buttons1 : "fullscreen,separator,preview,separator,cut,copy,paste,separator,undo,redo,separator,search,replace,separator,code,separator,cleanup,separator,bold,italic,underline,strikethrough,separator,forecolor,backcolor,separator,justifyleft,justifycenter,justifyright,justifyfull,separator,help",
    theme_advanced_buttons2 : "removeformat,styleselect,formatselect,fontselect,fontsizeselect,separator,bullist,numlist,outdent,indent,separator,link,unlink,anchor",
    theme_advanced_buttons3 : "sub,sup,separator,image,insertdate,inserttime,separator,tablecontrols,separator,hr,advhr,visualaid,separator,charmap,emotions,iespell,flash,separator,print"
  }
});
//tinyMCE.init({
//	// General options
//	mode : "textareas",
//	theme : "advanced",
//	plugins : "safari,pagebreak,style,layer,table,save,advhr,advimage,advlink,emotions,iespell,insertdatetime,preview,media,searchreplace,print,contextmenu,paste,directionality,fullscreen,noneditable,visualchars,nonbreaking,xhtmlxtras,template,inlinepopups",
//
//	// Theme options
//	theme_advanced_buttons1 : "save,newdocument,|,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,styleselect,formatselect,fontselect,fontsizeselect",
//	theme_advanced_buttons2 : "cut,copy,paste,pastetext,pasteword,|,search,replace,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,anchor,image,cleanup,help,code,|,insertdate,inserttime,preview,|,forecolor,backcolor",
//	theme_advanced_buttons3 : "tablecontrols,|,hr,removeformat,visualaid,|,sub,sup,|,charmap,emotions,iespell,media,advhr,|,print,|,ltr,rtl,|,fullscreen",
//	theme_advanced_buttons4 : "insertlayer,moveforward,movebackward,absolute,|,styleprops,|,cite,abbr,acronym,del,ins,attribs,|,visualchars,nonbreaking,template,pagebreak",
//	theme_advanced_toolbar_location : "top",
//	theme_advanced_toolbar_align : "left",
//	theme_advanced_statusbar_location : "bottom",
//	theme_advanced_resizing : true,
//
//	// Example word content CSS (should be your site CSS) this one removes paragraph margins
//	content_css : "css/word.css",
//
//	// Drop lists for link/image/media/template dialogs
//	template_external_list_url : "lists/template_list.js",
//	external_link_list_url : "lists/link_list.js",
//	external_image_list_url : "lists/image_list.js",
//	media_external_list_url : "lists/media_list.js",
//
//	// Replace values for the template plugin
//	template_replace_values : {
//		username : "Some User",
//		staffid : "991234"
//	}
//});
	//tinyMCE.init({
	//	mode : "textareas",
	//	theme : "simple"
	//});
	
//tinyMCE.init({
//		// General options
//		mode : "textareas",
//		theme : "advanced",
//		plugins : "safari,pagebreak,style,layer,table,save,advhr,advimage,advlink,emotions,iespell,inlinepopups,insertdatetime,preview,media,searchreplace,print,contextmenu,paste,directionality,fullscreen,noneditable,visualchars,nonbreaking,xhtmlxtras,template",
//
//		// Theme options
//		theme_advanced_buttons1 : "save,newdocument,|,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,styleselect,formatselect,fontselect,fontsizeselect",
//		theme_advanced_buttons2 : "cut,copy,paste,pastetext,pasteword,|,search,replace,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,anchor,image,cleanup,help,code,|,insertdate,inserttime,preview,|,forecolor,backcolor",
//		theme_advanced_buttons3 : "tablecontrols,|,hr,removeformat,visualaid,|,sub,sup,|,charmap,emotions,iespell,media,advhr,|,print,|,ltr,rtl,|,fullscreen",
//		theme_advanced_buttons4 : "insertlayer,moveforward,movebackward,absolute,|,styleprops,|,cite,abbr,acronym,del,ins,attribs,|,visualchars,nonbreaking,template,pagebreak",
//		theme_advanced_toolbar_location : "top",
//		theme_advanced_toolbar_align : "left",
//		theme_advanced_statusbar_location : "bottom",
//		theme_advanced_resizing : true,
//
//		// Example content CSS (should be your site CSS)
//		content_css : "css/content.css",
//
//		// Drop lists for link/image/media/template dialogs
//		template_external_list_url : "lists/template_list.js",
//		external_link_list_url : "lists/link_list.js",
//		external_image_list_url : "lists/image_list.js",
//		media_external_list_url : "lists/media_list.js",
//
//		// Replace values for the template plugin
//		template_replace_values : {
//			username : "Some User",
//			staffid : "991234"
//		}
//	});	