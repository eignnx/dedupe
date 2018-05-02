# dedupe.py
# An interactive program that compares two manifest.Manifest instances.
# If there is a duplicate file in both manifests, the user is given the
# option of deleting one of them.
#
# NOTE: No deletion happens until the program has finished.

from manifest import Manifest
import os
from collections import namedtuple
import time

def merge_dicts(Ds):
    merged = dict()
    for d in Ds:
        merged.update(d)
    return merged

class DedupeProgram:
    def __init__(self):
        self.kill_list = []
        self.menu_options = {"M": self.load_from_main,
                             "B": self.load_from_backup,
                             "F": self.add_filter_rules,
                             "R": self.review_dupes,
                             "D": self.delete_dupes,
                             "E": self.exit_program}

        self.extensions_ignored = set()
        self.main_manifests = []
        self.backup_manifests = []

        self.run = True
        self.main()

    def clearscreen(self):
        columns, rows = os.popen("stty size", "r").read().split()
        print("\n" * int(columns))

    def main(self):
        while self.run:
            self.clearscreen()
            print("---Dedupe Main Menu---")
            print("\t(M) Add manifest file for [M]AIN FILE SYSTEM")
            print("\t(B) Add manifest file for [B]ACKUP FILE SYSTEM")
            print("\t(F) Add [F]ILTER rules")
            if self.main_manifests and self.backup_manifests:
                print("\t(R) [R]EVIEW the {} duplicates you selected".format(len(self.kill_list)))
                if self.kill_list:
                    print("\t(D) [D]ELETE all {} selected duplicates".format(len(self.kill_list)))
            print("\t(E) [E]XIT program")

            inp = input("=> ")[0].upper()

            self.menu_options[inp]()
        print("Exited.")

    def load_from(self, selected_manifests, description):
        repeat_menu = True

        # Reset kill_list so changes must be reviewed before deletion.
        self.kill_list = []

        while repeat_menu:
            self.clearscreen()
            print("---Add manifest file from {}---".format(description.upper()))
            print("\tSelected manifest files:", end="\n\t\t")
            print("\n\t\t".join(selected_manifests) if selected_manifests else "None")
            print("\t(A) [A]DD to selected manifest files")
            print("\t(R) [R]EMOVE a manifest file")
            print("\t(E) [E]XIT to MAIN MENU")

            inp = input("=> ")[0].upper()

            if inp == "A":
                path = input("Enter the path to a manifest file: ")
                if os.path.isfile(os.path.expanduser(path)):
                    selected_manifests.append(path)
                else:
                    print("Invalid file path! Please try again.")
                    input("Press ENTER to continue.")
            elif inp == "R":
                path = input("Enter the path to a manifest file: ")
                if path in selected_manifests:
                    selected_manifests.remove(path)
                else:
                    print("Invalid filename! Please try again.")
                    input("Press ENTER to continue.")
            elif inp == "E":
                repeat_menu = False
            else:
                print("Please enter a valid command [A, R, E]")
                input("Press ENTER to continue.")

    def load_from_main(self):
        self.load_from(self.main_manifests, "main file system")

    def load_from_backup(self):
        self.load_from(self.backup_manifests, "backup file system")

    def add_filter_rules(self):
        repeat_menu = True

        # Reset kill_list so changes must be reviewed before deletion.
        self.kill_list = []

        while repeat_menu:
            self.clearscreen()
            print("---Modify Filter Rules---")
            print("\t(A) [A]DD to extensions specifically ignored: ", end="")
            print(self.extensions_ignored if self.extensions_ignored else "{}")
            print("\t(R) [R]EMOVE from extensions specifically ignored")
            print("\t(E) [E]XIT to MAIN MENU")

            inp = input("=> ")[0].upper()

            if inp == "A":
                msg = "Enter a (space separated) collection of file extensions that will be IGNORED.\n" + \
                      "[example '.jpeg .PNG .mov .TIFF']: "
                inp = input(msg)
                self.extensions_ignored.update({ ext.lower().strip() for ext in inp.split() })
            elif inp == "R":
                msg = "Enter a (space separated) collection of file extensions that will be REMOVED.\n" + \
                      "[example '.jpeg .PNG .mov .TIFF']: "
                inp = input(msg)
                self.extensions_ignored.difference_update({ ext.lower().strip() for ext in inp.split() })
            elif inp == "E":
                repeat_menu = False
            else:
                print("Please enter a valid command [A, R, E]")
                input("Press ENTER to continue.")

    def extension_filter(self, dup_pair):
        """
        Accepts a 'duplicate' namedtuple and checks if it's in
        the extensions_ignored list.
        """
        return dup_pair.main["Ext"].lower() not in self.extensions_ignored

    def review_dupes(self):
        self.clearscreen()
        print("---Display Filtered Duplicates---")
        print()

        # Load main and backup manifests from the given paths.
        main_mans = merge_dicts(Manifest.from_path(os.path.expanduser(path))
                        for path in self.main_manifests)
        backup_mans = merge_dicts(Manifest.from_path(os.path.expanduser(path))
                        for path in self.backup_manifests)

        # Define duplicate namedtuple class.
        duplicate = namedtuple("duplicate", ["main", "backup"])

        # Create list of duplicates.
        self.kill_list = list(filter(self.extension_filter,
            (duplicate(main=main_obj, backup=backup_obj)
                    for main_hash, main_obj in main_mans.items()
                    for backup_hash, backup_obj in backup_mans.items()
                    if main_hash == backup_hash)))

        # Display duplicates.
        print("{:^20}{:^50}{:^50}".format("Filesize (bytes)",
                                          "Name in Main Directory",
                                          "Name in Backup Directory"))
        
        for main, backup in self.kill_list:
            name_in_main = os.path.basename(main["Path"])
            name_in_backup = os.path.basename(backup["Path"])
            if name_in_main == name_in_backup:
                print("{:<10}{:^100}".format(main["Bytes"], name_in_main))
            else:
                print("{:<10}{:<55}{:<55}".format(main["Bytes"], name_in_main, name_in_backup))

        print()
        input("Press ENTER to continue.")

    def delete_dupes(self):
        self.clearscreen()
        print("---Delete Duplicates---")
        print()

        repeat_menu = True;

        while repeat_menu:
            print("\tThe following files will be deleted:")

            for main_file, _ in self.kill_list:
                print("\t", main_file["Path"])

            print()
            print("\t(D) [D]ELETE the files")
            print("\t(E) [E]XIT to main menu")
            inp = input("=> ")[0].upper()

            if inp == "D":
                print()
                print("Please CONFIRM DELETION of the files (this cannot be undone!)")
                inp = input("[Yes/No]: ").upper()

                if inp == "YES":
                    self.clearscreen()
                    bytes_removed = 0
                    for main_file, _ in self.kill_list:
                        bytes_removed += main_file["Bytes"]
                        print("DELETING: {}".format(main_file['Path']))
                        os.remove(main_file["Path"])

                    print()
                    print("{} bytes have been deleted from the MAIN FILE SYSTEM".format(bytes_removed))
                    print("The backup files are located here:")
                    print("\t", os.path.dirname(self.kill_list[0][1]["Path"]))
                    print()
                    input("Press ENTER to continue.")
                    repeat_menu = False
                    self.main_manifests = []
                    self.kill_list = []

                else:
                    self.clearscreen()
                    print("Files will NOT be deleted.")
                    print("Exiting to main menu...")
                    print()
                    input("Press ENTER to continue.")
                    repeat_menu = False
            elif inp == "E":
                repeat_menu = False
            else:
                print("Please enter a valid command [D, E]")
                input("Press ENTER to continue.")


    def exit_program(self):
        self.run = False

if __name__ == "__main__":
    p = DedupeProgram()





