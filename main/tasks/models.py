from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class TimeBlock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="time_blocks")
    name = models.CharField(max_length=50, help_text="A short name for the time block.")
    start_time = models.DateTimeField(help_text="When this time block starts.")
    end_time = models.DateTimeField(help_text="When this time block ends.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"


class Task(models.Model):
    PRIORITY_CHOICES = [
        (1, "Important and Urgent"),
        (2, "Important but Not Urgent (Schedule)"),
        (3, "Urgent but Not Important (Delegate)"),
        (4, "Neither Important Nor Urgent (Eliminate)"),
    ]

    TASK_TYPES = [
        (1, "Work"),
        (2, "School"),
        (3, "Personal"),
        (4, "Routine"),
        (5, "Chores"),
        (6, "Hobby"),
        (7, "Other"),
    ]

    PROGRESS_CHOICES = [
        (1, "Not Started"),
        (2, "In Progress"),
        (3, "On Hold"),
        (4, "Completed"),
    ]

    # Task Owner and Time Block
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    time_block = models.ForeignKey(
        TimeBlock, on_delete=models.CASCADE, related_name="tasks", null=True, blank=True
    )

    # Task Details
    name = models.CharField(max_length=255, help_text="The name of the task.")
    description = models.TextField(blank=True, help_text="Details about the task.")
    start_date = models.DateField(
        null=True, blank=True, help_text="The date when the task should start."
    )
    due_date = models.DateField(
        null=True, blank=True, help_text="The date by which the task should be completed."
    )

    # Task Priority, Type, and Progress
    priority = models.PositiveSmallIntegerField(
        choices=PRIORITY_CHOICES, default=2, help_text="Priority of the task."
    )
    task_type = models.PositiveSmallIntegerField(
        choices=TASK_TYPES, default=1, help_text="Type of task."
    )
    progress = models.PositiveSmallIntegerField(
        choices=PROGRESS_CHOICES, default=1, help_text="Progress of the task."
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
    
    def __str__(self):
        return self.name