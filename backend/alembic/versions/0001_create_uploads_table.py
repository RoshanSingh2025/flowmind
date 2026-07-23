"""create uploads table

Revision ID: 0001
Revises:
Create Date: 2026-07-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    # The unique constraint on `stored_filename` is declared inline as part of
    # `create_table` (rather than via a follow-up `op.create_unique_constraint`
    # call) so this migration runs unchanged on both PostgreSQL and SQLite.
    # SQLite has no `ALTER TABLE ... ADD CONSTRAINT` support outside of
    # Alembic's batch mode, but a constraint declared as part of the initial
    # `CREATE TABLE` statement works on every backend without it.
    op.create_table(
        "uploads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("original_filename", sa.String(length=512), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=128), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("checksum", sa.String(length=64), nullable=False),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default="uploaded",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("stored_filename", name="uq_uploads_stored_filename"),
    )
    op.create_index("ix_uploads_status", "uploads", ["status"])
    op.create_index("ix_uploads_checksum", "uploads", ["checksum"])


def downgrade() -> None:
    # No standalone `drop_constraint` call is needed: `drop_table` removes the
    # unique constraint along with everything else, and dropping it explicitly
    # first would hit the same SQLite ALTER-TABLE limitation noted above.
    op.drop_index("ix_uploads_checksum", table_name="uploads")
    op.drop_index("ix_uploads_status", table_name="uploads")
    op.drop_table("uploads")