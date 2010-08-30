//*************************************************************************************************
// nznl.com | nznl.net | nznl.org Internet Productions
// Geert Dekkers Web Studio 2008
// _do.js
//
//*************************************************************************************************


//*************************************************************************************************
//-------------------------------------------------------------------------------------------------
// Initiate application in project _do.js
//------------------------------ ajax -------------------------------------------------------------		
Ajax.Responders.register({
    onCreate: function(){Element.show('spinner');},
    onComplete: function(){Element.hide('spinner');}
});

//------------------------------ globals ----------------------------------------------------------
var thumbs = $H();
var args = [];
var current_album;
var album_drag;

var _draggable; // generic variable to hold current draggable
//------------------------------ actions ----------------------------------------------------------
var actions = {
	
	s: function(){return '_selected_group';},
	
	_c: function(){return $('content_main');},
	
	selectAll: function(){
		
			$$('dl.gallery').each(function(i){
				if(!i.id.startsWith('album')){
					genericSelector(i,'_selected');
				}
			});
			
		},
			

	deselectAll:  function(){
			var _c = actions._c();
			var s = actions.s();
			if ($(s)){_c.removeChild($(s));}
			$$('dl._selected').each(function(item){
				item.removeClassName('_selected');
			});
		},

	_select: function(e){

		$$('dl._selected').each(function(item){
			if (item.hasClassName('album')) item.removeClassName('_selected');
		});
		
		
		
		if(e.id.startsWith('album') && e.hasClassName('_selected')){
			e.removeClassName('_selected');
		}else{
			genericSelector(e, '_selected');	
		}
		

	},
	
	listThumbsArgs: function(){
		alert('start readout');
			thumbs.each(function(pair){
				alert(pair.value);
			});
			args.each(function(arg){
				alert(arg);
			});
	}
	};
		


//------------------------------ sort -------------------------------------------------------------
var sort = {
	asc: function(match, cat, weeks, page, renderCrumbs, group){
		
		var mAjax = new Ajax.Updater(
			{success: $('debug')},
			'/interface/change/order/' + 1 + '/',
			{
				method: 'get',
				onFailure: reportError
			});
		setTimeout(function(){doShowThumbs(args[0], args[1], args[2], args[3], args[4]);}, 100);
	},
	
	desc: function(match, cat, weeks, page, renderCrumbs, group){
		var mAjax = new Ajax.Updater(
			{success: $('debug')},
			'/interface/change/order/' + 0 + '/',
			{
				method: 'get',
				onFailure: reportError
			});
		setTimeout(function(){doShowThumbs(args[0], args[1], args[2], args[3], args[4]);}, 100);
	}
	
};
//------------------------------ messages ---------------------------------------------------------
var messages = {
	genericmessage: function(){
		$('debug').hide();
		$('debug').addClassName('debugmessage');
		$('debug').appear();
		setTimeout(function(){$('debug').fade();}, 2000);
	},
	
	debug: function(text){
		var d = $('debug');
		d.onclick = function(){d.hide();};
		d.hide();
		d.addClassName('debugmessage');
		d.update(text);
		d.show();
		
	},
	
	textmessage: function(text){
		
		$('debug').update(text);
		this.genericmessage();
	
	}
	
};

//------------------------------ popup ------------------------------------------------------------
var popup = {
	
	show: function(element, cmd){
		var u = new Element('ul', { 
			className: 'images-menu popup',
			style: 'min-height: 74px; top:' + (Element.cumulativeOffset($(element))[1] - 80) + 'px; left:' + (Element.cumulativeOffset($(element))[0] - 45) + 'px;'
			});
			
			u.onclick = function(){$('content').removeChild(u);};
			
		// fill the menu
		
		cmd.each(function(pair){
			l = new Element('li').update(pair.key);
			l.onclick = pair.value;
			u.appendChild(l);
		});
		
		$('content').appendChild(u);
		setTimeout(function(){u.fade(); setTimeout(function(){popup.hide(u);},2000);}, 5000);
	
	}, 
	
	click: function(element, cmd){
		
		if($('popup-container')){
			$('content').removeChild($('popup-container'));
		}else{
		
		
		var u = new Element('ul', {
			id: 'popup-container', 
			className: 'images-menu',
			style: 'top:' + (Element.cumulativeOffset($(element))[1] - 297) + 'px; left:' + Element.cumulativeOffset($(element))[0] + 'px;display: none'
			});
			
		// fill the menu
		
		cmd.each(function(pair){
			l = new Element('li').update(pair.key);
			l.onclick = pair.value;
			u.appendChild(l);
		});
	}
	
	}, 

	hide: function(element){
		$('content').removeChild($(element));
	}
	
	
	
};

//------------------------------ pulldown ---------------------------------------------------------

var pulldown = {
	
	show: function(element, cmd){

		if($('pulldown-container')){
			$('content').removeChild($('pulldown-container'));
		}else{

		// Initiate and position
		var u = new Element('ul', {
			id: 'pulldown-container', 
			className: 'images-menu pulldown',
			style: 'top:' + (Element.cumulativeOffset($(element))[1] + 10) + 'px; left:' + Element.cumulativeOffset($(element))[0] + 'px;'
			});
		// Click anywhere on the menu to remove	
			u.onclick = function(){
				$('content').removeChild(u);
			};
			
		// fill the menu
		cmd.each(function(pair){
			l = new Element('li').update(pair.key);
			l.onclick = pair.value;
			u.appendChild(l);
		});

		$('content').appendChild(u);
		setTimeout(function(){removegenericActions();}, 5000);
		}

	},
	
	hide: function(element){
		$('content').removeChild(element);	
		
	}

	
	
};



//------------------------------ generic actions --------------------------------------------------


function genericSelector(element, name){
	// adds or removes class name
	
	if(element.hasClassName(name)){
		element.removeClassName(name);
	}else{
		element.addClassName(name);
	}
}

function removegenericActions(){
	if($('pulldown-container')){
		$('pulldown-container').fade();
		setTimeout(function(){$('content').removeChild($('pulldown-container'));},1000);
	}
	
}

function removegenericActions(element){
	e = $(element);
	if(e){
		e.fade();
		setTimeout(function(){
			$('content').removeChild(e);
			},1000);
	}
	
}

function genericActions(element, cmd){
	
	if($('pulldown-container')){
		$('content').removeChild($('pulldown-container'));
	}else{
	
	// Initiate and position
	var u = new Element('ul', {
		id: 'pulldown-container', 
		className: 'LN-toolbar-category-pulldown-container',
		style: 'top:' + (Element.cumulativeOffset($(element))[1] + 16) + 'px; left:' + Element.cumulativeOffset($(element))[0] + 'px;'
		});
	// fill the menu
	cmd.each(function(pair){
		l = new Element('li').update(pair.key);
		l.onclick = pair.value;
		u.appendChild(l);
	});

	$('content').appendChild(u);
	}

}




function togglePageSize(element){
	
	if($(element).className == element){
		$(element).className = element + '_large';
		doShowFavorites('edit',1);
	}else if ($(element).className == element + '_large'){
		$(element).className = element;
		doShowFavorites('dock',1);
	}
	
	new Effect.Morph('content_favorites', {style: 'bottom: -7px', duration: 0.5});
	
	
}

function toggleMenuHeaders(element){
	
	//change menu header link classname 
	if (!$(element).className || $(element).className != "LN-menubar-header-active"){
		
		if($(element).descendantOf($('LN-menubar-show')) == true){
		
			$('LN-menubar-show').descendants().each(function(s){
				s.className = "";
			});
			
			element.className = "LN-menubar-header-active";
		}else if($(element).descendantOf($('LN-menubar-view')) == true){
			$('LN-menubar-view').descendants().each(function(s){
				s.className = "";
			});
			
			$(element).className = "LN-menubar-header-active";
			
		}
	
	
	}else{
		$(element).className = "";
	}
	
	
}



function toggleView(view){
	
	if (view == 'thumbs'){
		$('LN-toolbar-view-thumbs').src = "/s/_img_interface/ln-toolbar-view-thumbs-black.png";
		$('LN-toolbar-view-page').src = "/s/_img_interface/ln-toolbar-view-page-white.png";
	}else if (view == 'page'){
		$('LN-toolbar-view-thumbs').src = "/s/_img_interface/ln-toolbar-view-thumbs-white.png";
		$('LN-toolbar-view-page').src = "/s/_img_interface/ln-toolbar-view-page-black.png";
	}
	
}

function toggleSorter(view){
	
	if (view == 'date'){
		$('LN-toolbar-sorter-date-anchor').style.color = "black";
		$('LN-toolbar-sorter-az-anchor').style.color = "white";
	}else if (view == 'az'){
		$('LN-toolbar-sorter-az-anchor').style.color = "black";
		$('LN-toolbar-sorter-date-anchor').style.color = "white";
	}
	
	
}

function changeColour(element, changefrom, changeto){
	
	element.firstChild.src = element.firstChild.src.sub(changefrom,changeto);
	
}

function toggleCartPulldown(){
	// builds and presents cart pulldown
	// depends on Scriptaculous, Prototype
	// see doShow() for the way in which the cart is populated.
	
	// To do: We'll want to find out if the cart is populated before presenting it

		var d = document.createElement("div");
		d.id = 'LN-toolbar-cart-pulldown';
		d.style.display = 'none';
		var d1 = document.createElement("div");
		d1.className = 'LN-toolbar-cart-pulldown-background';//background for the whole cart
		d.appendChild(d1);
		
		var d2 = document.createElement("div");
		d2.id = "LN-cartItemsContainer";
		d2.className = 'LN-toolbar-cart-pulldown-items-background'; //background for the items
		d1.appendChild(d2);
		
				
		$('LN-cartContainer').appendChild(d);
		Effect.BlindDown(d.id,{duration:0.1}); //Scriptaculous effect...

	
}

//*************************************************************************************************
// ----------------------
// Category and Date Menu
// ----------------------
// 
//*************************************************************************************************
// ----------------------
// Configuration
// ----------------------
// Takes a categories and a weeks hash, where the key is passed to the app, and the value is presented 
// to the user interface.
// Please note that the strings are hard-coded to match the directory names, which in turn are passed 
// to the database. Changing directory names at the top level of the content will result in a non-match,
// thus rendering this function inactive.

var Categories = $H({'-Postcode-Loterij':'NPL', '-Sponsor-Bingo-Loterij':'SBL', '-BankGiro-Loterij':'BGL'});
var Weeks = $H({4: 'laatste maand', 12: 'laatste 3 maanden', 24: 'laatste 6 maanden'});


var matchContainer = ''; 								// initiate a match variable to hold the match between function calls
var catContainer = '_ALL_'; 							// ... and have the same for the categories
var weeksContainer = 1000; 								// ... and again for the chosen items from the weeks hash. But here, we set a default value



function toggleCategoryPulldown(element, source){
	//builds and presents a menu
	//here, presents an array as a clickable menu
	//this menu will be filled dynamically in further releases
	
	// Takes: 
	
	
	if (!$('LN-toolbar-category-pulldown-container')){
		var categoryPulldownContainer = new Element('ul', {
			id:'LN-toolbar-category-pulldown-container', 
			className: 'LN-toolbar-category-pulldown-container',
			title: 'Klik op een onderdeel om te kiezen, of klik om te sluiten'
			});
		Element.clonePosition(categoryPulldownContainer,source, {setHeight: false, setWidth: false, offsetTop: 14});
		categoryPulldownContainer.style.display = "none";
		categoryPulldownContainer.onclick = function(){
			toggleCategoryPulldown(element);
		};
	

		renderHash(Categories, categoryPulldownContainer, 'catsLink');
		renderHash(Weeks, categoryPulldownContainer, 'weeksLink');
	
		$('content').appendChild(categoryPulldownContainer);
		Effect.BlindDown(categoryPulldownContainer, {duration: 0.1});
	}else{
		$('content').removeChild($('LN-toolbar-category-pulldown-container'));
	}
	
	
	
}


function renderHash(hash, container, appendixId){
	
	hash.each(function(pair){
	
		var categoryPulldownItem = document.createElement("li");
		var categoryPulldownItemText = document.createTextNode(pair.value);
		var categoryPulldownItemTextCrumbAppendixText = document.createTextNode(" -> " + pair.value);
		var appendix = new Element('a', {
			id: appendixId, 
			href: "#",
			title: 'Klik om deze filter te verwijderen'
			});
		appendix.onclick = function(){
			
			if (parseInt(pair.key)){
				weeksContainer = 1000;
			}else{
				catContainer = '_ALL_';
			}
			
			$('content_crumbs').removeChild($(appendixId));
			doShowThumbs(matchContainer,catContainer,weeksContainer,1);
		};
		appendix.appendChild(categoryPulldownItemTextCrumbAppendixText);
		var categoryPulldownItemLink = document.createElement("a");
		categoryPulldownItemLink.href = "#";
		categoryPulldownItemLink.title = "Klik om de selectie te filteren";
		categoryPulldownItemLink.onclick = function(){ 
			
			if($(appendixId)){
				$('content_crumbs').removeChild($(appendixId));
			}
			
			$('content_crumbs').appendChild(appendix);
			
			
			
			if (parseInt(pair.key)){
				weeksContainer = pair.key;
			}else{
				catContainer = pair.key;
			}
			doShowThumbs(matchContainer,catContainer,weeksContainer,1);

		};
		categoryPulldownItemLink.appendChild(categoryPulldownItemText);
		categoryPulldownItem.appendChild(categoryPulldownItemLink);
		container.appendChild(categoryPulldownItem);
		
	
	});
	
	
}

function togglePageSizePulldown(element){
	// Renders pulldown
	// Todo: integrate these controls into a suite of generic app controls

	var container = 'images-pager-pulldown';
	
	
	if($(container)){
		$('content').removeChild($(container));
	}else{
	
		var d = new Element('ul', {id: container, className: 'images-menu pulldown', style: 'position:absolute;'});

		Element.clonePosition(d, element, {setHeight: false, setWidth: false, offsetTop: 14});
		
		(8).times(function(n){		
			n = 8 + (4 * n);	
			e = new Element('li');
			e.onclick = function(){		
						doChangePageSize(n);
						$('content').removeChild(d);
					};
			e.update(n + ' items per page');
			d.appendChild(e);
		});
			
		
		
		var f  = new Element('fieldset').update('or enter number');
		var i = new Element('input', {type: 'text', size: 5});
		i.onblur = function(){
			if(parseInt($F(i))){
			doChangePageSize($F(i));
			$('content').removeChild(d);
			}else{
				alert(gettext('Please enter a number. Or choose a value from the list.'));
			}
		};
		f.appendChild(i);
		d.appendChild(f);
	
		$('content').appendChild(d);
		
			setTimeout(function(){
				removegenericActions(container);
				}, 7000);
		
	}
}

function doChangePageSize(size){
	// Change the number of items per page in user prefs.
	var mAjax = new Ajax.Request('/interface/change/pagesize/' + size + '/', {method: 'get', onFailure: reportError});	
	setTimeout(function(){doShowThumbs(args[0], args[1], args[2], args[3], args[4]);}, 100);
}


function chooseSearchItemMode(){
	// Presents a search mode pulldown
	
	
	var contentHash = $H({'simple': 'simpel', 'advanced': 'uitgebreid', 'source': 'bron'});
	
	var container = new Element('div', {id: 'searchModeContainer'});
	Element.clonePosition(container, '$(\'LN-choose-search-mode\')', {setHeight: false, offsetTop: 14});
	
	contentHash.each(function(pair){
		
	});
	
	
}


// Cookies ----------------------------------------------------------------------------------------
// Note: deprecated. Check and delete

function createCookie(name,value,days) {
	
	// http://www.quirksmode.org/js/cookies.html
	// creates client cookie
	
	if (days) {
		var date = new Date();
		date.setTime(date.getTime()+(days*24*60*60*1000));
		var expires = "; expires="+date.toGMTString();
	}
	else var expires = "";
	document.cookie = name+"="+value+expires+"; path=/";
}

function readCookie(name) { 

	//http://www.quirksmode.org/js/cookies.html
	// reads client cookie
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return null;
}

function eraseCookie(name) { 
	
	//http://www.quirksmode.org/js/cookies.html
	// deletes client cookie
	
	
	createCookie(name,"",-1);
}

// ------------------------------------------------------------------------------------------------

function appendURLWithTimeString(){
	
	//generates an argument / value pair
	// usage: add to url
	// this is used to overcome nagging (IE) caching
	
	 return new Date().getTime();
	
}

function findPos(obj) { 
	
	//http://www.quirksmode.org/js/findpos.html
	// finds the position of an element
	// used to position elements such as menus and pop-up text blocks
	// Note: we mostly use prototype for this nowadays...
	
	var curleft = curtop = 0;
	if (obj.offsetParent) {
		curleft = obj.offsetLeft;
		curtop = obj.offsetTop;
		while (obj = obj.offsetParent) {
			curleft += obj.offsetLeft;
			curtop += obj.offsetTop;
		}
	}
	return [curleft,curtop];
}

var m = 0;
function toggleExplodeMenu(){

	if (m == 0 || m % 2 == 1){
		doShowMenu('menuContent','',3);
	}else{
		doShowMenu('menuContent','',2);
	} 
	
	m += 1;	
}

//-------------------------------------------------------------------------------------------------
// AJAX worker functions
// Generics
function reportError(request) {

	// generic prototype helper
	// to do: more detailed error reporting
	
		
		$('debug').update('An error has occurred: ' + request.status);
		messages.genericmessage();
	}


var myGlobalHandlers = {
	onCreate: function(){
		Element.show('systemWorking');
	},

	onComplete: function() {
		if(Ajax.activeRequestCount == 0){
			Element.hide('systemWorking');
		}
	}
};

//-------------------------------------------------------------------------------------------------
// Note: Probably not used. Check and delete (or store somewhere safe)
Element.addMethods({ //http://naneau.nl/2007/05/24/prototype-vs-jquery/
    spin: function(element, text) {
        element = $(element);

        var img = '<img src="/s/_img_interface/spinner.gif" class="icon" alt="Hang on..." /> ';
        //change this to some url that has your spinner image

        if (!text) {
            text = '';
        }
        //make sure there's text in string form

        element.update('<div class="spin">' + img + text + '</div>');
        //update the element with a div.spin and the img

        return element;
        //return the element for chaining
    },

    stopSpin: function(element) {
        element = $(element);
        if (element) {
            //element exists
            element.innerHTML = '';
            //reset it's contents to nothing
        }
    },

    spinBeside: function (element, text) {
        element = $(element);
        //the element next to which we will spin

        id = (element.id);
        id = 'spin_' + id;
        //id for the spinner

        var html = '<div id="' + id + '"></div>';
        //spinner html

        var body = $$('body')[0];
        //body

        new Insertion.Bottom(body, html);
        //insert

        var spinElement = $(id);
        //the spinner element

        spinElement.spin(text);
        //make it spin, see the spin() method above

        Position.absolutize(spinElement);
        Position.clone(element, spinElement, {
            offsetLeft: element.getWidth() + 10,
            offsetTop: Math.round(element.getHeight() / 2 - spinElement.getHeight() / 2),
            setWidth: false,
            setHeight: false
        });
        //position it

        return element;
        //return element for chaining
    },

    stopSpinBeside: function(element, id) {
        element = $(element);
        //the element next to which there's a spinner

        id = (element.id);
        id = 'spin_' + id;
        //id for the spinner

        if ($(id)) {
            //check whether it exists to be sure
            $(id).remove();
            //remove the element from the document
        }

        return element;
        //return element for chaining
    }

});

// Basket -----------------------------------------------------------------------------------------
// doOrder -> createEntry -> doShow


function doOrder(item){ 
	//alert('doing something..');
	//creates a client id or reads the client id from a cookie
	// Note: Deprecated: Check and delete
	if (!readCookie('-_LN_-')){
		var cName = 'LN-' + Math.floor(Math.random()*10000);
		createCookie('-_LN_-', cName, 365);
		createEntry(cName, item);
	}else{
		createEntry(readCookie('-_LN_-'),item);
	}
	
}

function createEntry(item){ 
	//create an entry in the Order table
	
	var url;
	if (item.startsWith('album-')){		
	    url = '/interface/clients/addalbum/' + item + '/';		
	}else{	
	    url = '/interface/clients/add/' + item + '/';
	}
	var updateContainer = 'LN-cartItemsContainer';
	var mAjax = new Ajax.Updater(
		{success: updateContainer}, 
		url,
		{
            method: 'get', 
			onFailure: reportError,
            onComplete: function(){setTimeout(doShow, 1000);}
		});
		
}


function doShow(){ 
    
	// show the products in the client basket
	// returns HTML
	// see also templates/partsdoShowBasket.html
	
	var updateContainer = 'LN-cartItemsContainer';
	var url = "/interface/show/basket/" + appendURLWithTimeString() + "/";
	var mAjax = new Ajax.Updater(
		{success: updateContainer}, 
		url,
		{
			method: 'get',
	       onFailure: reportError
		});
		
}

function doShowYears(element){
    // triggers serverside script to show date links in a DOM element 
    // takes element (str), DOM element id
    // returns HTML
    
    var url = '/interface/show/years/';
    var updateContainer = new Element('div', {id: 'menuyearsContainer'});
    $(element).appendChild(updateContainer);
    var mAjax = new Ajax.Updater(
		{success: updateContainer}, 
		url,
		{
			method: 'get'
		});
	
}

function showDownloadMessage(){
	setTimeout('doShow()', 2000);
}

function doRemoveFromBasket(client,item,view){ 
	
	//triggers doShow to regenerate the basket
	//takes item to execute the removal
	//passes client and view on to doShow()
	if (confirm(gettext("Do you REALLY want to remove this item from your basket?"))){
	
	var url = "/interface/basket/remove/" + item + "/";	
	var mAjax = new Ajax.Updater(
		{success: 'LN-cartItemsContainer'}, 
		url,
		{
			method: 'get', 
			onFailure: reportError
		});
		
	setTimeout(doShow, 500);
	}
}


function doEmptyBasket(client, view){
	
	// Empties basket completely
	
		if (confirm(gettext("Do your REALLY want to empty your WHOLE basket?"))){

		var url = "/interface/basket/empty/";	
		var mAjax = new Ajax.Updater(
			{success: 'LN-cartItemsContainer'}, 
			url,
			{
				method: 'get', 
				onFailure: reportError
			});

		setTimeout(doShow, 1000);
		}
}
	



function doShowBasketIcon(item){
	// fills a predefined, pre-created (the element to be filled is created just prior to the execution of this function), and named element
	// takes: item; argument item
	// returns HTML
	iconContainer = "LN-showCartIconContainer-" + item;
	iconImage = "LN-showCartIcon-" + item;
	
	var img = document.createElement("img");
	img.src = "/s/_img_interface/ln-toolbar-cart.gif";
	img.id = iconImage;
	
	$(iconContainer).appendChild(img);
	
}


function doUpdateBasket(item){
	// Updates user orders if the resolution checkbox is changed
	
	var url = "/interface/basket/update/" + item + "/";
	var mAjax = new Ajax.Request(
		url,
		{
			method: 'get', 
			onFailure: reportError
			
		});
	
	
}


function doShowTags(element,format,search,page){
	// triggers view
	// takes: element; DOM element to fill, format; list or cloud, search; a search term, page; page number to render
	// results of url
	
	var url = "/interface/show/tags/" + format+ "/" + search + "/" + page;
	var mAjax = new Ajax.Updater(
		{success: element}, 
		url,
		{
			method: 'get', 
			onFailure: reportError,
			onCreate: function(){Element.clonePosition('spinner', 'menuContent');}
			
		});
	
	
}



function doShowMenu(element, search){
	// Creates a div to be filled with a menu block
	// Takes: element; element to be filled, search; a path node
	// returns HTML
	var newId = element + "_" + search;
	
	if (!$(newId)){
		var dContainer = new Element('div', {id: newId});
		$(element).appendChild(dContainer);
		var url = "/interface/show/menu/" + search + "/";
		var mAjax = new Ajax.Updater(
		{success: $(newId)}, 
		url,
		{
			method: 'get'
            // onCreate: function(){Element.clonePosition('spinner', $(newId));},
            // onFailure: reportError
		});
	}else{
		$(element).removeChild($(newId));
	}	

}

function toggleMenuSiblings(element){
	
	// Sets all siblings in a menu to the passive position
	// Takes: element; an element
	thisLocation = location.protocol + '//' + location.host;
	
	parent = $(element).ancestors()[0];
	menuArray = parent.siblings();
	menuArray.each(function(item){
		imgElement = 'img-' + item;
		imgElement.src = thisLocation + '/s/_img_interface/triangle-bluegreen-right.png';
	});
	
	
}

function toggleMenuImg(element){
	// Toggle image in menu (triangle)
	// Takes: element; an image element
	
	thisLocation = location.protocol + '//' + location.host;
	
	if ($(element).src == thisLocation + '/s/_img_interface/triangle-bluegreen-right.png'){
		$(element).src = thisLocation + '/s/_img_interface/triangle-bluegreen-down.png';
	}else{
		$(element).src = thisLocation + '/s/_img_interface/triangle-bluegreen-right.png';
	}
	
	
}

function toggleFavoritesImageSize(element, direction){
	// Switch the source from gallery/miniThumbs to gallery/thumbs
	// and vice-versa
	// Takes: element; an image element, direction; up or down (string)
	var source = $(element).src;
	
	if(direction == 'up'){
		newsource = source.replace('miniThumbs', 'thumbs');
	}else if (direction == 'down'){
		newsource = source.replace('thumbs', 'miniThumbs');
	}
	
	$(element).src = newsource;
}

function urldecode( str ) {
    // http://kevin.vanzonneveld.net
    // +   original by: Philip Peterson
    // +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
    // +      input by: AJ
    // +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
    // %          note: info on what encoding functions to use from: http://xkr.us/articles/javascript/encode-compare/
    // *     example 1: urldecode('Kevin+van+Zonneveld%21');
    // *     returns 1: 'Kevin van Zonneveld!'
    // *     example 2: urldecode('http%3A%2F%2Fkevin.vanzonneveld.net%2F');
    // *     returns 2: 'http://kevin.vanzonneveld.net/'
    // *     example 3: urldecode('http%3A%2F%2Fwww.google.nl%2Fsearch%3Fq%3Dphp.js%26ie%3Dutf-8%26oe%3Dutf-8%26aq%3Dt%26rls%3Dcom.ubuntu%3Aen-US%3Aunofficial%26client%3Dfirefox-a');
    // *     returns 3: 'http://www.google.nl/search?q=php.js&ie=utf-8&oe=utf-8&aq=t&rls=com.ubuntu:en-US:unofficial&client=firefox-a'
    
    var histogram = {}, histogram_r = {}, code = 0, str_tmp = [];
    var ret = str.toString();
    
    var replacer = function(search, replace, str) {
        var tmp_arr = [];
        tmp_arr = str.split(search);
        return tmp_arr.join(replace);
    };
    
    // The histogram is identical to the one in urlencode.
    histogram['!']   = '%21';
    histogram['%20'] = '+';
    
    for (replace in histogram) {
        search = histogram[replace]; // Switch order when decoding
        ret = replacer(search, replace, ret); // Custom replace. No regexing   
    }
    
    // End with decodeURIComponent, which most resembles PHP's encoding functions
    ret = decodeURIComponent(ret);
 
    return ret;
}

function doShowThumbs(match, cat, weeks, page, renderCrumbs, groups){ 
	
	// Shows thumbnail images in content_main
	// Takes: match; a search string, cat; a path node; weeks; integer, page; a page number, renderCrumbs; boolean
	// Returns: HTML, and content for content_crumbs
	
	
	args = Array.prototype.slice.call(arguments); // Get args in array for reuse
	
	var dimension = $('content').getDimensions();
	var url;
	if (groups || groups == 0){
		
		url = "/interface/show/thumbs/" + match + "/" + cat + "/" + weeks + "/" + page + "/" + groups + "/";
	}else{
		
		url = "/interface/show/thumbs/" + match + "/" + cat + "/" + weeks + "/" + page + "/";
	}
	
	
	var mAjax = new Ajax.Updater(
		{success: 'content_main'}, 
		url,
		{
			method: 'get',
            onFailure: reportError,
              // onCreate: function(){Element.clonePosition('spinner', 'content_main', {offsetTop: -25, offsetLeft: -7});},
              onComplete: function(){
               // Empty all galleries before repopulating, otherwise galleries will concatentate
               myLightWindow.galleries = [];
               myLightWindow._setupLinks();
               }
  			
		});
		
		if (renderCrumbs == true){
			$('content_crumbs').innerHTML = '<a id="LN-crumbsLink" title="Klik om te zoeken binnen ' + urldecode(match) + ' " href="#" onclick="toggleCategoryPulldown(\'\',$(\'LN-crumbsLink\'))" >' + urldecode(match).truncate(17) + '</a>';
		}
		matchContainer = match; // fill the matchContainer variable for reuse in other functions

}


function doCheckBasket(element, item){
    
	// Check if cart already contains a certain image_LNID
	// Toggles the add-to-cart button
	// Takes: element; the element in lightbox to update, item; the image_LNID to check for
	// Returns: element content (HTML)

	var url = "/interface/check/basket/" + item + "/";
	
	var mAjax = new Ajax.Request(
		url,
		{
			method: 'get', 
			onFailure: reportError,
			onCreate: function(){Element.clonePosition('spinner', element);},
			onSuccess: function(transport){
				if (transport.responseText == 0){
					
					$(element).update('<a  href="#" onclick="createEntry(\'' + item + '\');">' + gettext('Add to basket') + '</a>');
				}else{
					$(element).update('<a  href="#">' + gettext('Already in there!') + '</a>');
				}
	
			}
			
		});
		

}

function doBasketNameUpdate(id){
    // Updates user current_project pref
    element = 'LN-toolbar-cart-basketnameinput';
    var mAjax = new Ajax.Request(
		'/interface/update/basketname/' + id + '/',
		{
			method: 'get', 
			onFailure: reportError,
			onCreate: function(){Element.clonePosition('spinner', element);},
			onComplete: function(){
			    // reload the cart
                // doShow();

			}
			
		});
		

	
    
}

function doProjectAdd(name){
    // adds project
    
    url = '/interface/add/project/'+ name + '/';
    element = 'LN-toolbar-cart-basketnameinput';
    var mAjax = new Ajax.Request(
		url,
		{
			method: 'get', 
			onFailure: reportError,
			onCreate: function(){Element.clonePosition('spinner', element);},
			onSuccess: function(transport){
                // doShow();
			}
			
		});
	
    
}




function doHideMDall(){
	
	// Hides metatdata info box
	
	if($('MDallContainer')){
		$('content').removeChild($('MDallContainer'));
	}
}

function doShowMDall(s,image_LNID){
	
	// builds and inits a div, then fills it using an AJAX helper 
	// takes: DOM element, image_LNID field
	// Returns: HTML
	
	if($('MDallContainer')){
		$('content').removeChild($('MDallContainer'));
	}
	
	
	
	var MDallContainer = new Element('div',
				{
				id: 'MDallContainer', 
				style: 'top:' + (Element.cumulativeOffset($(s.id))[1] + 16) + 'px; left:' + Element.cumulativeOffset($(s.id))[0] + 'px;'
				});
	
	
	$('content').appendChild(MDallContainer);
	
 	
	var url = "/interface/show/description/" + image_LNID + "/" + 0 + "/";
	
	var mAjax = new Ajax.Updater(
		{success: MDallContainer.id }, 
		url,
		{
			method: 'get', 
			onFailure: reportError,
			onCreate: function(){Element.clonePosition('spinner', MDallContainer);}
			
		});

	
	
}


//*************************************************************************************************
// Draggables
// makes elements draggable, assigns a droppable element
// needs scriptaculous & prototype
// takes element
// triggers createEntry (add item to basket)


// to do: create generic function for these draggables

var _draggable;
function assignDraggable(element){
    // Makes gallery item draggable.
    // takes: DOM element
    
    
	_draggable = new Draggable(element,{revert: true, handles: 'handle'});
		
	var elementStr = element.id;
	elementObj = elementStr.replace('-gallery', '');
    
    if( $('LN-cartItemsContainer')){
    	Droppables.add("LN-cartItemsContainer", 
    	{
    		accept:'gallery', 
    		hoverclass:'LN-cartItemsContainer-active', 
    		onDrop:function(){createEntry(elementObj);}
    		});
	}

	if ($('content_favorites'))	{
    	Droppables.add("content_favorites",
    	{
    		accept: 'gallery', 
    		hoverclass: 'content_favorites-active', 
    		onDrop:function(){
			
    			var myfave = new Favorite(elementObj,'','dock',1);
    			myfave.addItem();
			
    			}
    		});
    }

}

var myFavoritesDraggable;
function assignFavoritesDraggable(element){
	
	myFavoritesDraggable = new Draggable(element,{revert: true, handles: 'handle'});

	
	var elementStr = element;
	elementObj = elementStr.replace('-favorites', '');

	Droppables.add("LN-cartItemsContainer", 
	{
		accept:'favoritesItemContainer', 
		hoverclass:'LN-cartItemsContainer-active', 
		onDrop:function(){createEntry(elementObj);}
		});
	
}

var myFavoritesLargeDraggable;
function assignFavoritesLargeDraggable(element){
	
	myFavoritesLargeDraggable = new Draggable(element,{revert: true, handles: 'handle'});

	
	var elementStr = element;
	elementObj = elementStr.replace('-favorites', '');

	Droppables.add("LN-cartContainer", 
	{
		accept:'gallery', 
		hoverclass:'LN-cartContainer-active', 
		onDrop:function(){createEntry(elementObj);}
		});
	
}

var myCartItemDraggable;
function assignCartItemDraggable(element){
	
	myCartItemDraggable = new Draggable(element,{revert: true, handles: 'handle'});
	
	var elementStr = element;
	elementObj = elementStr.replace('-cartitem', '');

	Droppables.add("content_favorites", 
	{
		accept:'LN-toolbar-cart-basketItemContainer', 
		hoverclass:'content_favorites-active', 
		onDrop:function(){
			var f = new Favorite();
			f.item = elementObj;
			f.addItem();
			}
		});
	
}

var myCartFolderDraggable;
function assignCartFolderDraggable(element){
	
	myCartFolderDraggable = new Draggable(element,{revert: true, handles: 'handle'});
	
	var elementStr = element;
	elementObj = elementStr.replace('-cartitem', '');

	Droppables.add("content_favorites", 
	{
		accept:'LN-toolbar-cart-basketFolder', 
		hoverclass:'content_favorites-active', 
		onDrop:function(){
			var f = new Favorite();
			f.item = elementObj;
			f.addItem();
			}
		});
	
}

//end draggables
//*************************************************************************************************



function showEnlargement(item){
	// build enlargement of image
	// takes image_LNID
	// returns HTML
	
	var containerId = item + '-enlargementContainer';
	
	if(!$(containerId)){
	
		var container = new Element('div', {id: containerId, className: 'enlargementContainer'});
		var link = new Element('a', {href: '#', onclick: '$(\'content\').removeChild($(\'' + containerId + '\'))', title: 'Klik om te sluiten'});
		var image = new Element('img', {id: item + 'enlargementContainer-image', src: '/s/gallery/interface/' + item + '.jpg', border: 0});
		container.appendChild(link);
		link.appendChild(image);
		container.insert({top: '<div class="tagInputContainerClose"><a href="#" onclick="$(\'content\').removeChild($(\'' + containerId + '\'));">x</a></div>'});
		container.hide();
		$('content').appendChild(container);
		Effect.Appear(container, {duration: 0.5});
	}else{
		
		$('content').removeChild($(containerId));
	
	}
}


function buildStartPageFrame(){
	
	var frameTop = new Element('div', {id: 'frameTop'});
	var frameBottom = new Element('div', {id: 'frameBottom'});
	$('content_main').appendChild(frameTop);
	$('content_main').appendChild(frameBottom);
	
	$('content_crumbs').innerHTML = gettext('First 50 most recently added or changed');
	
}

function doShowIllustrationPanel(){
	
	var dimension = $('content').getDimensions();
	
	if (dimension.width > 1152){
		pageSize = 4;
	}else{
		pageSize = 3;
	}
	var startPageContainer = 'frameTop';
	if($('IllustrationStartPageDiv')){
		$(startPageContainer).removeChild($('IllustrationStartPageDiv'));
	}
	
	var startPage = new Element('div', {id: 'IllustrationStartPageDiv', className: 'LN-startPage'});
	$(startPageContainer).appendChild(startPage);
	
	var url = "/interface/start/" + pageSize + "/illustration/1/";
	

	var mAjax = new Ajax.Updater(
		{success: startPage}, 
		url,
		{
			method: 'get', 
			onFailure: reportError,
			onCreate: function(){Element.clonePosition('spinner', startPageContainer, {offsetTop: 74});}	
		});
	
	
	
}


function doShowStartPage(cat,page,start){
	
	// renders both the startpage containers
	// takes cat (ie photo's or illustrations)
	// takes page number
	// returns HTML
	
	// Get rid of any pageThruThumbs nav items	
	//removePageThruThumbsContainers();
	
	var dimension = $('content').getDimensions();
	
	if (dimension.width > 1152){
		pageSize = 4;
	}else{
		pageSize = 3;
	}
	
	
	if (cat == 'photo'){
		startPageContainer = 'frameBottom';
	}else{
		startPageContainer = 'frameTop';
	}
	
	
	
	if($(cat + 'StartPageDiv')){
		$(startPageContainer).removeChild($(cat + 'StartPageDiv'));
	}
	
	
	var startPage = new Element('div', {id: cat + 'StartPageDiv', className: 'LN-startPage'});
	$(startPageContainer).appendChild(startPage);
	
	var url = "/interface/start/" + pageSize + "/" + cat + "/" + page + "/";
	var completeAction;
	// Init an onComplete action only if this function is called standalone (i.e. not as part of the init sequence)
	if (start){
		completeAction = function(){};
	}else{
		completeAction = function(){myLightWindow._setupLinks();};
	}

	var mAjax = new Ajax.Updater(
		{success: startPage}, 
		url,
		{
			method: 'get', 
			onFailure: reportError,
			onCreate: function(){Element.clonePosition('spinner', startPageContainer, {offsetTop: 74});},
			onComplete: completeAction	
		});
	
}

function doEnlargeCartItem(item, source){
	// renders an enlargement of the minithumbnails in the cart
	// needs scriptaculous & prototype
	// takes item (id of an element to be displayed)
	
	if (!$('cartEnlargementDiv')){
		var cartEnlargement = new Element('div', {id: 'cartEnlargementDiv', className: 'BN-cartEnlargement'});
		cartEnlargement.style.display = "none";
		var enlargementImage = new Element('img', {src: '/gallery/interface/' + item, border: '0'});
		cartEnlargement.appendChild(enlargementImage);
		
		$('content').appendChild(cartEnlargement);
		Effect.Appear(cartEnlargement.id, {duration: 0.3});
	}else{
		$('content').removeChild($('cartEnlargementDiv'));
	}
	
}


function indentMenu(element, level, content){
	
	var inserter = new Element('div', {id: element + level});
	inserter.insert({top: content});
	element.appendChild(inserter);
	
}

function doShowHelp(){
	var url = "/interface/show/help/";
	var mAjax = new Ajax.Updater(
		{success: 'content_main'}, 
		url,
		{
			method: 'get', 
			onFailure: reportError,
			onCreate: function(){Element.clonePosition('spinner', $('content_main'));}, 
			onComplete: function(){
				$('content_crumbs').update("");
				new Effect.Morph('content_favorites', {style: 'bottom: -3500px'});
			}
			
		});
	
}

function toggleHelpContentContainers(element, containerHeight){
	
	if(element.next().visible() == false){
		element.next().show();
		element.next().style.height = containerHeight + "px";
		element.down('img').src='/s/_img_interface/triangle-orange-down.png';
	}else{
		element.next().hide();
		element.down('img').src='/s/_img_interface/triangle-orange-right.png';
		}
}

function removePageThruThumbsContainers(){
	// Removes "straggling" pageThruThumbsContainers
	
	$$('div.LN-pageThruThumbs-container').each(function(element){
		$('content').removeChild($(element));
	});	
	
}



function pageThruThumbs(container, image_LNID, page){
	
	// Builds album, pages through thumbs
	// Takes: container (string), image_LNID (string, image identifier), page (integer)

		var updateContainer = container + '-gallery';
		var url = "/interface/show/group/" + container + "/" + image_LNID + "/" + page + "/";
		var mAjax = new Ajax.Updater(
			{success: updateContainer}, 
			url,
			{
				method: 'get', 
				onCreate: function(){Element.clonePosition('spinner', updateContainer, {offsetTop: -74});},
				onFailure: reportError,
				onComplete: function(){
					// Empty all galleries before repopulating, otherwise galleries will concatentate
					//myLightWindow.galleries = [];
					myLightWindow._setupLinks();
					}
				
			});
		
}






function doShowPageLayout(item, element){
	// Shows metadata and image in page layout
	
	if($('pageContainer')){
		$('content').removeChild($('pageContainer'));
	}
	
	new Effect.Appear('LN-pageContainer', { duration: 0.2, from: 0.0, to: 0.7 });


	var pageContainer = new Element("div", {id: "pageContainer", style: "display: none"});
	$('content').appendChild(pageContainer);
	new Effect.Appear('pageContainer', { duration: 0.2, from: 0.0, to: 1.0 });
	
	var url = "/interface/show/description/" + item + "/" + 1 + "/";

	var mAjax = new Ajax.Updater(
		{success: pageContainer}, 
		url,
		{
			method: 'get', 
			onFailure: reportError,
			onCreate: function(){Element.clonePosition('spinner', element);}
			
		});
		
		
	setTimeout(
		function(){doCheckCart('LN-common-pagelayout-addToCartButton', item);
		new Effect.Appear('LN-common-pagelayout-addToCartButton', { duration: 0.2, from: 0.0, to: 1.0 });
		},500);
	
}
//*************************************************************************************************
// Search box with Scriptaculous Autocompleter
function searchItems(){
	
	// Autocompleter for the search box
	// Initiated onload
	

	var mAjax = new Ajax.Autocompleter(
		"LN-toolbar-searchbox", 
		"content_search", 
		"/interface/show/search/", 
		{
			paramName: "s", 
			minChars: 1,
			tokens: ',',
			indicator: 'spinner',
			updateElement: function(item){
				
			}
		});
	
}

function updateUserSearchSelect(mode){
	
	// Updates searchselect in images_user
	
	var url = "/interface/searchselect/update/" + mode + "/";
	var mAjax = new Ajax.Request(
		url,
		{
			method: 'get', 
			onFailure: reportError			
		});
	
	
}

function showSearchSelectMenu(){
	
	// Show search select menu
	
	//var hNames = $H({'simple': 'simpel', 'advanced': 'uitgebreid', 'source': 'bron', 'image': 'beeldnummer' });
	
	var hNames = $H({'simple': gettext('tag'), 'source': gettext('source'), 'image': gettext('image code') });
	
	var hTitles = $H({
		'simple' : '',
		'advanced': '',
		'source' : '',
		'image' : ''});
	
	if($('LN-toolbar-searchSelectMenu')){
		$('content').removeChild($('LN-toolbar-searchSelectMenu'));
	}else{
	
	var d = new Element('div', {id: 'LN-toolbar-searchSelectMenu'});
	Element.clonePosition(d, $('LN-toolbar-searchselect-container'), {offsetTop: 25, setHeight: false, setWidth: false});
	
	hNames.each(function(pair){		
		
		var m = new Element('div', {id: 'LN-toolbar-searchSelectMenuText-' + pair.key, title: hTitles.get(pair.key)});
		m.onclick = function(){
			updateUserSearchSelect(pair.key);
			if($('EMMA-toolbar-searchbox-label')){
        	    $('EMMA-toolbar-searchbox-label').update('Zoek ' + pair.value);
        	}else{
			    $('LN-toolbar-searchbox').value = 'Zoek ' + pair.value;
			}
			$('LN-toolbar-searchbox').title = hTitles.get(pair.key);
			$('content').removeChild($('LN-toolbar-searchSelectMenu'));
			$('LN-toolbar-searchselect-listItem').title = gettext('You have chosen for ') + pair.value;
			$('LN-toolbar-searchselect-image').title = gettext('You have chosen for ') + pair.value;
			};
		var i = new Element('img', {src: '/s/_img_interface/ln-search-select-items-' + pair.key + '.png', border: 0});
		m.appendChild(i);
		m.insert({bottom:pair.value});
		d.appendChild(m);
	});
	
	$('content').appendChild(d);
	}
	
}


function rotate(item,rotation){
	// Rotates image
	// Takes: item (image_LNID, string); rotation (integer)
	
	
	element = item + '-gallery';
	
	url = '/interface/rotate/' + item + '/' + rotation + '/';
	
	if (confirm(gettext('Do you really want to rotate this item?'))){
		var mAjax = new Ajax.Updater(
			{success: $('debug')}, 
			url,
			{
				method: 'get', 
				onFailure: reportError,
				onCreate: function(){Element.clonePosition('spinner', element);}
			
			});
		}
}


Autocompleter.Base.addMethods( {
  	// Redefine methods:
	// Change the behaviour of Autocompleter.Base
	// - return gives us results
	// - last item on the list can be used as switch

  onKeyPress: function(event) {
    if(this.active)
      switch(event.keyCode) {
       case Event.KEY_TAB:
       case Event.KEY_RETURN:
        
		doShowThumbs('+' + $F("LN-toolbar-searchbox").replace(' ',' +'),'_ALL_', 1000,1);
		
		
		Event.stop(event);
       case Event.KEY_ESC:
         this.hide();
         this.active = false;
         Event.stop(event);
         return;
       case Event.KEY_LEFT:
       case Event.KEY_RIGHT:
         return;
       case Event.KEY_UP:
         this.markPrevious();
         this.render();
         Event.stop(event);
         return;
       case Event.KEY_DOWN:
         this.markNext();
         this.render();
         Event.stop(event);
         return;
      }
     else 
       if(event.keyCode==Event.KEY_TAB || event.keyCode==Event.KEY_RETURN || 
         (Prototype.Browser.WebKit > 0 && event.keyCode == 0)) return;

    this.changed = true;
    this.hasFocus = true;

    if(this.observer) clearTimeout(this.observer);
      this.observer = 
        setTimeout(this.onObserverEvent.bind(this), this.options.frequency*1000);
  },

  onClick: function(event) {
    var element = Event.findElement(event, 'LI');
    this.index = element.autocompleteIndex;
	if(!$('LN-searchbox-toggle')){
    	this.selectEntry();
    	this.hide();
	}else{
		
        this.active = false;
        Event.stop(event);
        return;

	}
  }


});



