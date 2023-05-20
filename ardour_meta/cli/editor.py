import subprocess
import tempfile
from typing import List

import yaml

from ardour_meta.models import Session


def compile_initial_message(
    session: Session,
    header: str,
    tag_names: List[str],
    text: str,
    separator: str,
):
    metadata = yaml.dump(
        dict([
            ("tags", tag_names),
        ]), default_flow_style=False,
    )

    session_id, session_name, *_ = session

    header = f"[{session_name} (id={session_id})]\n{header}"

    return separator.join([header, metadata, text])


def editor_session(
    session: Session,
    editor: str,
    header: str,
    tag_names: List[str],
    text: str,
    separator: str,
):
    initial_message = compile_initial_message(
        session,
        header,
        tag_names,
        text,
        separator,
    )

    # TODO: use the ".ardour-meta" dir to create a file with the
    # range/region id, etc., so that you can make use of a swap file
    # if the process exits early for some reason. I.e., not a tmpfile.

    # open a tempfile to allow the user to enter messages
    with tempfile.NamedTemporaryFile(suffix=".tmp") as f:
        # dump the existing data as yaml
        f.write(initial_message.encode())
        f.flush()

        # TODO: make this configurable
        editor = (
            "gvim -f -geometry 150x50 \"+colorscheme desert\" {file}"
                .format(file=f.name)
        )

        # open an editor and let the user edit the file
        proc = subprocess.Popen(["bash", "-c", editor])
        proc.wait()

        # we read the file
        f.seek(0)
        _, tagsDict, edited_message = f.read().decode().split(separator)
        tagsDict = yaml.safe_load(tagsDict)
        tag_names = set(tagsDict.get("tags"))
    
    return tag_names, edited_message
