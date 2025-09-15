from pathlib import Path
import shutil
import config
import os



destination_root =Path(config.destination_path)
entries = Path(config.source_path)

print(f"[INFO] Scanning: {entries}")
if not entries.exists():
    print(f"[ERROR] Source path does not exist: {entries}")
    exit(1)
  
#count files to decide mode
def count_files_rglob(path):
    return sum(1 for p in path.rglob("*") if p.is_file())

def count_files_scandir(path):
    count = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                count += 1
            elif config.recursive and entry.is_dir():
                count += count_files_scandir(Path(entry.path))
    return count


print("[INFO] Counting files...")
estimated_files = count_files_rglob(entries)  # rglob is fine for counting, quick enough
print(f"[INFO] Found ~{estimated_files} files.")

#use method based on number of files returned by count
use_scandir = estimated_files > config.file_count_threshold
if use_scandir
    print(f"[INFO] Large dataset detected (> {config.file_count_threshold} files). Using os.scandir().")

#actually start doing stuff here

        