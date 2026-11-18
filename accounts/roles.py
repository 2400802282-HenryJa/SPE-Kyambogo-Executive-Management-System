from django.contrib.auth.models import Group, Permission

TOP_EXEC_GROUP = "Top Executives"

# Add an app label here when a new module is built so the top executives
# automatically get permissions for it in the admin site.
APP_LABELS = ["accounts", "departments", "projects", "programmes", "contacts", "resources"]


def ensure_top_exec_group():
    group, _ = Group.objects.get_or_create(name=TOP_EXEC_GROUP)
    perms = Permission.objects.filter(content_type__app_label__in=APP_LABELS)
    group.permissions.set(perms)
    return group
