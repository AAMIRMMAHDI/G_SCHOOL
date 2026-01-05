from django.contrib import admin
from .models import (
    Major, Feature, Requirement, Career, Skill, Work,
    Teacher, ResourceType, EducationalResource
)


# ---------- Majors & Related Inline ----------

class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 1
    verbose_name = "ویژگی"
    verbose_name_plural = "ویژگی‌ها"

class RequirementInline(admin.TabularInline):
    model = Requirement
    extra = 1
    verbose_name = "شرط ورود"
    verbose_name_plural = "شرایط ورود"

class CareerInline(admin.TabularInline):
    model = Career
    extra = 1
    verbose_name = "شغل"
    verbose_name_plural = "مشاغل"

class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1
    verbose_name = "مهارت"
    verbose_name_plural = "مهارت‌ها"

class WorkInline(admin.TabularInline):
    model = Work
    extra = 1
    verbose_name = "نمونه‌کار"
    verbose_name_plural = "نمونه‌کارها"

@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle')
    search_fields = ('title', 'description', 'subtitle')
    list_filter = ('title',)
    inlines = [FeatureInline, RequirementInline, CareerInline, SkillInline, WorkInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'image', 'icon', 'subtitle', 'introduction')
        }),
    )

# ---------- Hidden Admins for Relations ----------

class HiddenAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False  # پنهان کردن از منو

admin.site.register(Teacher, HiddenAdmin)
admin.site.register(ResourceType, HiddenAdmin)

# ---------- Educational Resource ----------

@admin.register(EducationalResource)
class EducationalResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'resource_type', 'major', 'grade', 'teacher', 'download_count', 'view_count', 'is_active']
    list_filter = ['resource_type', 'major', 'grade', 'is_active']
    search_fields = ['title', 'description', 'teacher__full_name']
    readonly_fields = ['download_count', 'view_count', 'created_at', 'updated_at']
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'description', 'resource_type', 'major', 'teacher', 'grade')
        }),
        ('فایل‌ها', {
            'fields': ('file', 'video_url', 'thumbnail', 'file_size', 'duration')
        }),
        ('آمار', {
            'fields': ('download_count', 'view_count', 'created_at', 'updated_at')
        }),
        ('تنظیمات', {
            'fields': ('is_active',)
        }),
    )




























# _________________________________________________________________________________________________________________________________________________
























from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Category, Blog, BlogImage, BlogComment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
    list_per_page = 20

    fieldsets = (
        (None, {
            'fields': ('name', 'slug')
        }),
        (_('Metadata'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at',)

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'city', 'slug', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'city', 'category', 'created_at')
    search_fields = ('title', 'content', 'author__username', 'slug')
    list_editable = ('is_approved',)
    ordering = ('-created_at',)
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['author', 'category']
    list_per_page = 20

    fieldsets = (
        (None, {
            'fields': (
                'author', 'title', 'slug', 'category', 'content', 'address', 'city', 'district', 'is_approved'
            )
        }),
        (_('Metadata'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category')

    def approve_blogs(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, _(f"{updated} وبلاگ با موفقیت تأیید شدند."))
    approve_blogs.short_description = _("تأیید وبلاگ‌های انتخاب‌شده")

    actions = [approve_blogs]



@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('blog', 'user', 'rating', 'created_at')
    list_filter = ('blog', 'rating', 'created_at')
    search_fields = ('blog__title', 'user__username', 'comment')
    ordering = ('-created_at',)
    raw_id_fields = ('user',)
    list_per_page = 20

    fieldsets = (
        (None, {
            'fields': ('blog', 'user', 'rating', 'comment')
        }),
        (_('Metadata'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('blog', 'user')
    


