# Implement a "Verbose" Flag

Many programs with a command-line interface provide a flag to enable verbose
output like logging messages. The more the flag is specified, the more is the
level of verbosity. For example using `-v` would only output warnings whereas
`-vvv` outputs warnings, info and debug messages.

```python
import logging

from powercli import Command, Static
from powercli.methods import Count


cmd = Command()
cmd.flag(
    identifier="verbose",
    short="v",
    long="verbose",
    description="Enables verbosity up to 5 different levels",
    method=Count(lambda _, amount: amount in range(1, 6), default=Static(2)),
)

if __name__ == "__main__":
    args = cmd.parse_args()
    level = {
        # show critical logs on `-v`
        1: logging.CRITICAL,

        # show critical logs and error logs on `-vv`
        2: logging.ERROR,

        # show critical logs, error logs and warning logs on `-vvv`
        3: logging.WARNING,

        # show critical logs, error logs, warning logs and info logs on `-vvvv`
        4: logging.INFO,

        # show critical logs, error logs, warning logs, info logs and debug logs on `-vvvvv`
        5: logging.DEBUG,
    }[args.value_of("verbose")]
    logging.basicConfig(level=level)
    # ... do something with args ...
```
