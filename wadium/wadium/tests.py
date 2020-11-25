from rest_framework import status
from django.test import TestCase


class GetRootTestCase(TestCase):
    URI = '/'
    expected_response = "Hi, this is wadium backend."

    def test_get_root(self):
        response = self.client.get(
            self.URI,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = response.content.decode('utf-8')
        self.assertEqual(content, self.expected_response)
