from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User, DirectMessage, Inbox, InboxMessengers
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.db.models import Max
from django.utils.html import format_html



from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string 
from django.utils import timezone

from django.core.paginator import Paginator

from django.conf import settings


# Create your views here.

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username = username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exit')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html', {'form': form})


def forgot_password(request):
    page = 'forgot_password'
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            subject = 'Reset Password Request:'

            reset_link = request.build_absolute_uri('/') + f'reset_password/{uid}/{token}/'
            message = f' Hello {user.username.upper()}, click on the link to reset your password: {reset_link}'
            email_from = "Macsauce Discuss<brasheed240@gmail.com>"
            send_mail(subject, message, email_from, [email], fail_silently=False)
            messages.success(request, 'An email has been sent to reset your password')
            return redirect ('login')
        else:
            messages.error(request, 'No user found with that email address')
            return render(request, 'base/login_register.html', {'page':page})           
    return render(request, 'base/login_register.html', {'page':page})

def reset_password(request, uid, token):
    page = 'reset_password'
    try:
        user_id = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=user_id)
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                password = request.POST.get('password')
                confirm_password = request.POST.get('confirm_password')
                if password == confirm_password:
                    user.set_password(password)
                    user.save()
                    # messages.success(request, 'Password reset successful')
                    return redirect('login')
                else:
                    messages.error(request, 'Passwords do not match')
            return render(request, 'base/login_register.html', {'page':page})
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    messages.error(request, 'Invalid or Expired link')
    return redirect('forgot_password')



        


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    paginator = Paginator(rooms, 10) 
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q))[0:10]

    context = {'rooms': rooms, 'topics': topics, 'page': page, 'page_range': paginator.page_range,
               'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)


@login_required(login_url='login')
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants}
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    paginator = Paginator(rooms, 10) 
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'page': page, 'page_range': paginator.page_range, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    # topics = Topic.objects.all()
    topics = Topic._meta.get_field('name').choices
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form': form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})



@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='login')
def activityPage(request):
    room_messages = Message.objects.all().order_by('-created')[0:5]
    return render(request, 'base/activity.html', {'room_messages': room_messages})


@login_required(login_url='login')
def myinbox(request):
    user = request.user
    inbox, created = Inbox.objects.get_or_create(user=user)

    messengers = inbox.messengers.all().annotate(
        last_message_time=Max(
            'sent_messages__created_at',
            filter=Q(received_messages__recipient=user) | Q(sent_messages__recipient=user)
        )
    ).order_by('-last_message_time')

    context = {
        'inbox': inbox,
        'messengers': messengers,
    }

    return render(request, 'base/inbox.html', context)



@login_required(login_url='login')
def direct_message(request, username):
    sender = request.user
    recipient = get_object_or_404(User, username=username)
    messages = DirectMessage.objects.filter(sender=sender, recipient=recipient) | DirectMessage.objects.filter(sender=recipient, recipient=sender)
    messages = messages.order_by('created_at')

    context = {
        'messages': messages,
        'sender': sender,
        'recipient': recipient,
        
    }
    recipient_inbox, created = Inbox.objects.get_or_create(user=recipient) 
    sender_inbox, created = Inbox.objects.get_or_create(user=sender)

    if request.method == 'POST':
        recipient_inbox.messengers.add(sender)
        sender_inbox.messengers.add(recipient)
        message = DirectMessage.objects.create(
            sender=sender,
            recipient=recipient,
            message=request.POST.get('body')
        )
        message.save()

        recipient_inbox.last_message_time = timezone.now()
        sender_inbox.last_message_time = timezone.now()
        sender_inbox.save() 
        recipient_inbox.save()

        return redirect('direct_messages', recipient)

    return render(request, 'base/direct_message.html', context)

    
@login_required(login_url='login')
def deleteDirectMessage(request, pk, chattee):
    # Get the message object or return 404 if not found
    message = get_object_or_404(DirectMessage, id=pk)
    user = message.sender
    message.delete()
    
    # Redirect back to the messages page or any other desired location
    return redirect('direct_messages', chattee)