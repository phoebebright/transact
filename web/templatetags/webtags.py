
from web.models import Say


register = Library()

@register.simple_tag
def say(phrase, page=None):
    """
    return block of text linked to phrase
    """
    

    return Say.say(phrase, page)
    

