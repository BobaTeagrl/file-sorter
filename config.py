source_path = "/home/bobateagrl/Documents/copytest"
destination_path = "/home/bobateagrl/Documents/copytest/test"
extentions = [".docx"]
# If True, program will go through all subfolders too.
# If False, it will only look in the top-level folder.
recursive = True
# If estimated files > this number, use os.scandir() instead of rglob()
file_count_threshold = 2000
