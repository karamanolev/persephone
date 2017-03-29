from django import template

register = template.Library()


@register.filter()
def as_percentage(val):
    return '{}%'.format(val * 100)
