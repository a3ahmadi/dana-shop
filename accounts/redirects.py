from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme


def safe_next_url(request, target):
    if isinstance(target, str) and target.startswith("/") and not target.startswith("//"):
        if url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return target
    return reverse("storefront:home")
