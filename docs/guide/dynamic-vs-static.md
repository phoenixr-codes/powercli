# Dynamic vs Static

One main concept of PowerCLI is dynamic evaluation of certain attributes of
arguments. It's possible to dynamically evaluate whether an argument is required
and/or allowed.

For example, we can create a flag `-f` that is only required when flag `-g` is
present and set to `"Hello"`.

```python
from powercli import Command, Flag

cmd = Command(name="something")
cmd.flag(
    identifier="foo",
    short="f",
    required=lambda ctx: ctx.is_present("bar") and ctx.value_of("bar") == ["Hello"],
)
cmd.flag(
    identifier="bar",
    short="g",
    values=[("X", str)],
)
cmd.parse_args()
```

```console
something          # fine
something -g Hello # error: `-f` is required
something -g Bye   # fine
```
