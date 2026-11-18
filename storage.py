import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile


class Storage:
    def __init__(self, path):
        self.path = Path(path)

    def load(self):
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {"areas": {}, "feriados": [], "externos": []}

    def save(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=self.path.parent, delete=False
        ) as temporary:
            name = temporary.name
            try:
                json.dump(data, temporary, ensure_ascii=False, indent=2)
                temporary.close()
                os.replace(name, self.path)
            finally:
                temporary.close()
                Path(name).unlink(missing_ok=True)
