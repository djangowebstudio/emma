/*
    @plugin jquery-image-viewer
    @description A simple jQuery slideshow plugin that supports autoplay, next/previous buttons, image links, thumbnails and more. This plugin aims to be unobtrusive and loosely coupled so making changes to the structure and style of the slideshow without having to mess with the JavaScript.
    @autors Dana Woodman and Reavis Stuphin-Gray.
*/
(function($) {

    // The main ``jquery.image_viewer()`` function.
    $.fn.image_viewer = function(options) {
        
        var options = $.extend({}, $.fn.image_viewer.options, options);
        
        return this.each(function() {
            
            // Turn the jQuery object into a variable to make it easier to modify.
            var $obj = $(this);
            
            // Build element specific options.
            $obj.options = $.meta ? $.extend({}, options, $obj.data()) : options;
            
            // Do lookups based on the selectors found in options.
            $obj.slideshow = $($obj.options.slideshow_images_selector);
            $obj.slides = $obj.slideshow.children();
            $obj.thumbnail_containers = $($obj.options.thumbnails_selector);
            $obj.next = $($obj.options.next_selector);
            $obj.previous = $($obj.options.previous_selector);
            
            // Validate thumbnail/slide parity.
            $obj.thumbnail_containers.each(function() {
                $obj.thumbnails = $(this).children();
                if( $obj.thumbnails.length > 0 && $obj.thumbnails.length != $obj.slides.length ) {
                    $.fn.image_viewer.debug('Can\'t match thumbnails to slides!');
                    return;
                };
            });
            
            // Validate start index.
            if($obj.options.start < 0 || $obj.options.start >= $obj.slides.length) {
                $.fn.image_viewer.debug("Start index out of range!");
                return;
            };
            
            // Sets the current slideshow.
            $obj.slideshow.data('current_slide', $obj.options.start);
            
            // Validate delay
            if($obj.options.delay < 0) {
                $.fn.image_viewer.debug('Delay out of range!');
                return;
            };
            
            // Hide all the slides.
            $obj.slides.each(function(i, n) {
                $(this).hide();
            });
            
            // Show a slide given its index.
            $obj.slideshow.show_slide = function(index) {
                var old_index = $obj.slideshow.data('current_slide');
                var $old = $($obj.slides[old_index]);
                var $new = $($obj.slides[index]);
                $old.hide();
                $new.fadeIn();
                $obj.slideshow.data('current_slide', index);
                
                $obj.thumbnail_containers.each(function() {
                    $obj.thumbnails = $(this).children();
                    $($obj.thumbnails[old_index]).removeClass($obj.options.active_thumbnail_class);
                    $($obj.thumbnails[index]).addClass($obj.options.active_thumbnail_class);
                });
            };
            
            // Show the next slide in sequence.
            $obj.slideshow.show_next = function() {
                var new_index = $obj.slideshow.data('current_slide') + 1;
                if (new_index >= $obj.slideshow.children().length) 
                    new_index = 0;
                $obj.slideshow.show_slide(new_index);
            };
            
            // Show the previous slide in sequence.
            $obj.slideshow.show_previous = function() {
                var new_index = $obj.slideshow.data('current_slide') - 1;
                if(new_index < 0)
                    new_index = $obj.slideshow.children().length - 1;
                $obj.slideshow.show_slide(new_index);              
            };            
            
            // Start the auto-play timer.
            $obj.slideshow.start_timer = function(){
                if($obj.options.delay > 0) {
                    $obj.slideshow.timer = setInterval(
                        $obj.slideshow.show_next,
                        $obj.options.delay
                    );
                };
            };
            
            // Stop the auto-play timer.
            $obj.slideshow.stop_timer = function() {
                clearInterval($obj.slideshow.timer);
            };
            
            // Reset the auto-play timer.
            $obj.slideshow.reset_timer = function() {
                $obj.slideshow.stop_timer();
                $obj.slideshow.start_timer();
            };
        
            // Show the first slide.
            $obj.slideshow.show_slide(options.start);
            
            // Stop the timer on ``mouseover``, resume on ``mouseout``.
            if($obj.options.delay > 0) {
                $obj.slideshow.start_timer();
                $obj.slideshow.bind('mouseover', function() {
                    $obj.slideshow.stop_timer();
                });
                $obj.slideshow.bind('mouseout', function() {
                    $obj.slideshow.start_timer();
                });
            };
            
            // Hook up click listeners to the thumbnails.
            $obj.thumbnail_containers.each(function() {
                $obj.thumbnails = $(this).children();
                $obj.thumbnails.each(function(index) {
                    $(this).bind('click', function() {
                        $obj.slideshow.show_slide(index);
                        $obj.slideshow.reset_timer();
                        return false;
                    });
                });
            });
            
            // Hook up click listener to the next link.
            $obj.next.bind('click', function() {
                $obj.slideshow.show_next();
                $obj.slideshow.reset_timer();
                return false;
            });
            
            // Hook up click listener to the previous link.            
            $obj.previous.bind('click', function() {
                $obj.slideshow.show_previous();
                $obj.slideshow.reset_timer();
                return false;
            });

        });
    };
    
    // A simple debug function that logs in the console on supported browsers or uses alerts in non-compatible browsers.
    $.fn.image_viewer.debug = function(string) {
        if ($.fn.image_viewer.debug) {
            if (window.console && window.console.log) {
                console.log(string);
            } else {
                alert(string);
            };
        };
    };
    
    // The options for the slideshow.
    $.fn.image_viewer.options = {
        autoplay: true, // [Boolean] - Indicates whether or not to have the slideshow autoplay by default.
        debug: false, // [Boolean] - Set this to 'true' if you want the funciton to log what it is doing.
        delay: 5000, // [Number] - Number of milliseconds to delay a slide. 1000 milliseconds = 1 second. 0 to disable autoplay.
        start: 0, // [Number] - The index of the first slide to show. 0 is the first slide.
        slideshow_images_selector: '#slideshow-slides', // [String] - The jQuery selector that finds the slideshow images on the page.
        previous_selector: '#slideshow-previous', // [String] - The jQuery selector that finds the previous link on the page.
        next_selector: '#slideshow-next', // [String] - The jQuery selector that finds the next link on the page.
        thumbnails_selector: '#slideshow-thumbnails', // [String] - The jQuery selector that finds the thumbnails on the page.
        active_thumbnail_class: 'active-thumbnail' // [String] - The class to add to the thumbnail of the image that is currently being viewed. Leave blank to disable.
    };
    
})(jQuery);
