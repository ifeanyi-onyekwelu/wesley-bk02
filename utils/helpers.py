import os
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def get_env_variable(key, default=None):
    """
    Retrieve an environment variable, returning a default value if not found.

    :param key: The name of the environment variable
    :param default: The default value to return if the variable is not set
    :return: The value of the environment variable or the default value
    """
    return os.getenv(key, default)


def json_response(success=True, message="", data=None, status=200):
    """
    Helper function to return a JSON response.

    :param success: Boolean indicating success or failure
    :param message: Response message
    :param data: Dictionary containing additional data
    :param status: HTTP status code
    :return: JsonResponse
    """
    response_data = {"success": success, "message": message}

    if data:
        response_data["data"] = data

    return JsonResponse(response_data, status=status)


def send_email(subject, template_name, context, recipient_list):
    """
    Helper function to send an email with a template.

    :param subject: Email subject
    :param template_name: Name of the template file (HTML)
    :param context: Context variables to be used in the template
    :param recipient_list: List of recipients
    """
    # Render the HTML content from the template and context
    message = render_to_string(template_name, context)
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
        html_message=message  # Adding the HTML version of the message
    )
