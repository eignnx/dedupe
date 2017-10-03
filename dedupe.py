# dedupe.py
# An interactive program that compares two manifest.Manifest instances.
# If there is a duplicate file in both manifests, the user is given the
# option of deleting one of them.
#
# NOTE: No deletion happens until the program has finished.

from manifest import Manifest
import os

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
        self.extensions_sought = set()
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
            if len(self.kill_list) > 0:
                print("\t(R) [R]EVIEW the {} duplicates you selected".format(len(self.kill_list)))
                print("\t(D) [D]ELETE all {} selected duplicates".format(len(self.kill_list)))
            print("\t(E) [E]XIT program")

            inp = input("=> ")[0].upper()

            self.menu_options[inp]()
        print("Exited.")

    def load_from_main(self):
        repeat_menu = True

        while repeat_menu:
            self.clearscreen()
            print("--Add manifest file from MAIN FILE SYSTEM---")
            print("\tSelected manifest files:", end="\n\t\t")
            print("\n\t\t".join(self.main_manifests) if self.main_manifests else "None")
            print("\t(A) [A]DD to selected manifest files")
            print("\t(R) [R]EMOVE a manifest file")
            print("\t(E) [E]XIT to MAIN MENU")

            inp = input("=> ")[0].upper()

            if inp == "A":
                path = input("Enter the path to a manifest file: ")
                if os.path.isfile(os.path.expanduser(path)):
                    self.main_manifests.append(path)
                else:
                    print("Invalid file path! Please try again.")
                    input("Press ENTER to continue.")
            elif inp == "R":
                path = input("Enter the path to a manifest file: ")
                if path in self.main_manifests:
                    self.main_manifests.remove(path)
                else:
                    print("Invalid filename! Please try again.")
                    input("Press ENTER to continue.")
            elif inp == "E":
                repeat_menu = False
            else:
                print("Please enter a valid command [A, R, E]")
                input("Press ENTER to continue.")
            

    def load_from_backup(self):
        print("Loading from backup")

    def add_filter_rules(self):
        repeat_menu = True
        
        while repeat_menu:
            self.clearscreen()
            print("---Modify Filter Rules---")
            print("\t(I) Add to extensions specifically [I]GNORED: ", end="")
            print(self.extensions_ignored if self.extensions_ignored else "{}")
            print("\t(S) Add to extensions specifically [S]OUGHT: ", end="")
            print(self.extensions_sought if self.extensions_sought else "{}")
            print("\t(E) [E]XIT to MAIN MENU")

            inp = input("=> ")[0].upper()

            if inp == "I":        
                msg = "Enter a (space separated) collection of file extensions that will be IGNORED.\n" + \
                      "[example '.jpeg .PNG .mov .TIFF']: "
                inp = input(msg)
                self.extensions_ignored.update({ ext.lower().strip() for ext in inp.split() })
            elif inp == "S":        
                msg = "Enter a (space separated) collection of file extensions that will be SOUGHT.\n" + \
                      "[example '.jpeg .PNG .mov .TIFF']: "
                inp = input(msg)
                self.extensions_sought.update({ ext.lower().strip() for ext in inp.split() })
            elif inp == "E":
                repeat_menu = False
            else:
                print("Please enter a valid command [I, S, E]")
                input("Press ENTER to continue.")

            confused_extensions = list(self.extensions_ignored.intersection(self.extensions_sought))
            while confused_extensions:
                ext = confused_extensions[0]
                print()
                print("'{}' is being both IGNORED and SOUGHT.".format(ext))
                print("Should it be [I]GNORED or [S]ought?")
                inp = input("=> ")[0].upper()
                if inp == "I":
                    self.extensions_sought.remove(ext)
                    confused_extensions.remove(ext)
                elif inp == "S":
                    self.extensions_ignored.remove(ext)
                    confused_extensions.remove(ext)
                else:
                    print("Please enter a valid command [I, S]")

    def review_dupes(self):
        print("Selecting dupes")

    def delete_dupes(self):
        print("Deleting dupes")

    def exit_program(self):
        self.run = False

if __name__ == "__main__":
    p = DedupeProgram()
        
    
    

    
