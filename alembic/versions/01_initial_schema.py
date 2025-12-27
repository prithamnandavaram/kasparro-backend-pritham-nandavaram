"""initial schema

Revision ID: 01_initial_schema
Revises: 
Create Date: 2023-10-27 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '01_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Raw CoinPaprika
    op.create_table('raw_coinpaprika',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('coin_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('symbol', sa.String(), nullable=True),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('price_usd', sa.Float(), nullable=True),
        sa.Column('last_updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.Column('ingested_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_raw_coinpaprika_coin_id'), 'raw_coinpaprika', ['coin_id'], unique=False)
    op.create_index(op.f('ix_raw_coinpaprika_id'), 'raw_coinpaprika', ['id'], unique=False)

    # Raw CSV
    op.create_table('raw_csv',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('symbol', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('price_usd', sa.Float(), nullable=True),
        sa.Column('last_updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.Column('ingested_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_raw_csv_external_id'), 'raw_csv', ['external_id'], unique=False)
    op.create_index(op.f('ix_raw_csv_id'), 'raw_csv', ['id'], unique=False)

    # Raw CoinGecko
    op.create_table('raw_coingecko',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('coin_id', sa.String(), nullable=True),
        sa.Column('symbol', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('current_price', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.Column('ingested_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_raw_coingecko_coin_id'), 'raw_coingecko', ['coin_id'], unique=False)
    op.create_index(op.f('ix_raw_coingecko_id'), 'raw_coingecko', ['id'], unique=False)

    # Unified Data
    op.create_table('unified_crypto_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('price_usd', sa.Float(), nullable=True),
        sa.Column('market_cap_usd', sa.Float(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('data_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ingested_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source', 'external_id', 'data_timestamp', name='uq_source_data_point')
    )
    op.create_index(op.f('ix_unified_crypto_data_id'), 'unified_crypto_data', ['id'], unique=False)
    op.create_index(op.f('ix_unified_crypto_data_source'), 'unified_crypto_data', ['source'], unique=False)
    op.create_index(op.f('ix_unified_crypto_data_symbol'), 'unified_crypto_data', ['symbol'], unique=False)

    # Checkpoints
    op.create_table('ingestion_checkpoints',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_name', sa.String(), nullable=True),
        sa.Column('last_ingested_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ingestion_checkpoints_id'), 'ingestion_checkpoints', ['id'], unique=False)
    op.create_index(op.f('ix_ingestion_checkpoints_source_name'), 'ingestion_checkpoints', ['source_name'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_ingestion_checkpoints_source_name'), table_name='ingestion_checkpoints')
    op.drop_index(op.f('ix_ingestion_checkpoints_id'), table_name='ingestion_checkpoints')
    op.drop_table('ingestion_checkpoints')
    
    op.drop_index(op.f('ix_unified_crypto_data_symbol'), table_name='unified_crypto_data')
    op.drop_index(op.f('ix_unified_crypto_data_source'), table_name='unified_crypto_data')
    op.drop_index(op.f('ix_unified_crypto_data_id'), table_name='unified_crypto_data')
    op.drop_table('unified_crypto_data')

    op.drop_index(op.f('ix_raw_coingecko_id'), table_name='raw_coingecko')
    op.drop_index(op.f('ix_raw_coingecko_coin_id'), table_name='raw_coingecko')
    op.drop_table('raw_coingecko')

    op.drop_index(op.f('ix_raw_csv_id'), table_name='raw_csv')
    op.drop_index(op.f('ix_raw_csv_external_id'), table_name='raw_csv')
    op.drop_table('raw_csv')

    op.drop_index(op.f('ix_raw_coinpaprika_id'), table_name='raw_coinpaprika')
    op.drop_index(op.f('ix_raw_coinpaprika_coin_id'), table_name='raw_coinpaprika')
    op.drop_table('raw_coinpaprika')
