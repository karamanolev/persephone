from rest_framework import serializers

from builds.models import Build, Project, Screenshot


class DisplayChoiceField(serializers.ChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = kwargs.pop('choices')
        self.choices_dict = dict(choices)
        self.inverse_dict = {v: k for k, v in choices}

    def to_representation(self, value):
        return self.choices_dict[value]

    def to_internal_value(self, data):
        return self.inverse_dict[data]


class ScreenshotSerializer(serializers.ModelSerializer):
    STATE_CHOICES = (
        (Screenshot.STATE_PENDING, 'pending'),
        (Screenshot.STATE_MATCHING, 'matching'),
        (Screenshot.STATE_DIFFERENT, 'different'),
        (Screenshot.STATE_NEW, 'new'),
        (Screenshot.STATE_DELETED, 'deleted'),
    )

    state = DisplayChoiceField(choices=STATE_CHOICES)
    state_display = serializers.CharField(source='get_state_display', read_only=True)

    class Meta:
        model = Screenshot
        fields = '__all__'


class FullScreenshotSerializer(ScreenshotSerializer):
    parent = ScreenshotSerializer()


class BuildSerializer(serializers.ModelSerializer):
    STATE_CHOICES = (
        (Build.STATE_INITIALIZING, 'initializing'),
        (Build.STATE_RUNNING, 'running'),
        (Build.STATE_FINISHING, 'finishing'),
        (Build.STATE_PENDING_REVIEW, 'pending_review'),
        (Build.STATE_NO_DIFF, 'no_diff'),
        (Build.STATE_APPROVED, 'approved'),
        (Build.STATE_REJECTED, 'rejected'),
        (Build.STATE_FAILED, 'failed'),
        (Build.STATE_SUPERSEDED, 'superseded'),
        (Build.STATE_FAILING, 'failing'),
    )

    project = serializers.PrimaryKeyRelatedField(read_only=True)
    state = DisplayChoiceField(choices=STATE_CHOICES, default=Build.STATE_INITIALIZING)
    state_display = serializers.CharField(source='get_state_display', read_only=True)

    class Meta:
        model = Build
        fields = '__all__'


class FullBuildSerializer(BuildSerializer):
    screenshots = FullScreenshotSerializer(read_only=True, many=True)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class FullProjectSerializer(ProjectSerializer):
    builds = BuildSerializer(read_only=True, many=True)
