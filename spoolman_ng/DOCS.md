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
   `https://github.com/sherrmann/spoolman-ng-addons`
2. Install **Spoolman NG** from the store and start it.
3. Open the web UI on port `8000` of your Home Assistant host.

The add-on is updated with every Spoolman NG release; updates appear in the Home Assistant UI
like any other add-on update.

## Opening the web UI

The UI is served on **host port 8000** — use the **OPEN WEB UI** button on the add-on page, or
browse to `http://<home-assistant-host>:8000` directly. There is no embedded (ingress) panel yet:
Home Assistant serves ingress under a rotating per-session path, which the server's static
`SPOOLMAN_BASE_PATH` cannot follow — a known limitation tracked upstream.

**Sidebar shortcut (works today, no ingress needed):** Home Assistant can embed any URL as a
dashboard — **Settings → Dashboards → Add dashboard → Webpage**, URL
`http://<home-assistant-host>:8000`. That puts Spoolman in the HA sidebar like a native panel.
Caveat: the embed is an iframe, so it works when you open Home Assistant over plain HTTP on your
LAN; if you access HA over HTTPS the browser blocks the plain-HTTP frame (mixed content) — use
the OPEN WEB UI button instead in that case.

**If port 8000 is already taken** on your host (the add-on then fails to start with a
"port is already allocated" error in its log), remap the host side under the add-on's
**Configuration → Network** settings — no rebuild needed, and the OPEN WEB UI button follows the
new port automatically. Integrations that talk to the REST API directly (Moonraker, OctoPrint,
the HACS integration) must then use the remapped port too.

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
