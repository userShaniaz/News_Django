from django import template

register = template.Library()

@register.simple_tag
def greet_user(name):
    return f'Hello, {name}!'