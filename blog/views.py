from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count, Avg
from .forms import BlogRegisterForm, BlogImageForm, BlogCommentForm
from .models import Blog, BlogImage, Category, BlogComment

@login_required
def send_register_view(request):
    if request.method == 'POST':
        form = BlogRegisterForm(request.POST)
        
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()

            # مدیریت آپلود چند تصویر
            files = request.FILES.getlist('images')
            if files:
                for file in files:
                    BlogImage.objects.create(blog=blog, image=file)
            else:
                messages.warning(request, _('هیچ تصویری آپلود نشد.'))

            messages.success(request, _('وبلاگ با موفقیت ثبت شد! پس از تأیید نمایش داده خواهد شد.'))
            return redirect('blog:send_list')
        else:
            messages.error(request, _('لطفاً خطاهای فرم را برطرف کنید'))
    else:
        form = BlogRegisterForm()
        image_form = BlogImageForm()

    return render(request, 'send/sent.html', {
        'form': form,
        'image_form': image_form,
    })

def send_list_view(request):
    categories = request.GET.getlist('category[]')
    cities = request.GET.getlist('city[]')
    search = request.GET.get('search', '')

    # گرفتن وبلاگ‌های تأییدشده
    blogs = Blog.objects.filter(is_approved=True).select_related('category', 'author').prefetch_related('images')

    # اعمال فیلترها
    if categories and 'all' not in categories:
        blogs = blogs.filter(category__slug__in=categories)

    if cities and 'all' not in cities:
        blogs = blogs.filter(city__in=cities)

    if search:
        blogs = blogs.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search) |
            Q(category__name__icontains=search)
        )

    # گرفتن دسته‌بندی‌ها و شهرها برای فیلتر
    all_categories = Category.objects.annotate(
        count=Count('blogs', filter=Q(blogs__is_approved=True))
    )
    all_cities = Blog.objects.filter(is_approved=True).values('city').annotate(
        count=Count('city')
    ).order_by('city')

    return render(request, 'send/list.html', {
        'blogs': blogs,
        'categories': all_categories,
        'cities': all_cities,
        'current_categories': categories if categories else ['all'],
        'current_cities': cities if cities else ['all'],
        'current_search': search,
    })

def send_detail_view(request, slug):
    blog = get_object_or_404(Blog, slug=slug, is_approved=True)
    avg_rating = blog.comments.aggregate(Avg('rating'))['rating__avg'] or 0.0
    rating_count = blog.comments.count()

    rating_percentages = {}
    for i in range(1, 6):
        count = blog.comments.filter(rating__gte=i - 0.5, rating__lt=i + 0.5).count()
        percentage = (count / rating_count * 100) if rating_count > 0 else 0
        rating_percentages[str(i)] = round(percentage, 1)

    similar_blogs = Blog.objects.filter(
        category=blog.category,
        is_approved=True
    ).exclude(slug=slug).select_related('category').prefetch_related('images')[:3]

    for similar in similar_blogs:
        similar.avg_rating = similar.comments.aggregate(avg=Avg('rating'))['avg'] or 0

    user_has_commented = False
    if request.user.is_authenticated:
        user_has_commented = BlogComment.objects.filter(
            blog=blog, 
            user=request.user
        ).exists()

    return render(request, 'send/detail.html', {
        'blog': blog,
        'images': blog.images.all(),
        'avg_rating': avg_rating,
        'rating_count': rating_count,
        'comments': blog.comments.select_related('user').order_by('-created_at')[:3],
        'rating_percentages': rating_percentages,
        'similar_blogs': similar_blogs,
        'user_has_commented': user_has_commented,
    })

@login_required
def add_comment_view(request, slug):
    blog = get_object_or_404(Blog, slug=slug, is_approved=True)
    existing_comment = BlogComment.objects.filter(blog=blog, user=request.user).first()
    if existing_comment:
        messages.warning(request, _('شما قبلاً برای این وبلاگ نظر داده‌اید.'))
        return redirect('blog:send_detail', slug=slug)

    if request.method == 'POST':
        form = BlogCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog = blog
            comment.user = request.user
            comment.save()
            messages.success(request, _('نظر شما با موفقیت ثبت شد!'))
            return redirect('blog:send_detail', slug=slug)
        else:
            messages.error(request, _('لطفاً خطاهای فرم را برطرف کنید'))
    else:
        form = BlogCommentForm()

    return render(request, 'send/comment.html', {
        'form': form,
        'blog': blog,
    })

