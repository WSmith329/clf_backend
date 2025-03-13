import datetime

from django.shortcuts import render


def account(request):
    current_user = request.user
    return render(request, 'registration/account.html',
                  {'title': 'Your Account', 'user': current_user})


def dashboard(request):
    current_user = request.user

    title = f'{current_user.first_name} {current_user.last_name}' if current_user.first_name and current_user.last_name\
        else current_user.username

    today = datetime.date.today()

    return render(
        request,
        'core/dashboard.html',
        {
            'title': title,
            'user': current_user
        }
    )
