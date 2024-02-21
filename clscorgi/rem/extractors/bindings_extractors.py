"""ReM bindings extractors"""

from pathlib import Path
from clscorgi.bindings_abc import BindingsExtractor


class ReMBindingsExtractor(BindingsExtractor):
    def __init__(self, header_path: Path):
        self.header_path = header_path
        super().__init__()

    def generate_bindings(self) -> dict:
        pass
