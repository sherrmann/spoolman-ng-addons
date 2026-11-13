"""Run container integration checks: python3 tests/smoke.py <built-image>."""

import json
import subprocess
import sys
import uuid
from pathlib import Path

IMAGE = sys.argv[1]
NAME = f"spoolman-ingress-{uuid.uuid4().hex[:10]}"
NETWORK, VOLUME = f"{NAME}-net", f"{NAME}-data"
TESTS = str(Path(__file__).resolve().parent)


def docker(*args, check=True):
    result = subprocess.run(
        ["docker", *args], check=False, text=True, capture_output=True, timeout=180
    )
    if check and result.returncode:
        raise RuntimeError(
            f"docker {args[0]} failed:\n{result.stdout}\n{result.stderr}"
        )
    return result.stdout.strip()


def options(token):
    value = json.dumps({"db_type": "sqlite", "api_token": token})
    docker(
        "run",
        "--rm",
        "-v",
        f"{VOLUME}:/data",
        "--entrypoint",
        "python3",
        IMAGE,
        "-c",
        "import pathlib,sys; pathlib.Path('/data/options.json').write_text(sys.argv[1])",
        value,
    )


def client(token, mode="check", ip="172.30.32.2"):
    print(
        docker(
            "run",
            "--rm",
            "--network",
            NETWORK,
            "--ip",
            ip,
            "-v",
            f"{TESTS}:/tests:ro",
            "--entrypoint",
            "python3",
            IMAGE,
            "/tests/check_ingress.py",
            "172.30.32.3",
            token,
            mode,
        )
    )


try:
    # This isolated network reproduces Supervisor's documented source IP. Run outside HAOS.
    docker("network", "create", "--subnet", "172.30.32.0/24", NETWORK)
    docker("volume", "create", VOLUME)
    options("addon-smoke-test-token")
    docker(
        "run",
        "-d",
        "--name",
        NAME,
        "--network",
        NETWORK,
        "--ip",
        "172.30.32.3",
        "-v",
        f"{VOLUME}:/data",
        IMAGE,
    )
    client("addon-smoke-test-token")
    client("addon-smoke-test-token", "deny", "172.30.32.4")
    docker("stop", "--time", "10", NAME)
    assert docker("inspect", "-f", "{{.State.ExitCode}}", NAME) == "0", (
        "Unclean shutdown"
    )
    docker("start", NAME)
    client("addon-smoke-test-token", "persist")

    # Losing nginx must stop Spoolman and fail the whole container.
    docker("exec", NAME, "sh", "-c", "kill -TERM $(cat /run/nginx.pid)")
    assert docker("wait", NAME) == "1", "nginx exit did not fail the container"

    # Exercise the default no-token mode on the same persistent inventory.
    options("")
    docker("start", NAME)
    client("")
    # Conversely, losing Spoolman must stop nginx and fail the whole container.
    docker(
        "exec",
        NAME,
        "python3",
        "-c",
        "import os,signal; from pathlib import Path; "
        "children = Path('/proc/1/task/1/children').read_text().split(); "
        "pids = [int(pid) for pid in children if b'spoolman.main:app' in "
        "Path('/proc', pid, 'cmdline').read_bytes()]; "
        "assert len(pids) == 1, pids; os.kill(pids[0], signal.SIGTERM)",
    )
    assert docker("wait", NAME) == "1", "Spoolman exit did not fail the container"
    print("PASS: persistence, clean stop, and failure propagation for both services")
except BaseException:
    print(docker("logs", NAME, check=False), file=sys.stderr)
    raise
finally:
    docker("rm", "-f", NAME, check=False)
    docker("volume", "rm", VOLUME, check=False)
    docker("network", "rm", NETWORK, check=False)
