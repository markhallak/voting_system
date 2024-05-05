import * as jssha from 'https://cdn.jsdelivr.net/npm/jssha@3.3.1/+esm'
import { Kyber1024 } from "https://cdn.jsdelivr.net/npm/crystals-kyber-js@1.1.1/+esm";

document.addEventListener('DOMContentLoaded', function() {
    const usernameInput = document.getElementById('username-input');
    const kyberPublicKeySignatureInput = document.getElementById('kyber-public-key-signature-input');
    const totpInput = document.getElementById('totp-input');
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
    } else if (kyberPublicKeySignatureInput) {
        const dilithiumPublicKeySignatureInput = document.getElementById('dilithium-public-key-signature-input');
        const continueButton2 = document.getElementById('continue-step-2');

        continueButton2.addEventListener('click', function(event) {
            const form = document.querySelector("form");
            event.preventDefault();

            if (checkHashes()) {
                form.submit();
            } else {
                console.log("Hash check failed.");
            }
        });

        function checkHashes() {
    try {
        var kyberPublicKey = document.querySelector('meta[name="kyberPublicKey"]').getAttribute('content');
        var dilithiumPublicKey = document.querySelector('meta[name="dilithiumPublicKey"]').getAttribute('content');
        console.log(kyberPublicKey)
        console.log(dilithiumPublicKey)

        const kyberHasher = new jsSHA("SHA3-512", "TEXT");
        kyberHasher.update(kyberPublicKey);
        const kyberPublicKeyHash = kyberHasher.getHash("HEX");

        const dilithiumHasher = new jsSHA("SHA3-512", "TEXT", { encoding: "UTF8" });
        dilithiumHasher.update(dilithiumPublicKey);
        const dilithiumPublicKeyHash = dilithiumHasher.getHash("HEX");

        console.log(`Kyber Hash: ${kyberPublicKeyHash}, Expected: ${kyberPublicKeySignatureInput.value}`);
        console.log(`Dilithium Hash: ${dilithiumPublicKeyHash}, Expected: ${dilithiumPublicKeySignatureInput.value}`);

        const kyberMatches = kyberPublicKeyHash.toLowerCase() === kyberPublicKeySignatureInput.value.toLowerCase();
        const dilithiumMatches = dilithiumPublicKeyHash.toLowerCase() === dilithiumPublicKeySignatureInput.value.toLowerCase();

        console.log(`Kyber Matches: ${kyberMatches}, Dilithium Matches: ${dilithiumMatches}`);

        return kyberMatches && dilithiumMatches;
    } catch (error) {
        console.error("Error in hash comparison: ", error);
        return false;
    }
}


        function areStep2FieldsFilled() {
            return kyberPublicKeySignatureInput.value.trim() !== '' &&
                dilithiumPublicKeySignatureInput.value.trim() !== '';
        }

        function areStep2FieldsValid() {
            return kyberPublicKeySignatureInput.value.length >= 8 &&
                dilithiumPublicKeySignatureInput.value.length >= 8;
        }

        [kyberPublicKeySignatureInput, dilithiumPublicKeySignatureInput].forEach(input => {
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

    } else if (totpInput) {
        var kyberPublicKey = document.querySelector('meta[name="kyberPublicKey"]').getAttribute('content');

async function encryptData(plainText, passphrase) {
    const encoder = new TextEncoder();
    const data = encoder.encode(plainText);
    const salt = crypto.getRandomValues(new Uint8Array(16));
    const keyMaterial = await crypto.subtle.importKey(
        'raw',
        encoder.encode(passphrase),
        { name: 'PBKDF2' },
        false,
        ['deriveKey']
    );
    const key = await crypto.subtle.deriveKey(
        { name: 'PBKDF2', salt: salt, iterations: 100000, hash: 'SHA-256' },
        keyMaterial,
        { name: 'AES-CBC', length: 256 },
        false,
        ['encrypt']
    );
    const iv = crypto.getRandomValues(new Uint8Array(16));
    const encrypted = await crypto.subtle.encrypt(
        { name: 'AES-CBC', iv },
        key,
        data
    );
    const combined = new Uint8Array(salt.length + iv.length + encrypted.byteLength);
    combined.set(salt, 0);
    combined.set(iv, salt.length);
    combined.set(new Uint8Array(encrypted), salt.length + iv.length);
    return window.btoa(String.fromCharCode(...combined));
}



        async function encrypt(plainText, sharedSecret) {
            const encryptedResult = await encryptData(plainText, sharedSecret);
            return encryptedResult;
        }

        const qrCodeImage = document.getElementById("qr-code");
        const continueButton3 = document.getElementById("continue-step-3");

        totpInput.addEventListener('input', function() {
            updateContinueButtonStep3();
        });

        const form = document.querySelector("form");

        form.addEventListener('submit', async function(event) {
            event.preventDefault();

            const keyBytes = Uint8Array.from(atob(kyberPublicKey), c => c.charCodeAt(0));
            let encryptedTotp;
            let tempEncapsulatedSharedSecret;

const kyber = new Kyber1024();
kyber.encap(keyBytes).then(([encapsulatedSharedSecret, plainSharedSecret]) => {
    encryptedTotp = encrypt(totpInput.value, plainSharedSecret);
    tempEncapsulatedSharedSecret = encapsulatedSharedSecret;
    console.log(encapsulatedSharedSecret, plainSharedSecret);
}).catch(error => {
    console.error('Error during key encapsulation:', error);
});

            fetch('/signup/3/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfTokenElement.value
                    },
                    body: JSON.stringify({
                        'totp': encryptedTotp,
                        "encapsulatedSharedSecret": tempEncapsulatedSharedSecret
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.isTotpCorrect) {
                        window.location.href = "/";
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        });

        fetchQRCode();

        function fetchQRCode() {
            fetch('/generate-qr-code')
                .then(function(response) {
                    return response.blob();
                })
                .then(function(blob) {
                    const qrUrl = URL.createObjectURL(blob);
                    qrCodeImage.src = qrUrl;
                })
                .catch(function(error) {
                    console.error('Error fetching QR code:', error);
                });
        }

        function updateContinueButtonStep3() {
            if (isValidTOTP(totpInput.value)) {
                enableButton(continueButton3);
            } else {
                disableButton(continueButton3);
            }
        }

        function isValidTOTP(totp) {
            return /^[0-9]{6}$/.test(totp);
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