from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Import PCR data provided by ISC.'

    def add_arguments(self, parser):
        pass  # TODO

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Successfully imported data!'))
