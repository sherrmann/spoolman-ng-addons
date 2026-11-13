"""Exercise the built add-on from a simulated Supervisor (or an untrusted peer)."""

import base64
import hashlib
import http.client
import json
import re
import struct
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

HOST, TOKEN, MODE = sys.argv[1:]
PREFIX = "/api/hassio_ingress/smokeSessionA"


def request(path, *, port=8099, prefix=PREFIX, token=TOKEN, data=None, method=None):
    headers = {"Host": "homeassistant.test", "X-Forwarded-Host": "homeassistant.test"}
    if prefix:
        headers["X-Ingress-Path"] = prefix
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data).encode()
    req = Request(
        f"http://{HOST}:{port}{path}", headers=headers, data=data, method=method
    )
    try:
        with urlopen(req, timeout=5) as response:
            return response.status, response.headers, response.read()
    except HTTPError as response:
        return response.code, response.headers, response.read()


for attempt in range(90):
    try:
        if request("/api/v1/health", port=8000, prefix=None)[0] == 200:
            break
    except (URLError, TimeoutError, ConnectionError):
        pass
    time.sleep(1)
else:
    raise AssertionError("Spoolman did not become ready within 90 seconds")

if MODE == "deny":
    # A forged header cannot grant access to the Supervisor-only listener.
    assert request("/")[0] == 403
    assert request("/api/v1/health", port=8000)[0] == 200
    print("PASS: untrusted peer denied ingress; direct listener reachable")
    sys.exit(0)

if MODE == "persist":
    status, _, body = request("/api/v1/spool")
    assert status == 200 and b"ingress smoke persisted" in body, body
    print("PASS: inventory survives restart")
    sys.exit(0)

for prefix in (PREFIX, "/api/hassio_ingress/smokeSessionB"):
    for path in ("/", "/spool", "/config.js", "/manifest.webmanifest"):
        status, headers, body = request(path, prefix=prefix)
        assert status == 200, (path, status, body)
        assert headers.get("Cache-Control") == "no-store", (path, headers)
        assert prefix.encode() in body, (path, body[:200])
        if path == "/config.js":
            assert b"window.SPOOLMAN_HA_INGRESS = true;" in body
        elif path == "/manifest.webmanifest":
            assert json.loads(body)["start_url"] == f"{prefix}/"
        elif path == "/":
            # Fetch the real bundled JS/CSS through the same prefix-stripped interface.
            assets = re.findall(rb'(?:src|href)="([^" ]+\.(?:js|css))"', body)
            assert assets, "No bundled assets found in the ingress document"
            for asset in assets:
                url = asset.decode()
                assert url.startswith(prefix + "/"), url
                assert request(url.removeprefix(prefix), prefix=prefix)[0] == 200, url

status, _, direct = request("/config.js", port=8000, prefix=None)
assert status == 200 and b'window.SPOOLMAN_BASE_PATH = "";' in direct
assert b"SPOOLMAN_HA_INGRESS" not in direct
for port in (8000, 8099):
    expected = 401 if TOKEN else 200
    assert request("/api/v1/spool", port=port, token="")[0] == expected
    assert request("/api/v1/spool", port=port, token="wrong-token")[0] == (
        401 if TOKEN else 200
    )
    assert request("/api/v1/spool", port=port)[0] == 200

# Open a real WebSocket through nginx and receive the event from a write through ingress.
conn = http.client.HTTPConnection(HOST, 8099, timeout=10)
key = base64.b64encode(b"0123456789abcdef").decode()
ws_headers = {
    "Host": "homeassistant.test",
    "Origin": "https://homeassistant.test",
    "X-Forwarded-Host": "homeassistant.test",
    "X-Ingress-Path": PREFIX,
    "Connection": "Upgrade",
    "Upgrade": "websocket",
    "Sec-WebSocket-Key": key,
    "Sec-WebSocket-Version": "13",
}
if TOKEN:
    ws_headers["Authorization"] = f"Bearer {TOKEN}"
conn.request("GET", "/api/v1/spool", headers=ws_headers)
response = conn.getresponse()
assert response.status == 101, (response.status, response.read())
expected_accept = base64.b64encode(
    hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()
).decode()
assert response.getheader("Sec-WebSocket-Accept") == expected_accept

status, _, filament = request(
    "/api/v1/filament",
    data={
        "name": "ingress smoke",
        "density": 1.24,
        "diameter": 1.75,
    },
)
assert status == 200, (status, filament)
status, _, spool = request(
    "/api/v1/spool",
    data={
        "filament_id": json.loads(filament)["id"],
        "initial_weight": 1000,
        "comment": "ingress smoke persisted",
    },
)
assert status == 200, (status, spool)


def read_exact(size):
    data = bytearray()
    while len(data) < size:
        chunk = response.fp.read(size - len(data))
        if not chunk:
            raise AssertionError("WebSocket closed before the inventory event")
        data.extend(chunk)
    return bytes(data)


# Ignore ping/control frames if any arrive before the event.
for _ in range(10):
    first, second = read_exact(2)
    size = second & 127
    if size == 126:
        size = struct.unpack("!H", read_exact(2))[0]
    elif size == 127:
        size = struct.unpack("!Q", read_exact(8))[0]
    payload = read_exact(size)
    if first & 15 == 1 and str(json.loads(spool)["id"]).encode() in payload:
        break
else:
    raise AssertionError("No spool change event received through ingress")
conn.close()
print(
    "PASS: session rotation, shell/assets, direct access, auth, writes and WebSocket events"
)
