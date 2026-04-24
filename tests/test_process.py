# SPDX-License-Identifier: LGPL-3.0-or-later
# SPDX-FileNotice: Part of the FreeCAD AI Agent Sidebar addon.

import unittest

from freecad.AIAgentSidebar.process import AgentProcess
from freecad.AIAgentSidebar.signals import SimpleSignal


class FakeProcess:
    def __init__(self) -> None:
        self.readyReadStandardOutput = SimpleSignal()
        self.readyReadStandardError = SimpleSignal()
        self.started = SimpleSignal()
        self.finished = SimpleSignal()
        self.errorOccurred = SimpleSignal()
        self.stdout = b""
        self.stderr = b""
        self.writes: list[bytes] = []
        self.started_with = None
        self.environment = None
        self.terminated = False
        self.input_closed = False

    def start(self, binary_path, args):
        self.started_with = (binary_path, args)
        self.started.emit()

    def write(self, payload):
        self.writes.append(payload)

    def setProcessEnvironment(self, environment):
        self.environment = environment

    def terminate(self):
        self.terminated = True

    def closeWriteChannel(self):
        self.input_closed = True

    def readAllStandardOutput(self):
        return self.stdout

    def readAllStandardError(self):
        return self.stderr


class AgentProcessTests(unittest.TestCase):
    def test_streams_fake_process_output_and_stderr(self) -> None:
        fake = FakeProcess()
        process = AgentProcess(process_factory=lambda: fake)
        stdout: list[str] = []
        stderr: list[str] = []
        started: list[bool] = []

        process.output_received.connect(stdout.append)
        process.error_received.connect(stderr.append)
        process.started.connect(lambda: started.append(True))

        process.start("/opt/homebrew/bin/codex", ["--test"])
        fake.stdout = b"hello"
        fake.stderr = b"warning"
        fake.readyReadStandardOutput.emit()
        fake.readyReadStandardError.emit()
        process.send("prompt")
        process.close_input()
        process.stop()

        self.assertEqual(fake.started_with, ("/opt/homebrew/bin/codex", ["--test"]))
        self.assertIsNotNone(fake.environment)
        self.assertEqual(stdout, ["hello"])
        self.assertEqual(stderr, ["warning"])
        self.assertEqual(fake.writes, [b"prompt\n"])
        self.assertTrue(fake.input_closed)
        self.assertTrue(fake.terminated)
        self.assertEqual(started, [True])


if __name__ == "__main__":
    unittest.main()
