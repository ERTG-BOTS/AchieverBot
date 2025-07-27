"""Create accruals table

Revision ID: 001_create_accruals
Revises:
Create Date: 2025-01-27 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001_create_accruals"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create accruals table
    op.create_table(
        "accruals",
        sa.Column(
            "id",
            sa.BIGINT(),
            nullable=False,
            autoincrement=True,
            primary_key=True,
        ),
        sa.Column(
            "chat_id",
            sa.BIGINT(),
            nullable=False,
        ),
        sa.Column("fullname", sa.Unicode(length=255), nullable=False),
        sa.Column("target_kpi", sa.String(length=255), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("period", sa.String(length=255), nullable=False),
        sa.Column("date", sa.String(length=255), nullable=False),
    )

    # Create indexes for better performance
    op.create_index("ix_accruals_chat_id", "accruals", ["chat_id"])
    op.create_index("ix_accruals_fullname", "accruals", ["fullname"])


def downgrade() -> None:
    op.drop_index("ix_accruals_chat_id", "accruals")
    op.drop_index("ix_accruals_fullname", "accruals")
    op.drop_table("accruals")
