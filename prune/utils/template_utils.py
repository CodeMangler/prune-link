from os import path
from google.appengine.ext.webapp import template

__author__ = 'CodeMangler'

def render_template(template_file, template_data = {}):
    template_path = path.join(path.join(path.dirname(__file__), path.join(path.join('..', '..'), 'templates')), template_file)
    return template.render(template_path, template_data)

