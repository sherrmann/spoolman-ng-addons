# Spoolman NG — Home Assistant add-on repository

Home Assistant add-on repository for [**Spoolman NG**](https://github.com/sherrmann/Spoolman-NG),
the community-maintained continuation of Spoolman: run the filament-inventory server as a
Supervisor add-on, no separate Docker host needed.

[![Add repository to my Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FCedricGatay%2Fspoolman-ng-addons%23home-assistant-ingress)

This branch is an **ingress preview** of the upstream add-on. Read
[the installation and inventory migration guide](INSTALL_INGRESS.md) before switching an
existing installation. The branch suffix in the repository URL is required.

## Installation

1. Click the badge above, or add this repository manually under
   **Settings → Add-ons → Add-on Store → ⋮ → Repositories**:
   `https://github.com/CedricGatay/spoolman-ng-addons#home-assistant-ingress`
2. Install **Spoolman NG** from the store and start it.
3. Select **Open Web UI** on the add-on page. Enable **Show in sidebar** for a shortcut.

Configuration options (external databases, API token) and details are in the add-on's
**Documentation** tab — or in [`spoolman_ng/DOCS.md`](spoolman_ng/DOCS.md).

## Add-ons

| Add-on | Description |
|---|---|
| [Spoolman NG](spoolman_ng/) | Track your 3D-printer filament spool inventory |

## Versioning

The add-on version tracks Spoolman NG releases: every release of
[sherrmann/Spoolman-NG](https://github.com/sherrmann/Spoolman-NG/releases) pushes a matching
version bump here, and Home Assistant then offers the update automatically. The add-on builds
from the published `ghcr.io/sherrmann/spoolman-ng` multi-arch image (`amd64`, `aarch64`, `armv7`).
Packaging-only releases add a fourth component (for example, add-on `2026.9.2.1` still
uses server image `2026.9.2`).

## Support

Issues and feature requests belong on the
[Spoolman NG issue tracker](https://github.com/sherrmann/Spoolman-NG/issues).

## License & attribution

[MIT](LICENSE), like the software it packages. Spoolman NG is a community-maintained
continuation of the original [Spoolman](https://github.com/Donkie/Spoolman) by
[Donkie](https://github.com/Donkie) (Daniel Hultgren), whose copyright the license retains.
This packaging follows the [Home Assistant add-on](https://developers.home-assistant.io/docs/add-ons)
conventions.
