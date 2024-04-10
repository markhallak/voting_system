from django.shortcuts import render


def displayLoginPage(request):
    return render(request, "login.html")
