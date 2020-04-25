from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.provider import GoogleProvider
from django import forms
from django.contrib.sites.shortcuts import get_current_site

from builds.models import GlobalSettings


class GlobalSettingsForm(forms.Form):
    google_login_enabled = forms.BooleanField(required=False)
    google_client_id = forms.CharField(required=False)
    google_client_secret = forms.CharField(widget=forms.PasswordInput(render_value=True))
    google_whitelist = forms.CharField(required=False)

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.request = request
        settings = GlobalSettings.get()
        self.fields['google_login_enabled'].initial = settings.google_login_enabled
        self.fields['google_whitelist'].initial = settings.google_whitelist
        try:
            social_app = SocialApp.objects.get_current(GoogleProvider.id, self.request)
            self.fields['google_client_id'].initial = social_app.client_id
            self.fields['google_client_secret'].initial = social_app.secret
        except SocialApp.DoesNotExist:
            pass

    def save(self):
        settings = GlobalSettings.get()
        settings.google_login_enabled = self.cleaned_data['google_login_enabled']
        settings.google_whitelist = self.cleaned_data['google_whitelist']
        settings.save()

        if self.cleaned_data['google_client_id'] or self.cleaned_data['google_client_secret']:
            try:
                social_app = SocialApp.objects.get_current(GoogleProvider.id, self.request)
            except SocialApp.DoesNotExist:
                social_app = SocialApp.objects.create(
                    name=GoogleProvider.name,
                    provider=GoogleProvider.id,
                )
                site = get_current_site(self.request)
                social_app.sites.add(site)
            social_app.client_id = self.cleaned_data['google_client_id']
            social_app.secret = self.cleaned_data['google_client_secret']
            social_app.save()
