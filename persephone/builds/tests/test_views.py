from functools import wraps
from unittest import mock

from django.contrib.auth.models import User
from django.test.testcases import TestCase
from django.urls.base import reverse

from builds.factories import ProjectFactory


def authenticated_test_case(f):
    @wraps(f)
    def inner(self, *args, **kwargs):
        self.user = User(username='test_user')
        self.user.set_password('test_pass')
        self.user.save()
        self.assertTrue(self.client.login(username='test_user', password='test_pass'))
        return f(self, *args, **kwargs)

    return inner


class APIBuildsTests(TestCase):
    @mock.patch('django.db.transaction.on_commit')
    @authenticated_test_case
    def test_create(self, mock_on_commit):
        project = ProjectFactory()
        r = self.client.post(
            reverse('builds:api_builds', args=[project.id]),
            {
                'commit_hash': 'asdf',
            }
        )
        self.assertEqual(r.status_code, 201)
        build = project.builds.get()
        self.assertEqual(mock_on_commit.call_count, 1)
        self.assertEqual(build.commit_hash, 'asdf')


class APIScreenshots(TestCase):
    pass
