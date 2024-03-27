from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

Topic_options =(

    ('FrontEnd WEB', 'FrontEnd WEB'),
    ('BackEnd WEB', 'BackEnd WEB'),
    ('Data Science', 'Data Science'),
    ('Data Analysis','Data Analysis'),
    ('Mobile Dev', 'Mobile Dev'),
    ('UI/UX', 'UI/UX'),
    ('Others', 'Others'),
    
)
class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)

    avatar = models.ImageField(null=True, default="avatar.svg")

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []




class Topic(models.Model): 
    name = models.CharField(max_length=200, choices=Topic_options, default="Others")

    def __str__(self):
        return self.name

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(
        User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta: 
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name
    
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.body[0:50]


class DirectMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        ordering = ['-created_at']

class InboxMessengers(models.Model):
    inbox = models.ForeignKey('Inbox', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Inbox(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='inbox')
    messengers = models.ManyToManyField(User, through=InboxMessengers, related_name='messenger_inbox')
    last_message_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Inbox for {self.user.username}"

   