# Install the Home Assistant ingress preview

This fork adds native **Open Web UI** and **Show in sidebar** support to Spoolman NG.
The add-on version is **2026.9.2.1**, using the unchanged Spoolman NG **2026.9.2** server image.

## Add the repository

Use [Add repository to Home Assistant](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FCedricGatay%2Fspoolman-ng-addons%23home-assistant-ingress),
or open **Settings → Add-ons → Add-on Store → ⋮ → Repositories** (called **Apps** in newer
Home Assistant versions) and add this exact URL:

```text
https://github.com/CedricGatay/spoolman-ng-addons#home-assistant-ingress
```

Keep `#home-assistant-ingress`: the fork's default branch does not contain the preview.
Home Assistant supports a `#branch` suffix on repository URLs; see its
[repository guide](https://contributors.home-assistant.io/apps/guides/repository/).

## Install and open

1. Find **Spoolman NG** under **Spoolman NG Add-ons (ingress preview)** and select **Install**.
   Installation builds the wrapper on your Home Assistant host and can take several minutes.
2. If the original Spoolman add-on is installed, take a Home Assistant backup including it.
   Keep that add-on installed. Disable its **Start on boot** and stop it before starting this
   preview on the same host port. The two instances cannot both bind host port 8000.
3. Copy your existing add-on configuration to the preview's **Configuration** tab, including
   database settings and any API token. Complete any inventory migration described below.
4. Select **Start**, then **Open Web UI**, and enable **Show in sidebar** on the preview's page.
   The sidebar panel is available to Home Assistant administrators.

If you only need ingress, disable the preview's host port 8000 in **Configuration → Network**.
Keep it mapped to the same host port as before if Moonraker, OctoPrint, or other integrations
connect directly. Port 8099 is internal and must not be published or forwarded.

The panel uses your existing Home Assistant connection, including remote HTTPS access and the
companion app. Existing Spoolman API-token or account login remains in effect.

## Preserve an existing inventory

**This is a separate installation, not an in-place upgrade.** Home Assistant derives add-on IDs
from the repository URL, including its branch, so the preview gets its own private `/data`
directory. Do not uninstall the original add-on until your inventory is verified in the preview.

- **External database:** copy the same database options into the preview and keep the original
  add-on stopped. The preview uses the same server release and database schema. The add-on's
  other local files still live in separate data directories.
- **Default SQLite database:** transfer the original add-on's complete `/data` contents to the
  preview's `/data` while both add-ons are stopped. This preserves `spoolman.db`, backups, local
  settings and authentication files together. It requires filesystem access to the add-on data
  through the Supervisor host; the ordinary File Editor does not expose these private directories.
  If the preview has not created its container yet, start it once with host port 8000 disabled,
  then stop it before copying data. Set the preview's options in Home Assistant as well: Supervisor
  manages `options.json` and rewrites it when the add-on starts.

For the underlying SQLite restore procedure, see
[Spoolman's backup documentation](https://github.com/sherrmann/Spoolman-NG/blob/v2026.9.2/docs/installation.md#backups--upgrades).
A Home Assistant backup of the original is a recovery copy; restoring that backup does not
automatically move its data into the fork's different add-on ID.

After migration, verify spool counts, a representative spool, login, and a printer integration.
For rollback, stop the preview and restart the original; keep only one writer connected to an
external database at a time.

## Updates and validation

Leave the repository URL unchanged to follow future versions published on this preview branch.
Use **Check for updates** in the store menu if it shows stale information. An installed add-on
needs a higher add-on version before Home Assistant offers an update; pushing code alone does
not update an existing installation.

Container checks cover ingress paths, authentication, WebSocket events, persistence and shutdown
on amd64, aarch64 and armv7. Actual Home Assistant sidebar behavior, external HTTPS and the
companion app still need validation on a live instance. The full checklist is in [TESTING.md](TESTING.md).
