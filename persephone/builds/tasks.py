from time import sleep

from django.db import transaction

from builds.models import Screenshot, Build
from persephone.celery import app


@app.task
@transaction.atomic
def process_build_created(build_id):
    build = Build.objects.select_for_update().get(id=build_id)
    if build.state != Build.STATE_INITIALIZING:
        raise Exception('Build is not initializing')
    build.parent = build.find_parent()
    build.state = Build.STATE_RUNNING
    build.update_github_status()
    build.save()
    build.project.archive_old_builds()
    if build.project.supersede_same_branch_builds:
        previous_builds = Build.objects.filter(
            state=Build.STATE_PENDING_REVIEW,
            branch_name=build.branch_name,
        )
        for previous_build in previous_builds:
            previous_build.supersede()
            previous_build.save()


@app.task
@transaction.atomic
def process_build_finished(build_id, retries_remaining=12):
    build = Build.objects.select_for_update().get(id=build_id)
    if any(s.state == Screenshot.STATE_PENDING for s in build.screenshots.all()):
        if retries_remaining == 0:
            raise Exception('Screenshot processing did not finish on time')

            # Proper retry logic if using Celery
        # process_build_finished.apply_async(args=(build_id, retries_remaining - 1), countdown=5)
        # return

        # Ugly retry logic
        sleep(2)
        return process_build_finished(build_id, retries_remaining - 1)

    build.finish()
    build.save()


@app.task
@transaction.atomic
def process_build_failed(build_id, retries_remaining=12):
    build = Build.objects.select_for_update().get(id=build_id)
    if any(s.state == Screenshot.STATE_PENDING for s in build.screenshots.all()):
        if retries_remaining == 0:
            raise Exception('Screenshot processing did not finish on time')

        # Proper retry logic if using Celery
        # process_build_failed.apply_async(args=(build_id, retries_remaining - 1), countdown=5)
        # return

        # Ugly retry logic
        sleep(2)
        return process_build_failed(build_id, retries_remaining - 1)

    build.fail()
    build.save()


@app.task
@transaction.atomic
def process_screenshot(screenshot_id, retries_remaing=3):
    screenshot = Screenshot.objects.select_for_update().get(id=screenshot_id)
    if screenshot.build.state == Build.STATE_INITIALIZING:
        if retries_remaing == 0:
            raise Exception('Build did not initialize on time')

        # Proper retry logic if using Celery
        # process_screenshot.apply_async(args=(screenshot_id, retries_remaing - 1), countdown=5)
        # return

        # Ugly retry logic
        sleep(2)
        return process_screenshot(screenshot_id, retries_remaing - 1)

    elif screenshot.build.state != Build.STATE_RUNNING:
        raise Exception('Trying to add a screenshot to a build that\'s not running')
    screenshot.process()
    screenshot.save()
