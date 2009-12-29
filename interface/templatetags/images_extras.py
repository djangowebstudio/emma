"""
images_extras.py
Extra template tags for images
Geert Dekkers Web Studio 2008, 2009
nznl.com | nznl.net | nznl.org INTERNET PRODUCTIONS
"""

from django.template import Library
register = Library()
from django.template.defaultfilters import stringfilter
import os, sys
from django.core.management import setup_environ
import settings
setup_environ(settings)


@register.filter(name='truncate')
@stringfilter
def truncate(value,arg):
	"""Truncates a string of a given length, adds three dots at the end."""
	try:
		if len(value) > arg:
			return "%s..." % value[0:arg-3]
		else:
			return value
	except ValueError:
		pass
		
		
def submit_row_inline(context):
    opts = context['opts']
    change = context['change']
    is_popup = context['is_popup']
    save_as = context['save_as']
    return {
        'onclick_attrib': (opts.get_ordered_objects() and change
                            and 'onclick="submitOrderForm();"' or ''),
        'show_delete_link': (not is_popup and context['has_delete_permission']
                              and (change or context['show_delete'])),
        'show_save_as_new': not is_popup and change and save_as,
        'show_save_and_add_another': context['has_add_permission'] and 
                            not is_popup and (not save_as or context['add']),
        'show_save_and_continue': not is_popup and context['has_change_permission'],
        'is_popup': is_popup,
        'show_save': True
    }

# As you can see, we really want the first template dir. UPDATE: Templates MUST be in the project, not in EMMA.
submit_row_inline = register.inclusion_tag(os.path.join(settings.TEMPLATE_DIRS[0],'admin/interface/metadata/submit_line.html'), takes_context=True)(submit_row_inline)