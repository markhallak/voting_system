document.addEventListener('DOMContentLoaded', function() {
    const usernameInput = document.getElementById('username-input');
    const imagePreview = document.getElementById('image-preview');
    const csrfTokenElement = document.querySelector('.csrfToken');

    if (imagePreview) {
        const imageUpload = document.getElementById('image-upload');
        const overlay = document.querySelector('#image-preview .overlay');
        const defaultImageHtml = `<svg class="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20"><path d="M10 0a10 10 0 1 0 10 10A10.011 10.011 0 0 0 10 0Zm0 5a3 3 0 1 1 0 6 3 3 0 0 1 0-6Zm0 13a8.949 8.949 0 0 1-4.951-1.488A3.987 3.987 0 0 1 9 13h2a3.987 3.987 0 0 1 3.951 3.512A8.949 8.949 0 0 1 10 18Z"/></svg>`;

        imagePreview.innerHTML = defaultImageHtml;
        imagePreview.title = "Add a picture";

        imageUpload.addEventListener('change', function(event) {
            if (event.target.files && event.target.files[0]) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.innerHTML = `<img src="${e.target.result}" class="object-cover w-full h-full">` + overlay.outerHTML;
                    imagePreview.title = "Change Picture";
                    overlay.classList.add('hidden');

                };
                reader.readAsDataURL(event.target.files[0]);
            }
        });

        document.body.addEventListener('click', function(event) {
            if (event.target.id === "svg-overlay") {
                imagePreview.innerHTML = defaultImageHtml;
                imageUpload.value = '';
                imagePreview.title = "Add a picture";
                overlay.classList.add('hidden');
            }

        });

        imagePreview.addEventListener('mouseenter', function() {
            if (imagePreview.querySelector('img')) {
                overlay.classList.remove('hidden');
            }
        });

        imagePreview.addEventListener('mouseleave', function() {
            overlay.classList.add('hidden');
        });

        imagePreview.addEventListener('click', function() {
            if (!imagePreview.querySelector('img')) {
                overlay.classList.add('hidden');
                imageUpload.click();
            }
        });
    }

    if (usernameInput) {
        const emailInput = document.getElementById('email-input');
        const continueButton1 = document.getElementById('continue-step-1');

        function updateContinueButtonStep4() {
            if (areAllFieldsFilled() && areAllFieldsValid()) {
                enableButton(continueButton4);
            } else {
                disableButton(continueButton4);
            }
        }

        function areAllFieldsFilled() {
            return usernameInput.value.trim() !== '' &&
                emailInput.value.trim() !== '' &&
                phoneInput.value.trim() !== '' &&
                addressInput.value.trim() !== '';
        }

        function areAllFieldsValid() {
            return isValidUsername(usernameInput.value) && isValidEmail(emailInput.value) && isValidPhone(phoneInput.value) && isValidAddressFormat(addressInput.value);
        }

        // Track the last value checked for each input to avoid redundant API calls
        let lastChecked = {
            username: '',
            email: '',
            phone: ''
        };

        usernameInput.addEventListener('input', function() {
            if (usernameInput.value.trim() === '' || validateInput(usernameInput, isValidUsername)) {
                hideFeedback(usernameInput);
            }
            updateContinueButtonStep4();
        });

        usernameInput.addEventListener('blur', function() {
            if (usernameInput.value.trim() !== '' &&
                validateInput(usernameInput, isValidUsername) &&
                lastChecked.username !== usernameInput.value.trim()) {

                lastChecked.username = usernameInput.value.trim();
                throttledCheckFieldAvailability('/checkUsername', {
                    'username': usernameInput.value
                }, usernameInput);
            }
        });

        emailInput.addEventListener('input', function() {
            if (emailInput.value.trim() === '' || validateInput(emailInput, isValidEmail)) {
                hideFeedback(emailInput);
            }
            updateContinueButtonStep4();
        });

        emailInput.addEventListener('blur', function() {
            if (emailInput.value.trim() !== '' &&
                validateInput(emailInput, isValidEmail) &&
                lastChecked.email !== emailInput.value.trim()) {

                lastChecked.email = emailInput.value.trim();
                throttledCheckFieldAvailability('/checkEmail', {
                    'email': emailInput.value
                }, emailInput);
            }
        });

        phoneInput.addEventListener('input', function() {
            if (phoneInput.value.trim() === '' || validateInput(phoneInput, isValidPhone)) {
                hideFeedback(phoneInput);
            }
            updateContinueButtonStep4();
        });

        phoneInput.addEventListener('blur', function() {
            if (phoneInput.value.trim() !== '' &&
                validateInput(phoneInput, isValidPhone) &&
                lastChecked.phone !== phoneInput.value.trim()) {

                lastChecked.phone = phoneInput.value.trim();
                throttledCheckFieldAvailability('/checkPhone', {
                    'phone': phoneInput.value
                }, phoneInput);
            }
        });

        addressInput.addEventListener('input', function() {
            if (addressInput.value.trim() === '' || validateInput(addressInput, isValidAddressFormat)) {
                hideFeedback(addressInput);
            }
            updateContinueButtonStep4();
        });

        function isValidUsername(username) {
            return /^[^\s\d][^\s]*$/.test(username);
        }




        function isValidEmail(email) {
            const regexPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
            return regexPattern.test(email);
        }

        function isValidPhone(phone) {
            const phoneRegex = /^\+\d{1,3} \d+$/; // Country code (1-3 digits) followed by space and rest of the number
            return phoneRegex.test(phone);
        }

        function isValidAddressFormat(address) {
            // This regex checks:
            // - Street name can start and end with numbers or letters
            // - City name must start and end with letters
            // - State is a two-letter code
            // - Zip code is exactly 5 digits
const addressRegex = /^[A-Za-z0-9]+(?:\s[A-Za-z0-9]+)*\s?,\s?[A-Za-z]+(?:\s[A-Za-z]+)*\s?,\s?[A-Z]{2}\s?,\s?\d{5}$/;
            return addressRegex.test(address);
        }
    }

    function validateInput(inputElement, validationFunction) {
            const isValid = validationFunction(inputElement.value);
            if (!isValid) {
                displayFeedback(inputElement, "Invalid format");
            }
            return isValid;
        }

    // Helper function to throttle function calls
    function throttle(callback, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                callback.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // Wrap the API call function in a throttled version
    const throttledCheckFieldAvailability = throttle(checkFieldAvailability, 2000);

    function checkFieldAvailability(url, data, inputElement) {

        fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfTokenElement.value
                },
                body: JSON.stringify(data),
            })
            .then(response => response.json())
            .then(data => {
                if (!data.isAvailable) {
                    displayFeedback(inputElement, `${inputElement.getAttribute('name')} is already being used`);
                } else {
                    hideFeedback(inputElement);
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    }


    function displayFeedback(inputElement, message) {
        let feedbackElement = document.getElementById(`${inputElement.id}-feedback`);
        let feedbackContainer = document.getElementById(`${inputElement.id}Feedback`);

        if(feedbackElement){
        feedbackElement.style.display = 'block';
        feedbackElement.textContent = message;
        }

        if(feedbackContainer){
        feedbackContainer.style.display = 'block';
        }
        inputElement.classList.add('border-red-500', 'error');
    }

    function hideFeedback(inputElement) {
            let feedbackElement = document.getElementById(`${inputElement.id}-feedback`);

            if(feedbackElement){
        feedbackElement.style.display = 'none';
        }

        let feedbackContainer = document.getElementById(`${inputElement.id}Feedback`);
        if(feedbackContainer){
        feedbackContainer.style.display = 'none';
        }
        inputElement.classList.remove('border-red-500', 'error');
    }

    function enableButton(button) {
        button.disabled = false;
        button.classList.remove('opacity-50', 'cursor-not-allowed');
    }

    function disableButton(button) {
        button.disabled = true;
        button.classList.add('opacity-50', 'cursor-not-allowed');
    }

});