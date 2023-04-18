
let form = [...document.getElementsByTagName("form")][0]

form.onsubmit = function() {

    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;

    $.ajax({
        url: '{{ url_for(`/account/register`) }}',
        type: 'POST',
        data: {
            email: email,
            password: password
        },
        success: function (response) {
            console.log(response);
        },
        error: function (response) {
            console.log(response);
        }
    })
};