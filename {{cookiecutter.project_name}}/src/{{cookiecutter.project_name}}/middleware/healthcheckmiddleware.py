from django.http import HttpResponse, HttpResponseServerError
from django.db.migrations.executor import MigrationExecutor
from django.db import connections, DEFAULT_DB_ALIAS
from django.core.cache import caches
from django.core.cache.backends.memcached import BaseMemcachedCache


class HealthCheckMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        if request.method == "GET":
            if request.path == "/readyz":
                return self.readiness(request)
            elif request.path == "/livez":
                return self.liveness(request)
        return self.get_response(request)

    def liveness(self, request):
        # Test DB readiness
        try:
            for name in connections:
                cursor = connections[name].cursor()
                cursor.execute("SELECT 1;")
                row = cursor.fetchone()
                if row is None:
                    return HttpResponseServerError("db: invalid response")
        except Exception:
            return HttpResponseServerError("db: cannot connect to database.")

        # Test cache readiness
        try:
            for cache in caches.all():
                if isinstance(cache, BaseMemcachedCache):
                    stats = cache._cache.get_stats()
                    if len(stats) != len(cache._servers):
                        return HttpResponseServerError("cache: cannot connect to cache.")
        except Exception:
            return HttpResponseServerError("cache: cannot connect to cache.")

        return HttpResponse("OK")

    def readiness(self, request):
        connection = connections[DEFAULT_DB_ALIAS]
        connection.prepare_database()
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        if not executor.migration_plan(targets):
            return HttpResponse("OK")
        else:
            return HttpResponseServerError("unapplied migrations found")
