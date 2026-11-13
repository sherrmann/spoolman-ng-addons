# Install and upgrade Spoolman NG with Home Assistant ingress

Spoolman NG supports native **Open Web UI** and **Show in sidebar** access through Home Assistant.
Add-on version **2026.9.2.1** enables ingress using the existing Spoolman NG **2026.9.2** server image.

## New installation

Use [Add repository to Home Assistant](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fsherrmann%2Fspoolman-ng-addons),
or open **Settings → Add-ons → Add-on Store → ⋮ → Repositories** (called **Apps** in newer
Home Assistant versions) and add:

```text
https://github.com/sherrmann/spoolman-ng-addons
```

1. Find **Spoolman NG** under **Spoolman NG Add-ons** and select **Install**. Installation builds
   the wrapper on your Home Assistant host and can take several minutes.
2. Set any external-database options or API token in the add-on's **Configuration** tab.
   SQLite is the default and needs no database configuration.
3. Select **Start**, then **Open Web UI**, and enable **Show in sidebar** on the add-on page.
   The sidebar panel is available to Home Assistant administrators.

## Update an existing installation

If Spoolman NG is already installed from this repository, update it through Home Assistant:

1. Take a Home Assistant backup including the add-on.
2. Select **Check for updates** in the store menu if the update is not listed, then install
   the available Spoolman NG add-on update.
3. Start the add-on if necessary, select **Open Web UI**, and enable **Show in sidebar**.

Updating the same add-on from the same repository preserves its configuration and persistent
`/data`, including inventory. No reinstall or manual data transfer is needed to enable ingress.
If switching between the classic and new Spoolman UI leaves an error page, refresh the page.

## Direct access and remote access

The panel uses your existing Home Assistant connection, including remote HTTPS access and the
companion app. Existing Spoolman API-token or account login remains in effect.

If you only need ingress, disable host port 8000 in **Configuration → Network**. Keep it mapped
if Moonraker, OctoPrint, SpoolmanSync or other integrations use the direct REST API. Those clients
should use `http://<home-assistant-host>:8000`, or the remapped host port. Port 8099 is internal
and must not be published or forwarded.

## Moving from another repository or branch

Home Assistant derives add-on IDs from the repository URL, including a branch suffix. Installing
from a different repository or branch therefore creates a separate add-on with its own private
`/data` directory. This applies when moving from a fork to this repository. See Home Assistant's
[repository guide](https://contributors.home-assistant.io/apps/guides/repository/).

Before moving, take a Home Assistant backup including the old add-on. Keep it installed, disable
its **Start on boot**, and stop it before starting the replacement on the same host port. The
two instances cannot both bind host port 8000. Copy the add-on options in Home Assistant as well
as any data; Supervisor manages `options.json` and rewrites it when an add-on starts.

- **External database:** configure the replacement with the same database options and keep the
  old add-on stopped. Check the server versions before reusing the database; do not connect an
  older server to a database migrated by a newer release. Other local files remain in separate
  add-on data directories.
- **Default SQLite database:** transfer the old add-on's complete `/data` contents to the
  replacement's `/data` while both add-ons are stopped. This preserves `spoolman.db`, backups,
  local settings and authentication files together. It requires filesystem access to the add-on
  data through the Supervisor host; the ordinary File Editor does not expose these private
  directories. If the replacement has not created its container yet, start it once with host
  port 8000 disabled, then stop it before copying data.

For the underlying SQLite restore procedure, see
[Spoolman's backup documentation](https://github.com/sherrmann/Spoolman-NG/blob/v2026.9.2/docs/installation.md#backups--upgrades).
Restoring a Home Assistant backup of the old add-on does not automatically move its data into
the replacement's different add-on ID.

Verify spool counts, a representative spool, login, and a printer integration before removing
the old installation. For rollback, stop the replacement and restart the old add-on; keep only
one writer connected to an external database at a time.

## Validation

Installation and ingress have been validated on a live Home Assistant instance. Container checks
cover ingress paths, authentication, WebSocket events, persistence and shutdown on amd64,
aarch64 and armv7. The dated validation record and reusable test procedures are in
[TESTING.md](TESTING.md).
