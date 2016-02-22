"""empty message

Revision ID: 0021_add_job_metadata
Revises: 0020_email_has_subject
Create Date: 2016-02-22 12:33:02.360780

"""

# revision identifiers, used by Alembic.
revision = '0021_add_job_metadata'
down_revision = '0020_email_has_subject'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('jobs', sa.Column('notification_count', sa.Integer(), nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('jobs', 'notification_count')
    ### end Alembic commands ###
