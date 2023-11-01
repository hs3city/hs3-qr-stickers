from local import source_sans_pro, stickers_folder, tree_sha
import os
import io
from PIL import Image, ImageFont, ImageDraw  # Generating images
import segno  # Generating QR code for the sticker
from github import Github  # Using REST API of the database


# ------------------------------DATA FOR STICKERS----------------------------------#
# ----------------------------------CONSTANTS--------------------------------------#
WHITE = (255, 255, 255)  # White
BLACK = (0, 0, 0)  # Black
A4_SIZE = [2480, 3508]  # px -> 210x297 mm in 300 dpi

# ----------------------------------VARIABLES--------------------------------------#
qr_size = 370  # px - QR code size
sticker_h = 500  # px
sticker_w = 400  # px
font_height = 40  # px
sticker_font = ImageFont.truetype(source_sans_pro, font_height)

# ------------------------CALCULATIONS BASED ON VARIABLES--------------------------#
sticker_margin = int((sticker_w - qr_size) / 2)  # px
label_start_y = 2 * sticker_margin + qr_size  # px


# -----------------------------GENERATING STICKERS---------------------------------#
def generate_sticker(file):
    """
    Generate a single QR sticker.
    """
    project_name = file.path.split(".")[0]
    url = f"https://hs3.pl/projekty/{project_name}"
    qrcode = segno.make_qr(url)
    out = io.BytesIO()
    qrcode.save(out, border=0, scale=5, kind="png")
    out.seek(0)  # Important to let PIL / Pillow load the image
    qr_img = Image.open(out)  # Done, do what ever you want with the PIL/Pillow image
    qr_img = qr_img.resize((qr_size, qr_size))
    background = Image.new(mode="RGB", size=(sticker_w, sticker_h), color=WHITE)
    background.paste(qr_img, [sticker_margin, sticker_margin])
    draw = ImageDraw.Draw(background)
    draw.text(
        (sticker_margin, label_start_y), project_name, font=sticker_font, fill=BLACK
    )
    end_folder = stickers_folder + os.path.sep + project_name + ".png"
    background.save(end_folder)


def generate_stickers():
    """
    Generate QR stickers based on all files in the repository folder.
    """
    g = Github()
    repo = g.get_repo("hs3city/hs3.pl")
    tree = repo.get_git_tree(tree_sha["content/pl/projekty"]).tree
    for file in tree:
        if file.path[0] != "_":
            print(file)
            generate_sticker(file)


# -----------------------------MERGING STICKERS TO A4 PAGE---------------------------------#


def merge_to_a4():
    """
    TO DO - Merge generated stickers to A4 sheets in pdf.
    """
    stickers_per_row = 9
    stickers_pdf_name = os.path.join(stickers_folder, "stickers_merged.pdf")

    sticker_counter = 1
    page_counter = 1
    offset_x = 100
    offset_y = 0
    background = Image.new(mode="RGB", size=A4_SIZE, color=WHITE)
    for root, dirs, files in os.walk(stickers_folder):
        for file in files:
            if file.endswith(".png"):
                sticker_img = Image.open(root + os.path.sep + file)
                sticker_counter += 1
                background.paste(sticker_img, (offset_x, offset_y))
                offset_y += 430
                if sticker_counter == stickers_per_row:  # New column
                    offset_x = 1150
                    offset_y = 0
                if (sticker_counter == 17):  # New page for the stickers, resetting counter and offsets
                    background.save(stickers_pdf_name)
                    background = Image.new(mode="RGB", size=A4_SIZE, color=WHITE)
                    offset_x = 100
                    offset_y = 0
                    sticker_counter = 1
                    page_counter += 1
    background.save(stickers_pdf_name) # Last page


# -----------------------------UTILITY FUNCTIONS---------------------------------#


def get_repo_files(repo, descendants):
    """
    Get all files and folders from the repository path specified by descendants.
    Use this function if you didn't find the GitHub tree sha in local.tree_sha dict.

    sample descendants = ['content', 'pl', 'projekty']
    """
    branch_head = repo.get_branch("main").commit.sha
    tree = repo.get_git_tree(branch_head).tree
    for desc in descendants:
        for b in tree:
            if b.path == desc:
                tree = repo.get_git_tree(b.sha).tree
                break
    return tree
    # TO DO: Handle not finding the path
