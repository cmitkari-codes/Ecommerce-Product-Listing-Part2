import os
from flask import Flask, render_template
from config import Config
from .db import init_app, init_db, seed_db, ensure_part23_schema
from .api import api_bp
from .auth import auth_bp, login_manager
from .cart import cart_bp
from .logging_config import configure_logging
from .metrics import metrics_response

def create_app():
 app=Flask(__name__); app.config.from_object(Config)
 os.makedirs(os.path.dirname(app.config['DATABASE']),exist_ok=True)
 configure_logging(app); init_app(app); login_manager.init_app(app)
 app.register_blueprint(api_bp,url_prefix='/api'); app.register_blueprint(auth_bp); app.register_blueprint(cart_bp)
 @app.get('/')
 def home(): return render_template('index.html')
 @app.get('/products/<int:product_id>')
 def detail(product_id): return render_template('product.html',product_id=product_id)
 @app.get('/metrics')
 def metrics(): return metrics_response()
 with app.app_context(): init_db(); seed_db(); ensure_part23_schema()
 return app
