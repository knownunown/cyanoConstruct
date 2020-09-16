/* Toggling sections */
function switchToggleText(headDiv){
	//Change the text displayed due to toggling display
	var span = headDiv.nextElementSibling;

	if(span.textContent == "[Click to show]"){
		span.textContent = "[Click to hide]";
	}
	else{
		span.textContent = "[Click to show]";
	}
}

function toggleDisplay(id){
	//Toggle whether the div with the id is displayed
	var div = document.getElementById(id);

	if(div.style.display == "none"){
		div.style.display = "block";
	}
	else{
		div.style.display = "none";
	}
}

/* Page loading-related functions */

//technically, removes the hash and then refreshes BUT IT DOESN'T QUITE WORK
function refreshPage(){
	if(window.location.hash){
		window.location.href = window.location.href.split('#')[0];
	}

	location.reload();
}

function loadNormal(){
	showLibrary("Personal");
}

function bodyOnload(){
	if(window.location.hash != ""){
		var contentID = window.location.hash.substring(1) + "Data";

		document.getElementById(contentID).parentNode.style.display = "block";
		document.getElementById(contentID).style.display = "block";

		//obviously this is suboptimal
		if(contentID.includes("Default")){
			showLibrary("Default");
		}
		else{
			showLibrary("Personal");
		}

	}
	else{
		loadNormal();
	}

	return false;
}

function showLibrary(libraryName){
	//Displays a library tab, either the Personal or Default library
	var allLibraries = document.getElementsByClassName("libraryContents");

	for(library of allLibraries){
		library.style.display = "none";
	}

	document.getElementById(libraryName + "Library").style.display = "block";

	//format the tabs

	var allTabs = document.getElementsByClassName("libraryTab");
	for(tab of allTabs){
		tab.className = tab.className.replace(" activeTab", "");
	}

	document.getElementById(libraryName + "Tab").className += " activeTab";

	return false;
}

/* Functions for removing things */

function removeComponent(id){
	//delete a component from the database
	if(window.confirm("This will permanently remove a component from your library.\nAre you sure?")){

		$.ajax({
			data : {compID: id},
			type : 'POST',
			url : '/removeComponent'
			})
		.done(function(data){
			if(data.succeeded){
				alert("Component removed");
				refreshPage();
			}
			else{
				alert("ERROR: " + data.errorMessage);
			}
		});

		return true;
	}
}

function removeSequence(id){
	//delete a named sequence from the database
	if(window.confirm("This will permanently remove this sequence and all components derived from it from your library.\nAre you sure?")){

		$.ajax({
			data : {sequenceID: id},
			type : 'POST',
			url : '/removeSequence'
			})
		.done(function(data){
			if(data.succeeded){
				alert("Sequence removed");
				refreshPage();
			}
			else{
				alert("ERROR: " + data.errorMessage);
			}
		});

		return true;
	}
}

function removeBackbone(id){
	//delete a backbone from the database
	if(window.confirm("This will permanently remove this backbone from your library.\nAre you sure?")){

		$.ajax({
			data : {backboneID: id},
			type : 'POST',
			url : '/removeBackbone'
			})
		.done(function(data){
			if(data.succeeded){
				alert("Backbone removed");
				refreshPage();
			}
			else{
				alert("ERROR: " + data.errorMessage);
			}

		});

		return true;
	}
}

/* Downloads */

function downloadLibrary(libName){
	//download an entire library
	$.ajax({
		data : {libraryName: libName},
		type : 'POST',
		url : '/downloadLibrary'
		})
	.done(function(data){
		if(data.succeeded){
			var date = new Date();
			var offset = date.getTimezoneOffset();
			window.location.href = "/library.zip?timezoneOffset=" + offset;
		}
		else{
			alert("ERROR: " + data.errorMessage);
		}

	});
	event.preventDefault();
}

function downloadComponentSequence(id){
	//download a single component
	var date = new Date();
	var offset = date.getTimezoneOffset();

	window.location.href = "/componentZIP.zip?id=" + id + "&timezoneOffset=" + offset;

	return false;
}
