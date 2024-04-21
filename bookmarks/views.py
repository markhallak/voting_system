from django.shortcuts import render


def displayBookmarksPage(request):
    return render(request, "bookmarks.html")
