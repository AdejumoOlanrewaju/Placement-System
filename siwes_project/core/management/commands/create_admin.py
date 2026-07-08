from django.core.management.base import BaseCommand
from core.models import User


class Command(BaseCommand):
    help = 'Create an admin user for the SIWES system'

    def add_arguments(self, parser):
        parser.add_argument('--username',  type=str, required=True)
        parser.add_argument('--email',     type=str, required=True)
        parser.add_argument('--password',  type=str, required=True)
        parser.add_argument('--firstname', type=str, default='Admin')
        parser.add_argument('--lastname',  type=str, default='User')

    def handle(self, *args, **options):
        username = options['username']

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User "{username}" already exists.'))
            return

        user = User.objects.create_superuser(
            username   = username,
            email      = options['email'],
            password   = options['password'],
            first_name = options['firstname'],
            last_name  = options['lastname'],
            role       = 'admin',
        )

        self.stdout.write(self.style.SUCCESS(
            f'Admin "{user.username}" created successfully.'
        ))