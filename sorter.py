from pathlib import Path
import shutil
import config




entries = Path(config.source_path)
for entry in entries.iterdir():
    print(entry.name, entry.suffix)