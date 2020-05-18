function bodyOnload(){
	return false;
}

function login(){
	var loginData = "{'email': '" + document.getElementById("emailLogin").value + "'}";

	//send request
	$.ajax({
		data : {"loginData": loginData},
		type : 'POST',
		url : '/loginProcess'
		})
	.done(function(data){
		document.getElementById("loginOutput").innerHTML = data.output;
		if(data.succeeded){
			document.getElementById("returnURL").innerHTML = "<a href = '/" + returnURL + "'>Go to " + returnURL + " page.</a>";
		}
	});
	event.preventDefault();

	return false;
}

function register(){
	var registrationData = "{'email': '" + document.getElementById("emailRegister").value + "'}";

	//send request
	$.ajax({
		data : {"registrationData": registrationData},
		type : 'POST',
		url : '/registerProcess'
		})
	.done(function(data){
		document.getElementById("loginOutput").innerHTML = data.output;
	});
	event.preventDefault();

	return false;
}

