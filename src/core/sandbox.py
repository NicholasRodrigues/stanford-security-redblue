"""File system sandbox using Pathlib for path traversal prevention."""

from __future__ import annotations

from pathlib import Path


class SandboxError(Exception):
    """Raised when a path violates sandbox boundaries."""


class Sandbox:
    """Sandboxed file system access confined to a root directory."""

    def __init__(self, root: Path | str):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def validate_path(self, path: str | Path) -> Path:
        """Resolve a path and verify it's within the sandbox.

        Raises SandboxError if the path escapes the sandbox root.
        """
        resolved = (self.root / path).resolve()
        if not str(resolved).startswith(str(self.root)):
            raise SandboxError(
                f"Path traversal detected: '{path}' resolves to '{resolved}' "
                f"which is outside sandbox root '{self.root}'"
            )
        return resolved

    def read(self, path: str | Path) -> str:
        """Read a file within the sandbox."""
        resolved = self.validate_path(path)
        if not resolved.exists():
            raise FileNotFoundError(f"File not found in sandbox: {path}")
        return resolved.read_text()

    def write(self, path: str | Path, content: str) -> Path:
        """Write content to a file within the sandbox."""
        resolved = self.validate_path(path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content)
        return resolved

    def list_files(self, subdir: str = "") -> list[str]:
        """List files in the sandbox (relative paths)."""
        target = self.validate_path(subdir) if subdir else self.root
        if not target.is_dir():
            return []
        return [str(p.relative_to(self.root)) for p in target.rglob("*") if p.is_file()]
