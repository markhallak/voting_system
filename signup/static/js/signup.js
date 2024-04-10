document.addEventListener('DOMContentLoaded', function() {
    const usernameInput = document.getElementById('username-input');
    const kyberPublicKeyInput = document.getElementById('kyber-public-key-input');
    const csrfTokenElement = document.querySelector('.csrfToken');

    if (usernameInput) {
        const imageUpload = document.getElementById('image-upload');
        const overlay = document.querySelector('#image-preview .overlay');
        const defaultImageHtml = `<svg class="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20"><path d="M10 0a10 10 0 1 0 10 10A10.011 10.011 0 0 0 10 0Zm0 5a3 3 0 1 1 0 6 3 3 0 0 1 0-6Zm0 13a8.949 8.949 0 0 1-4.951-1.488A3.987 3.987 0 0 1 9 13h2a3.987 3.987 0 0 1 3.951 3.512A8.949 8.949 0 0 1 10 18Z"/></svg>`;
        const imagePreview = document.getElementById('image-preview');
        const emailInput = document.getElementById('email-input');
        const continueButton1 = document.getElementById('continue-step-1');

        function updateContinueButtonStep1() {
            if (areStep1FieldsFilled() && areStep1FieldsValid()) {
                enableButton(continueButton1);
            } else {
                disableButton(continueButton1);
            }
        }

        function areStep1FieldsFilled() {
            return usernameInput.value.trim() !== '' &&
                emailInput.value.trim() !== '' && imageUpload.files.length != 0;
        }

        function areStep1FieldsValid() {
            return isValidUsername(usernameInput.value) && isValidEmail(emailInput.value);
        }

        usernameInput.addEventListener('input', function() {
            if (usernameInput.value.trim() === '' || validateInput(usernameInput, isValidUsername)) {
                hideFeedback(usernameInput);
            }
            updateContinueButtonStep1();
        });

        emailInput.addEventListener('input', function() {
            if (emailInput.value.trim() === '' || validateInput(emailInput, isValidEmail)) {
                hideFeedback(emailInput);
            }
            updateContinueButtonStep1();
        });

        function isValidUsername(username) {
            return /^[A-Za-z][^\s]*$/.test(username);
        }

        function isValidEmail(email) {
            const regexPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
            return regexPattern.test(email);
        }


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

            updateContinueButtonStep1();
        });

        document.body.addEventListener('click', function(event) {
            if (event.target.id === "svg-overlay") {
                imagePreview.innerHTML = defaultImageHtml;
                imageUpload.value = '';
                imagePreview.title = "Add a picture";
                overlay.classList.add('hidden');
                updateContinueButtonStep1();
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
    } else if (kyberPublicKeyInput) {
        const kyberPublicKeySignatureInput = document.getElementById('kyber-public-key-signature-input');
        const dilithiumPublicKeyInput = document.getElementById('dilithium-public-key-input');
        const dilithiumPublicKeySignatureInput = document.getElementById('dilithium-public-key-signature-input');
        const continueButton2 = document.getElementById('continue-step-2');

        function areStep2FieldsFilled() {
            return kyberPublicKeyInput.value.trim() !== '' &&
                kyberPublicKeySignatureInput.value.trim() !== '' &&
                dilithiumPublicKeyInput.value.trim() !== '' &&
                dilithiumPublicKeySignatureInput.value.trim() !== '';
        }

        function areStep2FieldsValid() {
            return kyberPublicKeyInput.value.length >= 8 &&
                kyberPublicKeySignatureInput.value.length >= 8 &&
                dilithiumPublicKeyInput.value.length >= 8 &&
                dilithiumPublicKeySignatureInput.value.length >= 8;
        }

        [kyberPublicKeyInput, kyberPublicKeySignatureInput, dilithiumPublicKeyInput, dilithiumPublicKeySignatureInput].forEach(input => {
            input.addEventListener('input', function() {
                updateContinueButtonStep2();
            });
        });

        function updateContinueButtonStep2() {
            if (areStep2FieldsFilled() && areStep2FieldsValid()) {
                enableButton(continueButton2);
            } else {
                disableButton(continueButton2);
            }
        }

    }




    function validateInput(inputElement, validationFunction) {
        const isValid = validationFunction(inputElement.value);
        if (!isValid) {
            displayFeedback(inputElement, "Invalid format");
        }
        return isValid;
    }

    function displayFeedback(inputElement, message) {
        let feedbackElement = document.getElementById(`${inputElement.id}-feedback`);
        let feedbackContainer = document.getElementById(`${inputElement.id}Feedback`);

        if (feedbackElement) {
            feedbackElement.style.display = 'block';
            feedbackElement.textContent = message;
        }

        if (feedbackContainer) {
            feedbackContainer.style.display = 'block';
        }
        inputElement.classList.add('border-red-500', 'error');
    }

    function hideFeedback(inputElement) {
        let feedbackElement = document.getElementById(`${inputElement.id}-feedback`);

        if (feedbackElement) {
            feedbackElement.style.display = 'none';
        }

        let feedbackContainer = document.getElementById(`${inputElement.id}Feedback`);
        if (feedbackContainer) {
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