
from django.utils import timezone
from users.models import Visitor

def visitors_count(request):
    # Get the current date
    current_date = timezone.now().date()

    # Filter visitors for the current day and count them
    visitors_count_today = Visitor.objects.filter(created_at__date=current_date).count()

    return {'visitors_count': visitors_count_today}