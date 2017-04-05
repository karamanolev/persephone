from allauth.account.adapter import DefaultAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect

from builds.models import GlobalSettings


class BuildsAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False


def validate_email(email, whitelist):
    entries = [s.strip() for s in whitelist.split(';')]
    for entry in entries:
        if not entry:
            continue
        if entry.startswith('@'):
            parts = email.split('@')
            if len(parts) == 2 and '@' + parts[1] == entry:
                return True
        else:
            if email == entry:
                return True
    return False


class BuildsSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return True

    def pre_social_login(self, request, sociallogin):
        settings = GlobalSettings.get()
        if not settings.google_login_enabled:
            raise ImmediateHttpResponse(redirect('builds:domain_not_allowed'))
        if not validate_email(sociallogin.user.email, settings.google_whitelist):
            raise ImmediateHttpResponse(redirect('builds:domain_not_allowed'))
