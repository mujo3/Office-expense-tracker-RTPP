import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import logging
from logging.config import fileConfig

from rtpp_app import create_app
from rtpp_app.extensions import db

config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


app = create_app()


with app.app_context():

    config.set_main_option('sqlalchemy.url', str(db.engine.url).replace('%', '%%'))
    target_metadata = db.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    with app.app_context():
        connectable = db.engine

        conf_args = {}

        migrate_ext = getattr(app.extensions, 'migrate', None)
        if migrate_ext is not None:
            conf_args = migrate_ext.configure_args
            if conf_args.get("process_revision_directives") is None:
                conf_args["process_revision_directives"] = process_revision_directives

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                **conf_args
            )

            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
