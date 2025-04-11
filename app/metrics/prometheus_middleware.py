from prometheus_client import Counter, Histogram, make_asgi_app
from starlette.middleware.base import BaseHTTPMiddleware
from time import time

REQUEST_COUNT = Counter('request_count', 'Nombre de requêtes', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Latence des requêtes', ['endpoint'])

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time()
        response = await call_next(request)
        duration = time() - start
        REQUEST_COUNT.labels(request.method, request.url.path).inc()
        REQUEST_LATENCY.labels(request.url.path).observe(duration)
        return response

prometheus_app = make_asgi_app()
