from django import template

register = template.Library()

@register.filter
def in_group(user, group_names):
    if not user.is_authenticated:
        return False
    names = [g.strip() for g in group_names.split(',')]
    return user.groups.filter(name__in=names).exists()
