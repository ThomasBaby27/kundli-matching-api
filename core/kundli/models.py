from django.db import models

class BirthProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    time_of_birth = models.TimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_gender_display()})"


class MatchHistory(models.Model):
    male_profile = models.ForeignKey(
        BirthProfile, 
        on_delete=models.CASCADE, 
        related_name='male_matches'
    )
    female_profile = models.ForeignKey(
        BirthProfile, 
        on_delete=models.CASCADE, 
        related_name='female_matches'
    )
    compatibility_score = models.IntegerField()  
    verdict = models.CharField(max_length=20)     
    breakdown = models.JSONField()               
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('male_profile', 'female_profile')

    def __str__(self):
        return f"{self.male_profile.name} x {self.female_profile.name} - Score: {self.compatibility_score}/36"