"""Verify real child-process behavior without Docker or external dependencies."""

import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SUPERVISOR = Path(__file__).resolve().parents[1] / "spoolman_ng" / "supervise.py"
CHILD = """
from pathlib import Path
import os
import signal
import sys
import time

path = Path(sys.argv[1])
def stop(signum, frame):
    path.with_suffix('.stopped').touch()
    sys.exit(0)
signal.signal(signal.SIGTERM, signal.SIG_IGN if sys.argv[2] == 'stubborn' else stop)
path.write_text(str(os.getpid()))
while True:
    if path.with_suffix('.exit').exists():
        sys.exit(0)
    time.sleep(0.01)
"""


class SupervisorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def launch(self, *, stubborn=False, missing=False):
        self.ready = [self.root / "one.ready", self.root / "two.ready"]
        commands = [
            [
                sys.executable,
                "-c",
                CHILD,
                str(path),
                "stubborn" if stubborn else "normal",
            ]
            for path in self.ready
        ]
        if missing:
            commands[1] = [str(self.root / "missing-executable")]
        source = (
            "import runpy,sys; "
            f"module = runpy.run_path({str(SUPERVISOR)!r}); "
            f"sys.exit(module['supervise']({commands!r}, stop_timeout=0.3))"
        )
        self.process = subprocess.Popen(
            [sys.executable, "-c", source],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.addCleanup(self.cleanup_process, self.process)
        if not missing:
            self.wait_for(lambda: all(path.exists() for path in self.ready))

    def cleanup_process(self, process):
        if process.poll() is None:
            process.terminate()
        process.communicate(timeout=5)

    def wait_for(self, predicate):
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if predicate():
                return
            if self.process.poll() is not None:
                self.fail(f"Supervisor exited early: {self.process.communicate()}")
            time.sleep(0.01)
        self.fail("Timed out waiting for child processes")

    def test_sigterm_stops_both_services_cleanly(self):
        self.launch()
        self.process.send_signal(signal.SIGTERM)
        self.assertEqual(self.process.wait(timeout=5), 0)
        self.assertTrue(
            all(path.with_suffix(".stopped").exists() for path in self.ready)
        )

    def test_either_service_exit_fails_container_and_stops_peer(self):
        for index in (0, 1):
            with self.subTest(service=index):
                for path in self.root.iterdir():
                    path.unlink()
                self.launch()
                self.ready[index].with_suffix(".exit").touch()
                self.assertEqual(self.process.wait(timeout=5), 1)
                self.assertTrue(self.ready[1 - index].with_suffix(".stopped").exists())
                self.process.communicate()

    def test_unresponsive_services_do_not_block_shutdown(self):
        self.launch(stubborn=True)
        self.process.send_signal(signal.SIGTERM)
        self.assertEqual(self.process.wait(timeout=5), 0)
        for path in self.ready:
            with self.assertRaises(ProcessLookupError):
                os.kill(int(path.read_text()), 0)

    def test_spawn_failure_exits_instead_of_leaving_partial_service(self):
        self.launch(missing=True)
        self.assertNotEqual(self.process.wait(timeout=5), 0)


if __name__ == "__main__":
    unittest.main()
