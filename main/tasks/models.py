from django.db import models
from django.contrib.auth import get_user_model
from datetime import date


User = get_user_model()

class Task(models.Model):
    URGENCY_CHOICES = [
        ('urgent', "Urgent"),
        ('soon', "Soon"),
        ('later', "Later"),
    ]
    
    PRIORITY_CHOICES = [
        ('high', "High Priority"),
        ('medium', "Medium Priority"),
        ('low', "Low Priority"),
    ]

    PROGRESS_CHOICES = [
        ('not_started', "Not Started"),
        ('in_progress', "In Progress"),
        ('paused', "Paused"),
        ('completed', "Completed"),
    ]

    # Task Owner and Time Block
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")

    # Task Details
    title = models.CharField(max_length=100, help_text="Title of the task.")
    description = models.TextField(blank=True, help_text="Details about the task.")
    start_date = models.DateField(
        null=True, blank=True, help_text="The date when the task should start."
    )
    due_date = models.DateField(
        null=True, blank=True, help_text="The date by which the task should be completed."
    )

    # Task Priority, Type, and Progress
    urgency = models.CharField(
        max_length=10, 
        choices=URGENCY_CHOICES, 
        default="soon", 
        help_text="Urgency of the task."
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="important",
        help_text="Importance of the task.",
    )
    
    progress = models.CharField(
        max_length=12,
        choices=PROGRESS_CHOICES, 
        default='not_started', 
        help_text="Progress of the task."
    )

    # Task Nesting
    parent_task = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subtasks",
        help_text="Parent task for subtasks, if any.",
    )

    # Task Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def days_until_due(self):
        today = date.today()
        due_date = self.due_date
        
        if due_date:
            time_until_due = due_date - today
            return time_until_due.days
        return None
    
    def __str__(self):
        return f"{self.title} (Due in {self.days_until_due()} days)."
    
    def save(self, *args, **kwargs):
        if self.start_date and self.due_date:
            if self.start_date > self.due_date:
                raise ValueError("Start date must be before due date.")
        super().save(*args, **kwargs)

class TimeBlock(models.Model):
    RECURSION_CHOICES = [
        (1, "Daily"),
        (2, "Weekly"),
        (3, "Monthly"),
        (4, "Yearly"),
        (5, "Once"),
    ]
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="time_block")
    start_time = models.DateTimeField(help_text="When this time block starts.")
    end_time = models.DateTimeField(help_text="When this time block ends.")
    recursion = models.PositiveSmallIntegerField(
        choices=RECURSION_CHOICES, default=1, help_text="Type of task."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"