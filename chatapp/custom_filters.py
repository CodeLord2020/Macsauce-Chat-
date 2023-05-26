from django import template

register = template.Library()

@register.filter
def filter_by_username(queryset, username):
    return queryset.filter(username=username)
