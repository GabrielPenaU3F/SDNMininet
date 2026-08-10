import argparse
import importlib
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--app-module', required=True)
    parser.add_argument('--app-class', required=True)
    parser.add_argument('--app-kwargs', default='{}')

    args = parser.parse_args()

    module = importlib.import_module(args.app_module)
    app_cls = getattr(module, args.app_class)

    kwargs = json.loads(args.app_kwargs)

    app = app_cls(**kwargs)
    app.run()


if __name__ == '__main__':
    main()