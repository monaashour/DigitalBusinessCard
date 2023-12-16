from django.shortcuts import render
from django.http import HttpResponse


def display_view(request, username):
    # return HttpResponse(f'hello {username}')
    return render(request, 'cards/card.html', {'name': username})