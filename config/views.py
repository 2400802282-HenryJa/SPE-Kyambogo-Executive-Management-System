from django.contrib import messages
from django.shortcuts import redirect


def csrf_failure(request, reason=""):
    """Friendly recovery when a form/login page has expired, instead of a raw 403."""
    if request.user.is_authenticated:
        messages.warning(request, "That page had expired. Please try again.")
        return redirect("dashboard")
    messages.warning(request, "Your sign-in page had expired. Please sign in again.")
    return redirect("login")
