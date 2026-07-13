import pytest

from pathlib import Path

from src.config.environment import Environment


@pytest.fixture
def env():
    Environment._reset_instance()
    return Environment.get_environment()


class TestEnvironmentBasics:

    def test_get_environment_returns_same_instance(self):
        env1 = Environment.get_environment()
        env2 = Environment.get_environment()

        assert env1 is env2

    def test_project_paths_are_relative_to_project_root(self, env):
        project_root = Path("/home/sskies/SDN")  # Change if necessary
        assert env.temp_path == project_root / 'temp'
        assert env.controllers_path == project_root / 'controllers'
        assert env.measurements_path == (
                project_root /
                'datasets' /
                'measurements'
        )


class TestEnvironmentFilesystem:

    def test_environment_creates_controllers_directory(self, env):
        assert env.controllers_path.exists()
        assert env.controllers_path.is_dir()

    def test_environment_creates_topologies_directory(self, env):
        assert env.topologies_path.exists()
        assert env.topologies_path.is_dir()

    def test_environment_creates_experiments_directory(self, env):
        assert env.experiments_path.exists()
        assert env.experiments_path.is_dir()

    def test_environment_creates_temp_directory(self, env):
        assert env.temp_path.exists()
        assert env.temp_path.is_dir()

    def test_environment_creates_measurements_directory(self, env):
        assert env.measurements_path.exists()
        assert env.measurements_path.is_dir()
