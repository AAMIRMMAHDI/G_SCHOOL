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
        verbose_name_plural = "رشته ها"


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
        verbose_name_plural = "فایل"
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



















# ____________________________________________________________________________________________________________________________________________________________________










from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.contrib.auth import get_user_model

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_('Slug'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('دسته بندی')

    def __str__(self):
        return self.name

class Blog(models.Model):
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='blogs',
        verbose_name=_('Author')
    )
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_('Slug'))
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blogs',
        verbose_name=_('Category')
    )
    content = models.TextField(verbose_name=_('Content'))
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Address'))
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('City'))
    district = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('District'))
    is_approved = models.BooleanField(default=False, verbose_name=_('Is Approved'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        verbose_name = _('Blog')
        verbose_name_plural = _('وبلاگ ها')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            if not base_slug:
                base_slug = f"blog-{Blog.objects.count() + 1}"
            unique_slug = base_slug
            counter = 1
            while Blog.objects.filter(slug=unique_slug).exclude(id=self.id).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

class BlogImage(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='images', verbose_name=_('Blog'))
    image = models.ImageField(upload_to='blog_images/', verbose_name=_('Image'))

    class Meta:
        verbose_name = _('Blog Image')
        verbose_name_plural = _('Blog Images')

    def __str__(self):
        return f"Image for {self.blog.title}"

class BlogComment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments', verbose_name=_('Blog'))
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_('User'))
    rating = models.FloatField(default=0.0, verbose_name=_('Rating'))
    comment = models.TextField(blank=True, null=True, verbose_name=_('Comment'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        verbose_name = _('Blog Comment')
        verbose_name_plural = _('کامنت ها')
        unique_together = ['blog', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.blog.title}: {self.rating}"

    def save(self, *args, **kwargs):
        if self.rating < 1:
            self.rating = 1
        elif self.rating > 5:
            self.rating = 5
        super().save(*args, **kwargs)








        