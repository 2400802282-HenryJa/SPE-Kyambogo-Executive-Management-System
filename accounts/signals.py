from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User
from .roles import TOP_EXEC_GROUP, ensure_top_exec_group


@receiver(post_save, sender=User)
def sync_top_exec_group(sender, instance, **kwargs):
    if instance.is_top_executive:
        instance.groups.add(ensure_top_exec_group())
    else:
        group = Group.objects.filter(name=TOP_EXEC_GROUP).first()
        if group:
            instance.groups.remove(group)
