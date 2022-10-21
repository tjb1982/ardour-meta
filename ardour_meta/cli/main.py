#!/usr/bin/env python3
from datetime import datetime
import signal
import sqlite3
import sys, tempfile, os, time
import subprocess
from typing import List
import yaml
import argparse

from ardour_meta import models
from ardour_meta.cli.actions import range, region


# EDITOR = os.environ.get('EDITOR','vim')
# We need a GUI, so vim by itself doesn't work -- we need gvim or gedit, etc.
EDITOR = "gvim"
DOC_SEPARATOR = "\n---\n"


def daemonize_process():
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)

    pid = os.fork()
    if (pid != 0):
            time.sleep(1)
            sys.exit(0)

    os.setsid()


def main():
    daemonize_process()

    args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="TODO",
    )
    parser.add_argument("appdata_directory")
    parser.add_argument("session_name")
    parser.add_argument("session_id")

    parser.set_defaults(
        _func=lambda _: parser.print_help(),
        EDITOR=EDITOR,
        DOC_SEPARATOR=DOC_SEPARATOR,
    )

    subparsers = parser.add_subparsers(title="action")

    range.configure(subparsers.add_parser(
        "range",
        help="TODO",
    ))

    region.configure(subparsers.add_parser(
        "region",
        help="TODO",
    ))

    app = parser.parse_args(args)

    with models.connect(
        database=f"{app.appdata_directory}/data.sqlite"
    ) as conn:
        app._func(app, conn)
        models.clean_tags(conn)
