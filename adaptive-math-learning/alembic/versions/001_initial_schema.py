"""Initial database schema

Revision ID: 001
Revises:
Create Date: 2025-01-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Topics table
    op.create_table(
        'topics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('grade_range_start', sa.Integer(), nullable=True),
        sa.Column('grade_range_end', sa.Integer(), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('color', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('ix_topics_slug', 'topics', ['slug'])

    # Users table (for Supabase auth sync)
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), nullable=False),  # UUID from Supabase
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(100), nullable=True),
        sa.Column('grade_level', sa.Integer(), nullable=True),
        sa.Column('ab_group', sa.String(20), nullable=True),  # 'control' or 'treatment'
        sa.Column('total_xp', sa.Integer(), default=0, nullable=False),
        sa.Column('level', sa.Integer(), default=1, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Sessions table
    op.create_table(
        'sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_key', sa.String(50), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('topic_id', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('questions_attempted', sa.Integer(), default=0, nullable=False),
        sa.Column('questions_correct', sa.Integer(), default=0, nullable=False),
        sa.Column('session_type', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_key')
    )
    op.create_index('ix_sessions_user_id', 'sessions', ['user_id'])
    op.create_index('ix_sessions_session_key', 'sessions', ['session_key'])

    # Questions table
    op.create_table(
        'questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.String(50), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=True),
        sa.Column('topic_id', sa.Integer(), nullable=True),
        sa.Column('question_type', sa.String(50), nullable=False),
        sa.Column('expression', sa.Text(), nullable=False),
        sa.Column('correct_answer', sa.String(100), nullable=False),
        sa.Column('difficulty_score', sa.Float(), nullable=True),
        sa.Column('difficulty_tier', sa.Integer(), nullable=True),
        sa.Column('story_text', sa.Text(), nullable=True),
        sa.Column('visual_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id']),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('question_id')
    )
    op.create_index('ix_questions_question_id', 'questions', ['question_id'])

    # Responses table
    op.create_table(
        'responses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('user_answer', sa.String(100), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id']),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_responses_user_id', 'responses', ['user_id'])

    # Mastery table (BKT parameters)
    op.create_table(
        'mastery',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('p_l', sa.Float(), default=0.1, nullable=False),  # P(L₀) - Prior Knowledge
        sa.Column('p_t', sa.Float(), default=0.3, nullable=False),  # P(T) - Learn Rate
        sa.Column('p_g', sa.Float(), default=0.25, nullable=False), # P(G) - Guess Rate
        sa.Column('p_s', sa.Float(), default=0.1, nullable=False),  # P(S) - Slip Rate
        sa.Column('mastery_score', sa.Float(), default=0.1, nullable=False),
        sa.Column('difficulty_tier', sa.Integer(), default=1, nullable=False),
        sa.Column('attempts', sa.Integer(), default=0, nullable=False),
        sa.Column('correct', sa.Integer(), default=0, nullable=False),
        sa.Column('current_streak', sa.Integer(), default=0, nullable=False),
        sa.Column('best_streak', sa.Integer(), default=0, nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'topic_id', name='uix_user_topic_mastery')
    )
    op.create_index('ix_mastery_user_id', 'mastery', ['user_id'])

    # Badges table
    op.create_table(
        'badges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('badge_type', sa.String(50), nullable=False),
        sa.Column('earned_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'badge_type', name='uix_user_badge')
    )

    # A/B Test Events table (for PostHog backup)
    op.create_table(
        'ab_test_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('event_name', sa.String(100), nullable=False),
        sa.Column('ab_group', sa.String(20), nullable=False),
        sa.Column('properties', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ab_test_events_user_id', 'ab_test_events', ['user_id'])
    op.create_index('ix_ab_test_events_ab_group', 'ab_test_events', ['ab_group'])

    # Seed initial topics
    op.execute("""
        INSERT INTO topics (name, slug, description, grade_range_start, grade_range_end, icon, color) VALUES
        ('Aritmetik', 'arithmetic', 'Toplama, cikarma, carpma ve bolme islemleri', 1, 6, 'calculator', '#4F46E5'),
        ('Kesirler', 'fractions', 'Kesir islemleri ve sadestirme', 3, 8, 'pie-chart', '#10B981'),
        ('Yuzdeler', 'percentages', 'Yuzde hesaplamalari', 5, 9, 'analytics', '#F59E0B'),
        ('Cebir', 'algebra', 'Denklem cozme ve degiskenler', 6, 12, 'code-slash', '#EF4444'),
        ('Geometri', 'geometry', 'Alan, cevre ve hacim hesaplamalari', 4, 12, 'shapes', '#8B5CF6'),
        ('Oranlar', 'ratios', 'Oran ve orantilar', 5, 9, 'git-compare', '#06B6D4')
    """)


def downgrade() -> None:
    op.drop_table('ab_test_events')
    op.drop_table('badges')
    op.drop_table('mastery')
    op.drop_table('responses')
    op.drop_table('questions')
    op.drop_table('sessions')
    op.drop_table('users')
    op.drop_table('topics')
