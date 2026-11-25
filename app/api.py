from flask import Blueprint,jsonify,request
from .db import get_db
api_bp=Blueprint('api',__name__)
def serialize(r):
 return {'id':r['id'],'name':r['name'],'description':r['description'],'price':r['price'],'category':r['category'],'image':'/static/images/'+r['image'],'stock':r['stock']}
@api_bp.get('/health')
def health(): return jsonify({'status':'ok'})
@api_bp.get('/products')
def products():
 q=request.args.get('q','').strip(); cat=request.args.get('category','').strip(); sort=request.args.get('sort','name')
 if len(q)>100 or len(cat)>50: return jsonify({'error':'Search/category value too long'}),400
 sorts={'name':'name COLLATE NOCASE ASC','price_low':'price ASC','price_high':'price DESC'}
 if sort not in sorts: return jsonify({'error':'Invalid sort. Use name, price_low or price_high'}),400
 sql='SELECT * FROM products WHERE 1=1'; args=[]
 if q:
  sql+=' AND (name LIKE ? OR description LIKE ? OR category LIKE ?)'; term='%'+q+'%'; args += [term,term,term]
 if cat and cat.lower()!='all': sql+=' AND category=?'; args.append(cat)
 rows=get_db().execute(sql+' ORDER BY '+sorts[sort],args).fetchall()
 return jsonify({'count':len(rows),'products':[serialize(r) for r in rows]})
@api_bp.get('/products/<int:pid>')
def product(pid):
 if pid<1: return jsonify({'error':'ID must be positive'}),400
 r=get_db().execute('SELECT * FROM products WHERE id=?',(pid,)).fetchone()
 if r is None: return jsonify({'error':'Product not found'}),404
 return jsonify({'product':serialize(r)})
