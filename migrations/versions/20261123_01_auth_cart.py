"""Add users, carts and cart items while preserving Part 1 products."""
from alembic import op
from sqlalchemy import inspect
import sqlalchemy as sa
revision='20261123_01'
down_revision=None
branch_labels=None
depends_on=None
def upgrade():
    existing=set(inspect(op.get_bind()).get_table_names())
    if 'users' not in existing: op.create_table('users',sa.Column('id',sa.Integer,primary_key=True),sa.Column('username',sa.String(40),nullable=False,unique=True),sa.Column('email',sa.String(255),nullable=False,unique=True),sa.Column('password_hash',sa.String(255),nullable=False),sa.Column('created_at',sa.DateTime,server_default=sa.text('CURRENT_TIMESTAMP')))
    if 'carts' not in existing: op.create_table('carts',sa.Column('id',sa.Integer,primary_key=True),sa.Column('user_id',sa.Integer,sa.ForeignKey('users.id',ondelete='CASCADE'),nullable=False,unique=True),sa.Column('created_at',sa.DateTime,server_default=sa.text('CURRENT_TIMESTAMP')))
    if 'cart_items' not in existing: op.create_table('cart_items',sa.Column('id',sa.Integer,primary_key=True),sa.Column('cart_id',sa.Integer,sa.ForeignKey('carts.id',ondelete='CASCADE'),nullable=False),sa.Column('product_id',sa.Integer,sa.ForeignKey('products.id'),nullable=False),sa.Column('quantity',sa.Integer,nullable=False),sa.UniqueConstraint('cart_id','product_id'))
def downgrade():
    op.drop_table('cart_items'); op.drop_table('carts'); op.drop_table('users')
