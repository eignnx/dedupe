from hashlib import md5
import os
import pickle
import pprint

class Manifest:
    def __init__(self, data=None):
        self.data = {} if data is None else data

    def scrape(self, start):
        self.start = os.path.expanduser(start)
        for root, dirs, files in os.walk(self.start):
            for filename in files:
                fullpath = os.path.join(root, filename)
                extension = os.path.splitext(filename)[1].upper()

                if extension != "":
                    byts = os.path.getsize(fullpath)
                    print("Adding", fullpath, byts, "bytes...")

                    try:
                        hsh = Manifest.file_hash(fullpath)
                    except OverflowError:
                        print()
                        print("\tOVERFLOW ERROR:", fullpath)
                        print()
                        continue

                    print("\twhich hash to ", hsh)

                    self.data[hsh] = {"Path":fullpath,
                                      "Ext":extension,
                                      "Bytes":byts}

    def export(self, filename="TempManifest.txt", path="~/Desktop"):
        os.chdir(os.path.expanduser(path))
        with open(filename, mode="wb") as outfile:
            pickle.dump(self.data, outfile)

    def load(self, filename="TempManifest.txt", path="~/Desktop"):
        os.chdir(os.path.expanduser(path))
        with open(filename, mode="rb") as infile:
            self.data = pickle.load(infile)

    def num_bytes(self):
        return sum( entry["Bytes"] for entry in self.data.values() )

    def unique_extensions(self):
        return { entry["Ext"] for entry in self.data.values() }

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def items(self):
        return self.data.items()

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    @classmethod
    def from_path(cls, path):
        M = cls()
        path = os.path.expanduser(path)
        M.load(os.path.basename(path), os.path.dirname(path))
        return M

    @staticmethod
    def file_hash(path):
        hasher = md5()
        with open(path, mode="rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hasher.update(chunk)
            return hasher.hexdigest()

    def __str__(self):
        return pprint.pformat(self.data)

    def __repr__(self):
        return "Manifest(" + str(self) + ")"


if __name__ == "__main__":
    M = Manifest()
    start_path = input("Enter a disk location to scrape from [example '~/Documents']: ")
    M.scrape(start_path)
    print()
    print("All files recorded:")
    print(M)
    print()
    print("--- Scraping complete ---")
    print("Searched through {} bytes of data from {} files".format(M.num_bytes(), len(M)))
    print("Found these unique file types: {}".format(M.unique_extensions()))
    print()
    save_file_name = input("Enter a file name to save the manifest to [example 'MoviesManifest.txt']: ")
    save_file_path = input("Enter a location to save the file to [example '~/Desktop']: ")
    M.export(filename=save_file_name, path=save_file_path)
    print()
    print("Manifest saved (pickled) to {}".format(
        os.path.join(save_file_path, save_file_name)))

