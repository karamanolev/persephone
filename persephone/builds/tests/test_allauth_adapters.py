from django.test.testcases import TestCase

from builds.allauth_adapters import validate_email


class ValidateEmailTests(TestCase):
    def test_validation(self):
        data = {
            '@test.com; @test2.com': {
                'valid': ['hello@test.com', 'test@test.com', 'test@test2.com'],
                'invalid': ['test@test.com.net', 'test@ttest.com'],
            },
            'test@test.com; @test2.com': {
                'valid': ['test@test2.com', 'test@test.com'],
                'invalid': ['hello@test.com', 'test@test.com.net', 'test@ttest.com'],
            },
        }

        for whitelist, d in data.items():
            for email in d['valid']:
                self.assertTrue(validate_email(email, whitelist))
            for email in d['invalid']:
                self.assertFalse(validate_email(email, whitelist))
