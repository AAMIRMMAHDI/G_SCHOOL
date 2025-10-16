from django.db import models
from django.conf import settings
from django.utils import timezone


class Schedule(models.Model):
    ZENG_CHOICES = (
        (1, 'Period 1'),
        (2, 'Period 2'),
        (3, 'Period 3'),
        (4, 'Period 4'),
        (5, 'All Periods'),
    )
    zeng = models.PositiveIntegerField(choices=ZENG_CHOICES, verbose_name="Period")
    start_time = models.TimeField(verbose_name="Start Time", null=True, blank=True)
    end_time = models.TimeField(verbose_name="End Time", null=True, blank=True)

    class Meta:
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"

    def __str__(self):
        if self.zeng == 5:
            return self.get_zeng_display()
        return f"{self.get_zeng_display()} ({self.start_time} - {self.end_time})"

    def is_active(self):
        if self.zeng == 5:
            return True
        now = timezone.localtime(timezone.now()).time()
        return self.start_time <= now <= self.end_time


class Class(models.Model):
    name = models.CharField(max_length=100, verbose_name="Class Name")

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    def __str__(self):
        return self.name


class Student(models.Model):
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students', verbose_name="Class")
    row_number = models.PositiveIntegerField(verbose_name="Row Number")
    first_name = models.CharField(max_length=50, verbose_name="First Name")
    last_name = models.CharField(max_length=50, verbose_name="Last Name")
    father_name = models.CharField(max_length=50, verbose_name="Father's Name")

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class ClassSchedule(models.Model):
    DAY_CHOICES = (
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
    )
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='schedules', verbose_name="Class")
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='class_schedules', verbose_name="Schedule")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='class_schedules', verbose_name="Teacher")
    day = models.CharField(max_length=3, choices=DAY_CHOICES, verbose_name="Day")
    subject = models.CharField(max_length=100, verbose_name="Subject", default="")
    unit = models.CharField(max_length=10, verbose_name="Unit", default="")
    is_split = models.BooleanField(default=False, verbose_name="Split Period")
    split_part = models.PositiveIntegerField(default=0, verbose_name="Split Part")  # 0: not split, 1: first half, 2: second half

    class Meta:
        verbose_name = "Class Schedule"
        verbose_name_plural = "Class Schedules"

    def __str__(self):
        if self.is_split:
            return f"{self.class_obj} - {self.schedule} - {self.get_day_display()} - {self.teacher} ({self.subject} - Part {self.split_part})"
        return f"{self.class_obj} - {self.schedule} - {self.get_day_display()} - {self.teacher} ({self.subject})"

    def is_active(self):
        today = timezone.now().strftime('%a')[:3]
        return self.day == today and (self.schedule.zeng == 5 or self.schedule.is_active())


class Attendance(models.Model):
    STATUS_CHOICES = (
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Late'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances', verbose_name="Student")
    class_schedule = models.ForeignKey(ClassSchedule, on_delete=models.CASCADE, related_name='attendances', verbose_name="Class Schedule")
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P', verbose_name="Status")
    date = models.DateField(auto_now_add=True, verbose_name="Date")

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"

    def __str__(self):
        return f"{self.student} - {self.get_status_display()} ({self.date})"
