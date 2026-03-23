"""Tests for core/sandbox.py."""

import pytest

from src.core.sandbox import Sandbox, SandboxError


class TestSandbox:
    def test_read_existing_file(self, sandbox):
        content = sandbox.read("public/note1.txt")
        assert "Public company policy" in content

    def test_read_nonexistent_file(self, sandbox):
        with pytest.raises(FileNotFoundError):
            sandbox.read("nonexistent.txt")

    def test_write_and_read(self, sandbox):
        sandbox.write("test.txt", "hello world")
        content = sandbox.read("test.txt")
        assert content == "hello world"

    def test_write_creates_subdirectory(self, sandbox):
        sandbox.write("new_dir/file.txt", "content")
        content = sandbox.read("new_dir/file.txt")
        assert content == "content"

    def test_path_traversal_dotdot(self, sandbox):
        with pytest.raises(SandboxError, match="Path traversal"):
            sandbox.read("../../etc/passwd")

    def test_path_traversal_absolute(self, sandbox):
        with pytest.raises(SandboxError, match="Path traversal"):
            sandbox.read("/etc/passwd")

    def test_path_traversal_write(self, sandbox):
        with pytest.raises(SandboxError, match="Path traversal"):
            sandbox.write("../../../tmp/evil.txt", "hacked")

    def test_list_files(self, sandbox):
        files = sandbox.list_files()
        assert len(files) >= 4  # 2 public + 2 private
        assert any("note1.txt" in f for f in files)

    def test_list_files_subdir(self, sandbox):
        files = sandbox.list_files("public")
        assert len(files) == 2
        assert all("public" in f for f in files)

    def test_validate_path_normal(self, sandbox):
        path = sandbox.validate_path("public/note1.txt")
        assert path.exists()
