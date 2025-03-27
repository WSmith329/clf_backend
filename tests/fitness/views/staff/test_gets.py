import pytest

from django.urls import reverse

from fitness.models import Exercise, Workout, WorkoutPlan


@pytest.mark.parametrize('django_client, expected_status_code', [
    pytest.param('staff_user_client', 200, id='staff'),
    pytest.param('client_user_client', 302, id='client')
])
@pytest.mark.parametrize('path_name', [
    'manage_exercises', 'create_exercise',
    'manage_workouts', 'create_workout',
    'manage_workout_plans', 'create_workout_plan'
])
def test_get_create_and_manage_activity(django_client, expected_status_code, path_name, request):
    django_client = request.getfixturevalue(django_client)
    response = django_client.get(path=reverse(path_name))
    assert response.status_code == expected_status_code


@pytest.mark.parametrize('django_client, expected_status_code', [
    pytest.param('staff_user_client', 200, id='staff'),
    pytest.param('client_user_client', 302, id='client')
])
@pytest.mark.parametrize('path_name, activity, extra_data_fixture', [
    pytest.param('create_exercise', 'exercise', None, id='copy-exercise'),
    pytest.param('create_workout', 'workout', None, id='copy-workout'),
    pytest.param('create_workout_plan', 'workout_plan', 'workout_assignment_on_mondays', id='copy-workout-plan')
])
def test_get_copy_activity(django_client, expected_status_code, path_name, activity, extra_data_fixture, request):
    django_client = request.getfixturevalue(django_client)
    activity = request.getfixturevalue(activity)
    if extra_data_fixture:
        request.getfixturevalue(extra_data_fixture)
    response = django_client.get(reverse(path_name), {'copy_from': activity.pk})
    assert response.status_code == expected_status_code


@pytest.mark.parametrize('django_client, expected_status_code', [
    pytest.param('staff_user_client', 200, id='staff'),
    pytest.param('client_user_client', 302, id='client')
])
@pytest.mark.parametrize('path_name, existing_activity', [
    pytest.param('update_exercise', 'exercise'),
    pytest.param('update_workout', 'workout'),
    pytest.param('update_workout_plan', 'workout_plan')
])
def test_get_update_activity(django_client, expected_status_code, path_name, existing_activity, request):
    existing_activity = request.getfixturevalue(existing_activity)

    django_client = request.getfixturevalue(django_client)
    response = django_client.get(path=reverse(path_name, args=[existing_activity.id]))

    assert response.status_code == expected_status_code


@pytest.mark.parametrize('django_client, path_name, existing_activity, activity_class, redirct_path, expected_count', [
    pytest.param('staff_user_client', 'delete_exercise', 'exercise', Exercise, 'manage_exercises', 0),
    pytest.param('client_user_client', 'delete_exercise', 'exercise', Exercise, 'admin:login', 1),
    pytest.param('staff_user_client', 'delete_workout', 'workout', Workout, 'manage_workouts', 0),
    pytest.param('client_user_client', 'delete_workout', 'workout', Workout, 'admin:login', 1),
    pytest.param('staff_user_client', 'delete_workout_plan', 'workout_plan', WorkoutPlan,
                 'manage_workout_plans', 0),
    pytest.param('client_user_client', 'delete_workout_plan', 'workout_plan', WorkoutPlan,
                 'admin:login', 1)
])
def test_get_delete_activity(django_client, path_name, existing_activity, activity_class, redirct_path,
                             expected_count, request):
    existing_activity = request.getfixturevalue(existing_activity)

    assert activity_class.objects.count() == 1

    django_client = request.getfixturevalue(django_client)
    response = django_client.get(path=reverse(path_name, args=[existing_activity.id]), follow=True)

    assert response.status_code == 200
    assert response.redirect_chain[0][0].startswith(reverse(redirct_path))

    assert activity_class.objects.count() == expected_count
