function checkPasswordsMatch(password1Input, password2Input) {
/**
 * Compares two password DOM objects and sets the second one
 * invalid if they are not matching
 *
 * @param password1Input The primary password to match
 * @param password2Input The second password that should be equal to password1
 */

    var password1val = password1Input.value;
    var password2val = password2Input.value;

    // Remove existing error message if present
    var nextSibling = password2Input.nextElementSibling;
    if (nextSibling && nextSibling.classList.contains("invalid-feedback")) {
        nextSibling.remove();
    }

    if(password1val === password2val) {
        password2Input.classList.remove("is-invalid");
        password2Input.classList.add("is-valid");
        return true;
    } else {
        password2Input.classList.add("is-invalid");
        // Create error message element
        var errorDiv = document.createElement("div");
        errorDiv.classList.add("invalid-feedback");
        errorDiv.style.display = "block";
        errorDiv.innerText = "Passwords don't match";
        password2Input.parentNode.insertBefore(errorDiv, password2Input.nextSibling);
        return false;
    }
}

function checkUsername(usernameInput) {
/**
 * Checks if a username is valid
 * It can be an email, but cannot have spaces
 */

    var usernameval = usernameInput.value;
    var usernameRegex = /^[a-zA-Z0-9_@.]{1,30}$/;

    // Remove existing error message if present
    var nextSibling = usernameInput.nextElementSibling;
    if (nextSibling && nextSibling.classList.contains("invalid-feedback")) {
        nextSibling.remove();
    }

    if(usernameRegex.test(usernameval)) {
        usernameInput.classList.remove("is-invalid");
        usernameInput.classList.add("is-valid");
        return true;
    } else {
        usernameInput.classList.add("is-invalid");
        var errorDiv = document.createElement("div");
        errorDiv.classList.add("invalid-feedback");
        errorDiv.style.display = "block";
        errorDiv.innerText = "Username must be between 3 and 15 characters and contain only letters, numbers, and underscores";
        usernameInput.parentNode.insertBefore(errorDiv, usernameInput.nextSibling);
        return false;
    }
}

function checkSignupForm() {
/**
 * Checks the signup form for errors
 */

    var username = document.getElementById("id_username");
    var password1 = document.getElementById("id_password1");
    var password2 = document.getElementById("id_password2");

    var usernameValid = checkUsername(username);
    var passwordsMatch = checkPasswordsMatch(password1, password2);

    if(usernameValid && passwordsMatch) {
         console.log("valid form");
         return true;
    } else {
         console.log("invalid form");
         return false;
    }
}
