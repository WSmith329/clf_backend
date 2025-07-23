import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path
from django.contrib.auth.decorators import login_required

from fitness.views import client, staff

urlpatterns = [
    path('', login_required(client.index), name='index'),
    path('all-workouts/', login_required(client.all_workouts), name='all_workouts'),
    path('workout/<str:workout_slug>/', login_required(client.workout), name='workout'),
    path('history/', login_required(client.completed_sessions), name='completed_sessions'),
    path('history/<int:session_id>', login_required(client.completed_session), name='completed_session'),
    path('completed-chart/', login_required(client.completed_chart), name='completed_chart'),
    path('calendar/<int:year>/<int:month>', login_required(client.monthly_calendar), name='calendar'),
    path(f'calendar/{datetime.datetime.today().year}/{datetime.datetime.today().month}',
         login_required(client.monthly_calendar), name='default_calendar'),
    path(f'calendar/<int:year>/<int:month>/<int:user_id>', login_required(client.monthly_calendar), name='user_calendar'),

    path('manage-exercises/', staff_member_required(staff.manage_exercises), name='manage_exercises'),
    path('create-exercise/', staff_member_required(staff.create_exercise), name='create_exercise'),
    path('update-exercise/<int:pk>/', staff_member_required(staff.create_exercise), name='update_exercise'),
    path('delete-exercise/<int:pk>/', staff_member_required(staff.delete_exercise), name='delete_exercise'),

    path('manage-workouts/', staff_member_required(staff.manage_workouts), name='manage_workouts'),
    path('create-workout/', staff_member_required(staff.create_workout), name='create_workout'),
    path('update-workout/<int:pk>/', staff_member_required(staff.create_workout), name='update_workout'),
    path('delete-workout/<int:pk>/', staff_member_required(staff.delete_workout), name='delete_workout'),

    path('manage-workout-plans/', staff_member_required(staff.manage_workout_plans), name='manage_workout_plans'),
    path('create-workout-plan/', staff_member_required(staff.create_workout_plan), name='create_workout_plan'),
    path('update-workout-plan/<int:pk>/', staff_member_required(staff.create_workout_plan), name='update_workout_plan'),
    path('delete-workout-plan/<int:pk>/', staff_member_required(staff.delete_workout_plan), name='delete_workout_plan')
]
