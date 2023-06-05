from django.shortcuts import render
from .models import Group, Chat

def index(request, group_name):
    print('Group name......:', group_name)
    # If a group with this name exists in db, returns it
    group = Group.objects.filter(name = group_name).first()
    chats = []
    if group:
        # Retrieve chats from this group and show it
        chats = Chat.objects.filter(group = group)
    # Otherwise saves this group in db
    else:
        group = Group(name = group_name)
        group.save()
    return render(request, 'app/index.html', 
    {'groupname': group_name,'chats': chats })
