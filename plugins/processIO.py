#!/usr/bin/env python3
"""
    ClipRocks is a scripting tool for DaVinci Resolve that enables instant copying and pasting
    of content into the timeline, with optional AI-powered features such as background removal
    and image upscaling.

    Copyright: (C) 2025, coderocksai https://github.com/coderocksAI/ClipRocks
    youtube channel : https://www.youtube.com/@CodeRocks
    website : coderocks.fr 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import subprocess
import json

class ProcessIO:
    """
    A utility class for managing inter-process communication using subprocess.
    Provides methods to start a subprocess, send and receive messages, and handle errors.
    """

    def __init__(self, script_path, *args):
        """
        Initializes the ProcessIO with the script to be executed.

        :param script_path: Path to the script to execute.
        :param args: Additional arguments to pass to the script.
        """
        self.script_path = script_path
        self.args = args
        self.process = None

    def start_process(self):
        """
        Starts the subprocess with the specified script and arguments.
        """
        self.process = subprocess.Popen(
            ["python", self.script_path, *self.args],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    def send_message(self, message):
        """
        Sends a message to the subprocess via stdin.

        :param message: A dictionary or string to send to the subprocess.
        """
        if not self.process or self.process.stdin.closed:
            raise RuntimeError("Process is not running or stdin is closed.")

        if isinstance(message, dict):
            message = json.dumps(message)

        self.process.stdin.write(message + "\n")
        self.process.stdin.flush()

    def receive_message(self):
        """
        Receives a message from the subprocess via stdout.

        :return: A decoded message as a dictionary or raw string.
        """
        if not self.process or self.process.stdout.closed:
            raise RuntimeError("Process is not running or stdout is closed.")

        line = self.process.stdout.readline()
        if line:
            try:
                return json.loads(line.strip())
            except json.JSONDecodeError:
                return line.strip()
        return None

    def process_messages(self, callback):
        """
        Continuously processes messages from the subprocess and applies a callback to each.

        :param callback: A function to handle each message received from the subprocess.
        """
        if not self.process or self.process.stdout.closed:
            raise RuntimeError("Process is not running or stdout is closed.")

        while True:
            message = self.receive_message()
            if message is None:
                break
            callback(message)
            
    def wait_for_completion(self):
        """
        Waits for the subprocess to complete and returns the exit code.

        :return: Exit code of the subprocess.
        """
        if not self.process:
            raise RuntimeError("Process is not running.")

        self.process.wait()
        return self.process.returncode

    def handle_errors(self):
        """
        Retrieves and returns any errors from stderr.

        :return: A string containing the error messages.
        """
        if not self.process or self.process.stderr.closed:
            raise RuntimeError("Process is not running or stderr is closed.")

        return self.process.stderr.read().strip()

    def close(self):
        """
        Closes all open streams and terminates the process.
        """
        if self.process:
            if self.process.stdin:
                self.process.stdin.close()
            if self.process.stdout:
                self.process.stdout.close()
            if self.process.stderr:
                self.process.stderr.close()
            self.process.terminate()

# Example usage:
# parent = ProcessIO("child_script.py")
# parent.start_process()
# parent.send_message({"status": "start", "payload": "data"})
# print(parent.receive_message())
# parent.wait_for_completion()
# parent.close()
