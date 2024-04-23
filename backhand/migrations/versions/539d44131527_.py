"""empty message

Revision ID: 539d44131527
Revises: 
Create Date: 2024-04-18 13:48:04.559867

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '539d44131527'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('motivations',
    sa.Column('_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('strength', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('motivations')
    # ### end Alembic commands ###