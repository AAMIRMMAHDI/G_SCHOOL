# models.py کامل اصلاح‌شده (family_info و achievements به TextField عوض شدن، بدون JSONField)
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

class Schedule(models.Model):
    """مدل برای تعریف زنگ‌های کلاسی"""
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
        verbose_name_plural = "زنگ"
        indexes = [
            models.Index(fields=['zeng']),
        ]

    def __str__(self):
        if self.zeng == 5:
            return self.get_zeng_display()
        return f"{self.get_zeng_display()} ({self.start_time} - {self.end_time})"

    def is_active(self):
        """بررسی فعال بودن زنگ بر اساس زمان فعلی"""
        if self.zeng == 5:
            return True
        now = timezone.localtime(timezone.now()).time()
        return self.start_time <= now <= self.end_time


class Class(models.Model):
    """مدل برای تعریف کلاس‌ها"""
    name = models.CharField(max_length=100, verbose_name="Class Name")
    major = models.ForeignKey('Major', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="رشته")
    grade_level = models.ForeignKey('GradeLevel', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="پایه تحصیلی")

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "کلاس"
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def has_capacity(self):
        return self.students.count() < 20


class Student(models.Model):
    """مدل برای تعریف دانش‌آموزان"""
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students', verbose_name="Class")
    row_number = models.PositiveIntegerField(verbose_name="Row Number")
    first_name = models.CharField(max_length=50, verbose_name="First Name")
    last_name = models.CharField(max_length=50, verbose_name="Last Name")
    father_name = models.CharField(max_length=50, verbose_name="Father's Name")

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "دانش آموز"
        indexes = [
            models.Index(fields=['first_name', 'last_name']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class ClassSchedule(models.Model):
    """مدل برای تعریف برنامه کلاسی"""
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
        verbose_name_plural = "کلاس های فعال"
        indexes = [
            models.Index(fields=['class_obj', 'schedule', 'day']),
        ]

    def clean(self):
        """اعتبارسنجی یکپارچگی داده‌ها"""
        if self.is_split and self.split_part not in [1, 2]:
            raise ValidationError("برای زنگ‌های تقسیم‌شده، split_part باید 1 یا 2 باشد.")
        if not self.is_split and self.split_part != 0:
            raise ValidationError("برای زنگ‌های غیرتقسیم‌شده، split_part باید 0 باشد.")

    def __str__(self):
        if self.is_split:
            return f"{self.class_obj} - {self.schedule.get_zeng_display()} - {self.get_day_display()} - {self.teacher} ({self.subject} - Part {self.split_part})"
        return f"{self.class_obj} - {self.schedule.get_zeng_display()} - {self.get_day_display()} - {self.teacher} ({self.subject})"

    def is_active(self):
        """بررسی فعال بودن برنامه کلاسی"""
        today = timezone.now().strftime('%a')[:3]
        return self.day == today and (self.schedule.zeng == 5 or self.schedule.is_active())


class Attendance(models.Model):
    """مدل برای ثبت حضور و غیاب"""
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
        verbose_name_plural = "حضور"
        indexes = [
            models.Index(fields=['student', 'date']),
        ]

    def __str__(self):
        return f"{self.student} - {self.get_status_display()} ({self.date})"


class Major(models.Model):
    """مدل برای رشته‌های تحصیلی"""
    name = models.CharField(max_length=100, verbose_name="نام رشته")

    class Meta:
        verbose_name = "رشته"
        verbose_name_plural = "رشته‌ها"

    def __str__(self):
        return self.name


class GradeLevel(models.Model):
    """مدل برای پایه‌های تحصیلی"""
    name = models.CharField(max_length=50, verbose_name="نام پایه")

    class Meta:
        verbose_name = "پایه تحصیلی"
        verbose_name_plural = "پایه"

    def __str__(self):
        return self.name


class Exam(models.Model):
    """مدل برای آزمون‌ها"""
    title = models.CharField(max_length=200, verbose_name="عنوان آزمون")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exams', verbose_name="معلم")
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='exams', verbose_name="کلاس")
    major = models.ForeignKey(Major, on_delete=models.SET_NULL, null=True, verbose_name="رشته")
    grade_level = models.ForeignKey(GradeLevel, on_delete=models.SET_NULL, null=True, verbose_name="پایه تحصیلی")
    duration = models.PositiveIntegerField(verbose_name="مدت زمان (دقیقه)", help_text="زمان آزمون به دقیقه")
    start_time = models.DateTimeField(verbose_name="زمان شروع", default=timezone.now)
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "آزمون"
        verbose_name_plural = "آزمون"
        indexes = [
            models.Index(fields=['teacher', 'class_obj']),
        ]

    def __str__(self):
        return f"{self.title} - {self.class_obj}"

    def is_ongoing(self):
        """بررسی اینکه آزمون در حال برگزاری است"""
        now = timezone.now()
        end_time = self.start_time + timezone.timedelta(minutes=self.duration)
        return self.start_time <= now <= end_time and self.is_active


class Question(models.Model):
    """مدل برای سوالات آزمون"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions', verbose_name="آزمون")
    text = models.TextField(verbose_name="متن سوال")
    option1 = models.CharField(max_length=200, verbose_name="گزینه ۱")
    option2 = models.CharField(max_length=200, verbose_name="گزینه ۲")
    option3 = models.CharField(max_length=200, verbose_name="گزینه ۳")
    option4 = models.CharField(max_length=200, verbose_name="گزینه ۴")
    correct_option = models.PositiveIntegerField(choices=((1, 'گزینه ۱'), (2, 'گزینه ۲'), (3, 'گزینه ۳'), (4, 'گزینه ۴')), verbose_name="گزینه درست")

    class Meta:
        verbose_name = "سوال"
        verbose_name_plural = "سوالات"
        ordering = ['id']

    def __str__(self):
        return f"سوال {self.id} از {self.exam}"


class StudentAnswer(models.Model):
    """مدل برای پاسخ‌های دانش‌آموزان"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='answers', verbose_name="دانش‌آموز")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name="سوال")
    selected_option = models.PositiveIntegerField(verbose_name="گزینه انتخاب‌شده")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ارسال")

    class Meta:
        verbose_name = "پاسخ دانش‌آموز"
        verbose_name_plural = "پاسخ‌های دانش‌آموزان"
        unique_together = ('student', 'question')
        indexes = [
            models.Index(fields=['student', 'question']),
        ]

    def is_correct(self):
        return self.selected_option == self.question.correct_option


class Grade(models.Model):
    """مدل برای نمرات آزمون"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades', verbose_name="دانش‌آموز")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='grades', verbose_name="آزمون")
    score = models.FloatField(verbose_name="نمره", default=0)
    calculated_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان محاسبه")

    class Meta:
        verbose_name = "نمره"
        verbose_name_plural = "نمرات"
        unique_together = ('student', 'exam')

    def __str__(self):
        return f"{self.student} - {self.exam}: {self.score}"

class EntryPermission(models.Model):
    """مدل برای درخواست اجازه ورود دانش‌آموز دیرآمده"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='entry_permissions', verbose_name="دانش‌آموز")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='entry_permissions', verbose_name="معلم")
    reason = models.TextField(verbose_name="دلیل تأخیر", blank=True, null=True)
    date = models.DateField(default=timezone.now, verbose_name="تاریخ")
    time = models.TimeField(default=timezone.now, verbose_name="ساعت")
    approved = models.BooleanField(default=False, verbose_name="تأیید شده توسط معلم")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_permissions', verbose_name="ایجاد شده توسط")

    class Meta:
        verbose_name = "اجازه ورود"
        verbose_name_plural = "اجازه‌های ورود"
        indexes = [
            models.Index(fields=['student', 'date']),
        ]

    def __str__(self):
        return f"اجازه ورود برای {self.student} به کلاس {self.teacher} در {self.date}"


class Notification(models.Model):
    """مدل برای نوتیفیکیشن‌ها"""
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications', verbose_name="گیرنده")
    message = models.TextField(verbose_name="پیام")
    related_permission = models.ForeignKey(EntryPermission, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications', verbose_name="مرتبط با اجازه ورود")
    is_read = models.BooleanField(default=False, verbose_name="خوانده شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")

    class Meta:
        verbose_name = "نوتیفیکیشن"
        verbose_name_plural = "نوتیفیکیشن‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return f"نوتیفیکیشن برای {self.recipient}: {self.message[:50]}"

class StudentRegistrationRequest(models.Model):
    STATUS_CHOICES = (
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
    )
    first_name = models.CharField(max_length=50, verbose_name="نام")
    last_name = models.CharField(max_length=50, verbose_name="نام خانوادگی")
    nickname = models.CharField(max_length=50, blank=True, null=True, verbose_name="نام مستعار")
    father_name = models.CharField(max_length=50, verbose_name="نام پدر")
    birth_day = models.PositiveIntegerField(verbose_name="روز تولد")
    birth_month = models.PositiveIntegerField(verbose_name="ماه تولد")
    birth_year = models.PositiveIntegerField(verbose_name="سال تولد")
    national_code = models.CharField(max_length=10, verbose_name="کد ملی")
    family_type = models.TextField(blank=True, verbose_name="نوع خانواده")  # e.g., "azadeh,janbaz"
    children_count = models.PositiveIntegerField(default=0, verbose_name="تعداد فرزندان")
    boys_count = models.PositiveIntegerField(default=0, verbose_name="تعداد پسر")
    girls_count = models.PositiveIntegerField(default=0, verbose_name="تعداد دختر")
    child_order = models.PositiveIntegerField(default=1, verbose_name="ترتیب فرزند")
    family_info = models.TextField(blank=True, verbose_name="اطلاعات خانواده")  # string ساده، مثل "پدر: نام,نام خانوادگی,کد ملی,شغل,شماره; مادر: ..."
    province = models.CharField(max_length=100, verbose_name="استان")
    county = models.CharField(max_length=100, verbose_name="شهرستان")
    city = models.CharField(max_length=100, verbose_name="شهر")
    postal_code = models.CharField(max_length=10, verbose_name="کد پستی")
    home_phone = models.CharField(max_length=15, blank=True, verbose_name="شماره منزل")
    father_education = models.CharField(max_length=100, blank=True, verbose_name="تحصیلات پدر")
    mother_education = models.CharField(max_length=100, blank=True, verbose_name="تحصیلات مادر")
    father_phone = models.CharField(max_length=15, blank=True, verbose_name="شماره پدر")
    mother_phone = models.CharField(max_length=15, blank=True, verbose_name="شماره مادر")
    address = models.TextField(blank=True, verbose_name="آدرس")
    interests_morning = models.TextField(blank=True, verbose_name="علاقه‌مندی صبحگاهی")
    interests_prayer = models.TextField(blank=True, verbose_name="علاقه‌مندی نماز")
    interests_art = models.TextField(blank=True, verbose_name="علاقه‌مندی هنری")
    competitions_quran = models.TextField(blank=True, verbose_name="مسابقات قرآن")
    competitions_sport = models.TextField(blank=True, verbose_name="مسابقات ورزشی")
    achievements = models.TextField(blank=True, verbose_name="عناوین کسب شده")  # string ساده، مثل "عنوان1,رتبه1,سطح1; عنوان2,رتبه2,سطح2"
    other_skills = models.TextField(blank=True, verbose_name="سایر مهارت‌ها")
    diseases = models.TextField(blank=True, verbose_name="بیماری‌های خاص")
    major = models.ForeignKey(Major, on_delete=models.SET_NULL, null=True, verbose_name="رشته")
    grade_level = models.ForeignKey(GradeLevel, on_delete=models.SET_NULL, null=True, verbose_name="پایه تحصیلی")
    report_card_image = models.ImageField(upload_to='report_cards/', verbose_name="عکس کارنامه")
    class_assigned = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="کلاس割り当て شده")  # ادمین انتخاب کنه
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P', verbose_name="وضعیت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    notes = models.TextField(blank=True, null=True, verbose_name="یادداشت ادمین")

    class Meta:
        verbose_name = "درخواست ثبت نام دانش‌آموز"
        verbose_name_plural = "درخواست‌های ثبت نام"

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_status_display()}"