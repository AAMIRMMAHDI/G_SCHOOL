from django.contrib import admin
from .models import (
    AboutPage, TeamMember, ContactMessage, ContactInfo,
    Major, Feature, Requirement, Career, Skill, Work,
    Teacher, ResourceType, EducationalResource
)

# ---------- About & Team ----------

@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'updated_at')
    search_fields = ('title', 'subtitle', 'description')

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'updated_at')
    search_fields = ('name', 'role', 'bio')

# ---------- Contact ----------

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject')
    list_filter = ('created_at',)

@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('title', 'email', 'phone')

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
