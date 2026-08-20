# Changelog

The add-on version mirrors [Spoolman NG releases](https://github.com/sherrmann/Spoolman-NG/releases);
each entry links the matching server release notes (upstream tags are `v`-prefixed).

## 2026.8.0

- Server changes: <https://github.com/sherrmann/Spoolman-NG/releases/tag/v2026.8.0>

## 2026.7.14

- Server changes: <https://github.com/sherrmann/Spoolman-NG/releases/tag/v2026.7.14>

## 2026.7.13

- Server changes: <https://github.com/sherrmann/Spoolman-NG/releases/tag/v2026.7.13>

## 2026.7.12

- Server changes: <https://github.com/sherrmann/Spoolman-NG/releases/tag/v2026.7.12>

## 2026.7.10

- Server changes: <https://github.com/sherrmann/Spoolman-NG/releases/tag/v2026.7.10>

## 2026.7.9

- Server changes: <https://github.com/sherrmann/Spoolman-NG/releases/tag/v2026.7.9>

## 2026.7.8

- Server changes: <https://github.com/sherrmann/Spoolman-NG/releases/tag/v2026.7.8>

## 2026.7.7

- Fix: with `api_token` (or user accounts) set, the server wrongly required authentication on
  `/api/v1/health`, `/docs` and even the login endpoint itself. Health is open again, so a
  Supervisor `watchdog` is safe to use alongside a token from this version on.
- Server changes: <https://github.com/sherrmann/Spoolman-NG/releases/tag/v2026.7.7>

## 2026.7.6

- First store-installable packaging: repository manifest at the git root, installable by URL, with
  automatic version bumps on every Spoolman NG release.
- **OPEN WEB UI** button on the add-on page (`webui:`), plus documentation for the port-collision
  remap path.
- Server changes: <https://github.com/sherrmann/Spoolman-NG/releases/tag/v2026.7.6>
