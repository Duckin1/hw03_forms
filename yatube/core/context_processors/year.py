from datetime import datetime

from django import forms


def year(request):
    date_year = datetime.now().year
    return {
       'year': date_year
    }
