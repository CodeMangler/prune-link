from os import path
from google.appengine.ext.webapp import template
from google.appengine.api import users

__author__ = 'CodeMangler'

def render_template(template_file, template_data = {}):
    template_path = path.join(path.join(path.dirname(__file__), path.join(path.join('..', '..'), 'templates')), template_file)
    return template.render(template_path, template_data)

def show_error_page(request_handler, error_code, error_message):
    template_parameters = {
        "login_url": users.create_login_url(request_handler.request.path),
        "logout_url": users.create_logout_url(request_handler.request.path),
        "message": error_message
    }
    request_handler.error(error_code) # Send a HTTP Not Found
    request_handler.response.out.write(render_template("error.html", template_parameters) )
