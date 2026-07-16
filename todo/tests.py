from django.test import TestCase
from django.test import Client
from django.utils import timezone
from datetime import datetime
from todo.models import Task


class SampleTestCase(TestCase):
    def test_sample(self):
        self.assertEqual(1 + 2, 3)


class TaskModelTestCase(TestCase):
    def test_create_task1(self):
        due = timezone.make_aware(datetime(2024, 6, 30, 23, 59, 59))
        task = Task(title='task1', due_at=due)
        task.save()

        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.title, 'task1')
        self.assertFalse(task.completed)
        self.assertEqual(task.due_at, due)

    def test_create_task2(self):
        task = Task(title='task2')
        task.save()

        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.title, 'task2')
        self.assertFalse(task.completed)
        self.assertEqual(task.due_at, None)

    def test_is_overdue_future(self):
        due = timezone.make_aware(datetime(2024, 6, 30, 23, 59, 59))
        current = timezone.make_aware(datetime(2024, 6, 30, 0, 0, 0))
        task = Task(title='task1', due_at=due)
        task.save()

        self.assertFalse(task.is_overdue(current))

    def test_is_overdue_past(self):
        due = timezone.make_aware(datetime(2024, 6, 30, 23, 59, 59))
        current = timezone.make_aware(datetime(2024, 7, 1, 0, 0, 0))
        task = Task(title='task1', due_at=due)
        task.save()

        self.assertTrue(task.is_overdue(current))

    def test_is_overdue_none(self):
        current = timezone.make_aware(datetime(2024, 7, 1, 0, 0, 0))
        task = Task(title='task2')
        task.save()

        self.assertFalse(task.is_overdue(current))


class TodoViewTestCase(TestCase):
    def test_index_get(self):
        client = Client()
        response = client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(len(response.context['tasks']), 0)

    def test_index_post(self):
        client = Client()
        data = {'title': 'Test Task', 'due_at': '2024-06-30 23:59:59'}
        response = client.post('/', data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(len(response.context['tasks']), 1)

    def test_index_get_order_post(self):
        task1 = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task1.save()
        task2 = Task(title='task2', due_at=timezone.make_aware(datetime(2024, 8, 1)))
        task2.save()
        client = Client()
        response = client.get('/?order=post')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(response.context['tasks'][0], task2)
        self.assertEqual(response.context['tasks'][1], task1)

    def test_index_get_order_due(self):
        task1 = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task1.save()
        task2 = Task(title='task2', due_at=timezone.make_aware(datetime(2024, 8, 1)))
        task2.save()
        client = Client()
        response = client.get('/?order=due')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(response.context['tasks'][0], task1)
        self.assertEqual(response.context['tasks'][1], task2)

    def test_detail_get_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        response = client.get('/{}/'.format(task.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/detail.html')
        self.assertEqual(response.context['task'], task)
        self.assertContains(response, 'Close')
        self.assertNotContains(response, 'Reopen')

    def test_detail_get_completed_task_shows_reopen(self):
        task = Task(
            title='task1',
            due_at=timezone.make_aware(datetime(2024, 7, 1)),
            completed=True,
        )
        task.save()
        client = Client()
        response = client.get('/{}/'.format(task.pk))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reopen')
        self.assertNotContains(response, 'Close')

    def test_detail_get_fail(self):
        client = Client()
        response = client.get('/1/')

        self.assertEqual(response.status_code, 404)

    def test_update_get_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        response = client.get('/{}/update'.format(task.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/edit.html')
        self.assertEqual(response.context['task'], task)

    def test_update_get_fail(self):
        client = Client()
        response = client.get('/1/update')

        self.assertEqual(response.status_code, 404)

    def test_update_post_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        data = {'title': 'updated task', 'due_at': '2024-08-01 12:30:00'}
        response = client.post('/{}/update'.format(task.pk), data)

        self.assertRedirects(response, '/{}/'.format(task.pk))
        task.refresh_from_db()
        self.assertEqual(task.title, 'updated task')
        self.assertEqual(task.due_at, timezone.make_aware(datetime(2024, 8, 1, 12, 30)))

    def test_update_post_blank_due_at(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        data = {'title': 'updated task', 'due_at': ''}
        response = client.post('/{}/update'.format(task.pk), data)

        self.assertRedirects(response, '/{}/'.format(task.pk))
        task.refresh_from_db()
        self.assertEqual(task.title, 'updated task')
        self.assertIsNone(task.due_at)

    def test_update_post_fail(self):
        client = Client()
        data = {'title': 'updated task', 'due_at': '2024-08-01 12:30:00'}
        response = client.post('/1/update', data)

        self.assertEqual(response.status_code, 404)

    def test_delete_get_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        response = client.get('/{}/delete'.format(task.pk))

        self.assertRedirects(response, '/')
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_delete_get_keeps_other_tasks(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        other_task = Task(title='task2', due_at=timezone.make_aware(datetime(2024, 8, 1)))
        other_task.save()
        client = Client()
        response = client.get('/{}/delete'.format(task.pk))

        self.assertRedirects(response, '/')
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())
        self.assertTrue(Task.objects.filter(pk=other_task.pk).exists())

    def test_delete_get_fail(self):
        client = Client()
        response = client.get('/1/delete')

        self.assertEqual(response.status_code, 404)

    def test_close_post_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        response = client.post('/{}/close'.format(task.pk))

        self.assertRedirects(response, '/')
        task.refresh_from_db()
        self.assertTrue(task.completed)

    def test_close_get_does_not_complete(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        response = client.get('/{}/close'.format(task.pk))

        self.assertEqual(response.status_code, 405)
        task.refresh_from_db()
        self.assertFalse(task.completed)

    def test_reopen_post_success(self):
        task = Task(
            title='task1',
            due_at=timezone.make_aware(datetime(2024, 7, 1)),
            completed=True,
        )
        task.save()
        client = Client()
        response = client.post('/{}/reopen'.format(task.pk))

        self.assertRedirects(response, '/')
        task.refresh_from_db()
        self.assertFalse(task.completed)

    def test_reopen_get_does_not_reopen(self):
        task = Task(
            title='task1',
            due_at=timezone.make_aware(datetime(2024, 7, 1)),
            completed=True,
        )
        task.save()
        client = Client()
        response = client.get('/{}/reopen'.format(task.pk))

        self.assertEqual(response.status_code, 405)
        task.refresh_from_db()
        self.assertTrue(task.completed)

    def test_reopen_post_fail(self):
        client = Client()
        response = client.post('/1/reopen')

        self.assertEqual(response.status_code, 404)
