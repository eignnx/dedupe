# dedupe
A utility program that deletes files from your disk if they are backed up in a different directory/drive.
## Requirements 
This program has been developed on macOS, but should work on any Unix system. I can't vouch for Windows...
## Instructions
First, you'll want to make two or more **manifest files** by running this command:
```
$ python3 manifest.py
```
This command will walk you through the process of creating a manifest. **Manifest files** contain md5 hashes of the files in all recursively-searched subdirectories of the manifest's root (which is chosen at creation time).
Once you've cataloged the files in your system, run:
```
$ python3 dedupe.py
```
Using the menu, you will need to select the manifest files you created previously, review the duplicates that were found, and then allow the program to delete the duplicates.  


---------------------------
Here is the code used to hash files (based on code shown by Raymond Hettinger):
```python
def file_hash(path):
    hasher = hashlib.md5()
    with open(path, mode="rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hasher.update(chunk)
        return hasher.hexdigest()
```
