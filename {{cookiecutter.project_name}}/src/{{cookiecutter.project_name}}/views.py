from django.http import JsonResponse, HttpResponse
import logging

logger = logging.getLogger(__name__)


def healthz(req):
    logger.info("BARP")
    health_data = {
        "app_name": "{{cookiecutter.project_name}}",
        "status": "running",
    }

    return JsonResponse(health_data)


def readyz(req):
    return HttpResponse('OK')


def livez(req):
    return HttpResponse('OK')
