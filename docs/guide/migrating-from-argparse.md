# Migrating from `argparse`

## `nargs`

:::{tab} `argparse`

```python
parser.add_argument("--foo", nargs=2)
parser.add_argument("--bar", nargs="?", const="c", default="d")
parser.add_argument("infile", nargs="?", type=argparse.FileType("r"), default=sys.stdin)
parser.add_argument("--baz", nargs="*")
parser.add_argument("--boo", nargs="+")
```

:::

:::{tab} PowerCLI

```python
cmd.flag(long="foo", values=[("A", float), ("B", int)])  # PowerCLI requires hints and converters
# It's not possible to recreate `--bar` 1:1 in PowerCLI
cmd.pos(name="infile", into=lambda filepath: pathlib.Path(filepath).read_bytes(), default=lambda _ctx: sys.stdin.read())
# It's not possible to recreate `--baz` 1:1 in PowerCLI
cmd.flag(long="boo", values[("A", float), ...])  # PowerCLI requires hints and converters
```

:::

## `metavar`

:::{tab} `argparse`

```python
parser.add_argument("-x", nargs=2, metavar=("bar", "baz"))
```

:::

:::{tab} PowerCLI

```python
cmd.flag(short="x", values=[("bar", str), ("baz", str)])
```

:::

## Mutual exclusion

:::{tab} `argparse`

```python
group1 = parser.add_mutually_exclusive_group()
group1.add_argument('--foo', action='store_true')
group1.add_argument('--bar', action='store_false')

group2 = parser.add_mutually_exclusive_group(required=True)
group2.add_argument('--moo', action='store_true')
group2.add_argument('--meow', action='store_false')
```

:::

:::{tab} PowerCLI

```python
cmd.add_args(
    one_of(
        Flag(long="foo"),
        Flag(long="bar"),
    )
)

cmd.add_args(
    one_of(
        Flag(long="moo"),
        Flag(long="meow"),
    ),
    required=Static(True)
)
```

:::
