import asyncio
import os
import subprocess
from typing import Any

from aiohttp import web
from server import PromptServer

import folder_paths

_PICKER_LOCK = asyncio.Lock()


def _get_default_directory(directory_type: str | None) -> str:
    if directory_type == "output":
        return os.path.abspath(folder_paths.get_output_directory())

    return os.path.abspath(folder_paths.get_input_directory())


def _normalize_initial_path(initial_path: str | None, directory_type: str | None) -> str:
    if not initial_path:
        return _get_default_directory(directory_type)

    normalized = os.path.abspath(os.path.expanduser(initial_path))
    if os.path.isdir(normalized):
        return normalized

    return _get_default_directory(directory_type)


def _pick_directory_tk(initial_path: str) -> str | None:
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    try:
        root.attributes("-topmost", True)
    except Exception:
        pass

    try:
        selected = filedialog.askdirectory(
            initialdir=initial_path,
            title="Select image folder",
            mustexist=True,
            parent=root,
        )
        return selected or None
    finally:
        root.destroy()


def _pick_directory_powershell(initial_path: str) -> str | None:
    escaped_path = initial_path.replace("'", "''")
    command = rf"""
Add-Type -AssemblyName System.Windows.Forms
$dialog = New-Object System.Windows.Forms.FolderBrowserDialog
$dialog.Description = 'Select image folder'
$dialog.UseDescriptionForTitle = $true
$dialog.ShowNewFolderButton = $false
$dialog.SelectedPath = '{escaped_path}'
$result = $dialog.ShowDialog()
if ($result -eq [System.Windows.Forms.DialogResult]::OK) {{
    [Console]::Write($dialog.SelectedPath)
}}
"""

    completed = subprocess.run(
        ["powershell", "-NoProfile", "-STA", "-Command", command],
        capture_output=True,
        text=True,
        check=False,
    )

    if completed.returncode not in (0, 1):
        stderr = completed.stderr.strip()
        raise RuntimeError(stderr or "PowerShell folder picker failed.")

    selected = completed.stdout.strip()
    return selected or None


def _pick_directory(initial_path: str) -> str | None:
    try:
        return _pick_directory_tk(initial_path)
    except Exception:
        if os.name == "nt":
            return _pick_directory_powershell(initial_path)
        raise


async def _run_picker(initial_path: str) -> str | None:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _pick_directory, initial_path)


@PromptServer.instance.routes.post("/image_anything/pick-folder")
async def pick_folder(request: web.Request) -> web.Response:
    payload: dict[str, Any] = {}

    if request.can_read_body:
        try:
            payload = await request.json()
        except Exception:
            payload = {}

    initial_path = _normalize_initial_path(
        payload.get("initial_path"),
        payload.get("directory_type"),
    )

    try:
        async with _PICKER_LOCK:
            selected_path = await _run_picker(initial_path)
    except Exception as exc:
        return web.json_response(
            {
                "status": "error",
                "message": f"Failed to open folder picker: {exc}",
            },
            status=500,
        )

    if not selected_path:
        return web.json_response({"status": "cancelled"})

    return web.json_response(
        {
            "status": "success",
            "path": os.path.abspath(selected_path),
        }
    )
