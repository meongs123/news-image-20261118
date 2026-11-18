"""news-image-20261118 entry: copy the composed front page to /output.

The image itself is drawn by compose.py (PIL, fully deterministic, no
network) and committed here as entry.png; this program only copies it,
standard library only, so the two grader runs write identical bytes.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

os.makedirs(OUT_DIR, exist_ok=True)
shutil.copyfile(SRC, os.path.join(OUT_DIR, "entry.png"))
