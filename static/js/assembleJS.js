var count = 1;

var submitted = false;

var currFidLimit;


function inArray(elem, array){
	for(arrayElement of array){
		if(arrayElement == elem){
			return true;
		}
	}
	return false;
}

//format element divs
function formatElements(){ //just get a thing for the seqElements
	var retString = "<select class = 'formField' name = 'elemType" + count + "' id = 'elemType" + count + "' onchange = 'updateForm(this)'>";
	for(seqElem of seqElements){
		retString += "<option value = '" + seqElem + "'>" + seqElem + "</option>"; //need an id?
	}
	retString += "</select>";
	return retString;
}

function formatOptions(elementToUse, idNumber = count){ //get a thing for the lower down stuff
	var retString = "<select class = 'formField' name = 'elemName" + idNumber + "' id = 'elemName" + idNumber + "'>";
	for(option of elemOptions[elementToUse]){
		var idString = idNumber.toString();
		if(inArray(idNumber, compByPosition[option])){
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
	format += "<span = 'elemName'>" + count + ":</span>";
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
	if (document.getElementsByClassName("elemDiv").length > 0){
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
		retValue = false;
	}

	//check if terminal is valid
	var termTypeStr = "elemType" + (count - 1);
	var termTypeVal = document.getElementById(termTypeStr).value;

	var termNameStr = "elemName" + (count - 1);
	var termNameVal = document.getElementById(termNameStr).value;

	var isValidTerm = false;
	for(name of validTerminals[termTypeVal]){
		if(name == termNameVal){
			isValidTerm = true;
			break;
		}
	}

	if(!isValidTerm){
		var errorStr = "There is no " + termTypeVal + " " + termNameVal + " component that can be the terminal.";
		$("#elementError").text(errorStr);
		retValue = false;
		//return false;
	}

	//check values of elements & make allData
	var allFields = document.getElementsByClassName("formField");

	var allData = "{";
	for (i = 0; i < allFields.length; i++){

		if(allFields[i].value == ""){
			$("#elementError").text("Not all elements have values.");
			retValue = false;
			break;		
		}

		var name = allFields[i].name; //key: name
		allData += "'" + name + "': ";
		var value = allFields[i].value; //value: value
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
	//great
	var fidelitySelect = document.getElementById("fidelity");

	currFidLimit = fidelityLimits[fidelitySelect.value];

	if(count - 1 > currFidLimit){
		$("#elementError").text("Can't have more than " + currFidLimit + " elements at current fidelity.");
	}
}

function bodyOnload(){
	fidelityChanged();
}
