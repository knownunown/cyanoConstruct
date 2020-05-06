function toggleDisplay(id){
	var div = document.getElementById(id);

	if(div.style.display == "none"){
		div.style.display = "block";
	}
	else{
		div.style.display = "none";
	}
}

//technically, removes the hash and then refreshes
function refreshPage(){
	if(window.location.hash){
		window.location.href = window.location.href.split('#')[0];
	}
}

function loadNormal(){
		showLibrary("Default");
}

function bodyOnload(){
	if(window.location.hash != ""){
		var contentID = window.location.hash.substring(1) + "Data";


		//it doesn't work because instead of returning null, it just aborts the script
		/*if(document.getElementByID(contentID) == null){
			loadNormal();
			return;
		}*/

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

function downloadComponentSequence(elemType, name, pos, terminal){
	componentInfo = "{'elemType': '" + elemType + "', 'name': '" + name + "', 'pos': '" + pos + "', 'terminal': '" + terminal + "'}";

	$.ajax({
		data : {component: componentInfo},
		type : 'POST',
		url : '/locateComponentForZip'
		})
	.done(function(data){
		if(data.succeeded){
			window.location.href = "/componentZip.zip";
		}

	});
	event.preventDefault();


	return false;
}

function showLibrary(libraryName){
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

function removeComponent(elemType, name, pos, terminal){
	if(window.confirm("This will permanently remove a component from your library.\nAre you sure?")){

		componentInfo = "{'elemType': '" + elemType + "', 'name': '" + name + "', 'pos': '" + pos + "', 'terminal': '" + terminal + "'}";

		$.ajax({
			data : {componentToRemove: componentInfo},
			type : 'POST',
			url : '/removeComponent'
			})
		.done(function(data){
			if(data.succeeded){
				alert("Component removed");
				refreshPage();
			}
			else{
				alert("There was a problem.");
			}

		});
		//event.preventDefault();


		return true;
	}
}

function removeSequence(elemType, name){
	if(window.confirm("This will permanently remove sequence " + name + " and all components derived from it from your library.\nAre you sure?")){

		sequenceInfo = "{'elemType': '" + elemType + "', 'name': '" + name + "'}";

		$.ajax({
			data : {sequenceToRemove: sequenceInfo},
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
		//event.preventDefault();


		return true;
	}
}