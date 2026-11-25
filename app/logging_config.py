import json, logging, os, time, uuid
from datetime import datetime, timezone
from flask import g, request
class JsonFormatter(logging.Formatter):
    def format(self, record):
        data={'timestamp':datetime.now(timezone.utc).isoformat(),'level':record.levelname,'message':record.getMessage()}
        for key in ('request_id','method','path','status','duration_ms','user_id'):
            value=getattr(record,key,None)
            if value is not None: data[key]=value
        if record.exc_info: data['exception']=self.formatException(record.exc_info)
        return json.dumps(data)
def configure_logging(app):
    handler=logging.StreamHandler(); handler.setFormatter(JsonFormatter())
    app.logger.handlers=[handler]; app.logger.setLevel(logging.INFO); app.logger.propagate=False
    @app.before_request
    def start_request():
        g.request_id=request.headers.get('X-Request-ID') or str(uuid.uuid4()); g.started_at=time.perf_counter()
    @app.after_request
    def finish_request(response):
        from .metrics import REQUESTS, LATENCY
        endpoint=request.endpoint or 'unknown'; status=str(response.status_code)
        elapsed=time.perf_counter()-getattr(g,'started_at',time.perf_counter())
        REQUESTS.labels(request.method,endpoint,status).inc(); LATENCY.labels(request.method,endpoint).observe(elapsed)
        response.headers['X-Request-ID']=getattr(g,'request_id','')
        app.logger.info('http_request',extra={'request_id':getattr(g,'request_id',''),'method':request.method,'path':request.path,'status':response.status_code,'duration_ms':round(elapsed*1000,2)})
        return response
    @app.teardown_request
    def log_unhandled(error):
        if error: app.logger.exception('request_exception',exc_info=error,extra={'request_id':getattr(g,'request_id','')})
