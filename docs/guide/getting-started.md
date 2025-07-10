# Getting Started

The first step is to create a new command.

```python
from powercli import Command

cmd = Command(
    name="prog",
    description="Short one-sentence description",
    long_description="Longer multi-sentence description.",
    add_common_flags=True,  # Add "help" and "list" flags
    add_common_subcommands=True,  # Add "help" and "list" subcommands
)
```

## Register Flags

The simplest way to register flags is by using the
{py:meth}`powercli.command.Command.flag` method:

```python
# ...

cmd.flag(
    identifier="foo",  # Unique identifier used to reference this argument
    short="f",  # A name that can be used when using the short prefix (commonly `-`)
    long="foo",  # A name that can be used when using the long prefix (commonly `--`)
    description="Short one-sentence description",
    long_description="Longer multi-sentence description",
)
```

Multiple flags can be combined when using their short name:

```console
prog -fg
```

## Register Positionals

The simplest way to register positionals is by using the
{py:meth}`powercli.command.Command.pos` method:

```python
# ...

from pathlib import Path

cmd.pos(
    identifier="file",  # Unique identifier used to reference this argument
    description="Short one-sentence description",
    long_description="Longer multi-sentence description",
    into=Path,  # Serialize the input (string) into a `Path` object
)
```

## Register Subcommands

```python
# ...

cmd.add_subcommand(
    Command(
        name="compile",
        description="Compile source code",
    )
)
```

## Parsing Arguments and Subcommands

The {py:meth}`powercli.command.Command.parse_args` method parses arguments
passed to the program. Alternatively you can explicitly specify which arguments
should be parsed instead of {py:obj}`sys.argv` by providing a list of strings as
an argument:

```python
# ...

if __name__ == "__main__":
    args = cmd.parse_args()
    
    if not args.raw_args:
        # Invoke help when no argument was provided by user
        args.parse_args([f"{cmd.prefix_long}help"])
        assert False, "unreachable"  # When the help flag is supplied then further execution stops
    
    if args.is_present("foo"):
        print("FOO")

    if (subargs := args.subcommand()) is not None and subargs.command.name == "compile":
        print("Compiling...")
    else:
        filepath = args.value_of("file")
        print(filepath.read_text())
```
