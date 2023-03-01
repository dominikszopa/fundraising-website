
function checkPasswordsMatch(password1, password2) {
/**
 * Compares two password DOM objects and sets the second one
 * invalid if they are not matching
 *
 * @param password1 The primary password to match
 * @param password2 The second password that should be equal to password1
 */

    var password1val = password1.val();
    var password2val = password2.val();


    if(password1val == password2val) {
        password2.removeClass("is-invalid");
        password2.addClass("is-valid");
        return true;
    } else {
        password2.addClass("is-invalid");
        password2.append("<div>don't match</div>");
        return false;
    }

}

function checkUsername(username) {
/**
 * Checks if a username is valid
 * It can be an email, but cannot have spaces
 */

    var usernameval = username.val();
    var usernameRegex = /^[a-zA-Z0-9_@.]{1,30}$/;

    if(usernameRegex.test(usernameval)) {
        username.removeClass("is-invalid");
        username.addClass("is-valid");
        return true;
    } else {
        username.addClass("is-invalid");
        username.append("<div>Username must be between 3 and 15 characters and contain only letters, numbers, and underscores</div>");
        return false;
    }
}

function checkSignupForm() {
/**
 * Checks the signup form for errors
 */

    var username = $("#id_username");
    var password1 = $("#id_password1");
    var password2 = $("#id_password2");

    var usernameValid = checkUsername(username);
    var passwordsMatch = checkPasswordsMatch(password1, password2);

    if(usernameValid && passwordsMatch) {
        console.log("valid form")
        return true;
    } else {
        console.log("invalid form")
        return false;
    }
}