from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


def healthz(req):
    health_data = {
        "app_name": "{{cookiecutter.project_name}}",
        "status": "running",
    }

    return JsonResponse(health_data)
