from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from .db import get_db
from .metrics import CART_OPS
cart_bp=Blueprint('cart',__name__)
def owned_cart():
 return get_db().execute('SELECT id FROM carts WHERE user_id=?',(int(current_user.id),)).fetchone()
def cart_rows(cart_id):
 return get_db().execute("""SELECT ci.product_id,ci.quantity,p.name,p.price,p.image,p.stock,(ci.quantity*p.price) AS subtotal FROM cart_items ci JOIN products p ON p.id=ci.product_id WHERE ci.cart_id=? ORDER BY p.name""",(cart_id,)).fetchall()
@cart_bp.get('/cart')
@login_required
def view_cart():
 cart=owned_cart(); rows=cart_rows(cart['id']); total=sum(r['subtotal'] for r in rows)
 return render_template('cart.html',items=rows,total=total)
@cart_bp.post('/api/cart/items')
@login_required
def add_item():
 data=request.get_json(silent=True) or request.form
 try: pid=int(data.get('product_id',0)); qty=int(data.get('quantity',1))
 except (TypeError,ValueError): return jsonify({'error':'Product and quantity must be integers'}),400
 if pid<1 or qty<1 or qty>99: return jsonify({'error':'Invalid product or quantity (1–99)'}),400
 db=get_db(); product=db.execute('SELECT id,stock FROM products WHERE id=?',(pid,)).fetchone()
 if not product: return jsonify({'error':'Product not found'}),404
 cart=owned_cart(); existing=db.execute('SELECT quantity FROM cart_items WHERE cart_id=? AND product_id=?',(cart['id'],pid)).fetchone(); new_qty=qty+(existing['quantity'] if existing else 0)
 if new_qty>product['stock']: return jsonify({'error':'Requested quantity exceeds available stock','available':product['stock']}),409
 if existing: db.execute('UPDATE cart_items SET quantity=? WHERE cart_id=? AND product_id=?',(new_qty,cart['id'],pid))
 else: db.execute('INSERT INTO cart_items(cart_id,product_id,quantity) VALUES(?,?,?)',(cart['id'],pid,qty))
 db.commit(); CART_OPS.labels('add').inc(); return jsonify({'message':'Item added to cart','quantity':new_qty}),201
@cart_bp.route('/api/cart/items/<int:pid>',methods=['PATCH','DELETE'])
@login_required
def update_item(pid):
 db=get_db(); cart=owned_cart(); item=db.execute('SELECT quantity FROM cart_items WHERE cart_id=? AND product_id=?',(cart['id'],pid)).fetchone()
 if not item: return jsonify({'error':'Cart item not found'}),404
 if request.method=='DELETE': db.execute('DELETE FROM cart_items WHERE cart_id=? AND product_id=?',(cart['id'],pid)); db.commit(); CART_OPS.labels('remove').inc(); return jsonify({'message':'Item removed'})
 data=request.get_json(silent=True) or request.form; 
 try: qty=int(data.get('quantity',0))
 except (TypeError,ValueError): return jsonify({'error':'Quantity must be an integer'}),400
 if qty<1 or qty>99: return jsonify({'error':'Quantity must be between 1 and 99'}),400
 product=db.execute('SELECT stock FROM products WHERE id=?',(pid,)).fetchone()
 if qty>product['stock']: return jsonify({'error':'Requested quantity exceeds available stock','available':product['stock']}),409
 db.execute('UPDATE cart_items SET quantity=? WHERE cart_id=? AND product_id=?',(qty,cart['id'],pid)); db.commit(); CART_OPS.labels('update').inc(); return jsonify({'message':'Quantity updated','quantity':qty})
@cart_bp.post('/cart/update/<int:pid>')
@login_required
def update_from_page(pid):
 response=update_item(pid)
 if isinstance(response,tuple) and response[1]>=400: flash(response[0].get_json().get('error','Unable to update'),'error')
 return redirect(url_for('cart.view_cart'))
@cart_bp.post('/cart/remove/<int:pid>')
@login_required
def remove_from_page(pid):
 db=get_db(); cart=owned_cart(); db.execute('DELETE FROM cart_items WHERE cart_id=? AND product_id=?',(cart['id'],pid)); db.commit(); CART_OPS.labels('remove').inc(); return redirect(url_for('cart.view_cart'))
@cart_bp.get('/api/cart')
@login_required
def cart_api():
 cart=owned_cart(); rows=cart_rows(cart['id']); return jsonify({'items':[dict(r) for r in rows],'total':sum(r['subtotal'] for r in rows)})
