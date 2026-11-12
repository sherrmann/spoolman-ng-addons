# Spoolman NG add-on

Run the [Spoolman NG](https://github.com/sherrmann/Spoolman-NG) filament-inventory server as a
Home Assistant add-on — no separate Docker host needed. The add-on wraps the published
multi-arch `ghcr.io/sherrmann/spoolman-ng` image and stores all data in the add-on's
persistent `/data` volume.

> ⚠️ **Experimental.** This packaging has had limited exposure to live Supervisor installs.
> Please report problems on the [Spoolman NG issue tracker](https://github.com/sherrmann/Spoolman-NG/issues).

> This is different from the third-party [HACS integration](https://github.com/Disane87/spoolman-homeassistant),
> which *connects* Home Assistant to an existing Spoolman instance. This add-on *runs* Spoolman.

## Installation

1. Add this repository to the add-on store (**Settings → Add-ons → Add-on Store → ⋮ → Repositories**):
   `https://github.com/CedricGatay/spoolman-ng-addons#home-assistant-ingress`
2. Install **Spoolman NG** from the store and start it.
3. Select **Open Web UI** on the add-on page. Enable **Show in sidebar** for a shortcut.

This ingress preview installs as a separate add-on from the upstream repository, with its own
data directory. Existing inventory is not copied automatically. See the
[installation and migration guide](https://github.com/CedricGatay/spoolman-ng-addons/blob/home-assistant-ingress/INSTALL_INGRESS.md)
before switching an existing installation.

The add-on is updated with every Spoolman NG release; updates appear in the Home Assistant UI
like any other add-on update.

## Opening the web UI

Select **Open Web UI** on the add-on page to open Spoolman inside Home Assistant using
**ingress**. Enable **Show in sidebar** on that same page to add **Spoolman NG** to the sidebar.
The panel is available to Home Assistant administrators.

Ingress uses your existing Home Assistant connection, including HTTPS, remote access and the
companion app. Once Home Assistant itself is reachable remotely, Spoolman is reachable through
it too; no separate Spoolman port forwarding or webpage dashboard is needed. Home Assistant
requires a valid session before forwarding requests. If you configured a Spoolman API token or
Spoolman user accounts, Spoolman's own login still applies inside the panel.

**Direct access and integrations:** `http://<home-assistant-host>:8000` remains available for
printer integrations and direct browser access. This route uses Spoolman's own authentication,
independently of Home Assistant. If you only use ingress, you may disable the host port under
**Configuration → Network**. Keep it enabled for clients that use the REST API directly.
The internal ingress port `8099` is reserved for Supervisor and is not exposed on the host.

**If port 8000 is already taken** on your host (the add-on then fails to start with a
"port is already allocated" error in its log), remap the host side under the add-on's
**Configuration → Network** settings — no rebuild needed; ingress is independent of that mapping.
Integrations that talk to the REST API directly (Moonraker, OctoPrint,
the HACS integration) must then use the remapped port too.

**QR labels and PWA:** Ingress URLs belong to a Home Assistant session. Set Spoolman's `base_url`
web setting to a stable direct URL before printing QR labels. The installable PWA/service worker
is available only through direct access; the embedded panel uses Home Assistant's app instead.

## Data

The add-on stores everything — the default SQLite database, backups and cache — under its persistent
`/data` volume (`SPOOLMAN_DIR_DATA=/data`), so your inventory survives restarts and add-on updates.

## Configuration

By default the add-on uses the bundled SQLite database and needs no configuration. To use an external
database instead, set the options below (they map to Spoolman's standard `SPOOLMAN_DB_*` environment
variables):

| Option | Meaning |
|---|---|
| `db_type` | `sqlite` (default), `postgres`, `mysql`, or `cockroachdb` |
| `db_host` / `db_port` | External database host and port |
| `db_name` | Database name |
| `db_username` / `db_password` | Database credentials |
| `api_token` | Optional bearer token; when set, API requests must send `Authorization: Bearer <token>` |

Full server documentation (all environment variables, backups, monitoring, NFC, label printing)
lives in the [Spoolman NG repository](https://github.com/sherrmann/Spoolman-NG/tree/master/docs).

## Seeing Spoolman data inside Home Assistant

The add-on runs the Spoolman *server*. To get **entities** into Home Assistant — per-spool
devices with remaining-weight/usage sensors for dashboards and automations (e.g. "notify me
when PLA drops below 200 g") — pair it with the community
[Spoolman integration](https://github.com/Disane87/spoolman-homeassistant), installable via HACS:

1. Install the integration through HACS and restart Home Assistant.
2. Add it under **Settings → Devices & Services** and point it at the add-on:
   `http://<home-assistant-host>:8000` (or your remapped port).
3. Each spool appears as a device with sensors; the author also publishes a matching
   Lovelace card for dashboards.

Notes:
- The integration speaks the same REST/websocket API as every other Spoolman client, so it
  works against the add-on unchanged.
- If you set `api_token`, check that your integration version supports bearer
  authentication before enabling it — on a LAN-only Home Assistant install it is fine to
  leave the token empty.

## Printer integrations

The add-on exposes the standard Spoolman REST API on port `8000`, so Moonraker, OctoPrint,
and every other upstream-compatible client work unchanged — point them at
`http://<home-assistant-host>:8000`. Printer-side state (which spool is loaded, live usage
updates while printing) flows through Moonraker/Klipper or OctoPrint as usual and shows up
in Spoolman automatically.
