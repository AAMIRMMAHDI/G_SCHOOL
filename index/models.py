from django.db import models
from django.conf import settings
from django.utils import timezone

# ===========================
# رشته‌ها و ویژگی‌ها
# ===========================
class Major(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان رشته")
    description = models.TextField(verbose_name="توضیحات")
    image = models.ImageField(upload_to='majors/', verbose_name="تصویر رشته")
    icon = models.CharField(max_length=10, verbose_name="آیکون (ایموجی)", help_text="یک ایموجی مثل 📱 یا 💻 وارد کنید")
    subtitle = models.CharField(max_length=200, verbose_name="زیرعنوان")
    introduction = models.TextField(verbose_name="معرفی رشته")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "رشته تحصیلی"
        verbose_name_plural = "Fields of study"


class Feature(models.Model):
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='features', verbose_name="رشته")
    text = models.CharField(max_length=200, verbose_name="ویژگی")

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "ویژگی"
        verbose_name_plural = "ویژگی‌ها"


class Requirement(models.Model):
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='requirements', verbose_name="رشته")
    text = models.CharField(max_length=200, verbose_name="شرط ورود")

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "شرط ورود"
        verbose_name_plural = "شرایط ورود"


class Career(models.Model):
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='careers', verbose_name="رشته")
    text = models.CharField(max_length=200, verbose_name="شغل")

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "شغل"
        verbose_name_plural = "مشاغل"


class Skill(models.Model):
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='skills', verbose_name="رشته")
    text = models.CharField(max_length=200, verbose_name="مهارت")

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "مهارت"
        verbose_name_plural = "مهارت‌ها"


class Work(models.Model):
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='works', verbose_name="رشته")
    image = models.ImageField(upload_to='works/', verbose_name="تصویر نمونه‌کار")
    title = models.CharField(max_length=200, verbose_name="عنوان نمونه‌کار", blank=True)

    def __str__(self):
        return self.title or "نمونه‌کار"

    class Meta:
        verbose_name = "نمونه‌کار"
        verbose_name_plural = "نمونه‌کارها"


# ===========================
# اساتید
# ===========================
class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="کاربر")
    full_name = models.CharField(max_length=200, verbose_name="نام کامل")
    specialty = models.CharField(max_length=100, verbose_name="تخصص")
    bio = models.TextField(verbose_name="بیوگرافی", blank=True)
    image = models.ImageField(upload_to='teachers/', blank=True, null=True, verbose_name="تصویر")

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "استاد"
        verbose_name_plural = "اساتید"


# ===========================
# انواع منابع آموزشی
# ===========================
class ResourceType(models.Model):
    name = models.CharField(max_length=100, verbose_name="نوع منبع")
    icon = models.CharField(max_length=50, verbose_name="آیکون", help_text="نام کلاس FontAwesome")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "نوع منبع"
        verbose_name_plural = "انواع منابع"


# ===========================
# منابع آموزشی
# ===========================
class EducationalResource(models.Model):
    GRADE_CHOICES = [
        (10, 'پایه دهم'),
        (11, 'پایه یازدهم'),
        (12, 'پایه دوازدهم'),
    ]

    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")
    resource_type = models.ForeignKey(ResourceType, on_delete=models.CASCADE, verbose_name="نوع منبع")
    major = models.ForeignKey(Major, on_delete=models.CASCADE, verbose_name="رشته تحصیلی")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="استاد")
    grade = models.IntegerField(choices=GRADE_CHOICES, verbose_name="پایه تحصیلی")
    file = models.FileField(upload_to='resources/', blank=True, null=True, verbose_name="فایل")
    video_url = models.URLField(blank=True, null=True, verbose_name="لینک ویدیو")
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True, verbose_name="تصویر شاخص")
    file_size = models.FloatField(blank=True, null=True, verbose_name="حجم فایل (مگابایت)")
    duration = models.DurationField(blank=True, null=True, verbose_name="مدت زمان ویدیو")
    download_count = models.IntegerField(default=0, verbose_name="تعداد دانلود")
    view_count = models.IntegerField(default=0, verbose_name="تعداد بازدید")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "منبع آموزشی"
        verbose_name_plural = "Educational resources"
        ordering = ['-created_at']


# ===========================
# لاگ‌ها
# ===========================
class DownloadLog(models.Model):
    resource = models.ForeignKey(EducationalResource, on_delete=models.CASCADE, verbose_name="منبع")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="کاربر")
    downloaded_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان دانلود")
    ip_address = models.GenericIPAddressField(verbose_name="آدرس IP")

    def __str__(self):
        return f"{self.user.username} - {self.resource.title}"

    class Meta:
        verbose_name = "لاگ دانلود"
        verbose_name_plural = "لاگ‌های دانلود"


class ViewLog(models.Model):
    resource = models.ForeignKey(EducationalResource, on_delete=models.CASCADE, verbose_name="منبع")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="کاربر")
    viewed_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان مشاهده")
    ip_address = models.GenericIPAddressField(verbose_name="آدرس IP")

    def __str__(self):
        return f"{self.user.username} - {self.resource.title}"

    class Meta:
        verbose_name = "لاگ مشاهده"
        verbose_name_plural = "لاگ‌های مشاهده"


# ===========================
# صفحات درباره ما و اعضای تیم
# ===========================
class AboutPage(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان صفحه")
    subtitle = models.CharField(max_length=500, verbose_name="زیرعنوان صفحه")
    description = models.TextField(verbose_name="توضیحات")
    stat_store_icon = models.CharField(max_length=100, default="store", verbose_name="آیکون فروشگاه")
    stat_store_number = models.CharField(max_length=50, default="۱,۲۵۰+", verbose_name="تعداد فروشگاه")
    stat_store_label = models.CharField(max_length=100, default="فروشگاه فعال", verbose_name="برچسب فروشگاه")
    stat_users_icon = models.CharField(max_length=100, default="users", verbose_name="آیکون کاربران")
    stat_users_number = models.CharField(max_length=50, default="۵۰,۰۰۰+", verbose_name="تعداد کاربران")
    stat_users_label = models.CharField(max_length=100, default="کاربر ثبت‌نام شده", verbose_name="برچسب کاربران")
    stat_rating_icon = models.CharField(max_length=100, default="star", verbose_name="آیکون رضایت")
    stat_rating_number = models.CharField(max_length=50, default="۴.۸/۵", verbose_name="امتیاز رضایت")
    stat_rating_label = models.CharField(max_length=100, default="رضایت کاربران", verbose_name="برچسب رضایت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "صفحه درباره ما"
        verbose_name_plural = "About Us Pages"


class TeamMember(models.Model):
    name = models.CharField(max_length=200, verbose_name="نام")
    role = models.CharField(max_length=200, verbose_name="نقش")
    bio = models.TextField(verbose_name="بیوگرافی")
    image = models.ImageField(upload_to='team_images/', verbose_name="تصویر")
    linkedin_url = models.URLField(blank=True, verbose_name="لینکدین")
    twitter_url = models.URLField(blank=True, verbose_name="توییتر")
    github_url = models.URLField(blank=True, verbose_name="گیت‌هاب")
    instagram_url = models.URLField(blank=True, verbose_name="اینستاگرام")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "عضو تیم"
        verbose_name_plural = "Team members"


# ===========================
# اطلاعات تماس و پیام‌ها
# ===========================
class ContactInfo(models.Model):
    title = models.CharField(max_length=100, default="با ما در ارتباط باشید")
    description = models.TextField(default="تیم پشتیبانی ما آماده پاسخگویی به سوالات و دریافت پیشنهادات شما می‌باشد.")
    address = models.CharField(max_length=255, default="تهران، خیابان ولیعصر، پلاک ۱۲۳۴، طبقه ۵")
    phone = models.CharField(max_length=20, default="۰۲۱-۱۲۳۴۵۶۷۸")
    email = models.EmailField(default="info@example.com")
    work_hours = models.CharField(max_length=100, default="شنبه تا چهارشنبه: ۸:۰۰ - ۱۷:۰۰ | پنجشنبه: ۸:۰۰ - ۱۴:۰۰")

    def __str__(self):
        return "اطلاعات تماس سایت"


class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
