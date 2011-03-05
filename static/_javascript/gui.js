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
	
	

	
	$('a.detail').bind("mouseover", function(){
		$('div#metadata')
						.show()
						.load('/interface/show/description/' + $(this).attr('id') + "/0/")
						.css({'top': ($(this).offset().top+16) + 'px', 'left': $(this).offset().left + 'px'});
	});
	$('a.detail').bind("mouseout", function(){$('div#metadata').hide();});
	
	// change sorting
	
    $('div#sorting').click(function(){
        $.get('/toggle/sorting/');
        setTimeout(function(){location.reload();}, 500);
    });
    $('ul#pagesize-container').hide();
    $('#page_size').click(function(){
        var position = $(this).position();
        $('ul#pagesize-container').css({'top': (position.top + 14) + "px", 'left': (position.left) + "px"}).toggle();
        setTimeout(function(){$('ul#pagesize-container').fadeOut();}, 5000 );
    });
    $('ul#pagesize-container li').click(function(){
        $.get('/change/pagesize/' + $(this).attr('title') + '/');
        setTimeout(function(){location.reload();}, 500);
    });
        
    $('#cart').ajaxSuccess(function(e, xhr, settings){
        if(settings.url.match(/^\/cart\/add\/item/g) || settings.url.match(/^\/cart\/empty/g) || settings.url.match(/^\/cart\/remove/g)){
            $(this).text(xhr.responseText);r();
        }
    });	
    

    
});
function r(){
     $('div#cart').load('/cart/show/').show('slow');
    }
    


