from builds.models import Project, GlobalSettings


def builds_context_processor(request):
    return {
        'projects': Project.objects.all(),
        'global_settings': GlobalSettings.get(),
    }
