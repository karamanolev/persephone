from django import template

register = template.Library()


@register.filter()
def as_percentage(val):
    return '{}%'.format(val * 100)


@register.filter('startswith')
def startswith(text, starts):
    if text is None or starts is None:
        return False
    return str(text).startswith(str(starts))
