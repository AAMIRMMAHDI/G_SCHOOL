from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import os

from .models import AboutPage, TeamMember, ContactInfo, Major, EducationalResource, DownloadLog, ViewLog
from .forms import ContactMessageForm, ResourceFilterForm


# ---------- صفحه درباره ما ----------
def about_view(request):
    about_page = AboutPage.objects.first()
    team_members = TeamMember.objects.all()

    context = {
        'about_page': about_page,
        'team_members': [
            {
                'name': member.name,
                'role': member.role,
                'bio': member.bio,
                'image': member.image.url if member.image else None,
                'social': [
                    {'platform': 'linkedin', 'url': member.linkedin_url} if member.linkedin_url else None,
                    {'platform': 'twitter', 'url': member.twitter_url} if member.twitter_url else None,
                    {'platform': 'github', 'url': member.github_url} if member.github_url else None,
                    {'platform': 'instagram', 'url': member.instagram_url} if member.instagram_url else None,
                ]
            } for member in team_members
        ],
        'stats': []
    }

    if about_page:
        context['stats'] = [
            {'icon': about_page.stat_store_icon, 'number': about_page.stat_store_number, 'label': about_page.stat_store_label},
            {'icon': about_page.stat_users_icon, 'number': about_page.stat_users_number, 'label': about_page.stat_users_label},
            {'icon': about_page.stat_rating_icon, 'number': about_page.stat_rating_number, 'label': about_page.stat_rating_label},
        ]

    return render(request, 'root/about.html', context)


# ---------- صفحه تماس ----------
def contact_view(request):
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "پیام شما با موفقیت ارسال شد!")
            return redirect('root:contact')
    else:
        form = ContactMessageForm()

    contact_info = ContactInfo.objects.first()

    return render(request, 'root/contact.html', {'form': form, 'contact_info': contact_info})


# ---------- لیست رشته‌ها ----------
def majors(request):
    majors = Major.objects.all()
    selected_major = majors.first()
    context = {
        'majors': majors,
        'selected_major': selected_major,
    }
    return render(request, 'root/majors.html', context)


# ---------- جزئیات رشته ----------
def major_detail(request, major_id):
    majors = Major.objects.all()
    selected_major = get_object_or_404(Major, id=major_id)
    context = {
        'majors': majors,
        'selected_major': selected_major,
    }
    return render(request, 'root/majors.html', context)


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

    return render(request, 'root/resources.html', context)


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
        return render(request, 'root/video_player.html', context)
    else:
        return render(request, 'root/resource_preview.html', context)


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
