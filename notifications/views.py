from django.shortcuts import render


def displayNotificationsPage(request):
    return render(request, "notifications.html")
