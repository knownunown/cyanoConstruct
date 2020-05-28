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

	if(document.getElementById("componentPos").value == ""){ //needs to be within range
		canProceed = false;
		document.getElementById("posError").textContent = "Need a position.";
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
	var spacersData = "{'componentPos': '" + document.getElementById("componentPos").value + 
						"', 'isTerminal': '" + document.getElementById("componentTerminal").checked + "'}";

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
		url : '/finishDomestication'
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
	var canProceed = true;

	if(document.getElementById("backboneName").value == ""){
		canProceed = false;
		document.getElementById("backboneNameError").textContent = "Need a name 1-20 characters long.";
	}
	else{
		document.getElementById("backboneNameError").textContent = "";
	}

	//sequence
	if(document.getElementById("backboneSeq").value == ""){
		canProceed = false;
		document.getElementById("backboneSeqError").textContent = "Need a sequence.";
	}
	else{
		document.getElementById("backboneSeqError").textContent = "";
	}

	return canProceed;
}

function newBackbone(){
	if(!validateBackbone()){
		return false;
	}

	document.getElementById("backboneSeq").value = document.getElementById("backboneSeq").value.replace(/\s/g,"");

	var newBackboneData = "{'backboneName' : '" + document.getElementById("backboneName").value +
						  "', 'backboneSeq' : '" + document.getElementById("backboneSeq").value + "'}";

	$.ajax({
		data : {"newBackboneData": newBackboneData},
		type : 'POST',
		url : '/newBackbone'
		})
	.done(function(data){
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