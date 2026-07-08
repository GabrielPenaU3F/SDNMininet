from src.environment import Environment


def launch_program(host, script_path: str, **kwargs):
    args = _parse_kwargs_to_args(**kwargs)
    python_path = Environment.get_environment().python_path
    command = [
        python_path,
        script_path,
        *args
    ]
    return host.popen(command, env=Environment.get_env_dict())

def _parse_kwargs_to_args(**kwargs):
    args = []
    for key, value in kwargs.items():
        args.append(f"--{key}")
        args.append(str(value))
    return args