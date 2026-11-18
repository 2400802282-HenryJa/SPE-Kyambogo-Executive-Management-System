from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = "Re-apply role rules (admin access and Top Executives group) to every user."

    def handle(self, *args, **options):
        count = 0
        for user in User.objects.all():
            user.save()
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Roles synced for {count} users."))
