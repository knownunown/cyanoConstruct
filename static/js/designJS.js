var submitted = false;

var newID = -1;

//smooth scrolling
function scrollToId(id){
	document.getElementById(id).scrollIntoView({block: "start", inline: "start", behavior: "smooth"})
}

function selectForm(){
	if(document.getElementById("designComponent").checked){
		document.getElementById("componentForm").style.display = "block";

		document.getElementById("sequenceForm").style.display = "none";
		document.getElementById("backboneForm").style.display = "none";

		scrollToId("componentForm");
	}
	else if(document.getElementById("designSequence").checked){
		//do that
		//disable all the other stuff?
		document.getElementById("sequenceForm").style.display = "block";

		document.getElementById("componentForm").style.display = "none";
		document.getElementById("backboneForm").style.display = "none";

		scrollToId("designSequence");
	}
	else if(document.getElementById("designBackbone").checked){
		document.getElementById("backboneForm").style.display = "block";

		document.getElementById("componentForm").style.display = "none";
		document.getElementById("sequenceForm").style.display = "none";

		scrollToId("backboneForm");
	}
}

//named sequence
function formatNSname(){
	var currentType = document.getElementById("NStype").value;

	//alter things in the spacer section
	if(currentType == "Pr"){
		document.getElementById("componentPos0").disabled = false;
		document.getElementById("componentPosT").disabled = true;

		document.getElementById("componentPosT").checked = false;
	}
	else if(currentType == "Term"){
		document.getElementById("componentPos0").disabled = true;
		document.getElementById("componentPosT").disabled = false;

		document.getElementById("componentPos0").checked = false;
	}
	else{
		document.getElementById("componentPos0").disabled = true;
		document.getElementById("componentPosT").disabled = true;

		document.getElementById("componentPosT").checked = false;
		document.getElementById("componentPos0").checked = false;
	}

	//format the options
	var retString = "";

	for(ns of namedSequencesNames[currentType]){ //change so the value is the ID?
		retString += "<option value = '" + ns.id + "'>" + ns.name + "</option>";
	}

	document.getElementById("NSname").innerHTML = retString;

	formatNSsequence();


	return false;
}

function formatNSsequence(){
	var currID = document.getElementById("NSname").value;

	//adjust sequence textarea
	document.getElementById("NSseq").innerText = namedSequencesSeqs[currID];

	return false;
}

function finishNSSection(){
	var id = document.getElementById("NSname").value

	//request
	$.ajax({
		data : {NSid: id},
		type : 'POST',
		url : '/findNamedSeq'
		})
	.done(function(data){
		document.getElementById("NSoutput").innerHTML = data.output;

		//only can proceed if successfully created
		if(data.succeeded){
			document.getElementById("selectNS").disabled = true;
			document.getElementById("componentSpacers").disabled = false;	

			document.getElementById("NStype").value;

			scrollToId("componentSpacers");
		}
		else{
			document.getElementById("selectNS").disabled = false;
			document.getElementById("componentSpacers").disabled = true;
		}
	});
	event.preventDefault();

	return false;
}

//spacers
function validateSpacers(){
	var canProceed = true;

	if(document.getElementById("componentPos").value == ""){
		var pos0 = document.getElementById("componentPos0");
		var posT = document.getElementById("componentPosT");

		if(!((!pos0.disabled && pos0.checked) || (!posT.disabled && posT.checked))){
			canProceed = false;
			document.getElementById("posError").textContent = "Need a position.";			
		}
	}
	else{
		document.getElementById("posError").textContent = "";
	}

	return canProceed;
}

function findSpacers(){
	//validate
	if(!validateSpacers()){
		return false;
	}

	//format data
	var pos0 = document.getElementById("componentPos0");
	var posT = document.getElementById("componentPosT");

	if(!pos0.disabled && pos0.checked){
		var spacersData = "{'componentPos': '0', 'isTerminal': '" + document.getElementById("componentTerminal").checked + "'}";
	}
	else if(!posT.disabled && posT.checked){
		var spacersData = "{'componentPos': '999', 'isTerminal': '" + document.getElementById("componentTerminal").checked + "'}";
	}
	else{
		var spacersData = "{'componentPos': '" + document.getElementById("componentPos").value + 
						"', 'isTerminal': '" + document.getElementById("componentTerminal").checked + "'}";
	}


	//actually find the spacers
	$.ajax({
		data : {"spacersData": spacersData},
		type : 'POST',
		url : '/findSpacers'
		})
	.done(function(data){
		document.getElementById("spacersOutput").innerHTML = data.output;

		//only can proceed if successfully created
		if(data.succeeded){
			document.getElementById("spacersFinish").disabled = false;
		}
		else{
			document.getElementById("spacersFinish").disabled = true;			
		}
	});

}

function finishSpacersSection(){
	document.getElementById("componentSpacers").disabled = true;
	document.getElementById("componentPrimers").disabled = false;

	scrollToId("componentPrimers");
	return false;
}

function goBackSpacers(){
	document.getElementById("selectNS").disabled = false;
	document.getElementById("componentSpacers").disabled = true;

	scrollToId("selectNS");

	return false;
}

//primers
function validatePrimers(){
	var canProceed = true;

	//melting point
	if(document.getElementById("componentTM").value == ""){ //needs to be within range
		canProceed = false;
		document.getElementById("TMError").textContent = "Need a melting point.";
	}
	else{
		document.getElementById("TMError").textContent = "";		
	}

	//melting point range
	if(document.getElementById("TMRange").value == ""){ //needs to be within range (1, 10)
		canProceed = false;
		document.getElementById("TMRangeError").textContent = "Need a range.";
	}
	else{
		document.getElementById("TMRangeError").textContent = "";
	}

	return canProceed;
}

function findPrimers(){
	//validate
	if(!validatePrimers()){
		return false;
	}

	primersData = "{'meltingPoint': '" + document.getElementById("componentTM").value + 
					"', 'meltingPointRange': '" + document.getElementById("TMRange").value + 
					"', 'skipPrimers': '" + document.getElementById("skipPrimers").checked +"'}";

	//actually find the primers
	$.ajax({
		data : {"primersData": primersData},
		type : 'POST',
		url : '/findPrimers'
		})
	.done(function(data){
		document.getElementById("primersOutput").innerHTML = data.output;

		//only can proceed if successfully created
		if(data.succeeded){
			document.getElementById("primersFinish").disabled = false;
		}
		else{
			document.getElementById("primersFinish").disabled = true;			
		}
	});

	return false;
}

function finishPrimersSection(){
	document.getElementById("componentPrimers").disabled = true;
	document.getElementById("createNewComponent").disabled = false;
	document.getElementById("createSubmit").disabled = false;
	document.getElementById("finishBack").disabled = false;

	scrollToId("createNewComponent");

	if(!submitted){
		document.getElementById("downloadSeqs").disabled = true;
		document.getElementById("resetForm").disabled = true;
	}

	return false;
}

function goBackPrimers(){
	document.getElementById("componentSpacers").disabled = false;
	document.getElementById("componentPrimers").disabled = true;

	scrollToId("componentSpacers");

	return false;
}

//finish & create component
function createComponent(){
	//send stuff through
	$.ajax({
		data : {},
		type : 'POST',
		url : '/finishComponent'
		})
	.done(function(data){
		document.getElementById("createOutput").innerHTML = data.output;

		if(data.succeeded){
			//document.getElementById("primersFinish").disabled = false;
			submitted = true;
			newID = data.newID;

			document.getElementById("createSubmit").disabled = true;
			document.getElementById("downloadSeqs").disabled = false;
			document.getElementById("resetForm").disabled = false;
			document.getElementById("finishBack").disabled = true;
		}
		else{
			document.getElementById("createSubmit").disabled = false;
			document.getElementById("downloadSeqs").disabled = true;	
			document.getElementById("resetForm").disabled = true;		
			document.getElementById("finishBack").disabled = false;
		}
	});


	return false;
}

function goBackFinish(){
	document.getElementById("componentPrimers").disabled = false;
	document.getElementById("createNewComponent").disabled = true;

	scrollToId("componentPrimers");

	return false;
}

function downloadZIPFile(){
	if(submitted && (newID != -1)){
		document.getElementById("downloadMessage").textContent = "Preparing files...";

		window.location.href = "/newComponent.zip?id=" + newID.toString();
		event.preventDefault();

		document.getElementById("downloadMessage").textContent = "Downloaded.";
	}
	else{
		document.getElementById("downloadMessage").textContent = "No component to download.";
	}

	return false;
}


/* Create Sequence */

function validateSequence(){
	var canProceed = true;

	if(document.getElementById("seqName").value == ""){
		canProceed = false;
		document.getElementById("seqNameError").textContent = "Need a name 1-20 characters long.";
	}
	else{
		document.getElementById("seqNameError").textContent = "";
	}

	//sequence
	if(document.getElementById("sequenceSeq").value == ""){
		canProceed = false;
		document.getElementById("sequenceSeqError").textContent = "Need a sequence.";
	}
	else{
		document.getElementById("sequenceSeqError").textContent = "";
	}

	return canProceed;
}

function newNS(){
	if(!validateSequence()){
		return false; //not very useful return value
	}

	//remove whitespace from sequence
	document.getElementById("sequenceSeq").value = document.getElementById("sequenceSeq").value.replace(/\s/g,"");

	//create the NamedSequence
	var newNSData = "{'NStype': '" + document.getElementById("seqType").value +
					"', 'NSname': '" + document.getElementById("seqName").value + 
					"', 'NSseq': '" + document.getElementById("sequenceSeq").value + "'}";

	//send request
	$.ajax({
		data : {"newNSData": newNSData},
		type : 'POST',
		url : '/newNamedSeq'
		})
	.done(function(data){
		document.getElementById("sequenceOutput").innerHTML = data.output;

		//only can proceed if successfully created
		if(data.succeeded){
			document.getElementById("resetSeqForm").disabled = false;
		}
		else{
		}
	});
	event.preventDefault();

	return false;
}

function resetSeq(){
	document.getElementById("sequenceForm").reset();

	document.getElementById("resetSeqForm").disabled = true;
}

/* backbone */
function validateBackbone(){
	/* UPDATE! */
	var canProceed = true;

	var errorArray = Array();

	//name
	if(document.getElementById("backboneName").value == ""){
		canProceed = false;
		document.getElementById("backboneNameError").textContent = "Need a name 1-20 characters long.";
		errorArray.push("name");
	}
	else if(document.getElementById("backboneName").value.length > 20){
		canProceed = false;
		document.getElementById("backboneNameError").textContent = "Name must be 20 or fewer characters long.";
		errorArray.push("name");
	}
	else{
		document.getElementById("backboneNameError").textContent = "";
	}

	//description
	if(document.getElementById("backboneDesc").value == ""){
		canProceed = false;
		document.getElementById("backboneDescError").textContent = "Need a description 1-128 characters long.";
		errorArray.push("description");
	}
	else if(document.getElementById("backboneDesc").value.length > 128){
		canProceed = false;
		document.getElementById("backboneDescError").textContent = "Description must be 128 or fewer characters long.";
		errorArray.push("description");
	}
	else{
		document.getElementById("backboneDescError").textContent = "";
	}

	//sequence
	if(document.getElementById("backboneSeq").value == ""){
		canProceed = false;
		document.getElementById("backboneSeqError").textContent = "Need a sequence.";
		errorArray.push("sequence");
	}
	else{
		document.getElementById("backboneSeqError").textContent = "";
	}

	if(!canProceed){
		var errorStr = "Error";
		if(errorArray.length > 1){
			errorStr += "s with the ";

			for(i = 0; i < errorArray.length - 2; i++){
				errorStr += errorArray[i] + ", ";
		    }
      
			errorStr += errorArray[errorArray.length - 2] + " and " + errorArray[errorArray.length - 1];
      
		}
	    else{
	        errorStr += " with the " + errorArray[0];
		}

		errorStr += ".";
      
		document.getElementById("backboneOutput").textContent = errorStr;
	}

	return canProceed;
}

function newBackbone(){
	if(!validateBackbone()){
		return false;
	}

	document.getElementById("backboneSeq").value = document.getElementById("backboneSeq").value.replace(/\s/g,"");

	var features = document.getElementById("featuresFile").innerText + "\n" + 
				   document.getElementById("featuresInput").innerText;

	console.log(features);

	var newBackboneData = "{'backboneName': '" + document.getElementById("backboneName").value +
						  "', 'backboneSeq': '" + document.getElementById("backboneSeq").value + 
						  "', 'backboneDesc': '" + document.getElementById("backboneDesc").value + 
						  "', 'backboneType': '" + document.getElementById("backboneType").value +
						  "', 'backboneFeatures': \"\"\"" + features + "\"\"\"}";

	$.ajax({
		data : {"newBackboneData": newBackboneData},
		type : 'POST',
		url : '/newBackbone'
		})
	.done(function(data){
		console.log(data)
		document.getElementById("backboneOutput").innerHTML = data.output;

		//only can proceed if successfully created
		if(data.succeeded){
			document.getElementById("resetBackboneForm").disabled = false;
		}
		else{
		}
	});
	event.preventDefault();
}

function backboneFileProcess(){
	var files = document.getElementById("backboneFile").files;
	if(files.length == 0){
		document.getElementById("backboneFileError").textContent = "No file selected";
		return false;
	}
	else {

		var backboneFileData = files[0];

		//alert(backboneFileData.size);

		$.ajax({
			data : backboneFileData,
			type : 'POST',
		    processData: false,
		    contentType: false,
			url : '/backboneFileProcess?size=' + backboneFileData.size.toString()
			})
		.done(function(data){
			document.getElementById("backboneFileError").innerHTML = data.output;

			//only can proceed if successfully created
			if(data.succeeded){
				document.getElementById("featuresFile").innerText = data.featureStr;
				document.getElementById("backboneSeq").value = data.sequence;
				document.getElementById("backboneDesc").value = data.definition;
				document.getElementById("backboneName").value = data.name;
				document.getElementById("resetBackboneForm").disabled = false;
			}
			else{
			}
		});
		event.preventDefault();

	}
}

function resetBackbone(){
	document.getElementById("backboneForm").reset();

	document.getElementById("resetBackboneForm").disabled = true;
}

/* misc */

function clearEverything(scrollToNS){
	//reset values
	document.getElementById("componentForm").reset();
	//and then. Reset the values on the server

	//clear output messages
	document.getElementById("createOutput").innerHTML = "";
	document.getElementById("primersOutput").innerHTML = "";
	document.getElementById("spacersOutput").innerHTML = "";
	document.getElementById("downloadMessage").textContent = "";
	
	submitted = false;

	//disable all fields but the first
	document.getElementById("selectNS").disabled = false;
	document.getElementById("componentSpacers").disabled = true;
	document.getElementById("componentPrimers").disabled = true;
	document.getElementById("createNewComponent").disabled = true;

	//disable all proceeding buttons
	document.getElementById("spacersFinish").disabled = true;
	document.getElementById("primersFinish").disabled = true;

	//format stuff
	formatNSname();
	formatNSsequence();

	//scroll
	if(scrollToNS){
		scrollToId("selectNS");
	}

	return false;
}

var featureCount = 0;

function formatFeature(selection, id){
	var value = selection.value;

	var str = "";

	//location
	switch(value){
		case "origin":
			var locID = "locationOrigin" + id.toString();
			str += "<div class = 'location'><label for = '" + locID + "'>Location</label>";
			str += "<input type = 'number' min = '1' id = '" + locID + "' name = '" + locID + "' class = 'featureField' size = '5'>";
			str += "<input type = 'button' value = 'Highlight' class = 'highlightButton' onclick = \"highlight('" + locID + "','" + locID + "')\"></div>";

			break;
		default:
			var locIDstart = "locationStart" + id.toString();
			var locIDend = "locationEnd" + id.toString();
			str += "<div class = 'location'><span>Location: </span><label for = '" + locIDstart + "'>from</label>";
			str += "<input type = 'number' min = '1' id = '" + locIDstart + "' name = '" + locIDstart + "' class = 'featureField' size = '5'>";
			str += "<label for = '" + locIDend + "'>to</label>";
			str += "<input type = 'number' min = '1' id = '" + locIDend + "' name = '" + locIDend + "' class = 'featureField' size = '5'>";
			str += "<input type = 'button' value = 'Highlight' class = 'highlightButton' onclick = \"highlight('" + locIDstart + "','" + locIDend + "')\"></div>";

			break;
	}

	//other things
	switch(value){
		case "origin":
			var dirID = "direction" + id.toString();
			str += "<div class = 'direction'><label for = '" + dirID + "'>Direction</label>";
			str += "<select class = 'featureField direction' id = '" + dirID + "' name = '" + dirID + "'><option value = 'none'>None</option><option value = 'left'>Left</option><option value = 'right'>Right</option><option value = 'both'>Both</option></select>";
			str += "</div>";

			break;
		case "CDS":
			var geneID = "geneName" + id.toString();
			str += "<div class = 'name'><label for = '" + geneID + "'>Gene name</label>";
			str += "<input type = 'text' name = '" + geneID + "' id = '" + geneID + "' maxlength = '64'></div>";

			break;
		case "misc":
			var miscID = "miscNote" + id.toString();
			str += "<div class = 'note'><label for = '" + miscID + "'>Note</label>";
			str += "<input type = 'text' name = '" + miscID + "' id = '" + miscID + "' maxlength = '1024'></div>";

			break;
		case "source":
			var organismID = "organism" + id.toString();
			str += "<div class = 'organism'><label for = '" + organismID + "'>Organism</label>";
			str += "<input type = 'text' name = '" + organismID + "' id = '" + organismID + "' maxlength = '64'></div>";

			var molID = "molType" + id.toString();
			str += "<div class = 'molType'><label for = '" + molID + "'>Molecule</label>";
			str += "<select class = 'featureField' id = '" + molID + "' name = '" + molID + "'><option value = 'genomicDNA'>Genomic DNA</option><option value = 'otherDNA'>Other DNA</option><option value = 'unassignedDNA'>Unassigned DNA</option>";
			str += "<option value = 'genomicRNA'>Genomic RNA</option><option value = 'mRNA'>mRNA</option><option value = 'tRNA'>tRNA</option><option value = 'rRNA'>rRNA</option><option value = 'otherRNA'>Other RNA</option><option value = 'transcribedRNA'>Transcribed RNA</option><option value = 'viralcRNA'>Viral cRNA</option><option value = 'unassignedRNA'>Unassigned RNA</option>";
			str += "</select></div>";

			break;
		default:

			break;
	}

	selection.parentNode.nextSibling.innerHTML = str;


	console.log(str);

	return false;
}

function addFeature(){
	if(featureCount >= 64){
		document.getElementById("backboneFeaturesError").innerText = "Cannot create more than 64 features.";
	}
	else{
		var newDiv = document.createElement("div");
		newDiv.classList.add("feature");
		newDiv.id = "feature" + featureCount.toString();
		var selectID = "featureType" + featureCount.toString();
		newDiv.innerHTML = "<div class = 'featureTypeDiv'><label for = '" + selectID + "'>Feature #" + featureCount.toString() + ": Type</label><select class = 'featureType featureField' id = '" + selectID + "'  name = '" + selectID + "' onchange = 'formatFeature(this," + featureCount.toString() + ")'><option value = 'none'>None</option><option value = 'origin'>Origin</option><option value = 'CDS'>Protein-coding</option><option value = 'source'>Source</option><option value = 'misc'>Miscellaneous</option></select></div><div class = 'featureAdditional'></div>";

		document.getElementById("backboneFeatures").appendChild(newDiv);

		document.getElementById("backboneFeaturesError").innerText = "";

		featureCount = featureCount + 1;
	}

	return false;
}

function removeFeature(){
	var backboneFeatures = document.getElementById("backboneFeatures");
	if(backboneFeatures.children.length > 0){
		backboneFeatures.removeChild(backboneFeatures.lastChild);
		featureCount = featureCount - 1;
	}
	else {
		document.getElementById("backboneFeaturesError").innerText = "No feature to remove.";
	}

	return false;
}

function allInput(element, array){
	if(element.nodeName == "SELECT" || element.nodeName == "INPUT"){
		if(element.type != "button"){
			array.push(element);
		}
	}
	else{
		for(child of element.children){
			allInput(child, array);
		}
	}

	return array;
}

function highlight(startID, endID){
	var start = parseInt(document.getElementById(startID).value);
	start -= 1;
	var end = parseInt(document.getElementById(endID).value);

	if(start <= end){
		const input = document.getElementById("backboneSeq");
		input.focus();
		input.setSelectionRange(start, end);
  	}

  	return false;
}

function previewFeatures(){
	var array = Array();

	var validInput = true;

	var features = document.getElementsByClassName("feature");

	var previewData = "{";

	for(i = 0; i < features.length; i++){

		var featureData = Array();
		allInput(features[i], featureData);
		console.log(featureData)

		previewData += "'" + i.toString() + "' : {";
		

		for(j = 0; j < featureData.length; j++){
			if(featureData[j].value == ""){
				validInput = false;
				break;
			}
			if(featureData[j].value != "none"){
				previewData += "'" + featureData[j].name + "': '" + featureData[j].value + "'";
			}

			if(j != featureData.length - 1){
				previewData += ", ";
			}
		} //end loop through each input

		previewData += "}";

		if(i != features.length - 1){
			previewData += ", ";
		}
	}//end loop through features

	previewData += "}";
	
	if(validInput){
		$.ajax({
			data : {previewData: previewData},
			type : 'POST',
			url : '/backbonePreview'
			})
		.done(function(data){
			document.getElementById("backboneOutput").innerHTML = data.output;

			//only can proceed if successfully created
			if(data.succeeded){
				document.getElementById("featuresInput").innerText = data.featureStr;
			}
			else{
			}
		});
		event.preventDefault();

	}
	else{
		document.getElementById("backboneFeaturesError").innerText = "Not all features have values.";
	}
}

function startOver(){
	clearEverything(true);

	return false;
}

//onload
function bodyOnload(){
	//clearEverything(false); //is this necessary?
	formatNSname();
	formatNSsequence();

	return false;
}