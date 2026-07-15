from typing import List

from config.environment import Environment

class HostProgramLauncher:

    def launch(self, mn_process_launcher, script_path: str, **kwargs):
        command = self._build_command(script_path, **kwargs)
        return mn_process_launcher.popen(command, env=Environment.get_env_dict())

    def _build_command(self, script_path: str, **kwargs) -> List[str]:
        python_path = Environment.get_environment().python_path
        args = self._build_command_args(**kwargs)
        command = [
            python_path,
            script_path,
            *args
        ]
        return command

    @staticmethod
    def _build_command_args(**kwargs):
        args = []
        for key, value in kwargs.items():
            args.append(f'--{key}')
            args.append(str(value))
        return args
