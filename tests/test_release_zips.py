import pytest
from release_zips.release_zips import build_clone_command


class TestBuildCloneCommand:
    """Test cases for the build_clone_command function."""

    @pytest.mark.parametrize("git_url,tag,directory,git_extra_args,expected", [
        # Basic clone command without extra arguments
        (
            "https://github.com/example/repo.git",
            "v1.0.0",
            "repo-v1.0.0",
            None,
            ['git', 'clone', '--recursive', '--branch', 'v1.0.0',
             'https://github.com/example/repo.git', 'repo-v1.0.0']
        ),
        # Single extra git argument
        (
            "https://github.com/example/repo.git",
            "v2.1.0",
            "my-repo-v2.1.0",
            "--depth=1",
            ['git', 'clone', '--recursive', '--branch', 'v2.1.0',
             '--depth=1', 'https://github.com/example/repo.git', 'my-repo-v2.1.0']
        ),
        # Multiple extra git arguments
        (
            "https://github.com/example/repo.git",
            "v3.0.0-beta",
            "repo-v3.0.0-beta",
            "--depth=1 --single-branch --no-tags",
            ['git', 'clone', '--recursive', '--branch', 'v3.0.0-beta',
             '--depth=1', '--single-branch', '--no-tags',
             'https://github.com/example/repo.git', 'repo-v3.0.0-beta']
        ),
        # Empty git_extra_args string
        (
            "https://github.com/example/repo.git",
            "v1.5.0",
            "test-repo-v1.5.0",
            "",
            ['git', 'clone', '--recursive', '--branch', 'v1.5.0',
             'https://github.com/example/repo.git', 'test-repo-v1.5.0']
        ),
    ])
    def test_build_clone_command(self, git_url, tag, directory, git_extra_args, expected):
        """Test build_clone_command with various parameter combinations."""
        result = build_clone_command(git_url, tag, directory, git_extra_args)
        assert result == expected
