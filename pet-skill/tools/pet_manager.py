#!/usr/bin/env python3
"""Pet profile CRUD and simple state management."""

import argparse
import json
import os
import sys
import re
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
PETS_DIR = os.path.join(PROJECT_DIR, "pets")

VALID_MOODS = ["happy", "neutral", "sad", "sleepy"]
SAD_THRESHOLD_HOURS = 48


def slugify(name: str) -> str:
    """Convert a pet name to a filesystem-safe slug."""
    try:
        from pypinyin import lazy_pinyin
        slug = "_".join(lazy_pinyin(name))
    except ImportError:
        slug = name.lower()

    slug = re.sub(r"[^a-z0-9_]", "_", slug)
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "pet"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def hours_since(iso_time: str) -> float:
    then = datetime.fromisoformat(iso_time)
    if then.tzinfo is None:
        then = then.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - then
    return delta.total_seconds() / 3600


def action_create(args):
    name = args.name
    slug = slugify(name)
    animal_type = args.type or "generic"
    personality = [t.strip() for t in args.personality.split(",")] if args.personality else []
    portrait_path = args.ascii_portrait

    pet_dir = os.path.join(PETS_DIR, slug)
    if os.path.exists(pet_dir) and os.path.exists(os.path.join(pet_dir, "meta.json")):
        print(f"Error: Pet '{slug}' already exists at {pet_dir}", file=sys.stderr)
        print(f"Use a different name or delete the existing pet first.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(pet_dir, exist_ok=True)
    os.makedirs(os.path.join(pet_dir, "custom_frames"), exist_ok=True)

    meta = {
        "name": name,
        "slug": slug,
        "animal_type": animal_type,
        "personality": personality,
        "mood": "happy",
        "created_at": now_iso(),
        "last_seen": now_iso(),
    }

    meta_path = os.path.join(pet_dir, "meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    if portrait_path and os.path.exists(portrait_path):
        with open(portrait_path, "r", encoding="utf-8") as src:
            portrait_content = src.read()
        with open(os.path.join(pet_dir, "portrait.txt"), "w", encoding="utf-8") as dst:
            dst.write(portrait_content)

    print(json.dumps(meta, ensure_ascii=False, indent=2))


def action_load(args):
    slug = args.slug
    meta_path = os.path.join(PETS_DIR, slug, "meta.json")

    if not os.path.exists(meta_path):
        print(f"Error: Pet '{slug}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    last_seen = meta.get("last_seen")
    if last_seen and hours_since(last_seen) > SAD_THRESHOLD_HOURS:
        if meta.get("mood") != "sad":
            meta["mood"] = "sad"
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)

    meta["last_seen"] = now_iso()
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    portrait_path = os.path.join(PETS_DIR, slug, "portrait.txt")
    if os.path.exists(portrait_path):
        with open(portrait_path, "r", encoding="utf-8") as f:
            meta["portrait"] = f.read()

    custom_dir = os.path.join(PETS_DIR, slug, "custom_frames")
    if os.path.exists(custom_dir):
        custom_actions = [f.replace(".json", "") for f in os.listdir(custom_dir) if f.endswith(".json")]
        meta["custom_animations"] = sorted(custom_actions)

    print(json.dumps(meta, ensure_ascii=False, indent=2))


def action_update_mood(args):
    slug = args.slug
    mood = args.mood

    if mood not in VALID_MOODS:
        print(f"Error: Invalid mood '{mood}'. Valid: {', '.join(VALID_MOODS)}", file=sys.stderr)
        sys.exit(1)

    meta_path = os.path.join(PETS_DIR, slug, "meta.json")
    if not os.path.exists(meta_path):
        print(f"Error: Pet '{slug}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    old_mood = meta.get("mood", "neutral")
    meta["mood"] = mood
    meta["last_seen"] = now_iso()

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"{meta['name']}: {old_mood} → {mood}")


def action_list(_args):
    if not os.path.exists(PETS_DIR):
        print("No pets found.")
        return

    pets = []
    for entry in sorted(os.listdir(PETS_DIR)):
        meta_path = os.path.join(PETS_DIR, entry, "meta.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            pets.append(meta)

    if not pets:
        print("No pets found.")
        return

    print(f"Found {len(pets)} pet(s):\n")
    for p in pets:
        personality_str = ", ".join(p.get("personality", []))
        mood = p.get("mood", "?")
        animal = p.get("animal_type", "?")
        print(f"  {p['name']} ({p['slug']})")
        print(f"    Type: {animal} | Mood: {mood} | Personality: {personality_str}")

        last_seen = p.get("last_seen")
        if last_seen:
            h = hours_since(last_seen)
            if h < 1:
                print(f"    Last seen: just now")
            elif h < 24:
                print(f"    Last seen: {int(h)} hours ago")
            else:
                print(f"    Last seen: {int(h / 24)} days ago")
        print()


def main():
    parser = argparse.ArgumentParser(description="Pet profile management")
    parser.add_argument(
        "--action",
        required=True,
        choices=["create", "load", "update-mood", "list"],
        help="Action to perform",
    )
    parser.add_argument("--name", help="Pet name (for create)")
    parser.add_argument("--slug", help="Pet slug (for load/update-mood)")
    parser.add_argument("--type", help="Animal type (for create)")
    parser.add_argument("--personality", help="Comma-separated personality traits (for create)")
    parser.add_argument("--ascii-portrait", help="Path to ASCII portrait file (for create)")
    parser.add_argument("--mood", help="New mood value (for update-mood)")

    args = parser.parse_args()

    if args.action == "create":
        if not args.name:
            parser.error("--name is required for create")
        action_create(args)

    elif args.action == "load":
        if not args.slug:
            parser.error("--slug is required for load")
        action_load(args)

    elif args.action == "update-mood":
        if not args.slug or not args.mood:
            parser.error("--slug and --mood are required for update-mood")
        action_update_mood(args)

    elif args.action == "list":
        action_list(args)


if __name__ == "__main__":
    main()
