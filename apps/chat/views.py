
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, render, redirect
from django_socketio import broadcast, broadcast_channel, NoSocket
from django.views.decorators.cache import *
from chat.models import ChatRoom
from schools.models import *

@never_cache
def multiroom(request, template="multiroomchat.html"):
    """
    Homepage - lists all rooms.
    """
    data = {}
    return render(request, template, data)
