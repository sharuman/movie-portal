from django import template

register = template.Library()


@register.filter
def addstr(arg1, arg2):  # Lets us concatenate 2 strings in a template
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)
