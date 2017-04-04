from unittest import mock

from django.test.testcases import TestCase

from builds.factories import BuildFactory
from builds.models import Build
from builds.tasks import process_build_created


class ProcessBuildCreatedTests(TestCase):
    @mock.patch('builds.models.Build.update_github_status')
    def test_superseding(self, mock_update_status):
        b1 = BuildFactory(branch_name='1', state=Build.STATE_APPROVED, pull_request_id=None)
        b2 = BuildFactory(branch_name='2', state=Build.STATE_PENDING_REVIEW, pull_request_id=None)
        b3 = BuildFactory(branch_name='1', state=Build.STATE_PENDING_REVIEW, pull_request_id=None)
        b4 = BuildFactory(branch_name='1', state=Build.STATE_INITIALIZING, pull_request_id=None)
        process_build_created(b4.id)
        [b.refresh_from_db() for b in [b1, b2, b3, b4]]
        self.assertEqual(b1.state, Build.STATE_APPROVED)
        self.assertEqual(b2.state, Build.STATE_PENDING_REVIEW)
        self.assertEqual(b3.state, Build.STATE_SUPERSEDED)
        self.assertEqual(b4.state, Build.STATE_RUNNING)
