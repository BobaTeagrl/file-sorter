from pathlib import Path
import shutil
import os
import time
from typing import Set, List

# Config
SOURCE_PATH = r"put path here"
DESTINATION_PATH = r"where it should make output folders"
#remember to separate with , OUTSIDE OF ""
EXTENSIONS = [".doc", ".pdf", ".png", ".webp"] 
#True to look through sub folders False to not
RECURSIVE = True
#how many files needed before switching copy method
FILE_COUNT_THRESHOLD = 2000

class FileSorter:
    def __init__(self, source_path: str, destination_path: str, extensions: List[str], 
                 recursive: bool = True, threshold: int = 2000):
        self.source_path = Path(source_path)
        self.destination_path = Path(destination_path)
        self.extensions = [ext.lower() for ext in extensions] if extensions else []
        self.recursive = recursive
        self.threshold = threshold
        self.copied_count = 0
        self.created_folders: Set[Path] = set()
        self.start_time = time.time()
        
    def validate_paths(self) -> bool:
        """Validate source and destination paths"""
        if not self.source_path.exists():
            print(f"[ERROR] Source path does not exist: {self.source_path}")
            return False
            
        if not self.source_path.is_dir():
            print(f"[ERROR] Source path is not a directory: {self.source_path}")
            return False
            
        return True
    
    def count_files_rglob(self) -> int:
        """Count files using rglob method"""
        try:
            if self.recursive:
                return sum(1 for p in self.source_path.rglob("*") if p.is_file())
            else:
                return sum(1 for p in self.source_path.iterdir() if p.is_file())
        except Exception as e:
            print(f"[WARNING] Error counting files with rglob: {e}")
            return 0
    
    def count_files_scandir(self, path: Path) -> int:
        """Count files using scandir method (recursive)"""
        count = 0
        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    if entry.is_file():
                        count += 1
                    elif self.recursive and entry.is_dir():
                        count += self.count_files_scandir(Path(entry.path))
        except (OSError, PermissionError) as e:
            print(f"[WARNING] Could not access {path}: {e}")
        return count
    
    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed based on extension"""
        if not self.extensions:  
            return True
        return file_path.suffix.lower() in self.extensions
    
    def create_destination_folder(self, file_path: Path) -> Path:
        """Create and return the destination folder for a file"""
        # Use extension without the dot as folder name
        folder_name = file_path.suffix.lower().lstrip(".") or "no_extension"
        subfolder = self.destination_path / folder_name
        
        if subfolder not in self.created_folders:
            try:
                subfolder.mkdir(parents=True, exist_ok=True)
                self.created_folders.add(subfolder)
                print(f"[INFO] Created folder: {subfolder}")
            except OSError as e:
                print(f"[ERROR] Could not create folder {subfolder}: {e}")
                return None
        
        return subfolder
    
    def process_file(self, file_path: Path, total_files: int):
        """Process a single file"""
        if not self.should_process_file(file_path):
            return
            
        # Skip if source file is within destination directory to avoid copying to itself
        try:
            if self.destination_path in file_path.parents or file_path == self.destination_path:
                return
        except (OSError, ValueError):
            pass  # Continue if path comparison fails
            
        try:
            subfolder = self.create_destination_folder(file_path)
            if subfolder is None:
                return
                
            destination_file = subfolder / file_path.name
            
            # Skip if file already exists and is identical
            if destination_file.exists():
                try:
                    # Check if files are identical (same size and modification time)
                    source_stat = file_path.stat()
                    dest_stat = destination_file.stat()
                    if (source_stat.st_size == dest_stat.st_size and 
                        abs(source_stat.st_mtime - dest_stat.st_mtime) < 1):
                        print(f"[SKIP] File already exists: {file_path.name}")
                        return
                except OSError:
                    pass  # If stat fails, continue with copy
                
                # Handle file name conflicts for different files
                counter = 1
                original_stem = file_path.stem
                while destination_file.exists():
                    new_name = f"{original_stem}_{counter}{file_path.suffix}"
                    destination_file = subfolder / new_name
                    counter += 1
            
            shutil.copy2(file_path, destination_file)  # copy2 preserves metadata
            self.copied_count += 1
            
            # Progress indicator
            elapsed = time.time() - self.start_time
            rate = self.copied_count / elapsed if elapsed > 0 else 0
            print(f"[{self.copied_count}/{total_files}] Copied: {file_path.name} "
                  f"({rate:.1f} files/sec)")
                  
        except (OSError, shutil.Error) as e:
            print(f"[ERROR] Could not copy {file_path}: {e}")
    
    def scan_rglob(self, total_files: int):
        """Scan files using rglob method"""
        try:
            iterator = (self.source_path.rglob("*") if self.recursive 
                       else self.source_path.iterdir())
            
            for entry in iterator:
                if entry.is_file():
                    self.process_file(entry, total_files)
        except Exception as e:
            print(f"[ERROR] Error during rglob scan: {e}")
    
    def scan_scandir(self, folder: Path, total_files: int):
        """Scan files using scandir method (recursive)"""
        try:
            with os.scandir(folder) as entries:
                for entry in entries:
                    if entry.is_file():
                        self.process_file(Path(entry.path), total_files)
                    elif self.recursive and entry.is_dir():
                        self.scan_scandir(Path(entry.path), total_files)
        except (OSError, PermissionError) as e:
            print(f"[ERROR] Could not scan {folder}: {e}")
    
    def sort_files(self):
        """Main method to sort files"""
        print(f"[INFO] Starting file sorter...")
        print(f"[INFO] Source: {self.source_path}")
        print(f"[INFO] Destination: {self.destination_path}")
        print(f"[INFO] Extensions: {self.extensions or 'All files'}")
        print(f"[INFO] Recursive: {self.recursive}")
        
        if not self.validate_paths():
            return
        
        # Count files
        print("[INFO] Counting files...")
        estimated_files = self.count_files_rglob()
        
        if estimated_files == 0:
            print("[INFO] No files found to process.")
            return
            
        print(f"[INFO] Found approximately {estimated_files} files.")
        
        # Choose method based on file count
        use_scandir = estimated_files > self.threshold
        if use_scandir:
            print(f"[INFO] Large dataset detected (>{self.threshold} files). Using scandir method.")
        else:
            print("[INFO] Using rglob method.")
        
        # Process files
        if use_scandir:
            self.scan_scandir(self.source_path, estimated_files)
        else:
            self.scan_rglob(estimated_files)
        
        # Final report
        elapsed = time.time() - self.start_time
        print(f"\n[INFO] Completed in {elapsed:.2f} seconds.")
        print(f"[INFO] {self.copied_count} files copied successfully.")
        print(f"[INFO] Created {len(self.created_folders)} destination folders.")

def main():
    sorter = FileSorter(
        source_path=SOURCE_PATH,
        destination_path=DESTINATION_PATH,
        extensions=EXTENSIONS,
        recursive=RECURSIVE,
        threshold=FILE_COUNT_THRESHOLD
    )
    
    try:
        sorter.sort_files()
    except KeyboardInterrupt:
        print(f"\n[INFO] Operation cancelled by user. {sorter.copied_count} files copied before interruption.")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

if __name__ == "__main__":
    main()