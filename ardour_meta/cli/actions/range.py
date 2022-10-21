from argparse import ArgumentParser, Namespace
from datetime import datetime
import sqlite3

from ardour_meta import models
from ardour_meta.cli.editor import editor_session


def configure(parser: ArgumentParser):
    parser.add_argument("name")
    parser.add_argument("start", type=int)
    parser.add_argument("end", type=int)
    parser.set_defaults(
        _func=run,
    )


def run(app: Namespace, conn: sqlite3.Connection):
    session = models.fetch_or_create_session(
        conn, app.session_name, app.session_id
    )

    range = models.fetch_or_create_range(
        conn, session, app.name, app.start, app.end
    )
    
    tags = models.fetch_range_tags(conn, range)

    name, start, end, text, *_ = range

    header = (
        f"Range: {name} [{start} – {end}]"
        if start != end else
        f"Location: {name} at {start}"
    )

    tag_names, edited_message = editor_session(
        app.EDITOR,
        header=header,
        tag_names=[tag[0] for tag in tags],
        text=text,
        separator=app.DOC_SEPARATOR,
    )

    session_ended = datetime.utcnow().isoformat()

    name, start, end, _, created, *_ = range

    models.update_range(
        conn,
        (
            name,
            start,
            end,
            edited_message,
            app.session_name,
            app.session_id,
            created,
            session_ended,
        ),
    )

    models.update_range_tags(conn, range, tag_names)
