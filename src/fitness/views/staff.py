from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from fitness.forms import ExerciseForm, WorkoutForm, WorkoutPlanForm, WorkoutAssignmentFormSet, WorkoutExerciseForm, \
    SetFormSet
from fitness.models import Exercise, Workout, WorkoutPlan, WorkoutExercise


def create_exercise(request, pk=None):
    exercise = get_object_or_404(Exercise, pk=pk) if pk else None
    is_new = exercise is None

    copied_m2m = {}
    if is_new and (copy_from_pk := request.GET.get('copy_from')):
        original = get_object_or_404(Exercise, pk=copy_from_pk)
        exercise = Exercise()
        for field in Exercise._meta.fields:
            if field.name not in ('id',):  # skip PK
                setattr(exercise, field.name, getattr(original, field.name))
        copied_m2m['categories'] = original.categories.all()

    if request.method == 'POST':
        exercise_form = ExerciseForm(request.POST, instance=exercise)

        if exercise_form.is_valid():
            exercise_form.save()
            messages.success(
                request,
                f'Created {exercise_form.instance.name}' if is_new else f'Updated {exercise_form.instance.name}'
            )
            return redirect('manage_exercises')

    else:
        exercise_form = ExerciseForm(instance=exercise, initial=copied_m2m)

    return render(request, 'fitness/create_exercise.html', {
        'title': 'Create a new exercise' if not exercise else 'Update exercise',
        'exercise_form': exercise_form
    })


def create_workout(request, pk=None):
    workout = get_object_or_404(Workout, pk=pk) if pk else None
    is_new = workout is None

    copied_m2m = {}
    if is_new and (copy_from_pk := request.GET.get('copy_from')):
        original = get_object_or_404(Workout, pk=copy_from_pk)
        workout = Workout()
        for field in Workout._meta.fields:
            if field.name not in ('id',):  # skip PK
                setattr(workout, field.name, getattr(original, field.name))
        copied_m2m['categories'] = original.categories.all()
        copied_m2m['exercises'] = original.exercises.all()

    if request.method == 'POST':
        workout_form = WorkoutForm(request.POST, instance=workout)

        if workout_form.is_valid():
            workout_form.save()
            messages.success(
                request,
                f'Created {workout_form.instance.name}' if is_new else f'Updated {workout_form.instance.name}'
            )

            if 'submit_and_add_another' in request.POST:
                return redirect('add_exercise_to_workout', workout_id=workout.id)
            elif 'submit_and_exit' in request.POST:
                return redirect('manage_workouts')

    else:
        workout_form = WorkoutForm(instance=workout, initial=copied_m2m)

    return render(request, 'fitness/create_workout.html', {
        'title': 'Create a new workout' if is_new else 'Update workout',
        'workout_form': workout_form
    })


def add_exercise_to_workout(request, workout_pk, workout_exercise_pk=None):
    workout = get_object_or_404(Workout, pk=workout_pk)
    workout_exercise = get_object_or_404(WorkoutExercise, pk=workout_exercise_pk) if workout_exercise_pk else None

    if request.method == 'POST':
        exercise_form = WorkoutExerciseForm(request.POST, instance=workout_exercise)
        set_formset = SetFormSet(request.POST, instance=workout_exercise)

        if exercise_form.is_valid() and set_formset.is_valid():
            workout_exercise = exercise_form.save(commit=False)
            workout_exercise.workout = workout
            workout_exercise.save()

            sets = set_formset.save(commit=False)
            for set in sets:
                set.workout_exercise = workout_exercise
                set.save()

            if 'submit_and_add_another' in request.POST:
                return redirect('add_exercise_to_workout', workout_id=workout.id)
            elif 'submit_and_exit' in request.POST:
                manage_workouts_url = reverse('manage_workouts')
                return redirect(f'{manage_workouts_url}?expand={workout.pk}')

    else:
        exercise_form = WorkoutExerciseForm(instance=workout_exercise)
        set_formset = SetFormSet(instance=workout_exercise)

    existing_exercises = WorkoutExercise.objects.filter(workout=workout).prefetch_related('set_set')

    return render(request, 'fitness/add_exercise.html', {
        'title': f'Add Exercise to {workout.name}',
        'workout': workout,
        'exercise_form': exercise_form,
        'set_formset': set_formset,
        'existing_exercises': existing_exercises
    })


def create_workout_plan(request, pk=None):
    workout_plan = get_object_or_404(WorkoutPlan, pk=pk) if pk else None
    is_new = workout_plan is None

    copied_assignments = []
    if is_new and (copy_from_pk := request.GET.get('copy_from')):
        original = get_object_or_404(WorkoutPlan, pk=copy_from_pk)
        workout_plan = WorkoutPlan()
        for field in WorkoutPlan._meta.fields:
            if field.name not in ('id',):  # skip PK
                setattr(workout_plan, field.name, getattr(original, field.name))

        original_assignments = original.workoutassignment_set.all()
        for assignment in original_assignments:
            assignment_data = {}
            for field in assignment._meta.fields:
                if field.name not in ('id', 'workout_plan'):  # skip PK and FK
                    assignment_data[field.name] = getattr(assignment, field.name)
            copied_assignments.append(assignment_data)

    if request.method == 'POST':
        workout_plan_form = WorkoutPlanForm(request.POST, instance=workout_plan)
        workout_assignment_formset = WorkoutAssignmentFormSet(request.POST, instance=workout_plan)

        if workout_plan_form.is_valid() and workout_assignment_formset.is_valid():
            workout_plan = workout_plan_form.save()
            assignments = workout_assignment_formset.save(commit=False)
            for assignment in assignments:
                assignment.workout_plan = workout_plan
                assignment.save()
            workout_assignment_formset.save_m2m()
            messages.success(request, f'Created workout plan' if is_new else f'Updated workout plan')
            return redirect('manage_workout_plans')

    else:
        workout_plan_form = WorkoutPlanForm(instance=workout_plan)
        workout_assignment_formset = WorkoutAssignmentFormSet(
            instance=workout_plan,
            initial=copied_assignments if copied_assignments else None
        )

    return render(request, 'fitness/create_workout_plan.html', {
        'title': 'Create a new workout plan' if is_new else 'Update workout plan',
        'workout_plan_form': workout_plan_form,
        'workout_assignment_formset': workout_assignment_formset
    })


def _manage_activities(request, model, template_name, search_field_name, context_key, title, activity,
                       custom_query_fn=None, **kwargs):
    search_query = request.POST.get(search_field_name, '').strip()

    if custom_query_fn:
        activities = custom_query_fn(search_query) if search_query else model.objects.all()
    else:
        activities = model.objects.filter(name__icontains=search_query) if search_query else model.objects.all()

    return render(request, template_name, {
        'title': title,
        context_key: activities,
        f'searched_{context_key[:-1]}': search_query,
        'activity': activity,
        **kwargs
    })


def manage_workout_plans(request):
    return _manage_activities(
        request,
        model=WorkoutPlan,
        template_name='fitness/manage_workout_plans.html',
        search_field_name='client_name',
        context_key='workout_plans',
        title='Manage workout plans',
        activity='workout_plans',
        custom_query_fn=WorkoutPlan.objects.get_by_client_name
    )


def manage_workouts(request):
    if expand := request.GET.get('expand'):
        expand = int(expand)

    return _manage_activities(
        request,
        model=Workout,
        template_name='fitness/manage_workouts.html',
        search_field_name='workout_name',
        context_key='workouts',
        title='Manage workouts',
        activity='workouts',
        expand=expand
    )


def manage_exercises(request):
    return _manage_activities(
        request,
        model=Exercise,
        template_name='fitness/manage_exercises.html',
        search_field_name='exercise_name',
        context_key='exercises',
        title='Manage exercises',
        activity='exercises'
    )


def _delete_activity(request, model, pk, success_message, redirect_url):
    instance = get_object_or_404(model, pk=pk)
    instance.delete()
    messages.success(request, success_message)
    return redirect(redirect_url)


def delete_workout_plan(request, pk):
    return _delete_activity(
        request,
        model=WorkoutPlan,
        pk=pk,
        success_message='Workout plan successfully deleted.',
        redirect_url='manage_workout_plans'
    )


def delete_workout(request, pk):
    return _delete_activity(
        request,
        model=Workout,
        pk=pk,
        success_message='Workout successfully deleted.',
        redirect_url='manage_workouts'
    )


def delete_exercise(request, pk):
    return _delete_activity(
        request,
        model=Exercise,
        pk=pk,
        success_message='Exercise successfully deleted.',
        redirect_url='manage_exercises'
    )


def delete_workout_exercise(request, pk):
    manage_workouts_url = reverse('manage_workouts')
    workout_pk = get_object_or_404(WorkoutExercise, pk=pk).workout.pk

    return _delete_activity(
        request,
        model=WorkoutExercise,
        pk=pk,
        success_message='Exercise successfully removed from workout.',
        redirect_url=f'{manage_workouts_url}?expand={workout_pk}'
    )


def reorder_workout_exercise(request, pk, direction):
    workout_exercise = get_object_or_404(WorkoutExercise, pk=pk)
    workout_exercise.reorder(direction)
    manage_workouts_url = reverse('manage_workouts')
    return redirect(f'{manage_workouts_url}?expand={workout_exercise.workout.pk}')
