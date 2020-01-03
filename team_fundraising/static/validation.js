
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
    } else {
        password2.addClass("is-invalid");
        password2.append("<div>don't match</div>");
    }

}

