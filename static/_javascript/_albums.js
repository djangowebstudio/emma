//-------------------------------------------------------------------------------------------------
// Geert Dekkers Web Studio 2009
// _albums.js
// javascript class file
//-------------------------------------------------------------------------------------------------

var Album = Class.create({
	initialize: function(album, album_name, item){
		
		this.album = album;
		item ? this.item = item : this.item = '';
		album_name ? this.album_name = album_name : this.album_name = '';
		
	},
	
	makeAlbumDroppable: function(){		

			album = this.album;						
			Droppables.add(album, 
					{
					accept:'gallery', 
					hoverclass:'album-active', 
					onDrop:function(){
						$$('dl._selected').each(function(item){	
							if (item.id != album){
								albums._add(album, item.id.replace('-gallery','')); 
							}
							});
						}
					});
				
	},
	
	newAlbum: function(){
			var album_identifier = 'album-' + appendURLWithTimeString();
			var dl = new Element('dl',{id: album_identifier, className: 'gallery album'});
			dl.onclick = function(){
				actions._select(this);
				albums._enable(this);
			};
			var dt = new Element('dt');
			var input = new Element('input', {id: 'input-' + album_identifier, type: 'text', className: 'album-input', value: 'untitled album'});
			input.onblur = function(){
				albums._edit(album_identifier);
			};
			var dd = new Element('dd', {id: 'dd-' + album_identifier});
			dd.update(gettext('drag items here...'));

			// Append the elements and insert them to the top...
			dt.appendChild(input);
			dl.appendChild(dt);
			dl.appendChild(dd);
			$('content_main_dl').insert({top: dl});
			
			this.album = album_identifier;
			this.doNewAlbum();
	},
	
	doNewAlbum: function(){
		
		var element = 'dd-' + this.album;
		var mAjax = new Ajax.Updater(
			{success: element}, 
			'/interface/addalbum/' + this.album + '/',
			{
				method: 'get', 
				onFailure: reportError
			});
		
		setTimeout(function(){$(element).update(gettext("Click to select the first item, then click this album, then drag the item in. "));}, 1000);
		
	},
	
	
	
	doAddToAlbum: function(){
		
		// Add item to album
		// takes: album (DOM element id), item (DOM element id)

		var mAjax = new Ajax.Updater(
			{success: $('debug')}, 
			'/interface/addtoalbum/' + this.album + '/' + this.item + '/',
			{
				method: 'get', 
				onFailure: reportError
			});
			setTimeout(function(){doShowThumbs(args[0], args[1], args[2], args[3], args[4]);}, 1000);
		
		
	},
	
	doRemoveFromAlbum: function(){
		// Removes item from album
		// 
		
		if(confirm(gettext('Do you really want to remove the item ') + this.item + gettext(' from the album?'))){
			var mAjax = new Ajax.Updater(
				{success: $('debug')}, 
				'/interface/removefromalbum/' + this.album + '/' + this.item + '/',
				{
					method: 'get', 
					onFailure: reportError,
					onComplete: messages.genericmessage
				});
				setTimeout(function(){doShowThumbs(args[0], args[1], args[2], args[3], args[4]);}, 1000);
			}
		
		
	},
	
	doAddToCart: function(){
		
		//messages.debug('doAddToCart (in album object): ' + this.album);
		
		var mAjax = new Ajax.Updater(
			{success: 'LN-cartItemsContainer'}, 
			'/interface/clients/addalbum/' + this.album + '/',
			{
				method: 'get', 
				onFailure: reportError,
				onComplete: function(){setTimeout("doShow()", 1000);}
			});

		
		
	}
	
	
	});
	
	
	
// interface

var albums = {
	
	_enable: function(element){
		
		var a = new Album();
		a.album = element.id;
		a.makeAlbumDroppable();
	},
	
	_new: function(){
		a = new Album();
		a.newAlbum();
	},
	
	_edit: function(album){
		// Edit album 
		
		text = $F('input-' + album);
		
		var mAjax = new Ajax.Updater(
			{success: $F('input-' + album)}, 
			'/interface/editalbum/' + album + '/' + text + '/',
			{
				method: 'get', 
				onFailure: reportError
			});
		
		setTimeout(function(){$('input-' + album).value = text;}, 1000);
	},
	
	_add: function(album, item){
		
		a = new Album();
		a.album = album;
		a.item = item;
		a.doAddToAlbum();
		
	},
	
	_remove: function(element){
		
		
		album = element.id.replace('dd-','');
		itemList = [];
		$$('dd.' + album).each(function(i){
			// Compile a list of visible items
			if(i.visible() == true) itemList.push(i);
			
		});
				
		a = new Album();
		a.album = album;
		a.item = itemList.last().id.replace('dd-','');
		a.doRemoveFromAlbum();
		
	},
	_drag: function(element){
				
		_draggable = new Draggable(element,{revert: true, handles: 'handle'});
		
		
		Droppables.add("LN-cartItemsContainer", 
		{
			accept:'album', 
			hoverclass:'LN-cartItemsContainer-active', 
			onDrop:function(){albums._addtocart(element.id);}
			});
			
		Droppables.add("content_favorites",
		{
			accept: 'gallery', 
			hoverclass: 'content_favorites-active', 
			onDrop:function(){

				myfave = new Favorite(element.id,'','dock',1);
				myfave.addItem();

				}
			});
	
		
	},
	_editinadmin: function(album){
		//takes: admin id (int)
		
		// Empty all galleries before repopulating, otherwise galleries will concatentate
		if(myLightWindow.galleries) myLightWindow.galleries = [];
		myLightWindow.activateWindow({
			href: '/admin/interface/album/' + album + '/',
			params: 'lightwindow_type=external'
			
		});
		
		
	},
	_addtocart: function(album){
		
		a = new Album();
		a.album = album;
		a.doAddToCart();
		
		
	},
	
	_empty: function(){
		
		var a = new Album();
		a.album = null;
		
	}, 
	
	_get_album_id: function(){
		var a = new Album();
		alert(a.id);
	},
	
	_page: function(album, paging){
		// hide items to simulate left paging
		
		var items = $$('dd.' + album);
		var messageBox = $(album + '-message');
		
		var visible_items = []; // Initiate an array to hold visible items
		var invisible_items = []; // ... and the same for invisible items
		
		items.each(function(item){
			if(item.visible()){	
				visible_items.push(item);	
			}else{
				invisible_items.push(item);
			}
			
		});
		
		if(paging == 'left'){
			if(visible_items.length > 1) {
					visible_items.last().hide();
				}
			
		}else{
			if(invisible_items.length > 0) invisible_items.first().show();

		}
		

	},
	
	show: function(){
		
		var mAjax = new Ajax.Updater(
			{success: $('debug')},
			'/interface/change/albums/' + 1 + '/',
			{
				method: 'get',
				onFailure: reportError
			});
		
		
		setTimeout(function(){doShowThumbs(args[0], args[1], args[2], args[3], args[4]);}, 100);
	},
	
	load: function(album_identifier, div){
		
		var mAjax = new Ajax.Updater(
			{success: $(album_identifier)},
			'/interface/loadalbum/' + album_identifier + '/' + div + '/',
			{
				method: 'get',
				onFailure: reportError,
				onComplete: function(){
					myLightWindow._setupLinks();
				}
			});
			
		
	},
	
	hide: function(){
		
		var mAjax = new Ajax.Updater(
			{success: $('debug')},
			'/interface/change/albums/' + 0 + '/',
			{
				method: 'get',
				onFailure: reportError
			});
		
		setTimeout(function(){doShowThumbs(args[0], args[1], args[2], args[3], args[4]);}, 100);
		
	}
	
	
};