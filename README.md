# Sort files into folders based on extension with one file
## switches method based on dataset size to be most efficient
### use on any platform with python support aka almost anything

#### main goals of this program were small file size, cross-compatibility, speed and efficiency even on low end hardware and ease of use

this small program sorts through directories and copies out files with specific extensions (e.g. .pdf, .doc, .mp4 ect) to their own folders for human review


 all you need to do is edit these few lines on the top of the file


```py
# Config
SOURCE_PATH = r"put path here"
DESTINATION_PATH = r"where it should make output folders"
#remember to separate with , OUTSIDE OF ""
EXTENSIONS = [".doc", ".pdf", ".png", ".webp"]
#True to look through sub folders False to not
RECURSIVE = True
#how many files needed before switching copy method
FILE_COUNT_THRESHOLD = 2000
```


then run it with


linux
``` 
python3 file-sorter.py

```
windows
``` 
double click or
python file-sorter.py

```
