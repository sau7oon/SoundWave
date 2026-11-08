from django.db import models
from django.shortcuts import render
from django.http import HttpResponseRedirect #1 Это инструмент, который отправляет браузеру команду перейти на другую страницу.
from django.urls import reverse #могает Django найти адрес страницы по её имени
from .models import Topic, Entry
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout 
from django.shortcuts import render, get_object_or_404 #ошибка если нет данных в базе
from .models import Topic
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST





from django.contrib.auth.decorators import login_required

def index(request):
    query = request.GET.get('q', '').strip()

    if request.user.is_authenticated:
        topics = Topic.objects.filter(
            models.Q(owner=request.user) | models.Q(is_public=True)
        )
    else:
        topics = Topic.objects.filter(is_public=True)

    if query:
        topics = topics.filter(
            models.Q(text__icontains=query) |
            models.Q(entry__text__icontains=query)
        ).distinct()

    topics = topics.order_by('date_added')

    context = {
        'topics': topics,
        'query': query,
    }

    return render(request, 'soundwave/index.html', context)

@login_required
def new_topic(request):
    if request.method == 'POST':
        topic_text = request.POST['text']

        Topic.objects.create(
            text=topic_text,
            owner=request.user
        )

        return HttpResponseRedirect(reverse('index'))

    return HttpResponseRedirect(reverse('index'))

@login_required
def toggle_topic_public(request, topic_id):
    topic = get_object_or_404(
        Topic,
        id=topic_id,
        owner=request.user
    )

    if request.method == 'POST':
        topic.is_public = not topic.is_public
        topic.save()

    return HttpResponseRedirect(reverse('topic', args=[topic_id])) #Что делает функция:находит тему текущего пользователя.Меняет настройку публичности на противоположную. Сохраняет изменение. Возвращает пользователя к теме.

def topic(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)

    if topic.owner != request.user and not topic.is_public:
        from django.http import Http404
        raise Http404

    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'soundwave/topic.html', context)

@login_required
def new_entry(request, topic_id):
    topic = get_object_or_404(
        Topic,
        id=topic_id,
        owner=request.user
    )
    if request.method == 'POST':
        entry = Entry(topic=topic, text=request.POST['text'])
        entry.save()
        return HttpResponseRedirect(reverse('topic', args=[topic_id]))

    return HttpResponseRedirect(reverse('topic', args=[topic_id]))

@login_required
def edit_entry(request, entry_id):
    entry = get_object_or_404(
        Entry,
        id=entry_id,
        topic__owner=request.user
    )
    topic = entry.topic

    if request.method == 'POST':
        entry.text = request.POST['text']
        entry.save()
        return HttpResponseRedirect(reverse('topic', args=[topic.id]))

    context = {'entry': entry, 'topic': topic}
    return render(request, 'soundwave/edit_entry.html', context)

@login_required
def delete_entry(request, entry_id):
    entry = get_object_or_404(
        Entry,
        id=entry_id,
        topic__owner=request.user
    )
    topic_id = entry.topic.id

    if request.method == 'POST':
        entry.delete()
        return HttpResponseRedirect(reverse('topic', args=[topic_id]))

    return HttpResponseRedirect(reverse('topic', args=[topic_id]))

def register(request):
    if request.method != 'POST':
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            return HttpResponseRedirect(reverse('index'))

    context = {'form': form}
    return render(request, 'soundwave/register.html', context)

def user_login(request):
    if request.method != 'POST':
        form = AuthenticationForm()
    else:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return HttpResponseRedirect(reverse('index'))

    return render(request, 'soundwave/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

@login_required
def profile(request, username):
    user_profile = get_object_or_404(
        User,
        username=username
    )

    if request.user == user_profile:
        topics = Topic.objects.filter(
            owner=user_profile
        ).order_by('date_added')
    else:
        topics = Topic.objects.filter(
            owner=user_profile,
            is_public=True
        ).order_by('date_added')

    context = {
        'profile_user': user_profile,
        'topics': topics
    }

    return render(
        request,
        'soundwave/profile.html',
        context
    )

@login_required
@require_POST
def delete_topic(request, topic_id):
    topic = get_object_or_404(
        Topic,
        id=topic_id,
        owner=request.user
    )

    topic_id = topic.id
    username = request.user.username
    topic.delete()

    if request.POST.get('next') == 'index':
        return HttpResponseRedirect(reverse('index'))

    return HttpResponseRedirect(
        reverse('profile', args=[username])
    )