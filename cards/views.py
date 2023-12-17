from django.shortcuts import render
from django.http import HttpResponse


def display_view(request, username):

    # username: str
    # first_name: str
    # last_name: str
    # job_title: [str]
    # email: str
    # linkedin: str
    context = {
        'username': 'mona.ashour',
        'first_name': 'Mona',
        'last_name': 'Ashour',
        'job_title': [
            'Head of International Automation',
            'Orange Business'
        ],
        'email': 'mona.ashour@orange.com',
        'linkedin': 'https://www.linkedin.com/monaashour',
    }
    return render(request, 'cards/card.html', context=context)


def download_vcard(request, username):
    return HttpResponse(f'download_vcard({username})')


def download_qrcode(request, username):
    return HttpResponse(f'download_qrcode({username})')