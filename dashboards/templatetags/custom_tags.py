from django import template

register = template.Library()

@register.filter(name='format_phase_name')
def format_phase_name(value):
    """
    Convert snake_case phase name to Title Case with spaces
    Example: finished_goods_store -> Finished Goods Store
    """
    if not value:
        return ""
    # Replace underscores with spaces
    value = value.replace("_", " ")
    # Return title-cased result
    return value.title()
    return value.title()
