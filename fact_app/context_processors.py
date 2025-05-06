from django.utils.translation import get_language

def language_context(request):
    """
    Inject LANGUAGE_CODE into the template context.
    """
    return {
        'LANGUAGE_CODE': get_language(),
    }
