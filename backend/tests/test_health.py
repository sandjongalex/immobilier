from django.test import SimpleTestCase
from django.urls import reverse


class HealthTests(SimpleTestCase):
    def test_liveness(self):
        response = self.client.get(reverse("health"))
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
