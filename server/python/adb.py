"""ADB (Android Debug Bridge) server module.

This module handles:
- ADB command execution
- Device list management
- Port forwarding management
- Screen capture functionality
"""

import asyncio
import json
import logging
import subprocess
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ADBDevice:
    """Information about an ADB device."""

    device_id: str
    model: str | None = None
    product: str | None = None
    device: str | None = None
    transport_id: str | None = None


class ADBError(Exception):
    """Exception raised for ADB command errors."""

    pass


class ADBManager:
    """Manages ADB operations."""

    def __init__(self, adb_path: str = "adb") -> None:
        """Initialize the ADB manager.

        Args:
            adb_path: Path to adb executable (default: "adb")
        """
        self.adb_path = adb_path

    async def _run_command(
        self, args: list[str], timeout: int = 30
    ) -> tuple[str, str, int]:
        """Run an ADB command.

        Args:
            args: Command arguments
            timeout: Command timeout in seconds

        Returns:
            Tuple of (stdout, stderr, return_code)
        """
        cmd = [self.adb_path] + args
        logger.debug(f"Running ADB command: {' '.join(cmd)}")

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )
            return (
                stdout.decode("utf-8", errors="ignore"),
                stderr.decode("utf-8", errors="ignore"),
                process.returncode or 0,
            )
        except asyncio.TimeoutError:
            if process:
                process.kill()
                await process.wait()
            raise ADBError(f"Command timed out: {' '.join(cmd)}")
        except FileNotFoundError:
            raise ADBError(f"ADB executable not found: {self.adb_path}")

    async def get_devices(self) -> list[ADBDevice]:
        """Get list of connected devices.

        Returns:
            List of ADBDevice objects
        """
        stdout, stderr, code = await self._run_command(["devices", "-l"])

        if code != 0:
            logger.error(f"Failed to get devices: {stderr}")
            return []

        devices: list[ADBDevice] = []
        lines = stdout.strip().split("\n")

        for line in lines[1:]:  # Skip header line
            if not line.strip():
                continue

            parts = line.split()
            if len(parts) >= 2 and parts[1] == "device":
                device_id = parts[0]

                # Parse device info
                model = None
                product = None
                device = None
                transport_id = None

                for part in parts[2:]:
                    if part.startswith("model:"):
                        model = part.split(":", 1)[1]
                    elif part.startswith("product:"):
                        product = part.split(":", 1)[1]
                    elif part.startswith("device:"):
                        device = part.split(":", 1)[1]
                    elif part.startswith("transport_id:"):
                        transport_id = part.split(":", 1)[1]

                devices.append(
                    ADBDevice(
                        device_id=device_id,
                        model=model,
                        product=product,
                        device=device,
                        transport_id=transport_id,
                    )
                )

        return devices

    async def forward_port(
        self, device_id: str, local_port: int, remote_port: int
    ) -> bool:
        """Set up port forwarding.

        Args:
            device_id: Device serial number
            local_port: Local port
            remote_port: Remote/port on device

        Returns:
            True if successful
        """
        stdout, stderr, code = await self._run_command(
            ["-s", device_id, "forward", f"tcp:{local_port}", f"tcp:{remote_port}"]
        )

        if code != 0:
            logger.error(f"Forward failed: {stderr}")
            return False

        logger.info(f"Forwarded {device_id}: tcp:{local_port} -> tcp:{remote_port}")
        return True

    async def reverse_port(
        self, device_id: str, remote_port: int, local_port: int
    ) -> bool:
        """Set up reverse port forwarding.

        Args:
            device_id: Device serial number
            remote_port: Port on device
            local_port: Local port

        Returns:
            True if successful
        """
        stdout, stderr, code = await self._run_command(
            ["-s", device_id, "reverse", f"tcp:{remote_port}", f"tcp:{local_port}"]
        )

        if code != 0:
            logger.error(f"Reverse failed: {stderr}")
            return False

        logger.info(f"Reversed {device_id}: tcp:{remote_port} -> tcp:{local_port}")
        return True

    async def remove_forward(self, device_id: str, local_port: int) -> bool:
        """Remove port forwarding.

        Args:
            device_id: Device serial number
            local_port: Local port

        Returns:
            True if successful
        """
        stdout, stderr, code = await self._run_command(
            ["-s", device_id, "forward", "--remove", f"tcp:{local_port}"]
        )

        if code != 0:
            logger.error(f"Remove forward failed: {stderr}")
            return False

        logger.info(f"Removed forward {device_id}: tcp:{local_port}")
        return True

    async def screen_capture(self, device_id: str, path: str = "/sdcard/screenshot.png") -> str | None:
        """Capture screen to device file.

        Args:
            device_id: Device serial number
            path: Path on device to save screenshot

        Returns:
            Path to screenshot file
        """
        stdout, stderr, code = await self._run_command(
            ["-s", device_id, "shell", "screencap", "-p", path]
        )

        if code != 0:
            logger.error(f"Screen capture failed: {stderr}")
            return None

        logger.info(f"Screen captured to {path}")
        return path

    async def pull_file(self, device_id: str, remote_path: str, local_path: str) -> bool:
        """Pull file from device.

        Args:
            device_id: Device serial number
            remote_path: Path on device
            local_path: Local path

        Returns:
            True if successful
        """
        stdout, stderr, code = await self._run_command(
            ["-s", device_id, "pull", remote_path, local_path]
        )

        if code != 0:
            logger.error(f"Pull failed: {stderr}")
            return False

        logger.info(f"Pulled {remote_path} -> {local_path}")
        return True

    async def shell_command(self, device_id: str, command: str) -> tuple[str, str, int]:
        """Execute shell command on device.

        Args:
            device_id: Device serial number
            command: Shell command to execute

        Returns:
            Tuple of (stdout, stderr, return_code)
        """
        return await self._run_command(["-s", device_id, "shell", command])

    async def get_device_ip(self, device_id: str) -> str | None:
        """Get device IP address.

        Args:
            device_id: Device serial number

        Returns:
            IP address or None
        """
        stdout, stderr, code = await self._run_command(
            ["-s", device_id, "shell", "ip", "route", "get", "1.1.1.1"]
        )

        if code != 0:
            # Try alternative method
            stdout, stderr, code = await self._run_command(
                ["-s", device_id, "shell", "ip", "addr", "show", "wlan0"]
            )

            if code != 0:
                return None

        # Parse IP from output
        for line in stdout.split("\n"):
            if "src" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "src" and i + 1 < len(parts):
                        return parts[i + 1]

        return None

    async def connect_wireless(self, ip: str, port: int = 5555) -> bool:
        """Connect to device wirelessly.

        Args:
            ip: Device IP address
            port: Port (default: 5555)

        Returns:
            True if successful
        """
        stdout, stderr, code = await self._run_command(["connect", f"{ip}:{port}"])

        if code != 0:
            logger.error(f"Wireless connect failed: {stderr}")
            return False

        logger.info(f"Connected to {ip}:{port}")
        return True

    async def disconnect_device(self, device_id: str) -> bool:
        """Disconnect device.

        Args:
            device_id: Device serial number

        Returns:
            True if successful
        """
        stdout, stderr, code = await self._run_command(["disconnect", device_id])

        if code != 0:
            logger.error(f"Disconnect failed: {stderr}")
            return False

        logger.info(f"Disconnected {device_id}")
        return True


# Global ADB manager instance
_adb_manager: ADBManager | None = None


def get_adb_manager(adb_path: str = "adb") -> ADBManager:
    """Get the global ADB manager instance.

    Args:
        adb_path: Path to adb executable

    Returns:
        ADBManager instance
    """
    global _adb_manager
    if _adb_manager is None:
        _adb_manager = ADBManager(adb_path=adb_path)
    return _adb_manager
