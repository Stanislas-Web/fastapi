"""add unique constraint on skaleet_card_id

Revision ID: 002
Revises: 001
Create Date: 2025-12-02 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Ajoute une contrainte unique sur skaleet_card_id pour éviter les doublons
    """
    # Nettoyer les doublons existants (garder le plus ancien)
    op.execute("""
        DELETE FROM cards 
        WHERE id IN (
            SELECT id FROM (
                SELECT id, ROW_NUMBER() OVER (PARTITION BY skaleet_card_id ORDER BY created_at ASC) AS rn
                FROM cards
            ) t
            WHERE t.rn > 1
        )
    """)
    
    # Ajouter la contrainte unique
    op.create_unique_constraint(
        'uq_cards_skaleet_card_id',
        'cards',
        ['skaleet_card_id']
    )


def downgrade() -> None:
    """
    Supprime la contrainte unique sur skaleet_card_id
    """
    op.drop_constraint('uq_cards_skaleet_card_id', 'cards', type_='unique')
