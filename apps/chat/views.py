
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, render, redirect
from django_socketio import broadcast, broadcast_channel, NoSocket
from django.views.decorators.cache import *
from chat.models import ChatRoom
from schools.models import *

@never_cache
def rooms(request, template="rooms.html"):
    """
    Homepage - lists all rooms.
    """
    context = {"rooms": ChatRoom.objects.all()}
    return render(request, template, context)

def candy(request):
    return render(request, "candy.html", {})

@never_cache
def room(request, school_id, class_id, template="room.html"):
    """
    Show a room.
    """
    existing_school = School.objects.get(id=school_id)
    print "(Looking up chat room) Got existing school for id %s named %s" % (school_id, existing_school)
    
    school_class = Classroom.objects.get(id=class_id)
    print "(Looking up chat room) Got existing class %s" % school_class
    
    chatroom_name = "%s: %s" % (existing_school.school_name, school_class.class_name)
    chatroom, created  = ChatRoom.objects.get_or_create(name=chatroom_name)
    print "(Looking up chat room) Created new chat room? %s" % created
    print "(Looking up chat room) Chat room found: %s" % chatroom
    
    context = { "school": existing_school, "school_class":  school_class, "room": chatroom }
    # context = {"room": get_object_or_404(ChatRoom, slug=slug)}
    return render(request, template, context)

@never_cache
def room_by_id(request, room_id, template="room.html"):
    
    chatroom  = ChatRoom.objects.get(id=room_id)
    print "(Looking up chat room) Chat room found: %s" % chatroom
    
    context = { "room": chatroom }
    # context = {"room": get_object_or_404(ChatRoom, slug=slug)}
    return render(request, template, context)

@never_cache
def create(request):
    """
    Handles post from the "Add room" form on the homepage, and
    redirects to the new room.
    """
    name = request.POST.get("name")
    if name:
        room, created = ChatRoom.objects.get_or_create(name=name)
        return redirect('/chat/%s' % room.id)
    return redirect(rooms)


@user_passes_test(lambda user: user.is_staff)
@never_cache
def system_message(request, template="system_message.html"):
    context = {"rooms": ChatRoom.objects.all()}
    if request.method == "POST":
        room = request.POST["room"]
        data = {"action": "system", "message": request.POST["message"]}
        try:
            if room:
                broadcast_channel(data, channel="room-" + room)
            else:
                broadcast(data)
        except NoSocket, e:
            context["message"] = e
        else:
            context["message"] = "Message sent"
    return render(request, template, context)
