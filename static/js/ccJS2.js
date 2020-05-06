var count = 1;

var submitted = false;

var seqElements = ["Pr", "RBS", "GOI", "Term"];

var elemOptions = {"Pr": ["psbA"],
					"RBS": ["S3", "A", "E"],
					"GOI": ["adh", "pdc", "PK", "EYFP", "sYFP2"],
					"Term": ["T1"]};

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
		retString += "<option value = '" + option + "'>" + option + "</option>"; //id?
	}
	retString += "</select>";
	return retString;
}

function formatSection(){
	var format = "<div class = 'elemDiv'>"; //div
	format += "<p class = 'elemName'>Element " + count + "</p>";
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
function addElem(){
	$("#elements").append(formatSection());
	$("#elementError").text("");
}

function rmLastElem(){
	if (document.getElementsByClassName("elemDiv").length > 0){
		var lastChild = document.getElementById("elements").lastChild;
		document.getElementById("elements").removeChild(lastChild);

		count -= 1;
	}
	else {
		$("#elementError").text("No elements to remove.");
	}
}

//submitForm and validate
function submitForm(){
	var allFields = document.getElementsByClassName("formField");

	//get data for all formFields
	var allData = "{";
	for (i = 0; i < allFields.length; i++){
		var name = allFields[i].name; //key: name
		allData += "'" + name + "': "; //: is toString necessary?
		var value = allFields[i].value; //value: value
		allData += "'" + value + "'";

		if(i < allFields.length - 1){ //,
			allData += ", ";
		}
	}
	allData += "}";

	$.ajax({
		data : {bigData: allData},
		type : 'POST',
		url : '/process'
		})
	.done(function(data){
		var newNode = document.createElement("p");
		newNode.innerHTML = data.output;

		var showOutput = document.getElementById("showOutput");
		var oldChild = document.getElementById("outputParagraph");

		newNode.id = "outputParagraph";

		showOutput.replaceChild(newNode, oldChild);
	});
	event.preventDefault();

	return 0;
}

function validate(){
	var retValue = true;

	//check number of elements
	if(document.getElementsByClassName("formField").length == 2){
		$("#elementError").text("No elements.");
		retValue = false;
	}
	else{
		$("#downloadMessage").text("")
		$("#elementError").text("");		
	}

	//submit
	if(retValue){
		submitForm();
		submitted = true;
	}

	return retValue;
}

//download file
function downloadFile(){
	if(submitted){
		$("#downloadMessage").text("Preparing files...");
		window.location.href = "/sequencesZip.zip";
		event.preventDefault();
		$("#downloadMessage").text("Downloaded.");
	}
	else{
		$("#downloadMessage").text("No sequence submitted.");
	}
}
