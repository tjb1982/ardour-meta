from argparse import ArgumentParser, Namespace
from datetime import datetime
import sqlite3

from ardour_meta import models
from ardour_meta.cli.editor import editor_session


def configure(parser: ArgumentParser):
    parser.add_argument("name")
    parser.add_argument("start", type=int)
    parser.add_argument("length", type=int)
    parser.set_defaults(
        _func=run,
    )


def run(app: Namespace, conn: sqlite3.Connection):
    session = models.fetch_or_create_session(
        conn, app.session_name, app.session_id
    )

    region = models.fetch_or_create_region(
        conn, session, app.name, app.start, app.length
    )
    
    tags = models.fetch_region_tags(conn, region)

    name, start, length, text, *_ = region

    tag_names, edited_message = editor_session(
        app.EDITOR,
        header=f"Region: {name} (start: {start}, length: {length})",
        tag_names=[tag[0] for tag in tags],
        text=text,
        separator=app.DOC_SEPARATOR,
    )

    session_ended = datetime.utcnow().isoformat()

    name, start, length, _, created, *_ = region

    models.update_region(
        conn,
        (
            name,
            start,
            length,
            edited_message,
            app.session_name,
            app.session_id,
            created,
            session_ended,
        ),
    )

    models.update_region_tags(conn, region, tag_names)
