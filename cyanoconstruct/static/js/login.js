const { startRegistration, startAuthentication, base64URLStringToBuffer, bufferToBase64URLString } = SimpleWebAuthnBrowser;

function bodyOnload(){
	return false;
}

window.addEventListener("load", () => {
	document.querySelector("#registrationForm").addEventListener("submit", register);
	document.querySelector("#loginForm").addEventListener("submit", login);

	console.log("registered");
});

function redirect(url){
	var numSecs = document.getElementById("numSecs");
	setTimeout(function() {numSecs.textContent = 4}, 1000);
	setTimeout(function() {numSecs.textContent = 3}, 2000);
	setTimeout(function() {numSecs.textContent = 2}, 3000);
	setTimeout(function() {numSecs.textContent = 1}, 4000);
	setTimeout(function() {window.location.replace(url)}, 5000);
}

async function login(event) {
	event.preventDefault();

	let email = document.getElementById("emailLogin").value;

	let response = await loginWebAuthN(email);
	if(response && response.verified) {
		window.location.replace(returnURL);
	}

	return false;
}

async function registerWebAuthN(email) {
	let statusElem = document.getElementById("loginOutput");

	const resp = await fetch('/auth/register/start', {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({"initial": true, email})
	});
	const opts = await resp.json();
	opts.user.id = base64URLStringToBuffer(opts.user.id);
	
    let attResp;
    try {
      // Pass the options to the authenticator and wait for a response
      attResp = await startRegistration(opts);
    } catch (error) {
      // Some basic error handling
      if (error.name === 'InvalidStateError') {
        statusElem.innerText = 'Error: Authenticator was probably already registered by user';
      } else {
        statusElem.innerText = error;
      }

      throw error;
    }

    // POST the response to the endpoint that calls
    // @simplewebauthn/server -> verifyRegistrationResponse()
    const verificationResp = await fetch('/auth/register/verify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(attResp),
    });

    // Wait for the results of verification
    const verificationJSON = await verificationResp.json();

    // Show UI appropriate for the `verified` status
    if (verificationJSON && verificationJSON.verified) {
      statusElem.innerHTML = 'Success!';
    } else {
      statusElem.innerHTML = `Oh no, something went wrong! Response: <pre>${JSON.stringify(
        verificationJSON,
      )}</pre>`;
    }
}

async function loginWebAuthN(email) {
	let statusElem = document.getElementById("loginOutput");

    // GET authentication options from the endpoint that calls
    // @simplewebauthn/server -> generateAuthenticationOptions()
    const resp = await fetch('/auth/login/start');

    let asseResp;
    try {
      // Pass the options to the authenticator and wait for a response
      asseResp = await startAuthentication(await resp.json());
    } catch (error) {
      // Some basic error handling
      statusElem.innerText = error;
      throw error;
    }

	// XX(tnytown): This field is broken in the library. Reset it to empty, it doesn't seem to be necessary.
	asseResp.response.userHandle = "";

    // POST the response to the endpoint that calls
    // @simplewebauthn/server -> verifyAuthenticationResponse()
    const verificationResp = await fetch('/auth/login/verify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(asseResp),
    });

	console.log("verify");
    // Wait for the results of verification
    return await verificationResp.json();
}

async function register(e) {
	e.preventDefault();

	let email = document.getElementById("emailRegister").value;

	//send request
	$.ajax({
		data : {email,
				"remember": document.getElementById("registerRememberMe").checked},
		type : 'POST',
		url : '/registerProcess'
		})
	.done(async (data) => {
		await registerWebAuthN(email);

		document.getElementById("loginOutput").innerHTML = data.output;
		if(data.succeeded){
			document.getElementById("returnURL").innerHTML = "<a href = '" + returnURL + "'>Go to " + returnURL.substr(1) + " page.</a> You will be redirected in <span id = 'numSecs'>5</span> seconds.";
			redirect(returnURL);
		}
	});

	return false;
}

function onSignIn(googleUser) {
	var profile = googleUser.getBasicProfile();

	var IDtoken = googleUser.getAuthResponse().id_token;

	$.ajax({
		data : {"fullName": profile.getName(),
				"email": profile.getEmail(),
				"remember": document.getElementById("googleRememberMe").checked,
				"IDtoken": IDtoken},
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
