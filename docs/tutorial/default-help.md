# Display Help when no arguments are provided

It's common for commands to display a help message when no arguments or
subcommands were provided.

```python
from powercli import Command

cmd = Command()
cmd.flag(identifier="foo", long="foo")
cmd.flag(identifier="bar", long="bar")

if __name__ == "__main__":
    args = cmd.parse_args()
    if not args.raw_args:
        # If the user has not provided anything apart from the command itself ...
        args = cmd.parse_args([f"{cmd.prefix_long}help"])  # ... invoke the command with `--help`
    # ... do something with args ...
```
