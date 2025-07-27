"""Create awards table

Revision ID: 002_create_awards
Revises: 001_create_accruals
Create Date: 2025-01-27 12:01:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "002_create_awards"
down_revision: Union[str, None] = "001_create_accruals"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create awards table
    op.create_table(
        "awards",
        sa.Column(
            "id", sa.Integer(), nullable=False, autoincrement=True, primary_key=True
        ),
        sa.Column("name", sa.Unicode(length=255), nullable=False),
        sa.Column("cost", sa.Integer(), nullable=False),
        sa.Column("in_charge", sa.Unicode(length=255), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("description", sa.Unicode(length=255), nullable=False),
        sa.Column("shift_dependent", sa.Boolean(), nullable=False, default=True),
    )

    # Create indexes for better performance
    op.create_index("ix_awards_name", "awards", ["name"])
    op.create_index("ix_awards_cost", "awards", ["cost"])
    op.create_index("ix_awards_in_charge", "awards", ["in_charge"])
    op.create_index("ix_awards_shift_dependent", "awards", ["shift_dependent"])


def downgrade() -> None:
    op.drop_index("ix_awards_shift_dependent", "awards")
    op.drop_index("ix_awards_in_charge", "awards")
    op.drop_index("ix_awards_cost", "awards")
    op.drop_index("ix_awards_name", "awards")
    op.drop_table("awards")
