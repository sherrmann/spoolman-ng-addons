# Testing handoff: Spoolman NG add-on on a live Home Assistant

Instructions for verifying this add-on against a real Home Assistant Supervisor —
written as a self-contained handoff for a Claude Code session (VS Code with Docker
on Windows **or** Linux), but equally usable by a human.

**Host choice**: a Linux host (e.g. dual-booted Linux Mint) is the smoother option —
KVM/virt-manager runs the HAOS VM better than Hyper-V/VirtualBox, and Docker is
native rather than behind WSL2. Windows works for every path too; pick by
convenience. One warning either way: the *Supervised* installer (HA on a raw OS)
officially supports **Debian only** — Mint is Ubuntu-based and not supported, so do
not take that route; use the HAOS VM instead.

## Context

- This repository packages the [Spoolman NG](https://github.com/sherrmann/Spoolman-NG)
  server as a Home Assistant add-on. It has **never been exercised against a live
  Supervisor** — everything below exists to close that gap.
- The add-on is a thin wrapper: `spoolman_ng/Dockerfile` layers a launcher
  (`run.sh`) over the published multi-arch image
  `ghcr.io/sherrmann/spoolman-ng:<version>` (see `spoolman_ng/build.yaml` for the
  per-arch mapping). `run.sh` maps add-on options from `/data/options.json` to
  `SPOOLMAN_*` env vars and stores data under `/data`.
- Version in `spoolman_ng/config.yaml` tracks Spoolman NG releases automatically
  (pushed by the main repo's release pipeline).

## The one thing to know first

**Plain Home Assistant Container (`docker run …/home-assistant`) has NO add-on
store.** Add-ons require a Supervisor, which ships with Home Assistant OS or a
Supervised install. Do not burn time trying to make the container image show an
add-on store — it cannot. The three viable paths on a Windows workstation:

## Path A — Home Assistant OS in a VM (the real user flow; do this one)

Tests exactly what an end user does, including the add-a-repository UI flow.

1. Download the official HAOS VM image for your hypervisor
   (<https://www.home-assistant.io/installation/> → Windows or Linux):
   - **Linux / KVM (recommended on Mint)** → `.qcow2`:
     `sudo apt install qemu-kvm libvirt-daemon-system virt-manager`, add yourself
     to the `libvirt` group (re-login), then in virt-manager: import existing disk
     → the qcow2 → OS "Generic Linux", ≥2 GB RAM / 2 vCPU, and in the details
     enable **UEFI firmware (OVMF)** before first boot; default NAT network is fine.
   - Windows Hyper-V → `.vhdx` (needs Windows Pro; Gen-2 VM, Secure Boot off,
     ≥2 GB RAM, external switch)
   - Windows VirtualBox → `.vdi` (Linux Other 64-bit, EFI enabled, bridged network)
2. Boot, wait for onboarding at `http://homeassistant.local:8123` (or the VM's IP),
   create a user.
3. **Settings → Add-ons → Add-on Store → ⋮ → Repositories** → add
   `https://github.com/sherrmann/spoolman-ng-addons`
   - ✅ verify: the dialog accepts the URL (no "not a valid add-on repository")
     and a "Spoolman NG Add-ons" section appears with the add-on and its icon.
4. Open the add-on → **Install**. This builds the wrapper image locally on the VM
   (pulls `ghcr.io/sherrmann/spoolman-ng:<version>` first) — allow several minutes.
5. **Start** it, then open `http://<vm-ip>:8000`.

### Verification checklist (Path A)

- [ ] Repository URL accepted; add-on listed with icon and Documentation tab
- [ ] Install succeeds (check the add-on Log tab for build errors)
- [ ] Add-on starts; log shows uvicorn serving on port 8000
- [ ] Web UI loads at `:8000`; create a manufacturer + filament + spool
- [ ] `GET http://<vm-ip>:8000/api/v1/health` returns healthy
- [ ] **Persistence**: restart the add-on (and reboot the VM once) — the spool is
      still there (data lives in the add-on's `/data`)
- [ ] **Options mapping**: set `api_token` in the add-on Configuration tab, restart;
      `GET /api/v1/spool` without a header → 401, with
      `Authorization: Bearer <token>` → 200.
      `/api/v1/health` behavior is **version-dependent**: on base image ≤ 2026.7.6 the
      health endpoint (and `/docs`, `/auth/status`, `/auth/login`) wrongly requires the
      token too — do NOT configure a Supervisor `watchdog:` against it while a token is
      set on those versions. Fixed after 2026.7.6 (Spoolman-NG PR #210): health stays
      open with a token set, and a watchdog becomes safe.
- [ ] **Uninstall/reinstall** leaves no errors in the Supervisor log

## Path B — Add-on devcontainer (for iterating on the packaging)

Home Assistant publishes a devcontainer that runs a Supervisor **inside Docker**,
with this repository mounted as a local add-on — the fastest edit-rebuild-test
loop, and it works on Docker Desktop (WSL2 backend).

1. Clone this repo; open it in VS Code with the **Dev Containers** extension.
2. Follow the official guide for local add-on testing (it provides the
   `.devcontainer` config and the "Start Home Assistant" task):
   <https://developers.home-assistant.io/docs/add-ons/testing>
   — verify against that page rather than trusting this summary; the image and
   task names have changed over time.
3. Once Supervisor is up (HA on `localhost:7123`), the add-on appears under
   **Local add-ons**; install/start/verify as in Path A's checklist.
4. If the config proves stable, commit the `.devcontainer` setup to this repo so
   future testing is one click.

## Path C — arm64 / armv7 smoke via QEMU (no Supervisor)

A Windows/amd64 host can't reasonably run HAOS for ARM, but it can verify the
wrapper image **builds and boots** on each architecture via binfmt emulation.
(The base images themselves are already QEMU-boot-tested in the main repo's CI;
this covers the add-on layer.)

Linux (bash) — on Windows use the PowerShell variant below:

```bash
docker run --privileged --rm tonistiigi/binfmt --install arm64,arm

# once per arch: armv7 → linux/arm/v7, arm64 → linux/arm64, amd64 → linux/amd64
docker buildx build --platform linux/arm/v7 \
  --build-arg BUILD_FROM=ghcr.io/sherrmann/spoolman-ng:2026.7.6 \
  -t spoolman-addon-smoke:armv7 --load ./spoolman_ng/

# fake the Supervisor's options file, then boot it
mkdir -p data && echo '{"db_type": "sqlite"}' > data/options.json
docker run --rm --platform linux/arm/v7 -p 8000:8000 -v "$PWD/data:/data" spoolman-addon-smoke:armv7
```

```powershell
docker run --privileged --rm tonistiigi/binfmt --install arm64,arm
docker buildx build --platform linux/arm/v7 `
  --build-arg BUILD_FROM=ghcr.io/sherrmann/spoolman-ng:2026.7.6 `
  -t spoolman-addon-smoke:armv7 --load .\spoolman_ng\
mkdir data; '{"db_type": "sqlite"}' | Out-File -Encoding ascii data\options.json
docker run --rm --platform linux/arm/v7 -p 8000:8000 -v ${PWD}\data:/data spoolman-addon-smoke:armv7
```

- ✅ per arch: container starts (QEMU is slow — give armv7 a couple of minutes),
  `curl http://localhost:8000/api/v1/health` responds, and a created spool
  survives a container restart (SQLite in `.\data`).
- Match `BUILD_FROM` to the current tag in `spoolman_ng/build.yaml`.
- A *true* ARM Supervisor test (HAOS on a Raspberry Pi adding this repo URL) is
  the only remaining gap after this; treat it as optional hardware follow-up.

## Troubleshooting notes

- Repo rejected at step A3 → check `repository.yaml` is at the repo root and the
  add-on directory is a direct child (that layout is exactly why this repo exists).
- Install fails pulling the base image → confirm the tag in `build.yaml` exists on
  GHCR (`docker manifest inspect ghcr.io/sherrmann/spoolman-ng:<version>`).
- Add-on starts then dies → Log tab; `run.sh` is the first suspect (it must end by
  exec-ing `/home/app/spoolman/entrypoint.sh`).
- Port collision on 8000 → change the host port in the add-on's Network settings.

## Report back

For each path attempted: HA version, host (Hyper-V/VirtualBox/devcontainer), arch,
each checklist item pass/fail, and full add-on log excerpts for any failure.
File findings at <https://github.com/sherrmann/Spoolman-NG/issues> (mention #89).
