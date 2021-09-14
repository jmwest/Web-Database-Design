// function validateForm()
// {
//   $(".errors").empty();
//   var username = document.forms["login_form"]["username"].value;
//   var password = document.forms["login_form"]["password"].value;

//   var login_JSON = {
//     "username": username,
//     "password": password
//   };
//   console.log(login_JSON);
//   $.ajax({
//     url: url_prefix + '/api/v1/login',
//     data: login_JSON,
//     contentType: "application/json; charset=utf-8",
//     type: 'POST',
//     success: function(response) {
//       // On success, do nothing
//     },
//     error: function(response) {
//       // This is called whenever a user types something in and it's wrong
//       var responseObj = JSON.parse(response.responseText);
//       console.log(responseObj.errors[0].message);
//       for (var i = 0; i < responseObj.errors.length; ++i) {
//         $(".errors").append("<p class=\"error\">" + responseObj.errors[i].message + "</p>");
//       }
//     }
//   });
// }
// validateForm();