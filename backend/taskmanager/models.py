from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]
    
    STATUS_CHOICES = [
        ('Upcoming', 'Upcoming'),
        ('Overdue', 'Overdue'),
        ('Completed', 'Completed'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Low', blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Upcoming', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")

    def save(self, *args, **kwargs):
        self.title = self.title.capitalize()
        super(Task, self).save(*args, **kwargs)

    
    def __str__(self):
        return f"{self.title} - {self.get_priority_display()}"

    class Meta:
        ordering = ['-due_date']