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
	$('a.iframe').bind("mouseout", function(){$('div#metadata').hide();});
	
	// menu item hiding
	$('div.menu-passive').hide();
	$('div#menuContent > div.menu-passive').show();
	var folder_id = location.pathname.replace(/^\/+|\/+$/g, '').replace('gui/folder/', '').replace('/', '_');
	if (folder_id){
    	var selector = 'div#' + folder_id + ', div#' + folder_id + ' > div.menu-passive';
        // $('#debug').text(selector + ' | ' + $(selector).length + ' | ' + $('div#' + folder_id).length);
    	$(selector).show().siblings().show();
    	$('div#' + folder_id + ' a').addClass('active');
	}
	
	// change sorting
	
    $('div#sorting').click(function(){
        $.get('/gui/toggle/sorting/');
        setTimeout(function(){location.reload();}, 500);
    });
    $('ul#pagesize-container').hide();
    $('#page_size').click(function(){
        var position = $(this).position();
        $('ul#pagesize-container').css({'top': (position.top + 14) + "px", 'left': (position.left) + "px"}).toggle();
        setTimeout(function(){$('ul#pagesize-container').fadeOut();}, 5000 );
    });
    $('ul#pagesize-container li').click(function(){
        $.get('/gui/change/pagesize/' + $(this).attr('title') + '/');
        setTimeout(function(){location.reload();}, 500);
    });
	
});

function r(){
	// render cart
	 $('div#cart').hide().load('/cart/show/').show('fast');
}	
