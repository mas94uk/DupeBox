#!/usr/bin/python3

# Display duplicate files, as found by 'rdfind', for user to select files to delete.
import os
import random
import sys
from picwindow import PicWindow
from tkinter import *

args = sys.argv[1:]

# '--random' flag to randomise order
if "--random" in args:
    randomise = True
    args.remove("--random")
else:
    randomise = False

# '--worst' flag to do worst offenders first
if "--worst" in args:
    worst_first = True
    args.remove("--worst")
else:
    worst_first = False

# Take rdfind results filename as parameter, or default to results.txt
if len(args) > 0:
    results_filename = args[0]
else:
    results_filename = "results.txt"

if not os.path.isfile(results_filename):
    print(f"No such file {results_filename}")
    exit(-1)

# Read in the rdfind results
results = []    # Each item is a list of filenames of duplicate files.
record = []     # A single set of duplicates. Each item is a filename.
with open(results_filename, "r") as file:
    for line in file:
        # Skip "# Automatically generated"
        if line.startswith("# Automatically"):
            continue
        # Headers
        if line.startswith("# duptype"):
            columns = line.strip().split(" ")[1:]
            num_columns = len(columns)
            duptype_column = columns.index("duptype")
            name_column = columns.index("name")
            continue
        # Skip comments
        if line.startswith("#"):
            continue
        
        # A real result
        parts = line.split(" ", maxsplit=num_columns-1)
        duptype = parts[duptype_column]
        filename = parts[name_column]
        if filename.endswith("\n"):
            filename = filename[:-1]    # Remove only one \n in case the filename end with \n (unlikely but possible)

        # If it's the first file in a set of duplicates
        if "DUPTYPE_FIRST_OCCURRENCE" == duptype:
            # Store the previous set, if we have one
            if record:
                results.append(record)
            # Create the new set
            record = [filename]
        else:
            record.append(filename)

print(f"Found {len(results)} sets of duplicates")

if randomise:
    import random
    random.shuffle(results)
elif worst_first:
    results.sort(key=lambda x: len(x))
    results.reverse()

# Go through the files one at a time
num_deletes = 0
with open("delete.txt", "w")  as delete_file:
    for record in results:
        # Check we can find all the files
        all_present = True
        for filename in record:
            if not os.path.isfile(filename):
                all_present = False

        first_filename = record[0]
        if not all_present:
            print(f"Skipping {first_filename} (et al) as one or more duplicate files missing")
            continue

        # Currently only process JPGs. Maybe add other formats later.
        # We will assume the extension of the first file is correct and represents that of the other files.
        stem, ext = os.path.splitext(first_filename)
        ext = ext.lower().lstrip(".")
        if ext in PicWindow.SUPPORTED_FORMATS:
            # Offer them to the user
            root = Tk()
            app = PicWindow(record, root)
            root.mainloop()
        else:
            print(f"Skipping {first_filename} (et al) as extension {ext} not supported")
            continue

        # Get the results
        files_to_delete = app.results
        
        # Special case: results = None means quit
        if files_to_delete is None:
            print("Quitting")
            break

        for filename in files_to_delete:
            delete_file.writelines(f'rm "{filename}"\n')
        num_deletes += len(files_to_delete)

print(f"Marked {num_deletes} files for deletion")
