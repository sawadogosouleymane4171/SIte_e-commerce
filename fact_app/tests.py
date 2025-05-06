from django.test import TestCase, Client
from django.urls import reverse
from django.utils.translation import get_language

class LanguageChangeTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_change_language_to_french(self):
        response = self.client.post(reverse('change_language'), {'language': 'fr'}, HTTP_REFERER='/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['django_language'], 'fr')
        self.assertEqual(get_language(), 'fr')

    def test_change_language_to_english(self):
        response = self.client.post(reverse('change_language'), {'language': 'en'}, HTTP_REFERER='/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['django_language'], 'en')
        self.assertEqual(get_language(), 'en')
