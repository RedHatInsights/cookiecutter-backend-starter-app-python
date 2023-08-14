from prometheus_client import Counter


class MetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.total_requests = Counter("starter_app_total_requests",
                                      "total number of processed events")

    def __call__(self, request):
        self.total_requests.inc()
        return self.get_response(request)
