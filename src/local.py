import os

# ------------------------ LOCAL FOLDERS ------------------------ #
script_folder = os.path.dirname(__file__)
main_folder = os.path.dirname(script_folder)
stickers_folder = os.path.join(main_folder, "stickers")
assets_folder = os.path.join(main_folder, "assets")
source_sans_pro = os.path.join(
    assets_folder, "Source_Sans_Pro", "SourceSansPro-Regular.ttf"
)
hs3_logo = os.path.join(assets_folder, "logo.png")

# ----------------------- GITHUB TREE SHA ----------------------- #

# sha to various trees in https://github.com/hs3city/hs3.pl repository
# use them to cut down on number of requests sent to the repository
tree_sha = {"content/pl/projekty": "7e5b71df41e0e2cc91dbc87e814807440698da12"}
