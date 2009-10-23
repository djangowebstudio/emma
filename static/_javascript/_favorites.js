//-------------------------------------------------------------------------------------------------
// Geert Dekkers Web Studio 2009
// _favorites.js
// javascript class file
// requires prototype.js
//-------------------------------------------------------------------------------------------------
var Favorite = Class.create({
	
	initialize: function(item, tag, page){
		
		item ? this.item = item : this.item = '';
		tag? this.tag = tag : this.tag = '';
		this.template = this.getTemplate();
		page ? this.page = page : this.page = 1;
		
	},
	
	enterTag: function(){

		// Builds enter favorite panel
		// Takes: item; an image_LNID
		// Returns HTML

		if($('tagInputContainer')){
			$('content').removeChild($('tagInputContainer'));
		}

		var tagInputContainer = new Element('div', {id: 'tagInputContainer'});
		var tagInputHeader = new Element('div', {className: 'tagInputHeader'});
		var tagFormContainer = new Element('div', {className: 'tagFormContainer'});
		tagFormContainer.insert({top: '<div class="tagImageContainer"><a href="#" onclick="showEnlargement(\'' + this.item + '\')"><img class="tagImage" border="0" src="/s/gallery/thumbs/' + this.item + '.jpg" /></a></div>'});
		var tagForm = new Element('form', {id: 'tagForm', action: '#'});
		var tagInput = new Element('textarea', {id: 'tagInput', className: 'tagInput'});
		tagInputHeader.insert({top: '<span class="tagInputContainerText">Nieuw trefwoord voor '+ this.item + '</span><span class="tagInputContainerClose"><a href="#" onclick="$(\'content\').removeChild($(\'tagInputContainer\'));">x</a></span>'});

		tagFormContainer.appendChild(tagForm);
		tagForm.appendChild(tagInput);

		var tagButton = new Element('input', {id: 'tagButton', type: 'button',  value: 'Bewaren'});
		// call a view to extract the data
		var url = "/interface/call/favorite/" + this.item;
		var mAjax = new Ajax.Request(
			url,
			{
				method: 'get', 
				onFailure: reportError,
				onCreate: function(){Element.clonePosition('spinner', $('content_favorites'));},
				onSuccess: function(transport){
					$('tagInput').update(transport.responseText);
				}

			});

		tagButton.onclick = function(){
			if($F('tagInput')){
				doEnterFavoriteValue(item,$F('tagInput'));
				$('content').removeChild($('tagInputContainer'));
			}else{
				alert('Geef je de favoriet een naam aub?');
			}
			};

		tagForm.appendChild(tagButton);

		Element.clonePosition(tagInputContainer, $('content_favorites'), {setHeight: false, setWidth: false,  setTop: false, offsetLeft: 148});
		tagInputContainer.appendChild(tagInputHeader);
		tagInputContainer.appendChild(tagFormContainer);
		tagInputContainer.hide();
		$('content').appendChild(tagInputContainer);
		Effect.Appear(tagInputContainer, {duration: 0.5});

	},

	getTemplate: function(){

		// Check which template for the view to use 
		// Returns: string

		if ($('content_favorites').className == 'content_favorites_large'){
			template = 'edit';
		}else if ($('content_favorites').className == 'content_favorites'){
			template = 'dock';
		}

		return template;
	},
	
	addItem: function(){
		// enter a favorite 
		// takes: item; image_LNID, value; string to enter

		// Find out which template to render the favorites bar in

		if ($('content_favorites').className == 'content_favorites_large'){
			this.template = 'edit';
		}else if ($('content_favorites').className == 'content_favorites'){
			this.template = 'dock';
		}


		
		var url = "/interface/add/favorite/" + this.item + "/";

		var mAjax = new Ajax.Request(url,
			{
				method: 'get', 
				onFailure: reportError,
				onCreate: function(){Element.clonePosition('spinner', $('content_favorites'), {offsetTop: 9});},
				onComplete: function(){
					f = new Favorite();
					f.show();
				}

			});
			


	},
	

	enter: function(){
		// enter a favorite 
		// takes: item; image_LNID, value; string to enter

		// Find out which template to render the favorites bar in

		if ($('content_favorites').className == 'content_favorites_large'){
			template = 'edit';
		}else if ($('content_favorites').className == 'content_favorites'){
			template = 'dock';
		}



		var url = "/interface/add/favorite/" + this.item + "/" + this.value + '/';

		var mAjax = new Ajax.Updater(
			{success: 'content_favorites' }, 
			url,
			{
				method: 'get', 
				onFailure: reportError,
				onCreate: function(){Element.clonePosition('spinner', $('content_favorites'));},
				onComplete: function(){
					this.show();
				}

			});


	},
	

	show: function(){

		// Shows the favorites interface
		// Takes a template name (string) and a page (int)
		// Returns HTML

	
		var dimension = $('content').getDimensions();
		


		if(this.template == 'dock'){
			if (dimension.width >= 1152){
				pageSize = 25;
			}else{
				pageSize = 20;
			}
			
		
			$('content_favorites').className = 'content_favorites';
			
		}else if (this.template == 'edit'){

			if (dimension.width >= 1152){
				pageSize = 16;
			}else{
				pageSize = 12;
			}
			
			$('content_favorites').className = 'content_favorites_large';

		}



		var url = "/interface/show/favorites/" + this.template + "/" + pageSize + "/" + this.page + "/";
		
		if(this.template == 'dock'){
			var completeAction = function(){};
		}else{
			var completeAction = function(){	
				myLightWindow.galleries = [];
				myLightWindow._setupLinks();
			};
		}

		var mAjax = new Ajax.Updater(
			{success: 'content_favorites' }, 
			url,
			{
				method: 'get', 
				onFailure: reportError,
				onCreate: function(){Element.clonePosition('spinner', $('content_favorites'), {offsetTop: 9});},
				onComplete: completeAction
			});

		

	


	},
	
	explode: function(){
		
		//
		
		
		if($(element).className == element){
			$(element).className = element + '_large';
			this.show()
		}else if ($(element).className == element + '_large'){
			$(element).className = element;
			this.show()
	
		}

		new Effect.Morph('content_favorites', {style: 'bottom: -7px', duration: 0.5});

		
	},

	remove: function(){

		// Remove item from favorites
		// Takes item_id (int) and a page (int)
		// Triggers view doRemoveFavorite (see urls.py )
		// Returns HTML
		
		if (confirm(gettext("Do you really want to remove this favorite?"))){
		var url = "/interface/remove/favorite/" + this.item + "/";

		var mAjax = new Ajax.Updater(
			{success: 'content_favorites' }, 
			url,
			{
				method: 'get', 
				onFailure: reportError,
				onCreate: function(){Element.clonePosition('spinner', $('content_favorites'));},
				onComplete: function(){
					f = new Favorite();
					f.template = 'edit';
					f.show();
					
					}				// Get the correct template
			});

			}


	},
	
	appear: function(){
		
		Effect.Appear('content_favorites', {duration: 0.4});
		
	}
	
	
	
});


var favorites = {
	
	// interface to Favorite
	
	add: function(image_LNID){
	    
	    var f = new Favorite();
		f.item = image_LNID;
		f.addItem();
	    
	},
	
	close: function(element){
		// interface to Favorite's close method.
		var f = new Favorite();
		f.item = element.id.replace('-favorites-close','');
		f.remove();
		myLightWindow._setupLinks();
	},
	
	show: function(page){
		var f = new Favorite();
		f.page = page;
		f.show();
		
	}, 
	
	explode: function(){
		var f = new Favorite(); 
		f.template = 'edit';
		f.pageSize = 16; 
		f.show();
	},
	
	collapse: function(){
		var f = new Favorite();
		f.template='dock';
		f.show();
	}
	
}


