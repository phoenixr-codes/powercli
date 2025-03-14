import importlib.util as imp
import sys
from pathlib import Path
from typing import cast

from .builder import Builder
from .cli import cmd as cli
from .man import ManBuilder
from .markdown import MarkdownBuilder


def run() -> None:
    args = cli.parse_args()

    pyfile: Path = cast(Path, args.value_of("PATH"))
    [obj] = cast(list[str], args.value_of("obj"))

    mod_name = pyfile.stem
    spec = imp.spec_from_file_location(mod_name, pyfile.resolve())
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot import from path {pyfile}")
    mod = imp.module_from_spec(spec)
    sys.modules[mod_name] = mod
    try:
        spec.loader.exec_module(mod)
    except BaseException as e:
        raise RuntimeError(f"Failed to execute module {pyfile}: {e}") from e
    try:
        cmd = getattr(mod, obj)
    except AttributeError as e:
        raise AttributeError(
            "try using `--obj` to specify the name of the variable that hold the command"
        ) from e

    builder: Builder
    if args.is_present("build-man"):
        builder = ManBuilder(cmd)
    elif args.is_present("build-md"):
        builder = MarkdownBuilder(cmd)
    else:
        raise NotImplementedError()

    builder.build()
