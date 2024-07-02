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
A4_SIZE = {
    "width": 2480, # px -> 210 mm in 300 dpi
    "height": 3508 # px -> 297 mm in 300 dpi
}

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
def generate_sticker(project_name, url):
    """
    Generate a single QR sticker and save it in a predefined repository folder.
    """
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


def gh_generate_stickers():
    """
    Generate QR stickers based on all files in the repository folder.
    """
    g = Github()
    repo = g.get_repo("hs3city/hs3.pl")
    tree = repo.get_git_tree(tree_sha["content/pl/projekty"]).tree
    for file in tree:
        if file.path[0] != "_":
            print(file)
            project_name = file.path.split(".")[0]
            url = f"https://hs3.pl/projekty/{project_name}"
            generate_sticker(project_name, url)


# ---------------------------------VALIDATING STICKERS-------------------------------------#

def stickers_fit_A4():
    """
    TO DO - Validates if stickers in the folder have the same size and are not too big for the A4 page.
    """
    stickers_size = get_stickers_size()
    if stickers_size:
        return True
    print("No stickers found.")
    return False

def get_stickers_size():
    """
    Gets a size of the first sticker found.
    Returns None if sticker was not found.
    """
    for root, dirs, files in os.walk(stickers_folder):
        for file in files:
            if file.endswith(".png"):
                sticker_img = Image.open(root + os.path.sep + file)
                size_dict = {
                    "width": sticker_img.size[0],
                    "height": sticker_img.size[1]
                }
                return size_dict
    return None

# -----------------------------MERGING STICKERS TO A4 PAGE---------------------------------#


def merge_to_a4():
    """
    Merge generated stickers to A4 sheets in pdf.
    All stickers need to be the same size.
    
    All measurements are in pixels.
    """
    
    if (stickers_fit_A4() == False):
        print("Please ensure that stickers have the same dimensions and fit on A4 page.")
        return 0
    
    stickers_size = get_stickers_size()
    page_margin = 177 # 15 mm in 300 dpi
    p_work_width = A4_SIZE["width"] - 2 * page_margin     # page work width
    p_work_height = A4_SIZE["height"] - 2 * page_margin   # page work height

    stickers_per_row = int(p_work_width/stickers_size["width"])
    stickers_per_column = int(p_work_height/stickers_size["height"])
    stickers_per_page = stickers_per_row * stickers_per_column

    stickers_pdf_name = os.path.join(stickers_folder, "stickers_merged.pdf")

    sticker_counter = 0
    page_counter = 1
    offset_x = page_margin
    offset_y = page_margin
    background = Image.new(mode="RGB", size=[A4_SIZE["width"], A4_SIZE["height"]], color=WHITE)
    for root, dirs, files in os.walk(stickers_folder):
        for file in files:
            if file.endswith(".png"):
                sticker_img = Image.open(root + os.path.sep + file)
                sticker_counter += 1
                background.paste(sticker_img, (offset_x, offset_y))
                offset_y += stickers_size["height"]
                if (sticker_counter == stickers_per_page):  # New page for the stickers, resetting counter and offsets
                    background.save(stickers_pdf_name)
                    background = Image.new(mode="RGB", size=[A4_SIZE["width"], A4_SIZE["height"]], color=WHITE)
                    offset_x = page_margin
                    offset_y = page_margin
                    sticker_counter = 0
                    page_counter += 1
                    continue
                if (sticker_counter % stickers_per_column) == 0:  # New column
                    offset_x += stickers_size["width"]
                    offset_y = page_margin
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
