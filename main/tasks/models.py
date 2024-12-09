from django.db import models
from django.contrib.auth import get_user_model
from datetime import date
from django.db.models import Q
from django.utils.timezone import now

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
    
    def get_all_descendants(self):
        descendants = Task.objects.filter(
            Q(parent_task=self) | Q(parent_task__in=self.subtasks.all())
        )
        return descendants.distinct()

    def get_all_ancestors(self):
        """
        Recursively fetch all parent tasks (ancestors) of the current task.
        """
        ancestors = []
        current_task = self.parent_task
        while current_task is not None:
            ancestors.append(current_task)
            current_task = current_task.parent_task
        return ancestors
    
    @property
    def all_subtasks_count(self):
        return self.get_all_descendants().count()
    
    def all_finished_subtasks_count(self):
        return self.get_all_descendants().filter(is_finished = True ).count()
    
    def percentage_of_completion(self):
        total = self.all_subtasks_count
        
        if total == 0:
            return 0
        finished = self.all_finished_subtasks_count()
        percentage = (finished / total) * 100 if total > 0 else 0
        return round(percentage, 0)
    
    @property
    def progress(self):
        return f"{self.all_finished_subtasks_count()} / {self.all_subtasks_count}"
    
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
        
        if self.is_finished and self.finished_at is None:
            # Set `finished_at` to current time if marked as finished
            self.finished_at = now()
        elif not self.is_finished:
            # Clear `finished_at` if marked as unfinished
            self.finished_at = None
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
    start_time = models.TimeField(help_text="When this time block starts.")
    end_time = models.TimeField(help_text="When this time block ends.")
    recursion = models.PositiveSmallIntegerField(
        choices=RECURSION_CHOICES, default=1, help_text="Type of task."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def total_time(self):
        start = self.start_time.hour * 60 + self.start_time.minute
        end = self.end_time.hour * 60 + self.end_time.minute
        
        total = end - start
        hours = total // 60
        minutes = total % 60
        
        return f"{hours} hours {minutes} minutes"

    def __str__(self):
        start_time = self.start_time.strftime("%H:%M")
        end_time = self.end_time.strftime("%H:%M")

        return f"{self.task.title} ({self.total_time()})."

    def save(self, *args, **kwargs):
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time.")
        super().save(*args, **kwargs)