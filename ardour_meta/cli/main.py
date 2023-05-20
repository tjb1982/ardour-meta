#!/usr/bin/env python3
from datetime import datetime
import signal
import sqlite3
import sys, tempfile, os, time
import subprocess
from typing import List
import yaml
import argparse

import tkinter as tk
from tkinter import messagebox

from ardour_meta import models
from ardour_meta.cli.actions import range, region


# EDITOR = os.environ.get('EDITOR','vim')
# We need a GUI, so vim by itself doesn't work -- we need gvim or gedit, etc.
EDITOR = "gvim"
DOC_SEPARATOR = "\n---\n"

def message(title: str, message: str):
    root = tk.Tk()
    root.withdraw()
    # root.after(1000, root.destroy)
    messagebox.showinfo(title, message)
    root.mainloop()


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
    parser.add_argument("session_dir")

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

    try:
        with open(app.session_dir + "/session-id", "r") as f:
            session_id = f.read().strip()

        with models.connect(
            database=f"{app.appdata_directory}/data.sqlite"
        ) as conn:
            app._func(app, conn, session_id)
            models.clean_tags(conn)
    except BaseException as e:
        import traceback as tb
        message(
            "Ardour Meta: Error",
            str(e) + "\n\n" + ''.join(
                tb.format_exception(None, e, e.__traceback__)
            )
        )
        sys.exit(1)
