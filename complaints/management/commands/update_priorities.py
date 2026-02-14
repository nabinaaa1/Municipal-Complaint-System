from django.core.management.base import BaseCommand
from complaints.models import Complaint
from django.utils import timezone

class Command(BaseCommand):
    help = 'Auto-update complaint priorities for complaints older than 7 days'

    def handle(self, *args, **kwargs):
        # Get all non-resolved complaints
        complaints = Complaint.objects.filter(status__in=['Pending', 'In Progress'])
        
        updated_count = 0
        for complaint in complaints:
            if complaint.update_priority():
                updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated_count} complaints to Urgent priority'
            )
        )