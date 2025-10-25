from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import activate
import json
from .services.lessons import load_lesson_pack
from .services.progress import get_progress, set_progress, get_subject_progress
from .services.tutor import get_tutor_reply

def home(request):
    """Home page: choose subject and grade."""
    return render(request, 'home.html')

def set_lang(request):
    """Set language in session."""
    lang = request.POST.get('lang', 'en')
    activate(lang)
    request.session['django_language'] = lang
    return JsonResponse({'status': 'ok'})

def subject_grade(request, subject, grade):
    """List units for subject/grade."""
    locale = request.session.get('django_language', 'en')
    try:
        lesson_pack = load_lesson_pack(subject, int(grade), locale)
    except FileNotFoundError:
        return render(request, 'error.html', {'message': 'Lesson not found'})
    progress = get_progress(request, locale)
    subj_progress = get_subject_progress(progress, subject, grade)
    units = lesson_pack['units']
    for unit in units:
        unit['progress'] = subj_progress.get(unit['id'], {})
    return render(request, 'subject_grade.html', {
        'subject': subject,
        'grade': grade,
        'units': units,
        'locale': locale
    })

def lesson(request, subject, grade, unit_id):
    """Render lesson cards."""
    locale = request.session.get('django_language', 'en')
    lesson_pack = load_lesson_pack(subject, int(grade), locale)
    unit = next((u for u in lesson_pack['units'] if u['id'] == unit_id), None)
    if not unit:
        return render(request, 'error.html', {'message': 'Unit not found'})
    return render(request, 'lesson.html', {
        'subject': subject,
        'grade': grade,
        'unit': unit,
        'locale': locale
    })

def quiz(request, subject, grade, unit_id):
    """Render quiz."""
    locale = request.session.get('django_language', 'en')
    lesson_pack = load_lesson_pack(subject, int(grade), locale)
    unit = next((u for u in lesson_pack['units'] if u['id'] == unit_id), None)
    if not unit:
        return render(request, 'error.html', {'message': 'Unit not found'})
    return render(request, 'quiz.html', {
        'subject': subject,
        'grade': grade,
        'unit': unit,
        'locale': locale
    })

# API views

def api_lessons(request):
    """Get lesson pack JSON."""
    subject = request.GET.get('subject')
    grade = request.GET.get('grade')
    locale = request.GET.get('locale', 'en')
    try:
        data = load_lesson_pack(subject, int(grade), locale)
        return JsonResponse(data)
    except:
        return JsonResponse({'error': 'Not found'}, status=404)

@csrf_exempt
def api_progress_set(request):
    """Set progress."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = json.loads(request.body)
    locale = request.session.get('django_language', 'en')
    progress = set_progress(request, locale, data['subject'], data['grade'], data['unitId'], data['status'], data.get('score'))
    return JsonResponse(progress)

def api_progress_get(request):
    """Get progress for subject/grade."""
    subject = request.GET.get('subject')
    grade = request.GET.get('grade')
    locale = request.session.get('django_language', 'en')
    progress = get_progress(request, locale)
    subj_progress = get_subject_progress(progress, subject, grade)
    return JsonResponse(subj_progress)

@csrf_exempt
def api_tutor(request):
    """Get tutor reply."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = json.loads(request.body)
    reply = get_tutor_reply(data['message'], data['subject'], data['grade'], data['locale'])
    return JsonResponse(reply)