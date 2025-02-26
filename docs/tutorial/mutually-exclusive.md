# Create mutually exclusive flags

```python
from powercli import Command
from powercli.utils import one_of, static

cmd = Command()
cmd.add_args(
    one_of(
        Flag(identifier="foo", long="foo"),
        Flag(identifier="bar", long="bar"),
        required=static(True),  # one of `foo` or `bar` **must** be present
    )
)
```

You can use any amount of flags.
