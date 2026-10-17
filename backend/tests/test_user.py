import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_user_uses_email_and_uuid():
    user = get_user_model().objects.create_user("bailleur@example.test", "temporary-pass")
    assert user.email == "bailleur@example.test"
    assert len(str(user.pk)) == 36
    assert user.check_password("temporary-pass")
