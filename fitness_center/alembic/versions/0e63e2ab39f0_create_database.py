"""create database

Revision ID: 0e63e2ab39f0
Revises: 
Create Date: 2024-06-29 17:11:13.092800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e63e2ab39f0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('fitness_center',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('address', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('contacts', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('address'),
    sa.UniqueConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('login', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=50), nullable=False),
    sa.Column('birth_date', sa.String(length=50), nullable=False),
    sa.Column('phone', sa.String(length=50), nullable=False),
    sa.Column('funds', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('login')
    )
    op.create_table('service',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=50), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('fitness_center', sa.Integer(), nullable=False),
    sa.Column('max_attendees', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['fitness_center'], ['fitness_center.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('trainer',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('fitness_center', sa.Integer(), nullable=False),
    sa.Column('age', sa.Integer(), nullable=False),
    sa.Column('sex', sa.String(length=6), nullable=False),
    sa.ForeignKeyConstraint(['fitness_center'], ['fitness_center.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('rating',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('trainer', sa.Integer(), nullable=False),
    sa.Column('user', sa.Integer(), nullable=False),
    sa.Column('points', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['trainer'], ['trainer.id'], ),
    sa.ForeignKeyConstraint(['user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('reservation',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('trainer', sa.Integer(), nullable=False),
    sa.Column('user', sa.Integer(), nullable=False),
    sa.Column('service', sa.Integer(), nullable=False),
    sa.Column('date', sa.String(length=10), nullable=False),
    sa.Column('time', sa.String(length=10), nullable=False),
    sa.ForeignKeyConstraint(['service'], ['service.id'], ),
    sa.ForeignKeyConstraint(['trainer'], ['trainer.id'], ),
    sa.ForeignKeyConstraint(['user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('services_balance',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user', sa.Integer(), nullable=False),
    sa.Column('service', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['service'], ['service.id'], ),
    sa.ForeignKeyConstraint(['user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('trainer_capacity',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('service', sa.Integer(), nullable=False),
    sa.Column('trainer', sa.Integer(), nullable=False),
    sa.Column('max_attendees', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['service'], ['service.id'], ),
    sa.ForeignKeyConstraint(['trainer'], ['trainer.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('trainer_schedule',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('trainer', sa.Integer(), nullable=False),
    sa.Column('date', sa.String(length=50), nullable=False),
    sa.Column('start_time', sa.String(length=50), nullable=False),
    sa.Column('end_time', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['trainer'], ['trainer.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('trainer_schedule')
    op.drop_table('trainer_capacity')
    op.drop_table('services_balance')
    op.drop_table('reservation')
    op.drop_table('rating')
    op.drop_table('trainer')
    op.drop_table('service')
    op.drop_table('user')
    op.drop_table('fitness_center')
    # ### end Alembic commands ###
