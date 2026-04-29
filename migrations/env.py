# migrations/env.py

import logging
from logging.config import fileConfig

from flask import current_app
from alembic import context

# ── This is the Alembic Config object ────────────────────────────────────────
# It gives access to the values in alembic.ini
config = context.config

# ── Set up Python logging from the alembic.ini config ────────────────────────
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


def get_engine():
    try:
        # Flask-Migrate >= 3.0 way of getting the engine
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        # Fallback for older versions
        return current_app.extensions['migrate'].db.engine


def get_engine_url():
    try:
        return get_engine().url.render_as_string(hide_password=False).replace('%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')


# ── Tell Alembic which database URL to connect to ────────────────────────────
# This reads the SQLALCHEMY_DATABASE_URI from your Flask app config (.env)
# so you never have to hardcode your DB URL here
config.set_main_option('sqlalchemy.url', get_engine_url())

# ── This is the key fix ───────────────────────────────────────────────────────
# We get the MetaData object from Flask-Migrate which contains ALL your models
# (User, Transaction) — this is what Alembic compares against the real DB
# to figure out what tables/columns need to be created or changed
target_db = current_app.extensions['migrate'].db


def get_metadata():
    # Handles both single and multiple MetaData binds
    if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]
    return target_db.metadata


# ── Offline mode: generates SQL script without connecting to DB ───────────────
# Run with: flask db upgrade --sql
def run_migrations_offline():
    url = config.get_main_option('sqlalchemy.url')
    context.configure(
        url=url,
        target_metadata=get_metadata(),
        literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online mode: connects to DB and runs migrations directly ──────────────────
# This is what runs when you do: flask db upgrade
def run_migrations_online():
    def process_revision_directives(context, revision, directives):
        # This prevents Alembic from creating an empty migration file
        # when there are no changes detected in your models
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes detected in models — skipping empty migration')

    conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get('process_revision_directives') is None:
        conf_args['process_revision_directives'] = process_revision_directives

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            **conf_args
        )
        with context.begin_transaction():
            context.run_migrations()


# ── Entry point: Alembic calls this file and picks online vs offline ──────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()