from datetime import datetime, timedelta
from unittest import mock

from django.test.testcases import TestCase
from django.utils import timezone
from pytz import UTC

from builds.factories import ProjectFactory, BuildFactory
from builds.models import Build


class ProjectBuilds(TestCase):
    def test_build_absolute_uri(self):
        project = ProjectFactory(
            public_endpoint='http://persephone.yourdomain.com/',
        )
        self.assertEqual(
            project.build_absolute_uri('/hello/world'),
            'http://persephone.yourdomain.com/hello/world',
        )

    def test_archiving(self):
        project = ProjectFactory()
        for i in range(2 * project.max_master_builds_to_keep):
            self.assertEqual(
                project.builds.count(),
                i,
            )
            self.assertEqual(
                project.builds.filter(archived=False).count(),
                min(i, project.max_master_builds_to_keep),
            )
            BuildFactory(project=project)
            project.archive_old_builds()


class BuildTests(TestCase):
    @mock.patch('builds.models.Build.github_commit', new_callable=mock.PropertyMock)
    def test_update_github_status_no_commit(self, mock_commit):
        build = BuildFactory(commit_hash='')
        build.update_github_status()
        mock_commit.assert_not_called()

    @mock.patch('builds.models.Build.github_commit', new_callable=mock.PropertyMock)
    def test_update_github_status(self, mock_commit):
        build = BuildFactory()
        build.update_github_status()
        mock_commit.assert_called_once_with()
        mock_commit().create_status.assert_called_once_with(
            context='persephone',
            description='Visual diff is approved.',
            state='success',
            target_url='http://persephone.yourdomain.com/projects/1/builds/1/',
        )

    def test_get_master_baseline(self):
        project = ProjectFactory()
        BuildFactory(project=project,
                     branch_name='test-branch')
        self.assertIsNone(project.get_master_baseline())
        BuildFactory(project=project,
                     branch_name='origin/master',
                     archived=True)
        self.assertIsNone(project.get_master_baseline())
        BuildFactory(project=project,
                     branch_name='origin/master',
                     state=Build.STATE_REJECTED)
        self.assertIsNone(project.get_master_baseline())
        b1 = BuildFactory(project=project,
                          branch_name='origin/master',
                          date_started=datetime(2017, 1, 2, 0, 0, 0, tzinfo=UTC),
                          date_finished=datetime(2017, 1, 2, 0, 0, 0, tzinfo=UTC))
        self.assertEqual(project.get_master_baseline(), b1)
        b2 = BuildFactory(project=project,
                          branch_name='origin/master',
                          date_started=datetime(2017, 1, 3, 0, 0, 0, tzinfo=UTC),
                          date_finished=datetime(2017, 1, 3, 0, 0, 0, tzinfo=UTC))
        self.assertEqual(project.get_master_baseline(), b2)
        BuildFactory(project=project,
                     branch_name='origin/master',
                     date_started=datetime(2017, 1, 1, 0, 0, 0, tzinfo=UTC),
                     date_finished=datetime(2017, 1, 1, 0, 0, 0, tzinfo=UTC))
        self.assertEqual(project.get_master_baseline(), b2)

    @mock.patch('builds.models.Build.github_pull_request', new_callable=mock.PropertyMock)
    def test_find_parent_pr(self, mock_pull_request):
        project = ProjectFactory()
        b1 = BuildFactory(project=project,
                          commit_hash='sha1_1')
        b2 = BuildFactory(project=project,
                          branch_name='test-branch',
                          pull_request_id=3)
        mock_pull_request.base.sha.return_value = b1
        self.assertEqual(b2.find_parent(), b1)
        mock_pull_request.assert_called_once_with()

    @mock.patch('builds.models.Build.github_pull_request', new_callable=mock.PropertyMock)
    def test_find_parent_master(self, mock_pull_request):
        project = ProjectFactory()
        b1 = BuildFactory(project=project,
                          branch_name='origin/master')
        b2 = BuildFactory(project=project,
                          branch_name='test-branch',
                          pull_request_id=None)
        mock_pull_request.base.sha.return_value = b1
        self.assertEqual(b2.find_parent(), b1)
        mock_pull_request.assert_not_called()

    @mock.patch('builds.models.Build.update_github_status')
    def test_finish(self, mock_update_status):
        build = BuildFactory(branch_name='test-branch')
        build.finish()
        self.assertEqual(build.state, Build.STATE_PENDING_REVIEW)
        self.assertLessEqual(timezone.now() - build.date_finished, timedelta(seconds=1))
        mock_update_status.assert_called_once_with()

    @mock.patch('builds.models.Build.update_github_status')
    def test_finish_auto_approve(self, mock_update_status):
        build = BuildFactory(branch_name='origin/master')
        build.finish()
        self.assertEqual(build.state, Build.STATE_APPROVED)
        self.assertLessEqual(timezone.now() - build.date_finished, timedelta(seconds=1))
        mock_update_status.assert_called_once_with()

    @mock.patch('builds.models.Build.update_github_status')
    def test_finish_no_auto_approve(self, mock_update_status):
        project = ProjectFactory(auto_approve_master_builds=False)
        build = BuildFactory(project=project,
                             branch_name='origin/master')
        build.finish()
        self.assertEqual(build.state, Build.STATE_PENDING_REVIEW)
        self.assertLessEqual(timezone.now() - build.date_finished, timedelta(seconds=1))
        mock_update_status.assert_called_once_with()

    def test_archive(self):
        build = BuildFactory()
        build.archive()
        self.assertTrue(build.archived)
        for screenshot in build.screenshots.all():
            self.assertTrue(screenshot.archived)

    def test_supersede(self):
        build = BuildFactory()
        build.supersede()
        self.assertEqual(build.state, Build.STATE_SUPERSEDED)
