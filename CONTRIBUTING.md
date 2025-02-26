# Contributing

## Running Tests

```console
nox -s tests
```

## Running Type Checks

```console
nox -s lint
```

## Documentation

You can build documentation locally with [nox][nox]:

```
nox -s docs
```

> [!TIP]
> Consider to not use [serve][serve] for viewing the built documentation as it
> turns `/foo/index.html` into `/foo` paths and that completely breaks links.
> For weeks I thought this was some bug related to Sphinx or some of its
> plugins.

[nox]: https://github.com/wntrblm/nox
[serve]: https://github.com/vercel/serve
