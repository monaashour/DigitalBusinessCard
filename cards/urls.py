from django.urls import path

import cards.views as card_views


urlpatterns = [
    path('cards/<str:username>', card_views.display_view, name='display-card')
]