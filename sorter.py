from pathlib import Path
import shutil
import config



destination_root =Path(config.destination_path)
entries = Path(config.source_path)
destination = Path(config.destination_path)
  
for entry in entries.iterdir():
    if entry.is_file():
        # make a subfolder 
        subfolder = destination_root / entry.suffix.lower().lstrip(".")
        subfolder.mkdir(parents=True, exist_ok=True)

        # copy the file into folder
        shutil.copy(entry, subfolder)
        print(f"Copied {entry.name} -> {subfolder}")