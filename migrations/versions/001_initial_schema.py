"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Créer la table cards
    op.create_table(
        'cards',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('skaleet_card_id', sa.Integer(), nullable=False),
        sa.Column('pan_alias', sa.String(), nullable=True),
        sa.Column('ni_card_ref', sa.String(), nullable=True),
        sa.Column('status_skaleet', sa.String(), nullable=False),
        sa.Column('status_ni', sa.String(), nullable=True),
        sa.Column('product_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_skaleet_card_id', 'cards', ['skaleet_card_id'], unique=False)
    # Index unique pour pan_alias (créé automatiquement par SQLAlchemy avec unique=True)
    op.create_index('ix_cards_pan_alias', 'cards', ['pan_alias'], unique=True)

    # Créer la table card_operations
    op.create_table(
        'card_operations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('card_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('operation_type', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('skaleet_event', sa.String(), nullable=True),
        sa.Column('skaleet_event_id', sa.String(), nullable=True),
        sa.Column('skaleet_webhook_id', sa.String(), nullable=True),
        sa.Column('ni_result_code', sa.String(), nullable=True),
        sa.Column('correlation_id', sa.String(), nullable=True),
        sa.Column('raw_webhook', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['card_id'], ['cards.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_card_id', 'card_operations', ['card_id'], unique=False)
    op.create_index('idx_correlation_id', 'card_operations', ['correlation_id'], unique=False)
    op.create_index('idx_created_at', 'card_operations', ['created_at'], unique=False)

    # Créer la table webhook_events
    op.create_table(
        'webhook_events',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('correlation_id', sa.String(), nullable=True),
        sa.Column('processed', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('payload', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('response', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('webhook_events')
    op.drop_index('idx_created_at', table_name='card_operations')
    op.drop_index('idx_correlation_id', table_name='card_operations')
    op.drop_index('idx_card_id', table_name='card_operations')
    op.drop_table('card_operations')
    op.drop_index('ix_cards_pan_alias', table_name='cards')
    op.drop_index('idx_skaleet_card_id', table_name='cards')
    op.drop_table('cards')

