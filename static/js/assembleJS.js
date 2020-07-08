var count = 1;

var submitted = false;

var currFidLimit;

function validPos(pos, name){
	for(combination of posTermComb[name]){
		if(pos == combination.position){
			return true;
		}
	}

	return false;
}

//format element divs
function formatElements(){ //just get a thing for the seqElements
	var retString = "<select class = 'formField' name = 'elemType" + count + "' id = 'elemType" + count + "' onchange = 'updateForm(this)'>";
	for(seqElem of seqElements){
		retString += "<option value = '" + seqElem[0] + "'>" + seqElem[1] + "</option>"; //need an id?
	}
	retString += "</select>";
	return retString;
}

function formatOptions(elementToUse, idNumber = count){ //get a thing for the lower down stuff
	var retString = "<select class = 'formField' name = 'elemName" + idNumber + "' id = 'elemName" + idNumber + "'>";
	for(option of elemOptions[elementToUse]){
		var idString = idNumber.toString();
		if(validPos(idNumber, option)){
			retString += "<option value = '" + option + "'>" + option + "</option>"; //id?			
		}
		else{
			retString += "<option value = '" + option + "' disabled>" + option + "</option>"
		}
	}
	retString += "</select>";
	return retString;
}

function formatSection(){
	var format = "<div class = 'elemDiv'>"; //div
	format += "<span class = 'elemName'>" + count + ":</span>";
	//first select
	format += "<label for = 'elemType" + count + "'>Type</label>";
	format += "<div>";
	format += formatElements();
	format += "</div>";
	//second select
	format += "<label for = 'elemName" + count + "'>Name</label>";
	format += "<div>";
	format += formatOptions("Pr"); //idk man
	format += "</div></div>";
	count += 1;
	return format;
}

function formatSec0(){
	var format = "<div class = 'elemDiv'>";
	format += "<span class = 'elemName'>0:</span>";
	//first select
	format += "<label for = 'elemType0'>Type</label>";
	format += "<div><select class = 'formField' name = 'elemType0' id = 'elemType0'><option value = 'Pr'>Promoter</option></select></div>";
	//second select
	format += "<label for = 'elemName0'>Name</label>";
	format += "<div>";
	format += formatOptions("Pr", 0); //idk man
	format += "</div></div>";
	return format;
}

function formatSecT(){
	var format = "<div class = 'elemDiv'>";
	format += "<span class = 'elemName'>T:</span>";
	//first select
	format += "<label for = 'elemType999'>Type</label>";
	format += "<div><select class = 'formField' name = 'elemType999' id = 'elemType999'><option value = 'Term'>Terminator</option></select></div>";
	//second select
	format += "<label for = 'elemName999'>Name</label>";
	format += "<div>";
	format += formatOptions("Term", 999);
	format += "</div></div>";
	return format;
}


function updateForm(selectSeq){
	//get all nodes
	var newValue = selectSeq.value;
	var bigDiv = selectSeq.parentNode.parentNode;
	var secondDiv = bigDiv.lastChild;
	var oldNode = secondDiv.lastChild;

	//get number for the name of the new form
	var oldName = selectSeq.name;
	var oldNumber = Number(oldName.substr(8)); //extract the number of the element

	//create new form as a node
	var newNode = document.createElement("div");
	newNode.innerHTML = formatOptions(newValue, oldNumber);
	
	//replace the old node
	secondDiv.replaceChild(newNode, oldNode);
}

//alter elements
function validateAddElem(){
	if(currFidLimit < count){
		$("#elementError").text("Can't have more than " + currFidLimit.toString() + " elements at current fidelity.");
		return false;
	}
	else{
		$("#elementError").text("");
		return true;
	}
}

function addElem(){
	if(validateAddElem()){
		$("#elements").append(formatSection());
	}
}

function rmLastElem(){
	if (document.getElementsByClassName("elemDiv").length > 2){
		var lastChild = document.getElementById("elements").lastChild;
		document.getElementById("elements").removeChild(lastChild);

		count -= 1;

		validateAddElem();

	}
	else {
		$("#elementError").text("No elements to remove.");
	}

}


//submitForm and validate
function submitForm(allData){
	var successfulSubmit;

	$.ajax({
		data : {assemblyData: allData},
		type : 'POST',
		url : '/processAssembly'
		})
	.done(function(data){
		document.getElementById("showOutput").innerHTML = data.output;

		if(data.succeeded){
			submitted = true;
		}
		else{
			submitted = false;
		}
	});
	event.preventDefault();

	return submitted;
}

function validate(){
	var retValue = true;

	//check number of elements
	if(document.getElementsByClassName("elemDiv").length == 2){
		$("#elementError").text("No elements.");
		retValue = false;
		return false;
	}
	else{
		$("#downloadMessage").text("");
		$("#elementError").text("");
	}

	//check number of elements vs fidelity
	if(count - 1 > currFidLimit){
		$("#elementError").text("Too many elements for current fidelity.");
		retValue = false;
		return false;
	}

	//check the positions of everything
	var collectedError = "";

	//check values of elements & make allData
	var allFields = document.getElementsByClassName("formField");

	var now = new Date();

	var allData = "{'timezoneOffset': '" + now.getTimezoneOffset() + "', ";
	for (i = 0; i < allFields.length; i++){

		//check if something is selected
		if(allFields[i].value == ""){
			$("#elementError").text("Not all elements have values.");
			retValue = false;
			//break;	
			return false;	
		}

		var name = allFields[i].name; 	//key: name
		var value = allFields[i].value; //value: value

		//check terminalLetter
		if(name.substr(0,8) == "elemName"){
			var pos = name.substr(8);
			var isTerminal = (pos == count - 1);

			//should never happen
			if(posTermComb[value] == "undefined"){
				retValue = false;
				collectedError += "Can't find valid " + value + ".";
			}
			
			else{
				var validPos = false;
				var validLetter = false;

				//go through all possible position & terminalLetter combinations
				for(posTerm of posTermComb[value]){
					//only look further if it has the right position
					if(pos == posTerm.position){
						//found a valid position
						validPos = true;

						//check the terminalLetter
											//last element
						if(isTerminal){
							if(posTerm.terminalLetter == "L"){
								validLetter = true;
								break;
							}
						}
											//middle element
						else if(posTerm.terminalLetter == "M"){
							validLetter = true;
							break;
						}
											//special element (S or T)
						else if((pos == "0" && posTerm.terminalLetter == "S") || (pos == "999" && posTerm.terminalLetter == "T")){
							validLetter = true;
							break;
						}
					}
				}
				
				//error messages
				if(!validPos){ 				//bad position
					retValue = false;
					collectedError += "No valid " + value + " at position " + pos + ". ";
				}
				if(!validLetter){ 			//bad terminalLetter
					retValue = false;
					if(isTerminal){
						collectedError += "No valid terminal " + value + " at position " + pos + ". ";
					}
					else{
						collectedError += "No valid non-terminal " + value + " at position " + pos + ". ";
					}
				}
			}
		}

		allData += "'" + name + "': ";
		allData += "'" + value + "'";

		if(i < allFields.length - 1){ //,
			allData += ", ";
		}
	}
	allData += "}";

	//submit
	if(retValue){
		submitted = submitForm(allData);
	}
	else{
		$("#elementError").text(collectedError);
	}

	return retValue;
}

//download file
function downloadFile(){
	if(submitted){
		$("#downloadMessage").text("Preparing files...");
		window.location.href = "/assembledSequence.zip";
		event.preventDefault();
		$("#downloadMessage").text("Downloaded.");
	}
	else{
		$("#downloadMessage").text("No sequence submitted.");
	}
}

//
function fidelityChanged(){
	var fidelitySelect = document.getElementById("fidelity");

	currFidLimit = fidelityLimits[fidelitySelect.value];

	if(count - 1 > currFidLimit){
		$("#elementError").text("Can't have more than " + currFidLimit + " elements at current fidelity.");
	}
}

function getBackboneType(){
	for(radio of document.getElementsByName("backboneType")){
		if(radio.checked){
			return radio.value;
		}
	}
}

function backboneChanged(){
	var currBackboneID = document.getElementById("backboneName").value;
	var currBackboneType = getBackboneType();
	document.getElementById("backboneDescription").textContent = backboneDescs[currBackboneID];
}

function backboneTypeChanged(){
	var currBackboneType = getBackboneType();

	var newOptions = "";

	for(bb of backbones[currBackboneType]){
		newOptions += "<option value = '" + bb[0] + "'>" + bb[1] + "</option>";
	}

	document.getElementById("backboneName").innerHTML = newOptions;

}


function bodyOnload(){
	fidelityChanged();
	backboneTypeChanged();
	backboneChanged();

	document.getElementById("elem0").innerHTML = formatSec0();
	document.getElementById("elemT").innerHTML = formatSecT();
}
