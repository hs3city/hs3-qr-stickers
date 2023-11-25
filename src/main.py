from local import stickers_folder           # Database information, fonts, paths to local folders
from sticker_generator import *             # Generating stickers and operations on them
import os

# TITLE:        QR CODE STICKER GENERATOR
# DESCRIPTION:  THE SCRIPT GENERATES A PNG STICKER WITH A QR CODE
# AUTHOR:       MARTA SIENKIEWICZ
# LICENSE:      MIT license

def main():
    generate_stickers()
    # merge_to_a4() # TO DO
    os.startfile(stickers_folder)

if __name__ == "__main__":
    main()


