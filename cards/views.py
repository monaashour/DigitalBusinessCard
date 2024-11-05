import json
import os

import vobject
import dotenv
import base64
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

dotenv.load_dotenv()


def display_view(request, username):
    user = get_object_or_404(User, username=username)

    break_titles = []
    for i in json.loads(user.card.job_title):
        for j in i.split('\n'):
            break_titles.append(j)

    context = {
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'job_title': break_titles,
        'linkedin': user.card.linkedin,
    }
    print(context)

    return render(request, 'cards/card.html', context=context)


# def download_vcard(request, username):
#     user = get_object_or_404(User, username=username)
#     vcard = generate_vcard(user)
#     response = HttpResponse(vcard)
#     response['Content-Type'] = 'text/x-vcard'
#     response['Content-Disposition'] = f'attachement;filename={user.first_name} {user.last_name}.vcf'
#     return response


# def download_qrcode(request, username):
#     user = get_object_or_404(User, username=username)
#     qr_image = base64.b64decode(user.card.qr_b64)
#     response = HttpResponse(qr_image)
#     response['Content-Type'] = 'image/jpg'
#     response['Content-Disposition'] = f'attachement;filename={user.first_name} {user.last_name}.jpg'
#     return response


# def download_apple_pass(request, username):
#     return HttpResponse(f'download_apple_pass({username})')


# def download_google_pass(request, username):
#     return HttpResponse(f'download_google_pass({username})')
