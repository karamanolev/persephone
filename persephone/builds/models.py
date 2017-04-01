import json
import urllib.parse
from collections import OrderedDict

from django.core.files.base import ContentFile
from django.db import models
from django.db.models.query_utils import Q
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.urls.base import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from github.MainClass import Github
from wand.image import Image


class Project(models.Model):
    name = models.CharField(max_length=128)
    public_endpoint = models.CharField(max_length=255)
    github_repo_name = models.CharField(max_length=128)
    github_api_key = models.CharField(max_length=128)
    auto_archive_no_diff_builds = models.BooleanField(default=True)
    auto_approve_master_builds = models.BooleanField(default=True)
    max_master_builds_to_keep = models.IntegerField(default=20)
    max_branch_builds_to_keep = models.IntegerField(default=20)
    supersede_same_branch_builds = models.BooleanField(default=True)

    @cached_property
    def github(self):
        return Github(login_or_token=self.github_api_key)

    @cached_property
    def github_repo(self):
        return self.github.get_repo(self.github_repo_name)

    def build_absolute_uri(self, uri):
        return urllib.parse.urljoin(self.public_endpoint, uri)

    def archive_old_builds(self):
        unarchived = self.builds.filter(archived=False).order_by('date_started')
        while True:
            master_builds = unarchived.filter(
                Q(branch_name=None) | Q(branch_name__in=['', 'master', 'origin/master']))
            if master_builds.count() <= self.max_master_builds_to_keep:
                break
            build = master_builds.first()
            build.archive()
            build.save()
        while True:
            branch_builds = unarchived.exclude(
                Q(branch_name=None) | Q(branch_name__in=['', 'master', 'origin/master']))
            if branch_builds.count() <= self.max_branch_builds_to_keep:
                break
            build = branch_builds.first()
            build.archive()
            build.save()

    class Meta:
        ordering = ('name',)


class Build(models.Model):
    MASTER_BRANCH_NAMES = ['', 'master', 'origin/master']

    STATE_INITIALIZING = 0
    STATE_RUNNING = 1
    STATE_FINISHING = 2
    STATE_PENDING_REVIEW = 3
    STATE_NO_DIFF = 4
    STATE_APPROVED = 5
    STATE_REJECTED = 6
    STATE_FAILED = 7
    STATE_SUPERSEDED = 8
    STATE_CHOICES = (
        (STATE_INITIALIZING, 'Initializing'),
        (STATE_RUNNING, 'Running'),
        (STATE_FINISHING, 'Finishing'),
        (STATE_PENDING_REVIEW, 'Pending Review'),
        (STATE_NO_DIFF, 'No Diff'),
        (STATE_APPROVED, 'Approved'),
        (STATE_REJECTED, 'Rejected'),
        (STATE_FAILED, 'Failed'),
        (STATE_SUPERSEDED, 'Superseeded'),
    )

    project = models.ForeignKey(Project, related_name='builds')
    parent = models.ForeignKey('self', null=True, related_name='children',
                               on_delete=models.SET_NULL)
    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_INITIALIZING)
    original_build_number = models.CharField(max_length=64, blank=True, null=True)
    original_build_url = models.CharField(max_length=256, blank=True, null=True)
    date_started = models.DateTimeField(auto_now_add=True)
    date_finished = models.DateTimeField(null=True)
    date_approved = models.DateTimeField(null=True)
    date_rejected = models.DateTimeField(null=True)
    reviewed_by = models.CharField(max_length=128, blank=True, null=True)
    branch_name = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    pull_request_id = models.CharField(max_length=16, blank=True, null=True)
    commit_hash = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    archived = models.BooleanField(default=False, db_index=True)

    @cached_property
    def github_commit(self):
        return self.project.github_repo.get_commit(self.commit_hash)

    @cached_property
    def github_pull_request(self):
        return self.project.github_repo.get_pull(int(self.pull_request_id))

    def update_github_status(self):
        if not self.commit_hash:
            return
        kwargs = {
            'state': {
                Build.STATE_INITIALIZING: 'pending',
                Build.STATE_RUNNING: 'pending',
                Build.STATE_FINISHING: 'finishing',
                Build.STATE_PENDING_REVIEW: 'pending',
                Build.STATE_NO_DIFF: 'success',
                Build.STATE_APPROVED: 'success',
                Build.STATE_REJECTED: 'failure',
                Build.STATE_FAILED: 'error',
            }[self.state],
            'description': {
                Build.STATE_INITIALIZING: 'Build is initializing.',
                Build.STATE_RUNNING: 'Build is running.',
                Build.STATE_FINISHING: 'Build is finishing.',
                Build.STATE_PENDING_REVIEW: 'Visual diff is pending review.',
                Build.STATE_NO_DIFF: 'There are no visual differences detected.',
                Build.STATE_APPROVED: 'Visual diff is approved.',
                Build.STATE_REJECTED: 'Visual diff is rejected.',
                Build.STATE_FAILED: 'Build failed.',
            }[self.state],
            'context': 'persephone',
        }
        if self.project.public_endpoint:
            url = self.project.build_absolute_uri(reverse(
                'builds:build', args=(self.project_id, self.id)))
            kwargs['target_url'] = url
        self.github_commit.create_status(**kwargs)

    def get_master_baseline(self):
        builds = self.project.builds.filter(
            Q(state=self.STATE_APPROVED, archived=False)
            &
            (Q(branch_name=None) | Q(branch_name__in=Build.MASTER_BRANCH_NAMES))
        )
        return builds.filter(date_finished__isnull=False).order_by('-date_started').first()

    def find_parent(self):
        if self.pull_request_id:
            pr_build = Build.objects.filter(
                commit_hash=self.github_pull_request.base.sha,
                date_finished__isnull=False,
                archived=False,
            ).order_by('-date_started').first()
            if pr_build is not None:
                return pr_build
        return self.get_master_baseline()

    def _finish_compute_state(self):
        if all(s.state == Screenshot.STATE_MATCHING for s in self.screenshots.all()):
            self.state = Build.STATE_NO_DIFF
            return

        is_master = self.branch_name in Build.MASTER_BRANCH_NAMES
        if is_master and self.project.auto_approve_master_builds:
            self.state = Build.STATE_APPROVED
            self.reviewed_by = 'autoapprover'
            return

        self.state = Build.STATE_PENDING_REVIEW

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
        self._finish_compute_state()
        if self.state == Build.STATE_NO_DIFF:
            if self.project.auto_archive_no_diff_builds:
                self.archive()
        self.date_finished = timezone.now()
        self.update_github_status()

    def archive(self):
        for screenshot in self.screenshots.filter(archived=False):
            screenshot.archive()
            screenshot.save()
        self.archived = True

    @cached_property
    def screenshots_by_color(self):
        screenshots = list(self.screenshots.all())
        total_expected = max(1, len(screenshots))
        if self.parent:
            total_expected = max(total_expected, self.parent.screenshots.count())
        return OrderedDict((
            ('success',
             len([s for s in screenshots if
                  s.state == Screenshot.STATE_MATCHING]) / total_expected),
            ('danger',
             len([s for s in screenshots if s.state in [
                 Screenshot.STATE_DELETED, Screenshot.STATE_DIFFERENT]]) / total_expected),
            ('warning',
             len([s for s in screenshots if s.state == Screenshot.STATE_PENDING]) / total_expected),
            ('active',
             len([s for s in screenshots if s.state == Screenshot.STATE_NEW]) / total_expected),
        ))

    def supersede(self):
        self.state = Build.STATE_SUPERSEDED

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
    metadata_json = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='screenshots/')
    image_diff = models.ImageField(upload_to='screenshot_diffs/', null=True)
    image_diff_amount = models.FloatField(null=True)
    archived = models.BooleanField(default=False, db_index=True)

    @cached_property
    def metadata(self):
        if self.metadata_json:
            return json.loads(self.metadata_json)
        return None

    @cached_property
    def metadata_pretty(self):
        if self.metadata:
            return json.dumps(self.metadata, indent=2, ensure_ascii=False)
        return None

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

    def archive(self):
        if self.image:
            self.image.delete(save=False)
        if self.image_diff:
            self.image_diff.delete(save=False)
        self.archived = True

    class Meta:
        unique_together = (
            ('build', 'name'),
        )


@receiver(pre_delete, sender=Screenshot)
def screenshot_pre_delete(sender, instance, using, **kwargs):
    instance.archive()
