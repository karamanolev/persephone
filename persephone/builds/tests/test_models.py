from datetime import datetime
from unittest import mock

from django.test.testcases import TestCase
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
    def test_update_github_status_no_commit(self):
        build = BuildFactory(commit_hash='')
        with mock.patch('builds.models.Build.github_commit',
                        new_callable=mock.PropertyMock) as mock_commit:
            build.update_github_status()
            mock_commit.assert_not_called()

    def test_update_github_status(self):
        build = BuildFactory()
        with mock.patch('builds.models.Build.github_commit',
                        new_callable=mock.PropertyMock) as mock_commit:
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

    def test_find_parent_pr(self):
        pass
