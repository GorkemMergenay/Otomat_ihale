"""init schema

Revision ID: 20260306_0001
Revises:
Create Date: 2026-03-06 10:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260306_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="viewer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role", "users", ["role"], unique=False)
    op.create_index("ix_users_is_active", "users", ["is_active"], unique=False)

    op.create_table(
        "source_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("base_url", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("crawl_frequency", sa.String(length=80), nullable=False, server_default="0 */6 * * *"),
        sa.Column("config_json", sa.JSON(), nullable=False),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_failure_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_source_configs_name", "source_configs", ["name"], unique=True)
    op.create_index("ix_source_configs_is_active", "source_configs", ["is_active"], unique=False)
    op.create_index("ix_source_configs_source_type", "source_configs", ["source_type"], unique=False)

    op.create_table(
        "keyword_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_negative", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("matching_type", sa.String(length=50), nullable=False, server_default="contains"),
        sa.Column("target_field", sa.String(length=50), nullable=False, server_default="any"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_keyword_rules_keyword", "keyword_rules", ["keyword"], unique=False)
    op.create_index("ix_keyword_rules_category", "keyword_rules", ["category"], unique=False)
    op.create_index("ix_keyword_rules_is_active", "keyword_rules", ["is_active"], unique=False)
    op.create_index("ix_keyword_rules_is_negative", "keyword_rules", ["is_negative"], unique=False)

    op.create_table(
        "tenders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("normalized_title", sa.String(length=500), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_name", sa.String(length=255), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("publishing_date", sa.Date(), nullable=True),
        sa.Column("deadline_date", sa.Date(), nullable=True),
        sa.Column("tender_date", sa.Date(), nullable=True),
        sa.Column("institution_name", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("region", sa.String(length=120), nullable=True),
        sa.Column("tender_type", sa.String(length=120), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("extracted_keywords", sa.JSON(), nullable=False),
        sa.Column("match_explanation", sa.JSON(), nullable=False),
        sa.Column("relevance_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("commercial_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("technical_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("classification_label", sa.String(length=50), nullable=False, server_default="irrelevant"),
        sa.Column("official_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("signal_found", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="new"),
        sa.Column("assigned_to", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("dedupe_key", sa.String(length=255), nullable=False),
        sa.Column("content_checksum", sa.String(length=128), nullable=True),
        sa.Column("parser_version", sa.String(length=50), nullable=True),
        sa.Column("last_scored_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_tenders_id", "tenders", ["id"], unique=False)
    op.create_index("ix_tenders_normalized_title", "tenders", ["normalized_title"], unique=False)
    op.create_index("ix_tenders_source_type", "tenders", ["source_type"], unique=False)
    op.create_index("ix_tenders_source_name", "tenders", ["source_name"], unique=False)
    op.create_index("ix_tenders_external_id", "tenders", ["external_id"], unique=False)
    op.create_index("ix_tenders_publishing_date", "tenders", ["publishing_date"], unique=False)
    op.create_index("ix_tenders_deadline_date", "tenders", ["deadline_date"], unique=False)
    op.create_index("ix_tenders_institution_name", "tenders", ["institution_name"], unique=False)
    op.create_index("ix_tenders_city", "tenders", ["city"], unique=False)
    op.create_index("ix_tenders_total_score", "tenders", ["total_score"], unique=False)
    op.create_index("ix_tenders_classification_label", "tenders", ["classification_label"], unique=False)
    op.create_index("ix_tenders_official_verified", "tenders", ["official_verified"], unique=False)
    op.create_index("ix_tenders_signal_found", "tenders", ["signal_found"], unique=False)
    op.create_index("ix_tenders_status", "tenders", ["status"], unique=False)
    op.create_index("ix_tenders_dedupe_key", "tenders", ["dedupe_key"], unique=False)
    op.create_index("ix_tenders_content_checksum", "tenders", ["content_checksum"], unique=False)
    op.create_index(
        "ix_tender_dedupe_signature",
        "tenders",
        ["normalized_title", "institution_name", "publishing_date"],
        unique=False,
    )

    op.create_table(
        "tender_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tender_id", sa.Integer(), sa.ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_type", sa.String(length=120), nullable=True),
        sa.Column("document_url", sa.Text(), nullable=False),
        sa.Column("local_path", sa.Text(), nullable=True),
        sa.Column("parsed_text", sa.Text(), nullable=True),
        sa.Column("checksum", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_tender_documents_tender_id", "tender_documents", ["tender_id"], unique=False)
    op.create_index("ix_tender_documents_checksum", "tender_documents", ["checksum"], unique=False)

    op.create_table(
        "tender_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tender_id", sa.Integer(), sa.ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("event_data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_tender_events_tender_id", "tender_events", ["tender_id"], unique=False)
    op.create_index("ix_tender_events_event_type", "tender_events", ["event_type"], unique=False)

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tender_id", sa.Integer(), sa.ForeignKey("tenders.id", ondelete="SET NULL"), nullable=True),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("recipient", sa.String(length=255), nullable=False),
        sa.Column("notification_type", sa.String(length=80), nullable=False),
        sa.Column("delivery_status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_notifications_channel", "notifications", ["channel"], unique=False)
    op.create_index("ix_notifications_recipient", "notifications", ["recipient"], unique=False)
    op.create_index("ix_notifications_notification_type", "notifications", ["notification_type"], unique=False)
    op.create_index("ix_notifications_delivery_status", "notifications", ["delivery_status"], unique=False)
    op.create_index("ix_notifications_idempotency_key", "notifications", ["idempotency_key"], unique=True)

    op.create_table(
        "collector_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "source_config_id",
            sa.Integer(),
            sa.ForeignKey("source_configs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="running"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("items_discovered", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_created", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("snapshot_path", sa.Text(), nullable=True),
        sa.Column("parser_version", sa.String(length=50), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
    )
    op.create_index("ix_collector_runs_source_config_id", "collector_runs", ["source_config_id"], unique=False)
    op.create_index("ix_collector_runs_status", "collector_runs", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_collector_runs_status", table_name="collector_runs")
    op.drop_index("ix_collector_runs_source_config_id", table_name="collector_runs")
    op.drop_table("collector_runs")

    op.drop_index("ix_notifications_idempotency_key", table_name="notifications")
    op.drop_index("ix_notifications_delivery_status", table_name="notifications")
    op.drop_index("ix_notifications_notification_type", table_name="notifications")
    op.drop_index("ix_notifications_recipient", table_name="notifications")
    op.drop_index("ix_notifications_channel", table_name="notifications")
    op.drop_table("notifications")

    op.drop_index("ix_tender_events_event_type", table_name="tender_events")
    op.drop_index("ix_tender_events_tender_id", table_name="tender_events")
    op.drop_table("tender_events")

    op.drop_index("ix_tender_documents_checksum", table_name="tender_documents")
    op.drop_index("ix_tender_documents_tender_id", table_name="tender_documents")
    op.drop_table("tender_documents")

    op.drop_index("ix_tender_dedupe_signature", table_name="tenders")
    op.drop_index("ix_tenders_content_checksum", table_name="tenders")
    op.drop_index("ix_tenders_dedupe_key", table_name="tenders")
    op.drop_index("ix_tenders_status", table_name="tenders")
    op.drop_index("ix_tenders_signal_found", table_name="tenders")
    op.drop_index("ix_tenders_official_verified", table_name="tenders")
    op.drop_index("ix_tenders_classification_label", table_name="tenders")
    op.drop_index("ix_tenders_total_score", table_name="tenders")
    op.drop_index("ix_tenders_city", table_name="tenders")
    op.drop_index("ix_tenders_institution_name", table_name="tenders")
    op.drop_index("ix_tenders_deadline_date", table_name="tenders")
    op.drop_index("ix_tenders_publishing_date", table_name="tenders")
    op.drop_index("ix_tenders_external_id", table_name="tenders")
    op.drop_index("ix_tenders_source_name", table_name="tenders")
    op.drop_index("ix_tenders_source_type", table_name="tenders")
    op.drop_index("ix_tenders_normalized_title", table_name="tenders")
    op.drop_index("ix_tenders_id", table_name="tenders")
    op.drop_table("tenders")

    op.drop_index("ix_keyword_rules_is_negative", table_name="keyword_rules")
    op.drop_index("ix_keyword_rules_is_active", table_name="keyword_rules")
    op.drop_index("ix_keyword_rules_category", table_name="keyword_rules")
    op.drop_index("ix_keyword_rules_keyword", table_name="keyword_rules")
    op.drop_table("keyword_rules")

    op.drop_index("ix_source_configs_source_type", table_name="source_configs")
    op.drop_index("ix_source_configs_is_active", table_name="source_configs")
    op.drop_index("ix_source_configs_name", table_name="source_configs")
    op.drop_table("source_configs")

    op.drop_index("ix_users_is_active", table_name="users")
    op.drop_index("ix_users_role", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
