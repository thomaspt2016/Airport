from django.db import models

class Airport(models.Model):
    code = models.CharField(max_length=3, unique=True, help_text="3-letter IATA airport code")
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Route(models.Model):
    start_airport = models.ForeignKey(Airport, related_name='departures', on_delete=models.CASCADE)
    end_airport = models.ForeignKey(Airport, related_name='arrivals', on_delete=models.CASCADE)
    direction = models.CharField(max_length=10, choices=[('left', 'Left'), ('right', 'Right')])
    distance_km = models.IntegerField(help_text="Distance in kilometers")
    duration_minutes = models.IntegerField(help_text="Duration in minutes")

    def __str__(self):
        return f"Route from {self.start_airport} to {self.end_airport}"