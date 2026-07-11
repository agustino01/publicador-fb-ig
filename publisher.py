import os
import json
import random
import requests
from pathlib import Path
from datetime import datetime, timezone

IMAGES_DIR = Path("images")
STATE_FILE = Path("state.json")

FB_PAGE_ID = os.environ["FB_PAGE_ID"]
FB_PAGE_ACCESS_TOKEN = os.environ["FB_PAGE_ACCESS_TOKEN"]
IG_USER_ID = os.environ["IG_USER_ID"]
IG_ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN", FB_PAGE_ACCESS_TOKEN)
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")  # owner/repo
GITHUB_REF_NAME = os.environ.get("GITHUB_REF_NAME", "main")

POST_INTERVAL_HOURS = 20
VALID_EXT = {".jpg", ".jpeg", ".png"}


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"used_images": [], "last_post_utc": None}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def hours_since(iso_ts):
    if not iso_ts:
        return None
    last = datetime.fromisoformat(iso_ts)
    now = datetime.now(timezone.utc)
    return (now - last).total_seconds() / 3600


def pick_image(state):
    all_images = sorted(
        p.name for p in IMAGES_DIR.iterdir() if p.suffix.lower() in VALID_EXT
    )
    unused = [img for img in all_images if img not in state["used_images"]]
    if not unused:
        return None
    return random.choice(unused)


def raw_github_url(filename: str) -> str:
    return (
        f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/"
        f"{GITHUB_REF_NAME}/images/{filename}"
    )


def post_to_facebook(image_url: str):
    resp = requests.post(
        f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/photos",
        data={
            "url": image_url,
            "access_token": FB_PAGE_ACCESS_TOKEN,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def post_to_instagram(image_url: str):
    create = requests.post(
        f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media",
        data={
            "image_url": image_url,
            "access_token": IG_ACCESS_TOKEN,
        },
        timeout=60,
    )
    create.raise_for_status()
    creation_id = create.json()["id"]

    publish = requests.post(
        f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media_publish",
        data={"creation_id": creation_id, "access_token": IG_ACCESS_TOKEN},
        timeout=60,
    )
    publish.raise_for_status()
    return publish.json()


def main():
    state = load_state()

    elapsed = hours_since(state["last_post_utc"])
    if elapsed is not None and elapsed < POST_INTERVAL_HOURS:
        print(f"Todavia no pasaron {POST_INTERVAL_HOURS}hs (van {elapsed:.1f}hs). No publico.")
        return

    filename = pick_image(state)
    if filename is None:
        print("No quedan imagenes sin usar en la carpeta images/. Subi fotos nuevas.")
        return

    image_url = raw_github_url(filename)

    print(f"Publicando {filename} -> {image_url}")

    fb_result = post_to_facebook(image_url)
    print("Facebook OK:", fb_result)

    ig_result = post_to_instagram(image_url)
    print("Instagram OK:", ig_result)

    state["used_images"].append(filename)
    state["last_post_utc"] = datetime.now(timezone.utc).isoformat()
    save_state(state)


if __name__ == "__main__":
    main()
