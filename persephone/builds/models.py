from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=128)


class Build(models.Model):
    STATE_RUNNING = 0
    STATE_PENDING_REVIEW = 1
    STATE_APPROVED = 1
    STATE_REJECTED = 1
    STATE_CHOICES = (
        (STATE_RUNNING, 'Running'),
        (STATE_PENDING_REVIEW, 'Pending Review'),
        (STATE_APPROVED, 'Approved'),
        (STATE_REJECTED, 'Rejected'),
    )

    project = models.ForeignKey(Project)
    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_RUNNING)
    build_id = models.CharField(max_length=64)
    date_started = models.DateTimeField(auto_now_add=True)
    date_finished = models.DateTimeField(null=True)
    branch_name = models.CharField(max_length=128)
    pull_request_id = models.CharField(max_length=16)
    commit_hash = models.CharField(max_length=64)
