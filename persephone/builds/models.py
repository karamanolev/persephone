from django.db import models
from django.utils.functional import cached_property
from github.MainClass import Github


class Project(models.Model):
    name = models.CharField(max_length=128)
    github_repo_name = models.CharField(max_length=128)
    github_api_key = models.CharField(max_length=128)

    @cached_property
    def github(self):
        return Github(login_or_token=self.github_api_key)

    @cached_property
    def github_repo(self):
        return self.github.get_repo(self.github_repo_name)


class Build(models.Model):
    STATE_RUNNING = 0
    STATE_PENDING_REVIEW = 1
    STATE_APPROVED = 2
    STATE_REJECTED = 3
    STATE_CHOICES = (
        (STATE_RUNNING, 'Running'),
        (STATE_PENDING_REVIEW, 'Pending Review'),
        (STATE_APPROVED, 'Approved'),
        (STATE_REJECTED, 'Rejected'),
    )

    project = models.ForeignKey(Project, related_name='builds')
    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_RUNNING)
    build_number = models.CharField(max_length=64)
    date_started = models.DateTimeField(auto_now_add=True)
    date_finished = models.DateTimeField(null=True)
    branch_name = models.CharField(max_length=128, blank=True, null=True)
    pull_request_id = models.CharField(max_length=16, blank=True, null=True)
    commit_hash = models.CharField(max_length=64)

    @cached_property
    def github_commit(self):
        return self.project.github_repo_name.commit()

    class Meta:
        unique_together = (
            ('project', 'build_number'),
        )
