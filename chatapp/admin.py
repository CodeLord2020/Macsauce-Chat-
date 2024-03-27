from django.contrib import admin

# Register your models here.

from .models import Room, Topic, Message, User, DirectMessage, Inbox, InboxMessengers

admin.site.register(User)
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(DirectMessage)
admin.site.register(Inbox)
admin.site.register(InboxMessengers)