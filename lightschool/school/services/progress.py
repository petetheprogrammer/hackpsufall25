def get_progress(request, locale):
    """Get progress dict for locale."""
    return request.session.get('progress', {}).get(locale, {})

def set_progress(request, locale, subject, grade, unit_id, status, score=None):
    """Set progress for a unit."""
    progress = request.session.setdefault('progress', {})
    loc_progress = progress.setdefault(locale, {})
    subj_progress = loc_progress.setdefault(subject, {})
    grade_progress = subj_progress.setdefault(str(grade), {})
    grade_progress[unit_id] = {'status': status}
    if score is not None:
        grade_progress[unit_id]['score'] = score
    request.session.modified = True
    return progress

def get_subject_progress(progress, subject, grade):
    """Get progress for subject/grade."""
    return progress.get(subject, {}).get(str(grade), {})