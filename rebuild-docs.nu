#!/usr/bin/env nu

# Script to rebuild documentation when changes are detected.
# This script is written in [Nushell](https://www.nushell.sh/).

use std log

let watch_path = ("docs" | path expand)

def skip-path [] {
  let outer_dir = ($in | path relative-to $watch_path | path split | first)
  (
    ($outer_dir | str starts-with ".") # not required for rebuild (e.g. `.mypy-cache`)
    or ($in | str ends-with "~")       # temporary files created by sphinx extension
    or ($outer_dir == "_build")        # generated files
    or ($outer_dir == "api")           # generated files
  )
}

def build-docs [] {
  poetry run sphinx-build -M html docs docs/_build
}

build-docs
run-external $env.BROWSER docs/_build/html/index.html

watch $watch_path {|operation, path, new_path|
  if ($path | skip-path) {
    log debug $"Skipping ($path)"
    return
  }
  log info $"($operation) ($path) ($new_path)"
  build-docs
}
