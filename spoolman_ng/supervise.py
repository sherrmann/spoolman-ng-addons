"""Run nginx and Spoolman together, stopping the container if either service exits."""

import os
import signal
import subprocess
import sys
import time


def supervise(commands: list[list[str]], stop_timeout: float = 7) -> int:
    """Forward shutdown to both process groups and reap services before exiting."""
    stopping = False
    children: list[subprocess.Popen] = []

    def request_stop(signum, frame):
        nonlocal stopping
        stopping = True

    for signum in (signal.SIGTERM, signal.SIGINT):
        signal.signal(signum, request_stop)

    try:
        for command in commands:
            if stopping:
                return 0
            children.append(subprocess.Popen(command, start_new_session=True))

        while not stopping:
            for child in children:
                code = child.poll()
                if code is not None:
                    print(
                        f"Service {child.args[0]} exited with status {code}; stopping add-on.",
                        file=sys.stderr,
                        flush=True,
                    )
                    # Even a clean service exit is unexpected while the add-on is running.
                    return code if code > 0 else 1
            time.sleep(0.1)
        return 0
    finally:
        # Signal the groups even if their leader exited: descendants must not be left running.
        for child in children:
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        deadline = time.monotonic() + stop_timeout
        for child in children:
            try:
                child.wait(timeout=max(0, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()


if __name__ == "__main__":
    sys.exit(
        supervise(
            [
                ["/home/app/spoolman/entrypoint.sh"],
                ["nginx", "-g", "daemon off;"],
            ]
        )
    )
