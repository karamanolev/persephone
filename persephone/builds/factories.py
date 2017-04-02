from datetime import datetime

import factory
from pytz import UTC

from builds.models import Project, Build, Screenshot


class ProjectFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda x: 'Project {}'.format(x))
    public_endpoint = 'http://persephone.yourdomain.com/'
    github_repo_name = 'fake/repo'
    github_api_key = 'asdfqwerty'

    class Meta:
        model = Project


class ScreenshotFactory(factory.DjangoModelFactory):
    state = Screenshot.STATE_DIFFERENT
    name = factory.Sequence(lambda x: 'Screenshot {}'.format(x))
    metadata_json = '{"test": "data"}'
    image = 'screenshots/test.png'
    image_diff = 'screenshots/test_diff.png'
    archived = False

    class Meta:
        model = Screenshot


class BuildFactory(factory.DjangoModelFactory):
    project = factory.SubFactory(ProjectFactory)
    state = Build.STATE_APPROVED
    original_build_number = '150'
    original_build_url = 'http://jenkins.example.com/builds/150'
    date_approved = datetime(2017, 3, 1, 9, 0, 0, tzinfo=UTC)
    reviewed_by = 'test_user'
    branch_name = 'origin/master'
    pull_request_id = '123'
    commit_hash = '927569e0f8af30d1b3f10682ef9fb981d65ab569'
    archived = False

    @factory.post_generation
    def add_screenshots(self, create, extracted, **kwargs):
        ScreenshotFactory(build=self)

    class Meta:
        model = Build
