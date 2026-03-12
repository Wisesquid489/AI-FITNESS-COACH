from django.core.management.base import BaseCommand
from aifitnesscoach_app.views import cleanup_old_workout_images


class Command(BaseCommand):
    help = 'Delete workout images older than specified days to save storage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Number of days to keep (default: 1)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Showing what would be deleted (older than {days} days)...')
            )
        else:
            self.stdout.write(f'Starting cleanup of workout images older than {days} days...')
        
        result = cleanup_old_workout_images(days=days, dry_run=dry_run)
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would delete {result["deleted"]} images, {result["errors"]} errors'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {result["deleted"]} images, {result["errors"]} errors'
                )
            )

