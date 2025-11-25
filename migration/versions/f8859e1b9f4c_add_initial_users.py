"""add_initial_users

Revision ID: f8859e1b9f4c
Revises: 75109cb3807c
Create Date: 2025-11-25 19:17:51.319979

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8859e1b9f4c'
down_revision: Union[str, Sequence[str], None] = '75109cb3807c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO users (name, surname, email, hashed_password, role, is_active) VALUES
        (
            'Admin', 
            'User', 
            'admin@example.com', 
            '$argon2id$v=19$m=65536,t=3,p=4$g5RGiB07S9AzDx+l7GyxeQ$8GvSgmPDAZXNOPL/d0WOKkYngYivHv2AquUcarv2Bto',
            'admin', 
            true
        ),
        (
            'Manager', 
            'User', 
            'manager@example.com', 
            '$argon2id$v=19$m=65536,t=3,p=4$yo/gkifu14Su83gzdgEgXw$05LWMVT27+PTQ7cVGpNLALs3vOPyxDypdMB+4ObZNUk',
            'manager', 
            true
        ),
        (
            'Regular', 
            'User', 
            'user@example.com', 
            '$argon2id$v=19$m=65536,t=3,p=4$IM0loXJqUR/HMnjte2M5Fw$4rYYFFlxNnsF/zeovVSMZHDRAtuAwg1ZeF8PKbKxWs8',
            'user', 
            true
        )
        """)


def downgrade():
    op.execute("""
    DELETE FROM users 
    WHERE email IN (
        'admin@example.com',
        'manager@example.com', 
        'user@example.com'
    );
    """)