from rest_framework import exceptions, status
from researchdt.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _

class InvalidCredentials(AuthenticationFailed):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("Invalid email or password")
    default_code = "bad_credentials"