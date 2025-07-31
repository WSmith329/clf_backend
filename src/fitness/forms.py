from django import forms
from django.forms import MultiWidget, DateInput, inlineformset_factory
from durationwidget.widgets import TimeDurationWidget

from common.widgets.json import ListTextInputWidget
from .models import Workout, WorkoutSession, Steps, Weekday, WorkoutAssignment, CompletedSteps, WorkoutPlan, Exercise, \
    WorkoutExercise, Set


class MultiDateInputWidget(MultiWidget):
    def __init__(self, attrs=None):
        widgets = [DateInput(attrs={'type': 'date', 'class': 'date-input'})]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value
        return [None]


class ExerciseForm(forms.ModelForm):
    instructions = forms.JSONField(widget=ListTextInputWidget())

    class Meta:
        model = Exercise
        fields = '__all__'


class WorkoutForm(forms.ModelForm):
    duration = forms.DurationField(widget=TimeDurationWidget(
        show_days=False, show_hours=True, show_minutes=True, show_seconds=False
    ), required=False)

    class Meta:
        model = Workout
        fields = '__all__'
        exclude = ['slug', 'exercises', 'thumbnail']


class WorkoutExerciseForm(forms.ModelForm):
    class Meta:
        model = WorkoutExercise
        fields = ['exercise']


SetFormSet = inlineformset_factory(
    WorkoutExercise,
    Set,
    fields=['reps', 'until_failure', 'weight_level'],
    extra=1,
    can_delete=True
)


class WorkoutPlanForm(forms.ModelForm):
    class Meta:
        model = WorkoutPlan
        fields = ['client']


class WorkoutAssignmentForm(forms.ModelForm):
    weekday = forms.MultipleChoiceField(
        choices=Weekday.choices,
        widget=forms.CheckboxSelectMultiple
    )

    def clean_weekday(self):
        data = self.cleaned_data['weekday']
        return [int(day) for day in data]

    class Meta:
        model = WorkoutAssignment
        fields = '__all__'


WorkoutAssignmentFormSet = inlineformset_factory(
    WorkoutPlan,
    WorkoutAssignment,
    fields=('workout', 'weekday', 'exact_dates'),
    form=WorkoutAssignmentForm,
    extra=1,
    can_delete=True
)


class WorkoutSessionForm(forms.ModelForm):
    class Meta:
        model = WorkoutSession
        fields = ['completed_by']


class StepsForm(forms.ModelForm):
    weekday = forms.MultipleChoiceField(
        choices=Weekday.choices,
        widget=forms.CheckboxSelectMultiple
    )

    def clean_weekday(self):
        data = self.cleaned_data['weekday']
        return [int(day) for day in data]

    class Meta:
        model = Steps
        fields = '__all__'


class CompletedStepsForm(forms.ModelForm):
    class Meta:
        model = CompletedSteps
        fields = ['completed']
