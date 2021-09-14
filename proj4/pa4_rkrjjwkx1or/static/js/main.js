console.log("Hello, EECS485");
whatIsJavascript = 0;

function getRootUrl() {
	return window.location.origin?window.location.origin+'/':window.location.protocol+'/'+window.location.host+'/';
}

var url_prefix_no_first_slash = 'b966cc054de14c43b479/pa3';
var url_prefix = '/' + url_prefix_no_first_slash;

function getFullRootURL() {
	return getRootUrl() + url_prefix_no_first_slash;
}

function createNewUser() {
	console.log("clicked create new user");
	var username_input = $("#new_username_input").val();
	var firstname_input = $("#new_firstname_input").val();
	var lastname_input = $("#new_lastname_input").val();
	var password1_input = $("#new_password1_input").val();
	var password2_input = $("#new_password2_input").val();
	var email_input = $("#new_email_input").val();
	console.log('email input is');
	console.log(email_input);
	var user_JSON = {
		"username": username_input,
		"firstname": firstname_input,
		"lastname": lastname_input,
		"password1": password1_input,
		"password2": password2_input,
		"email": email_input
	};
	if (whatIsJavascript == 0) {
		$.ajax( {
			url: url_prefix + '/api/v1/user',
			data: JSON.stringify(user_JSON),
			dataType: "json",
			contentType: "application/json",
			mimeType: "application/json",
			type: 'POST', 
			success: function(data) {
				//redirect happens here
				console.log('about to redirect to ' + url_prefix + "/login");
				window.location = url_prefix + "/login";
			},
			error: function(data) {
				console.log('failed to create new user from main.js')
				$(".errors").empty();
				var responseObj = JSON.parse(data.responseText);
				console.log(responseObj.errors[0].message);
				for (var i = 0; i < responseObj.errors.length; ++i) {
					$(".errors").append("<p class=\"error\">" + responseObj.errors[i].message + "</p>");
				}
				
			}
		});
	} else {
		console.log('doubt it');
		console.log(whatIsJavascript);
	}
}

function editUser() {
	console.log('Trying to edit User');
	var username_input = currentUser;
	var firstname_input = $("#update_firstname_input").val();
	var lastname_input = $("#update_lastname_input").val();
	var password1_input = $("#update_password1_input").val();
	var password2_input = $("#update_password2_input").val();
	var email_input = $("#update_email_input").val();

	if (whatIsJavascript == 0) {
		var user_JSON = {
			"username": username_input,
			"firstname": firstname_input,
			"lastname": lastname_input,
			"password1": password1_input,
			"password2": password2_input,
			"email": email_input
		};

		console.log(user_JSON);

		$.ajax( {
			url: url_prefix + '/api/v1/user',
			data: JSON.stringify(user_JSON),
			dataType: "json",
			contentType: "application/json",
			mimeType: "application/json",
			type: 'PUT',
			success: function() {
				console.log('Successfully putted into editUser');
				//clear password fields
				document.getElementById('update_password1_input').value = "";
				document.getElementById('update_password2_input').value = "";
				//document.getElementById("name title").innerHTML = "Logged in as: BUTTT";// + firstname + " " + lastname;
				//window.location = 
			}, error: function(data) {
				console.log('Failed to put into editUser');
				$(".errors").empty();
				var responseObj = JSON.parse(data.responseText);
				console.log(responseObj.errors[0].message);
				for (var i = 0; i < responseObj.errors.length; ++i) {
					$(".errors").append("<p class=\"error\">" + responseObj.errors[i].message + "</p>");
				}
			}
		});
	} else {
		console.log('I dont think so Tim');
		console.log(whatIsJavascript);
	}
}

// This function is attached to the login button on /login
function login() {
	console.log("User is logging in. Sending login data...");
	var button = $("#login_submit");
	var username = $("#login_username_input").val();
	var password = $("#login_password_input").val();
	console.log("  Username: " + username);
	console.log("  Password: " + password);
	var login_JSON = {
		'username': username,
		'password': password
	};
	console.log(JSON.stringify(login_JSON));
	$.ajax({
		url: url_prefix + '/api/v1/login',
		data: JSON.stringify(login_JSON),
		dataType: "json",
		contentType: "application/json",
		mimeType: "application/json",
		type: 'POST',
		success: function(data) {
			console.log("Successfully logged in user.");
			console.log("  Received data: " + JSON.stringify(data));
			console.log("  Received username: " + data.username);

			console.log("  Looking for breadcrumb in URL...");
			// Get query parameters (if any)
			var query_string = window.location.href.slice(window.location.href.indexOf('login') + 'login'.length);
			if (query_string.length > 0) {
				console.log("  Found breadcrumb. Starting redirection process.");
				var startingIndex = query_string.indexOf('url=/') + 'url=/'.length;
				var breadcrumb_url;
				var rest_of_query_string = "";
				if (query_string.indexOf('&') == -1) {
					breadcrumb_url = query_string.slice(startingIndex);
				}
				else {
					breadcrumb_url = query_string.slice(startingIndex, query_string.indexOf('&'));
					rest_of_query_string = '?' + query_string.slice(query_string.indexOf('&') + 1);
				}
				console.log("  breadcrumb_url: " + breadcrumb_url);
				console.log("  rest_of_query_string: " + rest_of_query_string);
				var full_backtracked_url = getRootUrl() + breadcrumb_url + rest_of_query_string;
				window.location.replace(getRootUrl() + breadcrumb_url + rest_of_query_string);
				console.log("  Redirecting to " + full_backtracked_url);
			}
			else {
				console.log("  Could not find breadcrumb. Redirecting to index.");
				window.location.replace(getFullRootURL());
			}
		},
		error: function(data) {
			// This is returned when the user actually hits "login" and things are wrong
			$(".errors").empty();
			console.log("Error in response from /api/v1/login");
			console.log(data);
			var responseObj = JSON.parse(data.responseText);
			console.log(responseObj.errors[0].message);
			for (var i = 0; i < responseObj.errors.length; ++i) {
				$(".errors").append("<p class=\"error\">" + responseObj.errors[i].message + "</p>");
			}
		}
	});
}

function logout() {
	console.log("User clicked logout");
	$.ajax( {
		url: url_prefix + '/api/v1/logout',
		type: 'POST', 
		success: function() {
			console.log('Sent logout requests');
			window.location.replace(getFullRootURL());
		},
		error: function() {
			console.log('ERROR could not send logout request');
		}
	});
}

$(function() {
	$('#new_submit').click(createNewUser);
	$('#update_submit').click(editUser);
	$('#nav_logout').click(logout);
	$('#login_submit').click(login);
});