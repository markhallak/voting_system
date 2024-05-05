import json
import uuid

from django.shortcuts import render
from django.views.decorators.http import require_GET

from globals import sp


def displayMyElectionsPage(request):
    return render(request, "elections.html")


@require_GET
def createElection(request):
    data = json.loads(request.body.decode('utf-8'))
    candidates = data['Candidates']

    sp.table("Elections").insert({"id": uuid.uuid4(), "Name": data['Name'], "Description": data['Description'], "image_url": data["Image Url"], "category": data['Category'], "candidates": candidates, "host_username": request.session['signup_info']['username']})