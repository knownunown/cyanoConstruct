function bodyOnload(){
	return false;
}

function redirect(url){
	var numSecs = document.getElementById("numSecs");
	setTimeout(function() {numSecs.textContent = 4}, 1000);
	setTimeout(function() {numSecs.textContent = 3}, 2000);
	setTimeout(function() {numSecs.textContent = 2}, 3000);
	setTimeout(function() {numSecs.textContent = 1}, 4000);
	setTimeout(function() {window.location.replace(url)}, 5000);
}

function login(){
	var loginData = "{'email': '" + document.getElementById("emailLogin").value + "', 'remember': '" + document.getElementById("loginRememberMe").checked.toString() + "'}";

	//send request
	$.ajax({
		data : {"loginData": loginData},
		type : 'POST',
		url : '/loginProcess'
		})
	.done(function(data){
		document.getElementById("loginOutput").innerHTML = data.output;
		if(data.succeeded){
			document.getElementById("returnURL").innerHTML = "<a href = '" + returnURL + "'>Go to " + returnURL.substr(1) + " page.</a> You will be redirected in <span id = 'numSecs'>5</span> seconds.";
			redirect(returnURL);
		}
	});
	event.preventDefault();

	return false;
}

function register(){
	var registrationData = "{'email': '" + document.getElementById("emailRegister").value + "', 'remember': '" + document.getElementById("registerRememberMe").checked.toString() + "'}";
	//send request
	$.ajax({
		data : {"registrationData": registrationData},
		type : 'POST',
		url : '/registerProcess'
		})
	.done(function(data){
		document.getElementById("loginOutput").innerHTML = data.output;
		if(data.succeeded){
			document.getElementById("returnURL").innerHTML = "<a href = '" + returnURL + "'>Go to " + returnURL.substr(1) + " page.</a> You will be redirected in <span id = 'numSecs'>5</span> seconds.";
			redirect(returnURL);
		}
	});
	event.preventDefault();

	return false;
}

function onSignIn(googleUser) {
	var profile = googleUser.getBasicProfile();

	var IDtoken = googleUser.getAuthResponse().id_token;

	var loginData = "{'fullName': \"\"\"" + profile.getName() + "\"\"\", 'email': \"\"\"" + profile.getEmail() + 
					"\"\"\", 'remember': '" + document.getElementById("googleRememberMe").checked.toString() + "', 'IDtoken': \"\"\"" + IDtoken + "\"\"\"}";

	alert(loginData);

	$.ajax({
		data : {loginData: loginData},
		type : 'POST',
		url : '/loginGoogle'
		})
	.done(function(data){
		document.getElementById("loginOutput").innerHTML = data.output;
		if(data.succeeded){
			document.getElementById("returnURL").innerHTML = "<a href = '" + returnURL + "'>Go to " + returnURL.substr(1) + " page.</a> You will be redirected in <span id = 'numSecs'>5</span> seconds.";
			redirect(returnURL);
		}
		else{
			googleSignOut();
		}
	});
	event.preventDefault();
}
