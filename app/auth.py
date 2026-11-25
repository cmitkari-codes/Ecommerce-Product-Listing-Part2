from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .db import get_db
from .metrics import AUTH_FAILURES
login_manager=LoginManager(); login_manager.login_view='auth.login'; login_manager.login_message='Please log in to continue.'
auth_bp=Blueprint('auth',__name__)
class User(UserMixin):
 def __init__(self,row): self.id=str(row['id']); self.username=row['username']; self.email=row['email']
@login_manager.user_loader
def load_user(user_id):
 row=get_db().execute('SELECT * FROM users WHERE id=?',(user_id,)).fetchone()
 return User(row) if row else None
@auth_bp.route('/register',methods=['GET','POST'])
def register():
 if request.method=='POST':
  username=request.form.get('username','').strip(); email=request.form.get('email','').strip().lower(); password=request.form.get('password','')
  if len(username)<3 or len(username)>40 or '@' not in email or len(password)<8:
   flash('Use a username of 3–40 characters, a valid email and a password of at least 8 characters.','error')
  else:
   try:
    db=get_db(); cur=db.execute('INSERT INTO users(username,email,password_hash) VALUES(?,?,?)',(username,email,generate_password_hash(password))); db.execute('INSERT INTO carts(user_id) VALUES(?)',(cur.lastrowid,)); db.commit()
    flash('Account created. Please log in.','success'); return redirect(url_for('auth.login'))
   except Exception:
    get_db().rollback(); flash('Username or email is already registered.','error')
 return render_template('auth.html',mode='register')
@auth_bp.route('/login',methods=['GET','POST'])
def login():
 if request.method=='POST':
  identity=request.form.get('identity','').strip(); row=get_db().execute('SELECT * FROM users WHERE username=? OR email=?',(identity,identity.lower())).fetchone()
  if row and check_password_hash(row['password_hash'],request.form.get('password','')):
   login_user(User(row)); return redirect(request.args.get('next') or url_for('home'))
  AUTH_FAILURES.inc(); from flask import current_app; current_app.logger.warning('authentication_failed',extra={'method':'POST','path':'/login'})
  flash('Invalid username/email or password.','error')
 return render_template('auth.html',mode='login')
@auth_bp.post('/logout')
@login_required
def logout(): logout_user(); flash('You have been logged out.','success'); return redirect(url_for('home'))
