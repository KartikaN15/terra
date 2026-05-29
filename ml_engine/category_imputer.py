"""Category Imputer stub"""
from typing import Optional, Any


class CategoryImputer:
    def __init__(self):
        self.model = None

    def load(self, path: str):
        self.model = {"path": path}
