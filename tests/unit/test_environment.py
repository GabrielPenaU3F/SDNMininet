import pytest

from pathlib import Path

from config.environment import Environment

@pytest.fixture
def fake_env(tmp_path):
    env = Environment(project_root=tmp_path)
    return env


class TestEnvironmentBasics:

    def test_get_environment_returns_same_instance(self):
        env1 = Environment.get_environment()
        env2 = Environment.get_environment()

        assert env1 is env2

    def test_project_paths_are_relative_to_project_root(self):
        env = Environment.get_environment()

        expected_project_root = Path(__file__).resolve().parents[2]
        assert env.temp_path == expected_project_root / 'temp'
        assert env.controllers_path == expected_project_root / 'controllers'


class TestEnvironmentFilesystem:

    def test_environment_creates_controllers_directory(self, fake_env):
        assert fake_env.controllers_path.exists()
        assert fake_env.controllers_path.is_dir()

    def test_environment_creates_topologies_directory(self, fake_env):
        assert fake_env.topologies_path.exists()
        assert fake_env.topologies_path.is_dir()

    def test_environment_creates_experiments_directory(self, fake_env):
        assert fake_env.experiments_path.exists()
        assert fake_env.experiments_path.is_dir()

    def test_environment_creates_temp_directory(self, fake_env):
        assert fake_env.temp_path.exists()
        assert fake_env.temp_path.is_dir()
