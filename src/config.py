from pathlib import Path

# Default constants
REPO_ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = REPO_ROOT / "images"
OUTPUT_IMAGES_DIR = REPO_ROOT / "output_images"
OUTPUT_JSON_DIR = REPO_ROOT / "output_json"

DEFAULT_PEOPLE_CONF = 0.45
DEFAULT_TEXT_CONF = 0.3
MAX_IMAGE_SIDE = 1600  # resize large images to this max side for faster inference
