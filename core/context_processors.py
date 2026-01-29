from .translation import get_lang_dict

def language(request):
    """Add language translations to all templates"""
    lang = request.session.get('language', 'en')
    return {
        'lang': lang,
        'translations': get_lang_dict(lang),
        't': get_lang_dict(lang),  # Shorter alias
    }