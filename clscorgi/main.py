"""Public entry point for the clscorgi script."""

import argparse

from collections.abc import Callable
from types import SimpleNamespace

from clscorgi.eltec.runner import eltec_runner
from clscorgi.rem.runner import rem_runner


runners = SimpleNamespace()
runners.eltec = eltec_runner
runners.rem = rem_runner


parser = argparse.ArgumentParser(
    prog="CLSCorGI",
    description="Main entry point for CLSCoR Graph generation.",
)
parser.add_argument("corpus", choices=runners.__dict__.keys())


if __name__ == "__main__":
    arg: str = parser.parse_args().__dict__["corpus"]

    runner: Callable = getattr(runners, arg)
    runner()
