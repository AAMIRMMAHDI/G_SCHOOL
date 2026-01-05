from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import os

from .models import  Major, EducationalResource, DownloadLog, ViewLog
from .forms import  ResourceFilterForm

# ---------- لیست رشته‌ها ----------
def majors(request):
    majors = Major.objects.all()
    selected_major = majors.first()
    context = {
        'majors': majors,
        'selected_major': selected_major,
    }
    return render(request, 'index/String.html', context)


# ---------- جزئیات رشته ----------
def major_detail(request, major_id):
    majors = Major.objects.all()
    selected_major = get_object_or_404(Major, id=major_id)
    context = {
        'majors': majors,
        'selected_major': selected_major,
    }
    return render(request, 'index/String.html', context)


# ---------- لیست منابع آموزشی ----------
def resources_list(request):
    form = ResourceFilterForm(request.GET or None)
    resources = EducationalResource.objects.filter(is_active=True)

    if form.is_valid():
        major = form.cleaned_data.get('major')
        grade = form.cleaned_data.get('grade')
        search = form.cleaned_data.get('search')

        if major and major != 'all':
            resources = resources.filter(major_id=major)
        if grade and grade != 'all':
            resources = resources.filter(grade=grade)
        if search:
            resources = resources.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(teacher__full_name__icontains=search)
            )

    video_resources = resources.filter(resource_type__name='ویدیو')
    other_resources = resources.exclude(resource_type__name='ویدیو')

    context = {
        'form': form,
        'resources': other_resources,
        'video_resources': video_resources,
        'majors': Major.objects.all(),
        'stats': {
            'pdf_count': resources.filter(resource_type__name='PDF').count(),
            'video_count': video_resources.count(),
            'total_downloads': sum(resource.download_count for resource in resources),
            'total_resources': resources.count(),
        }
    }

    return render(request, 'index/Question.html', context)


# ---------- دانلود منبع آموزشی ----------
@login_required
def download_resource(request, resource_id):
    resource = get_object_or_404(EducationalResource, id=resource_id, is_active=True)

    resource.download_count += 1
    resource.save()

    DownloadLog.objects.create(
        resource=resource,
        user=request.user,
        ip_address=get_client_ip(request)
    )

    if resource.file:
        response = HttpResponse(resource.file, content_type='application/force-download')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(resource.file.name)}"'
        return response

    return JsonResponse({'status': 'success', 'message': 'دانلود با موفقیت ثبت شد'})


# ---------- مشاهده منبع آموزشی ----------
@login_required
def view_resource(request, resource_id):
    resource = get_object_or_404(EducationalResource, id=resource_id, is_active=True)

    resource.view_count += 1
    resource.save()

    ViewLog.objects.create(
        resource=resource,
        user=request.user,
        ip_address=get_client_ip(request)
    )

    context = {'resource': resource}

    if resource.resource_type.name == 'ویدیو':
        return render(request, 'index/video_player.html', context)
    else:
        return render(request, 'index/Detailed_question.html', context)


# ---------- API منابع آموزشی ----------
def api_resources(request):
    resources = EducationalResource.objects.filter(is_active=True)

    data = {
        'resources': [
            {
                'id': res.id,
                'title': res.title,
                'description': res.description,
                'resource_type': res.resource_type.name,
                'major': res.major.title,
                'teacher': res.teacher.full_name,
                'grade': res.get_grade_display(),
                'download_count': res.download_count,
                'view_count': res.view_count,
                'created_at': res.created_at.strftime('%Y/%m/%d'),
                'file_size': res.file_size,
                'duration': str(res.duration) if res.duration else None,
                'thumbnail_url': res.thumbnail.url if res.thumbnail else None,
            }
            for res in resources
        ]
    }

    return JsonResponse(data)


# ---------- گرفتن IP کاربر ----------
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


















# _____________________________________________________________________________________________________________________________________________________________________














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
            return redirect('root:send_list')
        else:
            messages.error(request, _('لطفاً خطاهای فرم را برطرف کنید'))
    else:
        form = BlogRegisterForm()
        image_form = BlogImageForm()

    return render(request, 'index/Blog_registration.html', {
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

    return render(request, 'index/Blog_List.html', {
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

    return render(request, 'index/Blog_details.html', {
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
        return redirect('root:send_detail', slug=slug)

    if request.method == 'POST':
        form = BlogCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog = blog
            comment.user = request.user
            comment.save()
            messages.success(request, _('نظر شما با موفقیت ثبت شد!'))
            return redirect('root:send_detail', slug=slug)
        else:
            messages.error(request, _('لطفاً خطاهای فرم را برطرف کنید'))
    else:
        form = BlogCommentForm()

    return render(request, 'index/comment.html', {
        'form': form,
        'blog': blog,
    })

