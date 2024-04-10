function showToast() {
var emailInput = document.getElementById('email-input');
var csrfTokenElement = document.getElementsByClassName('csrfToken')[0];

let data = {
'email': emailInput.value};

    fetch('/signin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                     'X-CSRFToken': csrfTokenElement.value
                },
                body: JSON.stringify(data),
            })
            .then(data => {
                console.log('Success:', data);
            })
            .catch((error) => {
                console.error('Error:', error);
            });

    	var toast = document.getElementById('toast-top-right');
    	toast.classList.remove('hidden', 'fade-out');
    	toast.classList.add('fade-in');

    	setTimeout(function() {
    		toast.classList.remove('fade-in');
    		toast.classList.add('fade-out');
    		setTimeout(function() {
    			toast.classList.add('hidden');
    		}, 400); // Match with fade-out animation duration
    	}, 5000); // Toast will stay visible for 3 seconds
}

document.addEventListener('DOMContentLoaded', function() {
	var signinBtn = document.getElementById('signin-btn');

	signinBtn.addEventListener('click', function() {
		showToast();
	});
});