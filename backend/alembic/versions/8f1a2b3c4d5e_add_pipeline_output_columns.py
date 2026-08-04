"""add_pipeline_output_columns

Revision ID: 8f1a2b3c4d5e
Revises: 3d627c7e342e
Create Date: 2026-07-30 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8f1a2b3c4d5e"
down_revision: str | None = "3d627c7e342e"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("uploads", sa.Column("transcript", sa.Text(), nullable=True))
    op.add_column("uploads", sa.Column("documentation_markdown", sa.Text(), nullable=True))
    op.add_column("uploads", sa.Column("sop_markdown", sa.Text(), nullable=True))
    op.add_column("uploads", sa.Column("faq_markdown", sa.Text(), nullable=True))
    op.add_column("uploads", sa.Column("summary_markdown", sa.Text(), nullable=True))
    op.add_column("uploads", sa.Column("processing_error", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("uploads", "processing_error")
    op.drop_column("uploads", "summary_markdown")
    op.drop_column("uploads", "faq_markdown")
    op.drop_column("uploads", "sop_markdown")
    op.drop_column("uploads", "documentation_markdown")
    op.drop_column("uploads", "transcript")