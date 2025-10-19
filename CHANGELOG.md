# Changelog

## [unreleased]

### Added

- Support for positionals with variable amount of values (#1).
- Implementation of `powercli.args.Flag.deprecation` to deprecate flags (#2).
- `powercli.utils.member_of` for easy integration of string enums.
- `--section` options for PowerDOC.
- Generate description for flags in manpage output in PowerDOC.
- Help output adds "default", "deprecated" and "required" tags if inferable.
- Support for examples via `powercli.command.Command.examples`.

### Changed

- Require Python 3.13 or greater.
- Deprecate `powercli.utils.static` in favor of `powercli.static.Static`.
- Better support for inspecting subcommand arguments (via
  `powercli.parser.ParsedCommand.subcommand()`).
- Usage section in help now includes parent commands names.
- `list` command and `--list` flag now display all nested subcommands.
- `list` command and `--list` flag now display commands with their description.

### Fixed

- Make `cmd -` and `cmd --` behave equivalent.

## [0.1.1] - 2025-06-18

### Changed

- Wider dependency range for `attrs` and `loguru`.

## [0.1.0] - 2025-03-14

Initial release.

[unreleased]: https://github.com/phoenixr-codes/powercli/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/phoenixr-codes/powercli/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/phoenixr-codes/powercli/releases/tag/v0.1.0
