function onSignIn(googleUser) {
	var profile = googleUser.getBasicProfile();

	var IDtoken = googleUser.getAuthResponse().id_token;
	
	$.ajax({
		data : {"IDtoken": IDtoken,
				"fullName": profile.getName(),
				"email": profile.getEmail()},
		type : 'POST',
		url : '/googleConnect'
		})
	.done(function(data){
		document.getElementById("connectOutput").innerHTML = data.output;
	});
	event.preventDefault();
}


function googleConnect(){
	return false;
}

function bodyOnload(){}