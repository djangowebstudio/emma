//-------------------------------------------------------------------------------------------------
// Overriding and extending Lightwindow
// Checking cart in _processWindow
// Adding multipage thumbnail support in the custom method(s) tagged _extra[...]
// 
lightwindow.addMethods({
	
	activate : function(e, link){	
		
		// If the active element has a specified className
		if ($(e.element().id).hasClassName('album-items') ){
			this._extraBuildGallery(e, link);
		}else{
		// Do the usual stuff (back to the original lightwindow method)

		// Clear out the window Contents
		this._clearWindowContents(true);
		
		
		// Add back in out loading panel
		this._addLoadingWindowMarkup();

		// Setup the element properties
		this._setupWindowElements(link);

		// Setup everything
		this._getScroll();
		this._browserDimensions();
		this._setupDimensions();
		this._toggleTroubleElements('hidden', false);
		this._displayLightWindow('block', 'hidden');
		this._setStatus(true);
		this._monitorKeyboard(true);
		this._prepareIE(true);
		this._loadWindow();
		
		}

	},
	deactivate : function(){
		// The window is not active
		this.windowActive = false;
		
		// There is no longer a gallery active
		this.activeGallery = false;
		if (!this.options.hideGalleryTab) {
			this._handleGalleryAnimation(false);
		}
		
		// Kill the animation
		this.animating = false;
		
		// Clear our element
		this.element = null;
		
		// hide the window.
		this._displayLightWindow('none', 'visible');
		
		// Clear out the window Contents
		this._clearWindowContents(false);
		
		// Stop all animation
		var queue = Effect.Queues.get('lightwindowAnimation').each(function(e){e.cancel();});
		
		// Undo the setup
		this._prepareIE(false);
		this._setupDimensions();
		this._toggleTroubleElements('visible', false);	
		this._monitorKeyboard(false);
		this._extraRemoveGallery();	
	},
	
	activateWindow : function(options) {

		this.element = Object.extend({
			href : null,
			title : null,
			author : null,
			caption : null,
			rel : null,
			top : null,
			left : null,
			type : null,
			showImages : null,
			height : null,
			width : null,
			loadingAnimation : null,
			iframeEmbed : null,
			form : null
		}, options || {});
		
		// Set the window type
		this.contentToFetch = this.element.href;
		this.windowType = this.element.type ? this.element.type : this._fileType(this.element.href);	
		
		// Clear out the window Contents
		this._clearWindowContents(true);
			
		// Add back in out loading panel
		this._addLoadingWindowMarkup();
		
		// Setup everything
		this._getScroll();
		this._browserDimensions();
		this._setupDimensions();
		this._toggleTroubleElements('hidden', false);
		this._displayLightWindow('block', 'visible'); // _displayLightWindow is hidden in original. 
		this._setStatus(true);
		this._monitorKeyboard(true);
		this._prepareIE(true);
		this._loadWindow();
	},
	
	
	_extraBuildGallery: function(e,link){
		// extending Lightwindow
		
		// Get image_LNID and the album identifier from the especially crafted image id (e)
		element_id = e.element().id.replace('album-item-','');
		album_identifier = element_id.split('_').pop();
		image_LNID = element_id.split('_')[0];
		
		
			
			// If the div already exists, remove it.
			if ($('lightwindowThumbnailContainer')){
				$('content').removeChild($('lightwindowThumbnailContainer'));
			}
			
			// Proceed if it doesn't 
			if(!$('lightwindowThumbnailContainer')){
				var lightwindowThumbnailContainer = new Element('div', {id: 'lightwindowThumbnailContainer', className: 'LN-lightwindow-thumbnailContainer', 'style': 'display: none;'});
				lightwindowThumbnailContainer.onmouseout = function(){
					lightwindowThumbnailContainer.setOpacity(0.1);
				};
				lightwindowThumbnailContainer.onmouseover = function(){
					lightwindowThumbnailContainer.setOpacity(1);
				};
				$('content').appendChild(lightwindowThumbnailContainer);


				// Read each value into a clickable image
				$$('dl#' + album_identifier + ' a[rel]').each(function(item){
					
					lightwindowThumbnail = new Element('img', {id: item, src: '/gallery/thumbs/' + item.id + '.jpg' });
					lightwindowThumbnail.onclick = function(){
						myLightWindow.activateWindow({
							href: '/gallery/images/' + item.id + '.jpg',
							title: item.id,
							left: 820
							
						});
					};
					lightwindowThumbnailContainer.appendChild(lightwindowThumbnail);
				});
	
				// Apply an appear effect to the thumbs	
				new Effect.Appear($('lightwindowThumbnailContainer'), {duration: 1.0});
				// Open the first window
				myLightWindow.activateWindow({
					href: '/gallery/images/' + image_LNID + '.jpg',
					title: image_LNID,
					left: 820,
					caption: 'First image in the series'
					
				});
			}
		

	},
	
	_processWindow : function() {
		// Clean out our effects
		this.dimensions.dataEffects = [];

		// Set up the data-slide if we have caption information
		if (this.element.caption || this.element.author || (this.activeGallery && this.options.showGalleryCount)) {
			if (this.element.caption) {
				$('lightwindow_data_caption').innerHTML = this.element.caption;
				$('lightwindow_data_caption').setStyle({
					display: 'block'
				});
			} else {
				$('lightwindow_data_caption').setStyle({
					display: 'none'
				});				
			}
			if (this.element.author) {
				$('lightwindow_data_author').innerHTML = this.element.author;
				$('lightwindow_data_author_container').setStyle({
					display: 'block'
				});
			} else {
				$('lightwindow_data_author_container').setStyle({
					display: 'none'
				});				
			}
			if (this.activeGallery && this.options.showGalleryCount) {
				$('lightwindow_data_gallery_current').innerHTML = this.galleryLocation.current;
				$('lightwindow_data_gallery_total').innerHTML = this.galleryLocation.total;
				$('lightwindow_data_gallery_container').setStyle({
					display: 'block'
				});
			} else {
				$('lightwindow_data_gallery_container').setStyle({
					display: 'none'
				});				
			}

			$('lightwindow_data_slide_inner').setStyle({
				width: this.resizeTo.width+'px',
				height: 'auto',
				visibility: 'visible',
				display: 'block'
			});
			$('lightwindow_data_slide').setStyle({
				height: $('lightwindow_data_slide').getHeight()+'px',
				width: '1px',
				overflow: 'hidden',
				display: 'block'
			});
		} else {
			$('lightwindow_data_slide').setStyle({
				display: 'none',
				width: 'auto'
			});
			$('lightwindow_data_slide_inner').setStyle({
				display: 'none',
				visibility: 'hidden',
				width: this.resizeTo.width+'px',
				height: '0px'
			});
		}
		// Check the basket to find out if the item is already in there.
				
		if (this.element.title != 'null') {	
				doCheckBasket('lightwindow_title_bar_title', this.element.title);
		} else {
			$('lightwindow_title_bar_title').innerHTML = '';
		}
		
		var originalContainerDimensions = {height: $('lightwindow_container').getHeight(), width: $('lightwindow_container').getWidth()};
		// Position the window
    	$('lightwindow_container').setStyle({
			height: 'auto',
			// We need to set the width to a px not auto as opera has problems with it
			width: $('lightwindow_container').getWidth()+this.options.contentOffset.width-(this.windowActive ? this.options.contentOffset.width : 0)+'px'
		});
		var newContainerDimensions = {height: $('lightwindow_container').getHeight(), width: $('lightwindow_container').getWidth()};
 		
		// We need to record the container dimension changes
		this.containerChange = {height: originalContainerDimensions.height-newContainerDimensions.height, width: originalContainerDimensions.width-newContainerDimensions.width};

		// Get out general dimensions
		this.dimensions.container = {height: $('lightwindow_container').getHeight(), width: $('lightwindow_container').getWidth()};
		this.dimensions.cruft = {height: this.dimensions.container.height-$('lightwindow_contents').getHeight()+this.options.contentOffset.height, width: this.dimensions.container.width-$('lightwindow_contents').getWidth()+this.options.contentOffset.width};
		
		// Set Sizes if we need too
		this._presetWindowSize();
		this._resizeWindowToFit(); // Even if the window is preset we still don't want it to go outside of the viewport

		if (!this.windowActive) {
			// Position the window
		   	$('lightwindow_container').setStyle({
				left: -(this.dimensions.container.width/2)+'px',
				top: -(this.dimensions.container.height/2)+'px'
			});
		}
	   	$('lightwindow_container').setStyle({
			height: this.dimensions.container.height+'px',
			width: this.dimensions.container.width+'px'
		});
		
		// We are ready, lets show this puppy off!
		this._displayLightWindow('block', 'visible');
		this._animateLightWindow();
	},
	
	
	_extraRemoveGallery: function(){
		if($('lightwindowThumbnailContainer')){
		$('content').removeChild($('lightwindowThumbnailContainer'));
		}
	}
	
	
});


/*-----------------------------------------------------------------------------------------------*/

Event.observe(window, 'load', lightwindowInit, false);

//
//	Set up all of our links
//
var myLightWindow = null;
function lightwindowInit() {
	myLightWindow = new lightwindow();
}
