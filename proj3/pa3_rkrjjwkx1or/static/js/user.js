//<script type="text/javascript">
  var icharGood = false;
  var badUsername = false;
  function isOnlyLetterDigitUnderscore(donald_trump) {
    lower = donald_trump.toLowerCase();
    blob = "abcdefghijklmnopqrstuvwxyz1234567890_";
    icharGood = false;
    badUsername = false;
    for (var i = 0; len = lower.length, i < len; i++) {
      // console.log("i is ");
      // console.log(i);
      for (var j = 0; j < 37; j++) {
        if (lower[i] == blob[j]) {
          icharGood = true;
          /*console.log("found a match, i is");
          console.log(i);
          console.log("j is ");
          console.log(j);*/
        }
      }
      //console.log("icharGood is "+icharGood);
      if (!icharGood) {
        // console.log("bad char in username");
        badUsername = true;
      }
      icharGood = false;
    }
    //alert(badUsername);
    // console.log("badUsername is ");
    // console.log(badUsername);
    return !badUsername;
  }

  function containsBothLetterAndNumber(donald_trump) {
    lower = donald_trump.toLowerCase();
    letterBlob = "abcdefghijklmnopqrstuvwxyz";
    numberBlob = "0123456789";
    var gotLetter = false;
    var gotNumber = false;
    for (var i = 0; i < lower.length; i++) {
      for (var j = 0; j < 26; j++) {
        if (lower[i] == letterBlob[j]) {
          gotLetter = true;
        }
      }
      for (var j = 0; j < 10; j++) {
        if (lower[i] == numberBlob[j]) {
          gotNumber = true;
        }
      }
    }
    return (gotLetter && gotNumber);
  }

  function validEmail(donald_trump) {
    // console.log('we inside validEmail');
    // console.log('donald_trump is ');
    // console.log(donald_trump);
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    // console.log(re.test(donald_trump));
    return re.test(donald_trump);
  }

  function validateFields(firstname, lastname, password1, password2, email, edit) {
    // console.log('inside validateFields, email is ');
    // console.log(email);
    // console.log(firstname)
    if (edit) {
      // alreadyHave8CharWarning = false;
      if (password1.length > 0) {
        if (password1.length < 8) {
          $(".errors").append("<p class=\"error\">Passwords must be at least 8 characters long</p>");
          whatIsJavascript = whatIsJavascript + 1;
          // alreadyHave8CharWarning = false;
        }
        if (!containsBothLetterAndNumber(password1)) {
          $(".errors").append("<p class=\"error\">Passwords must contain at least one letter and one number</p>");
          whatIsJavascript = whatIsJavascript + 1;
        }
        if (!isOnlyLetterDigitUnderscore(password1)) {
          $(".errors").append("<p class=\"error\">Passwords may only contain letters, digits, and underscores</p>");
          whatIsJavascript = whatIsJavascript + 1;
        }         
      }
    } else {
      if (password1.length < 8 || password2.length < 8) {
        $(".errors").append("<p class=\"error\">Passwords must be at least 8 characters long</p>");
        whatIsJavascript = whatIsJavascript + 1;
      }
      if (!containsBothLetterAndNumber(password1) || !containsBothLetterAndNumber(password2)) {
        $(".errors").append("<p class=\"error\">Passwords must contain at least one letter and one number</p>");
        whatIsJavascript = whatIsJavascript + 1;
      }
      if (!isOnlyLetterDigitUnderscore(password1) || !isOnlyLetterDigitUnderscore(password2)) {
        $(".errors").append("<p class=\"error\">Passwords may only contain letters, digits, and underscores</p>");
        whatIsJavascript = whatIsJavascript + 1;
      } 
    }
    if (password1 != password2) {
      $(".errors").append("<p class=\"error\">Passwords do not match</p>");
      whatIsJavascript = whatIsJavascript + 1;
    }
    // console.log('about to call validEmail');
    // console.log('email is ');
    // console.log(email);
    if (!validEmail(email)) {
      $(".errors").append("<p class=\"error\">Email address must be valid</p>");
      whatIsJavascript = whatIsJavascript + 1;
    }
    if (firstname.length > 20) {
      $(".errors").append("<p class=\"error\">Firstname must be no longer than 20 characters</p>");
      whatIsJavascript = whatIsJavascript + 1;
    }
    if (lastname.length > 20) {
      $(".errors").append("<p class=\"error\">Lastname must be no longer than 20 characters</p>");
      whatIsJavascript = whatIsJavascript + 1;
    }
    if (email.length > 40) {
      $(".errors").append("<p class=\"error\">Email must be no longer than 40 characters</p>");
      whatIsJavascript = whatIsJavascript + 1;
    }
  }

  function validateForm()
  {
    console.log('we in validateForm, and whatIsJavascript is ');
    console.log(whatIsJavascript);
    whatIsJavascript = 0;
    $(".errors").empty();
    var a=document.forms["Create Form"]["username"].value;
    var b=document.forms["Create Form"]["firstname"].value;
    var c=document.forms["Create Form"]["lastname"].value;
    var d=document.forms["Create Form"]["password1"].value;
    var e=document.forms["Create Form"]["password2"].value;
    var f=document.forms["Create Form"]["email"].value;
    if (a.length < 3) {
      $(".errors").append("<p class=\"error\">Usernames must be at least 3 characters long</p>");
      whatIsJavascript = whatIsJavascript + 1;
    }
    if (!isOnlyLetterDigitUnderscore(a)) {
      $(".errors").append("<p class=\"error\">Usernames may only contain letters, digits, and underscores</p>");
      whatIsJavascript = whatIsJavascript + 1;
    }
    if (a.length > 20) {
      $(".errors").append("<p class=\"error\">Username must be no longer than 20 characters</p>");
      whatIsJavascript = whatIsJavascript + 1;      
    }
    validateFields(b, c, d, e, f, false);
  }

  function validateEditForm() {
    console.log('we in validateEditForm, and whatIsJavascript was ');
    console.log(whatIsJavascript);
    whatIsJavascript = 0;

    $(".errors").empty();
    var b=document.forms["Edit Form"]["firstname"].value;
    var c=document.forms["Edit Form"]["lastname"].value;
    var d=document.forms["Edit Form"]["password1"].value;
    var e=document.forms["Edit Form"]["password2"].value;
    var f=document.forms["Edit Form"]["email"].value;
    // console.log('about to call validateFields');
    // console.log(b);
    // console.log('omg');
    // console.log(e);
    // console.log(f);
    validateFields(b, c, d, e, f, true)
  }
  currentUser = "none";
  //console.log(window.location.href);
  if (window.location.href.substr(window.location.href.length - 4) == "edit") {
    //make get request to api/user/v1, use that info to pre-load the fields
    $.ajax( {
      url: url_prefix + '/api/v1/user',
      contentType: "application/json",
      mimeType: "application/json",
      type: 'GET',
      success: function(data) {
        currentUser = data.username;
        document.getElementById('update_firstname_input').value = data.firstname;
        document.getElementById('update_lastname_input').value = data.lastname;
        document.getElementById('update_email_input').value = data.email;
        validateEditForm();
      }, 
      error: function(data) {
        console.log('how do you computer');
      }
    })
  } else {
    validateForm();
  }

//</script>