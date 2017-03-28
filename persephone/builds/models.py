import urllib.parse

from django.core.files.base import ContentFile
from django.db import models
from django.db.models.query_utils import Q
from django.urls.base import reverse
from django.utils.functional import cached_property
from github.MainClass import Github
from wand.image import Image


class Project(models.Model):
    name = models.CharField(max_length=128)
    public_endpoint = models.CharField(max_length=255)
    github_repo_name = models.CharField(max_length=128)
    github_api_key = models.CharField(max_length=128)

    @cached_property
    def github(self):
        return Github(login_or_token=self.github_api_key)

    @cached_property
    def github_repo(self):
        return self.github.get_repo(self.github_repo_name)

    def build_absolute_uri(self, uri):
        return urllib.parse.urljoin(self.public_endpoint, uri)


class Build(models.Model):
    STATE_INITIALIZING = 0
    STATE_RUNNING = 1
    STATE_FINISHING = 2
    STATE_PENDING_REVIEW = 3
    STATE_NO_DIFF = 4
    STATE_APPROVED = 5
    STATE_REJECTED = 6
    STATE_CHOICES = (
        (STATE_INITIALIZING, 'Initializing'),
        (STATE_RUNNING, 'Running'),
        (STATE_FINISHING, 'Finishing'),
        (STATE_PENDING_REVIEW, 'Pending Review'),
        (STATE_NO_DIFF, 'No Diff'),
        (STATE_APPROVED, 'Approved'),
        (STATE_REJECTED, 'Rejected'),
    )

    project = models.ForeignKey(Project, related_name='builds')
    parent = models.ForeignKey('self', null=True, related_name='children')
    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_INITIALIZING)
    original_build_number = models.CharField(max_length=64, blank=True, null=True)
    original_build_url = models.CharField(max_length=256, blank=True, null=True)
    date_started = models.DateTimeField(auto_now_add=True)
    date_finished = models.DateTimeField(null=True)
    date_approved = models.DateTimeField(null=True)
    date_rejected = models.DateTimeField(null=True)
    reviewed_by = models.CharField(max_length=128, blank=True, null=True)
    branch_name = models.CharField(max_length=128, blank=True, null=True)
    pull_request_id = models.CharField(max_length=16, blank=True, null=True)
    commit_hash = models.CharField(max_length=64, db_index=True)

    @cached_property
    def github_commit(self):
        return self.project.github_repo.get_commit(self.commit_hash)

    @cached_property
    def github_pull_request(self):
        return self.project.github_repo.get_pull(int(self.pull_request_id))

    def update_github_status(self):
        kwargs = {
            'state': {
                self.STATE_INITIALIZING: 'pending',
                self.STATE_RUNNING: 'pending',
                self.STATE_FINISHING: 'finishing',
                self.STATE_PENDING_REVIEW: 'pending',
                self.STATE_NO_DIFF: 'success',
                self.STATE_APPROVED: 'success',
                self.STATE_REJECTED: 'failure',
            }[self.state],
            'description': {
                self.STATE_INITIALIZING: 'Build is initializing.',
                self.STATE_RUNNING: 'Build is running.',
                self.STATE_FINISHING: 'Build is finishing.',
                self.STATE_PENDING_REVIEW: 'Visual diff is pending review.',
                self.STATE_NO_DIFF: 'There are no visual differences detected.',
                self.STATE_APPROVED: 'Visual diff is approved.',
                self.STATE_REJECTED: 'Visual diff is rejected.',
            }[self.state],
            'context': 'persephone',
        }
        if self.project.public_endpoint:
            url = self.project.build_absolute_uri(reverse(
                'builds:build', args=(self.project_id, self.id)))
            kwargs['target_url'] = url
        self.github_commit.create_status(**kwargs)

    def find_parent(self):
        if self.pull_request_id:
            try:
                return Build.objects.filter(
                    commit_hash=self.github_pull_request.base.sha,
                    date_finished__isnull=False,
                ).order_by('-date_started').last()
            except Build.DoesNotExist:
                pass
        builds = self.project.builds.filter(
            Q(state=self.STATE_APPROVED) & (
                Q(branch_name=None) | Q(branch_name__in=['', 'master', 'origin/master'])),
        )
        return builds.filter(date_finished__isnull=False).order_by('-date_started').first()

    def finish(self):
        screenshots = {s.name: s for s in self.screenshots.all()}
        if self.parent:
            parent_screenshots = {s.name: s for s in self.parent.screenshots.all()}
            for parent_name, parent_screenshot in parent_screenshots.items():
                if parent_name not in screenshots:
                    Screenshot.objects.create(
                        build=self,
                        state=Screenshot.STATE_DELETED,
                        parent=parent_screenshot,
                        name=parent_screenshot.name,
                    )
        if all(s.state == Screenshot.STATE_MATCHING for s in self.screenshots.all()):
            self.state = Build.STATE_NO_DIFF
        else:
            self.state = Build.STATE_PENDING_REVIEW
        self.update_github_status()

    class Meta:
        ordering = ('-date_started',)


class Screenshot(models.Model):
    STATE_PENDING = 0
    STATE_MATCHING = 1
    STATE_DIFFERENT = 2
    STATE_NEW = 3
    STATE_DELETED = 4
    STATE_CHOICES = (
        (STATE_PENDING, 'Pending'),
        (STATE_MATCHING, 'Matching'),
        (STATE_DIFFERENT, 'Different'),
        (STATE_NEW, 'New'),
        (STATE_DELETED, 'Deleted'),
    )

    build = models.ForeignKey(Build, related_name='screenshots')
    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_PENDING)
    parent = models.ForeignKey('self', null=True, related_name='children')
    date_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='screenshots/')
    image_diff = models.ImageField(upload_to='screenshot_diffs/', null=True)
    image_diff_amount = models.FloatField(null=True)

    def find_parent(self):
        parent_build = self.build.parent
        if parent_build:
            return parent_build.screenshots.filter(name=self.name).first()
        else:
            return None

    def process(self):
        self.parent = self.find_parent()
        if self.parent is None:
            self.state = Screenshot.STATE_NEW
        else:
            wand_current = Image(filename=self.image.path)
            wand_parent = Image(filename=self.parent.image.path)
            wand_diff, difference = wand_current.compare(wand_parent, metric='root_mean_square')

            self.image_diff_amount = difference
            if difference > 0:
                self.image_diff = ContentFile(
                    wand_diff.make_blob('png'),
                    name='{}_{}_diff.png'.format(self.parent.id, self.id),
                )
                self.state = Screenshot.STATE_DIFFERENT
            else:
                self.state = Screenshot.STATE_MATCHING

    class Meta:
        unique_together = (
            ('build', 'name'),
        )
