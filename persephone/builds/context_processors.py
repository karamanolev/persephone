from builds.models import Project


def builds_context_processor(request):
    return {
        'projects': Project.objects.all(),
    }
