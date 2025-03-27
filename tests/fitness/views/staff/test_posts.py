import pytest

from django.urls import reverse

from config.factories.fitness import ExerciseFactory, WorkoutFactory
from fitness.models import Exercise, Workout, WorkoutAssignment, WorkoutPlan


@pytest.mark.parametrize('factory, activity', [
    pytest.param(ExerciseFactory, 'exercise', id='exercise'),
    pytest.param(WorkoutFactory, 'workout', id='workout')
])
@pytest.mark.parametrize('search_slice, narrows_queryset', [
    pytest.param(slice(None), True, id='exact-single'),
    pytest.param(slice(-1, None), True, id='partial-single'),
    pytest.param(slice(2, 5), False, id='partial-all'),
])
def test_manage_activities_post(factory, activity, search_slice, narrows_queryset, staff_user_client, request):
    instance = request.getfixturevalue(activity)
    additional_instances = factory.create_batch(5)

    response = staff_user_client.post(
        path=reverse(f'manage_{activity}s'),
        data={f'{activity}_name': instance.name[search_slice]}
    )
    assert response.status_code == 200
    assert list(response.context[0].dicts[3][f'{activity}s']) == [instance] if narrows_queryset \
        else [instance]+additional_instances


@pytest.mark.parametrize('name_field', ['first_name', 'last_name'])
def test_manage_plans_post(name_field, staff_user_client, workout_plan):
    response = staff_user_client.post(
        path=reverse(f'manage_workout_plans'),
        data={'client_name': getattr(workout_plan.client.user, name_field)}
    )
    assert response.status_code == 200
    assert list(response.context[0].dicts[3]['workout_plans']) == [workout_plan]


def test_exercise_post(staff_user_client, activity_category):
    form_inputs = {
        'name': ['Leg Press'],
        'description': [''],
        'categories': [str(activity_category.id)],
        'difficulty': ['MO'],
        'thumbnail': [''],
        'instructions': ['Push with legs until almost straight', 'Slowly bend knees back to chest'],
        'notes': [''],
        'video_url': ['https://www.youtube.com/watch?v=p5dCqF7wWUw']
    }

    response = staff_user_client.post(
        path=reverse(f'create_exercise'),
        data=form_inputs,
        follow=True
    )

    assert response.status_code == 200
    assert response.redirect_chain[0][0] == reverse('manage_exercises')

    assert Exercise.objects.count() == 1
    assert Exercise.objects.get(name='Leg Press')


def test_workout_post(staff_user_client, activity_category, exercise):
    form_inputs = {
        'name': ['Chest Workout'],
        'description': [''],
        'categories': [str(activity_category.id)],
        'difficulty': ['BA'],
        'thumbnail': [''],
        'exercises': [str(exercise.id)],
        'duration_0': ['1'],
        'duration_1': ['30']
    }

    response = staff_user_client.post(
        path=reverse(f'create_workout'),
        data=form_inputs,
        follow=True
    )

    assert response.status_code == 200
    assert response.redirect_chain[0][0] == reverse('manage_workouts')

    assert Workout.objects.count() == 1
    assert Workout.objects.get(name='Chest Workout')


def test_workout_plan_post(staff_user_client, business_client, workout):
    second_workout = WorkoutFactory()

    form_inputs = {
        'client': [business_client.pk],
        'workoutassignment_set-TOTAL_FORMS': ['2'],
        'workoutassignment_set-INITIAL_FORMS': ['0'],
        'workoutassignment_set-MIN_NUM_FORMS': ['0'],
        'workoutassignment_set-MAX_NUM_FORMS': ['1000'],
        'workoutassignment_set-0-workout': [workout.pk],
        'workoutassignment_set-0-weekday': ['0', '2'],
        'workoutassignment_set-0-id': [''],
        'workoutassignment_set-1-workout': [second_workout.pk],
        'workoutassignment_set-1-weekday': ['1', '4'],
        'workoutassignment_set-1-id': ['']
    }

    assert WorkoutAssignment.objects.count() == 0
    assert WorkoutPlan.objects.count() == 0

    response = staff_user_client.post(
        path=reverse(f'create_workout_plan'),
        data=form_inputs,
        follow=True
    )

    assert response.status_code == 200
    assert response.redirect_chain[0][0] == reverse('manage_workout_plans')

    assert WorkoutAssignment.objects.count() == 2
    assert WorkoutPlan.objects.count() == 1

    created_workout_plan = WorkoutPlan.objects.get(client=business_client.pk)
    assert list(created_workout_plan.workouts.all()) == [workout, second_workout]

    assert created_workout_plan.workoutassignment_set.get(workout=workout).weekday == [0, 2]
    assert created_workout_plan.workoutassignment_set.get(workout=second_workout).weekday == [1, 4]
