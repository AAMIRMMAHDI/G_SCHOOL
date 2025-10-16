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
        verbose_name_plural = _('Categories')

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
        verbose_name_plural = _('Blogs')

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
        verbose_name_plural = _('Blog Comments')
        unique_together = ['blog', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.blog.title}: {self.rating}"

    def save(self, *args, **kwargs):
        if self.rating < 1:
            self.rating = 1
        elif self.rating > 5:
            self.rating = 5
        super().save(*args, **kwargs)








        