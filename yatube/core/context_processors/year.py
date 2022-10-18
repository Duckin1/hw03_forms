from django.utils import timezone


def year(request):
    date_year = timezone.now().year
    return {
        'year': date_year
    }
