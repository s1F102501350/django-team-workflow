from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from todo.models import Task


def index(request):
    if request.method == 'POST':
        task = Task(
            title=request.POST['title'],
            due_at=make_aware(parse_datetime(request.POST['due_at'])),
        )
        task.save()

    if request.GET.get('order') == 'due':
        tasks = Task.objects.order_by('due_at')
    else:
        tasks = Task.objects.order_by('-posted_at', '-pk')
    context = {
        'tasks': tasks,
    }
    return render(request, 'todo/index.html', context)


def detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    context = {
        'task': task,
    }
    return render(request, 'todo/detail.html', context)


def delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    return redirect('index')
