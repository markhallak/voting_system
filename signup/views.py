import json
import logging
import os
import uuid

from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST, require_GET
from postgrest.types import CountMethod
from user_agents import parse

from util.qr_code_generator import QRCodeGenerator
from supabase_client import sp


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


@require_POST
def checkPhone(request):
    data, count = sp.table("User").select('phone_number', count=CountMethod.exact).eq('phone_number',
                                                                                      json.loads(request.body)[
                                                                                          'phone']).execute()
    if count and count[1] == 0:
        return JsonResponse({'isAvailable': True})
    else:
        return JsonResponse({'isAvailable': False})


def confirm(request):
    return render(request, template_name="confirmation.html")


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

    # Add the direct IP address
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


def signuup(request, step):
    context = {'step': step}

    if 'signup_info' not in request.session:
        request.session['signup_info'] = {}
        request.session['step_completed'] = 0

    if request.method == "POST":

        if step == 1 and 'account-type' in request.POST:
            accountType = request.POST['account-type']
            request.session['signup_info']['account-type'] = accountType
            request.session['step_completed'] = 1
            request.session.modified = True
            return redirect("signup_step", step=2)
        elif step == 2 and 'username' in request.POST and 'email' in request.POST and 'phone' in request.POST and 'address' in request.POST:
            request.session['signup_info']['username'] = request.POST['username']
            request.session['signup_info']['email'] = request.POST['email']
            request.session['signup_info']['phone'] = request.POST['phone']
            request.session['signup_info']['address'] = request.POST['address']
            request.session['step_completed'] = 2
            request.session.modified = True
            return redirect('signup_step', step=3)

        elif step == 3 and 'profile-picture' in request.FILES:
            myFile = request.FILES['profile-picture']
            fs = FileSystemStorage(location='temp/')
            filename = fs.save(myFile.name, myFile)
            request.session['signup_info']['image_path'] = fs.path(filename)
            request.session['step_completed'] = 3
            request.session.modified = True

            if request.session['signup_info']['account-type'] == "Individual":
                return redirect('signup_step', step=4)
            else:
                return redirect('signup_step', step=5)

        elif step == 4 and all(k in request.POST for k in ['first name', 'last name', 'date-of-birth']):

            request.session['signup_info']['first-name'] = request.POST['first name']
            request.session['signup_info']['last-name'] = request.POST['last name']
            request.session['signup_info']['date-of-birth'] = request.POST['date-of-birth']
            request.session['step_completed'] = 4
            request.session.modified = True
            return redirect("signup")
        elif step == 5 and 'name' in request.POST and 'ein' in request.POST:
            request.session['signup_info']['name'] = request.POST['name']
            request.session['signup_info']['ein'] = request.POST['ein']
            request.session['step_completed'] = 5
            request.session.modified = True
            return redirect("signup")

    else:
        if step < 1:
            return redirect("signup_step", step=1)

        if step > 5:
            if request.session['signup_info']['account-type'] == "Dealership":
                return redirect("signup_step", step=5)
            else:
                return redirect("signup_step", step=4)

        if ((step != 5 and step > request.session['step_completed'] + 1) or (
                step == 5 and request.session['step_completed'] != 3)) and request.session['step_completed'] != 5:
            return redirect("signup_step", step=request.session['step_completed'] + 1)

    return render(request, 'signup.html', context)


def signup(request):
    return redirect("signup_step", 1)


def signup_step(request, step):
    context = {'step': step}

    if request.method == "POST":
        if step == 1:
            myFile = request.FILES['profile-picture']
            fs = FileSystemStorage(location='temp/')
            filename = fs.save(myFile.name, myFile)
            request.session['signup_info']['image_path'] = fs.path(filename)

            request.session['signup_info']['username'] = request.POST['username']
            request.session['signup_info']['email'] = request.POST['email']
            sp.table()

            return redirect("signup_step", 2)
        elif step == 2:
            return redirect("signup_step", 3)
        elif step == 3:
            if QRCodeGenerator.verifyCode(request.session['secret'], request.session['code']):
                return redirect("home")
            else:
                return JsonResponse({'isOtpCorrect': False})
    else:
        return render(request, "signup.html", context)


@require_GET
def generate_qr_code(request):
    return HttpResponse(QRCodeGenerator.generate_qr_code(), content_type='image/png')


@require_POST
def verify_code(request):
    return HttpResponse(QRCodeGenerator.verifyCode(secret, code))
