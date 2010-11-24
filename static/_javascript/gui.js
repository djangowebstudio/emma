$(function(){
	r();
	$("a.group").fancybox({
			'transitionIn'	:	'elastic',
			'transitionOut'	:	'elastic',
			'speedIn'		:	600, 
			'speedOut'		:	200, 
			'overlayShow'	:	true
		});
	$("a.iframe").fancybox({
			'transitionIn'	:	'elastic',
			'transitionOut'	:	'elastic',
			'speedIn'		:	600, 
			'speedOut'		:	200, 
			'width'			:   842,
			'height'		:   '85%',
			'overlayShow'	:	true
		});
	
	
	$('a.iframe').bind("mouseover", function(){
		$('div#metadata')
						.show()
						.load('/interface/show/description/' + $(this).attr('id') + "/0/")
						.css({'top': ($(this).offset().top+16) + 'px', 'left': $(this).offset().left + 'px'});
	});
	$('a.iframe').bind("mouseout", function(){$('div#metadata').hide()});
	
});

function r(){
	// 
	 $('div#cart').hide().load('/cart/show/').show('fast');
}	
	
function menu(el, s){
	// open or close menu items
	if ($('div#' + el + '_' + s).length == 0){
		$('<div/>').attr({'id': el + '_' + s}).appendTo($('div#' + el)).load('/menu/' + s + '/');			
	}else{
		$('div#' + el + '_' + s).detach();
	}

}