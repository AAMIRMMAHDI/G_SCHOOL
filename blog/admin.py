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

@admin.register(BlogImage)
class BlogImageAdmin(admin.ModelAdmin):
    list_display = ('blog', 'image', 'id')
    list_filter = ('blog',)
    search_fields = ('blog__title',)
    ordering = ('blog',)
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('blog')

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
    


