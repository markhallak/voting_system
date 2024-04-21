from django.shortcuts import render

def displayMyElectionsPage(request):
    return render(request, "elections.html")
