"""Create the directories for training."""

import shutil
from pathlib import Path
from typing import Tuple, Union

PathT = Union[Path, str]


def get_paths(
    base: PathT,
    scope: str,
    add=False,
    no_create=False,
    confirm=True,
) -> Tuple[Path, Path]:
    """Prepare the directories where models and logs are saved.

    This function can be used to create or return the directories used for
    training. The convention is the following: logs and models are saved
    respectively in the directories

        base/scope/<id>/models
        base/scope/<id>/logs

    :param base: the initial portion of the path.
    :param scope: some name that identifies a set of runs. For example,
        a training dataset name.
    :param add: keep old directories, add a new one.
    :param no_create: If True, do not create new directories, just return the
        most recent ones.
    :param confirm: if True, when a diretory needs to be deleted, it asks a
        confirm for deletion.
    :return: two paths, respectively for models and logs.
    """

    # Common path
    common_path = Path(base) / scope
    common_path.mkdir(parents=True, exist_ok=True)

    # Find most recent run
    run_dirs = {child.name for child in common_path.iterdir()}
    run_ids = {int(name) for name in run_dirs if name.isdigit()}
    runs_found = len(run_dirs) > 0
    last_run_id = max(run_ids) if runs_found else -1

    # Just return?
    if no_create:
        if not runs_found:
            raise RuntimeError("No previous run found")
        last_run = common_path / str(last_run_id)
        return last_run / "models", last_run / "logs"

    # Delete old ones
    if runs_found and not add:

        # Ask for confirm
        if confirm:
            print(f"Old runs under {common_path} will be deleted.")
            print("  Continue (Y/n)?", end=" ")
            c = input()
            if c not in ("y", "Y", ""):
                quit()

        # Delete and re-create
        shutil.rmtree(common_path)
        return get_paths(
            base=base,
            scope=scope,
            add=False,
            no_create=False,
            confirm=confirm,
        )

    # Create new
    run_path = common_path / str(last_run_id + 1)
    models_path = run_path / "models"
    logs_path = run_path / "logs"
    models_path.mkdir(parents=True)
    logs_path.mkdir(parents=True)

    return models_path, logs_path
