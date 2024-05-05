import base64
import json
import logging
import os
import uuid

import keyring
import msgpack
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST, require_GET
from postgrest.types import CountMethod
from user_agents import parse
from Crypto.Hash import SHA3_512

from globals import sp
from manage import addEmailToQueue
from util.DilithiumAPI import DilithiumAPI
from util.kyber.ccakem import kem_decaps1024
from util.kyberAPI import KyberAPI
from util.qr_code_generator import QRCodeGenerator


@require_POST
def checkUsername(request):
    data, count = sp.table("User").select('username', count=CountMethod.exact).eq('username',
                                                                                  json.loads(request.body)[
                                                                                      'username']).execute()
    if count and count[1] == 0:
        return JsonResponse({'isAvailable': True})
    else:
        return JsonResponse({'isAvailable': False})


@require_POST
def checkEmail(request):
    data, count = sp.table("User").select('email', count=CountMethod.exact).eq('email',
                                                                               json.loads(request.body)[
                                                                                   'email']).execute()
    if count and count[1] == 0:
        return JsonResponse({'isAvailable': True})
    else:
        return JsonResponse({'isAvailable': False})


def deleteTempPic(path):
    if os.path.exists(path):
        os.remove(path)


def generate_random_filename(extension):
    return str(uuid.uuid4()) + extension


def get_client_ips(request):
    ip_list = []
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip_list.extend([ip.strip() for ip in x_forwarded_for.split(',')])

    remote_addr = request.META.get('REMOTE_ADDR')

    if remote_addr:
        ip_list.append(remote_addr)

    return ','.join(ip_list)


def getDeviceInfo(request):
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_string)

    device_info = {
        "is_mobile": user_agent.is_mobile,
        "is_tablet": user_agent.is_tablet,
        "is_pc": user_agent.is_pc,
        "is_bot": user_agent.is_bot,
        "browser": {
            "family": user_agent.browser.family,
            "version": user_agent.browser.version_string,
        },
        "os": {
            "family": user_agent.os.family,
            "version": user_agent.os.version_string,
        },
        "device": {
            "family": user_agent.device.family,
        }
    }

    return device_info


def signup_attempt(request):
    if 'step_completed' in request.session:
        completed_step = request.session['step_completed']

        if completed_step != 4 or completed_step != 5:
            return HttpResponseForbidden()

    accountInfo = request.session['signup_info']
    filepath = accountInfo['image_path']
    filename = os.path.basename(filepath)
    file_extension = os.path.splitext(filename)[1]
    filename = generate_random_filename(file_extension)
    deviceInfo = getDeviceInfo(request)

    try:
        with open(filepath, 'rb') as f:
            content_type = "image/jpeg" if file_extension in ['.jpg', '.jpeg'] else "image/png"
            sp.storage.from_("images").upload(file=f, path=filename,
                                              file_options={"content-type": content_type, 'cache-control': '3600'})
            picURL = sp.storage.from_("images").get_public_url(filename)

            sp.table('User').insert({'username': accountInfo['username'], 'email': accountInfo['email'],
                                     'phone_number': accountInfo['phone'], 'address': accountInfo['address'],
                                     'profile_image_url': picURL, 'user_type': accountInfo['account-type']}).execute()

            sp.table('Device Info').insert({'username': accountInfo['username'], 'is_mobile': deviceInfo['is_mobile'],
                                            'is_tablet': deviceInfo['is_tablet'], 'is_pc': deviceInfo['is_pc'],
                                            'is_bot': deviceInfo['is_bot'],
                                            'browser_family': deviceInfo['browser']['family'],
                                            'browser_version': deviceInfo['browser']['version'],
                                            'os_family': deviceInfo['os']['family'],
                                            'os_version': deviceInfo['os']['version'],
                                            'device_family': deviceInfo['device']['family']}).execute()

            if accountInfo['account-type'] == 'Individual':
                sp.table('Individual').insert(
                    {'username': accountInfo['username'], 'first_name': accountInfo['first-name'],
                     'last_name': accountInfo['last-name'], 'date_of_birth': accountInfo['date-of-birth']}).execute()
            else:
                sp.table('Dealership').insert(
                    {'username': accountInfo['username'], 'name': accountInfo['name'],
                     'ein': accountInfo['ein']}).execute()

        del request.session['signup_info']
        request.session['step_completed'] = 0
        request.session.modified = True
        deleteTempPic(filepath)
        return redirect('confirm')

    except Exception as E:
        logging.error(str(E))

    return JsonResponse({'success': False})


def signup(request):
    return redirect("signup_step", 1)


def toBase64(data):
    try:
        if isinstance(data, bytes):
            return base64.b64encode(data).decode('utf-8')
        elif isinstance(data, list):
            if all(isinstance(x, int) for x in data):
                bytes_array = bytes([x % 256 for x in data])
                return base64.b64encode(bytes_array).decode('utf-8')
            else:
                raise ValueError("List must contain only integers")
        elif isinstance(data, str):  # Handling string data by converting to bytes
            bytes_data = data.encode('utf-8')
            return base64.b64encode(bytes_data).decode('utf-8')
        else:
            raise ValueError(f"Data must be bytes, list of byte values, or string, got {type(data)} with value {data}")
    except Exception as e:
        print(f"Error processing data for base64 encoding: {e}")
        raise


def fromBase64(data):
    padding_needed = len(data) % 4
    if padding_needed != 0:
        data += '=' * (4 - padding_needed)
    return base64.b64decode(data)


def getUnpackedData():
    with open('data.msgpack', 'rb') as file:
        read_data = file.read()

    if len(read_data) != 0:
        unpacked_data = msgpack.unpackb(read_data, raw=False)
        return unpacked_data
    else:
        return {}

def bytes_to_int_list(byte_data):
    return [b for b in byte_data]

def signup_step(request, step):
    if request.method == "POST":
        if step == 1:
            if 'signup_info' not in request.session:
                request.session['signup_info'] = {}
                request.session.modified = True
                request.session.save()

            if "signup_info" in request.session:
                myFile = request.FILES.get('profile-picture')
                fs = FileSystemStorage(location='temp/')
                filename = fs.save(myFile.name, myFile)

                username = request.POST['username']
                request.session['signup_info']['username'] = username

                email = request.POST["email"]
                request.session['signup_info']['email'] = email

                kyberPrivateKey, kyberPublicKey = KyberAPI().generateKeyPair()
                plainSharedSecret, encapsulatedSharedSecret = KyberAPI().encapsulateSecret(kyberPublicKey)
                dilithiumPrivateKey, dilithiumPublicKey = DilithiumAPI().getPairKey()

                try:
                    unpackedData = getUnpackedData()

                    unpackedData[f"server-{username}-kyberPublicKey"] = toBase64(kyberPublicKey)
                    unpackedData[f"server-{username}-kyberPrivateKey"] = toBase64(kyberPrivateKey)
                    unpackedData[f"server-{username}-dilithiumPublicKey"] = dilithiumPublicKey
                    unpackedData[f"server-{username}-dilithiumPrivateKey"] = dilithiumPrivateKey
                    unpackedData[f"server-{username}-encapsulatedSharedSecret"] = toBase64(encapsulatedSharedSecret)

                    packed_data = msgpack.packb(unpackedData, use_bin_type=True)

                    with open('data.msgpack', 'wb') as file:
                        file.write(packed_data)

                    sp.table("Users").insert({"id": str(uuid.uuid4()), "username": username, "email": email,
                                              "profile_picture_url": fs.path(filename)}).execute()
                except Exception as e:
                    print("ERROR: " + str(e))

                kyber_hasher = SHA3_512.new()
                kyber_hasher.update(
                    toBase64(kyberPublicKey).encode())
                kyberPublicKeyHash = kyber_hasher.hexdigest()

                dilithium_hasher = SHA3_512.new()
                dilithium_hasher.update(
                    dilithiumPublicKey.encode())
                dilithiumPublicKeyHash = dilithium_hasher.hexdigest()

                addEmailToQueue({"kyberPublicKeyHash": kyberPublicKeyHash,
                                 "dilithiumPublicKeyHash": dilithiumPublicKeyHash, "receiverEmail": email,
                                 "username": username
                                 })

                return redirect("signup_step", 2)
            else:
                return HttpResponse("Couldn't find the data sent")
        elif step == 2:
            username = request.session["signup_info"]["username"]
            kyberPublicKeyHashInput = request.POST["kyber-public-key-signature"]
            dilithiumPublicKeyHashInput = request.POST["dilithium-public-key-signature"]

            unpackedData = getUnpackedData()

            kyberPublicKey = unpackedData[f"server-{username}-kyberPublicKey"]
            dilithiumPublicKey = unpackedData[f"server-{username}-dilithiumPublicKey"]

            kyber_hasher = SHA3_512.new()
            kyber_hasher.update(
                kyberPublicKey.encode())
            kyberPublicKeyHash = kyber_hasher.hexdigest()

            dilithium_hasher = SHA3_512.new()
            dilithium_hasher.update(
                dilithiumPublicKey.encode())
            dilithiumPublicKeyHash = dilithium_hasher.hexdigest()

            if dilithiumPublicKeyHash == dilithiumPublicKeyHashInput and kyberPublicKeyHash == kyberPublicKeyHashInput:
                return redirect("signup_step", 3)
            else:
                return JsonResponse({'areHashesValid': False})
        elif step == 3:
            username = request.session["signup_info"]["username"]
            formData = json.loads(request.body.decode('utf-8'))

            data, count = sp.table("Users").select("totp_secret").eq("username", username).execute()
            encryptedTotpSecret = data[1][0]["totp_secret"]
            unpackedData = getUnpackedData()

            kyberPrivateKey = bytes_to_int_list(fromBase64(unpackedData[f"server-{username}-kyberPrivateKey"]))
            encapsulatedSharedSecret = bytes_to_int_list(
                fromBase64(unpackedData[f"server-{username}-encapsulatedSharedSecret"]))

            plainSharedSecret = kem_decaps1024(kyberPrivateKey, encapsulatedSharedSecret)
            decryptedTotpSecret = KyberAPI().decrypt_data(plainSharedSecret, encryptedTotpSecret)

            encryptedTotpCode = formData['totp']
            decryptedTotpCode = KyberAPI().decryptDataJS(plainSharedSecret, base64.b64decode(encryptedTotpCode))

            is_valid = QRCodeGenerator.verifyCode(decryptedTotpSecret, decryptedTotpCode)
            return JsonResponse({'isTotpCorrect': is_valid})
    else:
        if step > 1:
            username = request.session.get('signup_info', {}).get('username')
            unpackedData = getUnpackedData()

            print(unpackedData[f"server-{username}-kyberPublicKey"])
            print(f"\n{unpackedData[f'server-{username}-dilithiumPublicKey']}")
            context = {
                'step': step,
                'kyberPublicKey': unpackedData[f"server-{username}-kyberPublicKey"],
                'dilithiumPublicKey': unpackedData[f"server-{username}-dilithiumPublicKey"]
            }
        else:
            context = {'step': step}

        return render(request, "signup.html", context)


@require_GET
def generate_qr_code(request):
    username = request.session["signup_info"]["username"]
    secret = QRCodeGenerator.generate_totp_secret()

    unpackedData = getUnpackedData()
    kyberPrivateKey = list(fromBase64(unpackedData[f"server-{username}-kyberPrivateKey"]))
    encapsulatedSharedSecret = list(fromBase64(unpackedData[f"server-{username}-encapsulatedSharedSecret"]))
    plainSharedSecret = kem_decaps1024(kyberPrivateKey, encapsulatedSharedSecret)

    # Ensure plainSharedSecret is bytes before encrypting
    plainSharedSecret = bytes([(x % 256) for x in plainSharedSecret])
    encryptedTotpSecret = KyberAPI().encrypt_data(plainSharedSecret, bytes(secret.encode('utf-8')))

    sp.table("Users").update({"totp_secret": toBase64(encryptedTotpSecret)}).eq("username",
                                                                                request.session.get('signup_info',
                                                                                                    {}).get(
                                                                                    'username')).execute()
    return HttpResponse(QRCodeGenerator.generate_qr_code("Safivote", secret), content_type='image/png')
