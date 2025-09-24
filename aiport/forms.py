from django import forms
from .models import Route,Airport

class AirportRouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['start_airport', 'end_airport', 'direction', 'distance_km', 'duration_minutes']
        labels = {
            'direction': 'Position (Left or Right)',
            'distance_km': 'Distance (km)',
            'duration_minutes': 'Duration (minutes)',
        }
        widgets = {
            'direction': forms.Select(choices=[('left', 'Left'), ('right', 'Right')]),
        }

class AirportForm(forms.ModelForm):
    class Meta:
        model = Airport
        fields = ['code', 'name']
        labels = {
            'code': 'Airport Code',
            'name': 'Airport Name',
        }