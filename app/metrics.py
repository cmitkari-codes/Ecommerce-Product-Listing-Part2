from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from flask import Response
REQUESTS = Counter('ecommerce_http_requests_total','Total HTTP requests',['method','endpoint','status'])
LATENCY = Histogram('ecommerce_http_request_duration_seconds','HTTP request latency',['method','endpoint'])
CART_OPS = Counter('ecommerce_cart_operations_total','Successful cart operations',['operation'])
AUTH_FAILURES = Counter('ecommerce_auth_failures_total','Failed login attempts')
def metrics_response(): return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
