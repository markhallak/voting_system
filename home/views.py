from django.shortcuts import render


def displayHomePage(request):
    return render(request, "index.html")
