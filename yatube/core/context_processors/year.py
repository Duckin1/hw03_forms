from datetime import datetime


def year(request):
    date_year = datetime.now().year
    return {
        'year': date_year
    }
