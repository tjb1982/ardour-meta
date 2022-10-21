import subprocess
import tempfile
from typing import List

import yaml


def compile_initial_message(
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

    return separator.join([header, metadata, text])


def editor_session(
    editor: str,
    header: str,
    tag_names: List[str],
    text: str,
    separator: str,
):
    initial_message = compile_initial_message(
        header,
        tag_names,
        text,
        separator,
    )

    # open a tempfile to allow the user to enter messages
    with tempfile.NamedTemporaryFile(suffix=".tmp") as f:
        # dump the existing data as yaml
        f.write(initial_message.encode())
        f.flush()

        # open an editor and let the user edit the file
        proc = subprocess.Popen([editor, "-f", f.name])
        proc.wait()

        # we read the file
        f.seek(0)
        _, tagsDict, edited_message = f.read().decode().split(separator)
        tagsDict = yaml.safe_load(tagsDict)
        tag_names = set(tagsDict.get("tags"))
    
    return tag_names, edited_message
