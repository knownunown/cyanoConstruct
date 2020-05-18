var submitted = false;

//smooth scrolling
function scrollToId(id){
	document.getElementById(id).scrollIntoView({block: "start", inline: "start", behavior: "smooth"})
}

//named sequence
function formatNSname(){
	var currentType = document.getElementById("NStype").value;

	var retString = "<option value ='new'>Create new</option>";

	for(ns of namedSequencesNames[currentType]){
		retString += "<option value = '" + ns + "'>" + ns + "</option>";
	}

	document.getElementById("NSname").innerHTML = retString;

	formatNSsequence();

	return false;
}

function formatNSsequence(){
	var currentName = document.getElementById("NSname").value;

	if(currentName == "new"){ //making new sequence
		//adjust ability to name new sequence
		document.getElementById("newNSname").style.visibility = "visible";
		document.getElementById("newNSnameInput").disabled = false;

		//adjust sequence textarea
		document.getElementById("NSseq").value = "";
		document.getElementById("NSseq").readOnly = false;

		//adjust buttons
		document.getElementById("newNSsubmitDiv").style.visibility = "visible";
		document.getElementById("newNSsubmit").disabled = false;

		document.getElementById("NSfinish").disabled = true;
	}
	else{ //using already existing sequence
		//adjust ability to name new sequence
		document.getElementById("newNSname").style.visibility = "hidden";
		document.getElementById("newNSnameInput").disabled = true;

		//adjust sequence textarea
		document.getElementById("NSseq").value = namedSequencesSeqs[currentName];
		document.getElementById("NSseq").readOnly = true;

		//adjust buttons
		document.getElementById("newNSsubmitDiv").style.visibility = "hidden";
		document.getElementById("newNSsubmit").disabled = true;

		document.getElementById("NSfinish").disabled = false;
	}

	//clear sequence error message
	document.getElementById("sequenceError").textContent = "";

	return false;
}

function validateNS(){
	var canProceed = true;

	if(document.getElementById("NSname").value == "new"){
		//name
		if(document.getElementById("newNSnameInput").value == ""){
			canProceed = false;
			document.getElementById("nameError").textContent = "Need a name."; //also it should be less then X characters
		}
		else{
			document.getElementById("nameError").textContent = "";
		}

		//sequence
		if(document.getElementById("NSseq").value == ""){
			canProceed = false;
			document.getElementById("sequenceError").textContent = "Need a sequence."; //need to be changed if you use default
		}
		else{
			document.getElementById("sequenceError").textContent = "";
		}
	}

	return canProceed;
}

function newNS(){
	if(!validateNS()){
		return false; //not very useful return value
	}

	//remove line breaks from sequence (what about spaces?)
	document.getElementById("NSseq").value = document.getElementById("NSseq").value.replace(/\s/g,"");

	//create the NamedSequence

	//get Data
	var newNSData = "{'NStype': '" + document.getElementById("NStype").value +
					"', 'NSname': '" + document.getElementById("newNSnameInput").value + 
					"', 'NSseq': '" + document.getElementById("NSseq").value + "'}";

	//send request
	$.ajax({
		data : {"newNSData": newNSData},
		type : 'POST',
		url : '/newNamedSeq'
		})
	.done(function(data){
		document.getElementById("NSoutput").innerHTML = data.output;

		//only can proceed if successfully created
		if(data.succeeded){
			document.getElementById("NSfinish").disabled = false;
		}
		else{
			document.getElementById("NSfinish").disabled = true;			
		}
	});
	event.preventDefault();

	return false;
}

function finishNSSection(){
	//send the NS data (is a "confirm" button always necessary? I think not)

	if(document.getElementById("NSname").value == "new"){
		var namedSeqData = "{'NStype': '" + document.getElementById("NStype").value + 
							"', 'NSname': '" + document.getElementById("newNSnameInput").value +
							"', 'NSseq': '" + document.getElementById("NSseq").value + "'}";
	}
	else{
		var namedSeqData = "{'NStype': '" + document.getElementById("NStype").value +
							"', 'NSname': '" + document.getElementById("NSname").value +
							"', 'NSseq': '" + document.getElementById("NSseq").value + "'}";
	}

	//request
	$.ajax({
		data : {"namedSeqData": namedSeqData},
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
	if(submitted){
		document.getElementById("downloadMessage").textContent = "Preparing files...";
		window.location.href = "/domesticationZIPs.zip";
		event.preventDefault();
		document.getElementById("downloadMessage").textContent = "Downloaded.";
	}
	else{
		document.getElementById("downloadMessage").textContent = "No component to download.";
	}

	return false;
}

function clearEverything(scrollToNS){
	//reset values
	document.getElementById("domesticationForm").reset();
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
	document.getElementById("NSfinish").disabled = true;
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
	clearEverything(false);

	return false;
}