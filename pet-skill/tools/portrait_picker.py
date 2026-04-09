#!/usr/bin/env python3
"""Browse, pick, and display ASCII pet portraits from the gallery.

The gallery (portraits/gallery.json) contains pre-made ASCII art for
various animal types, inspired by https://www.asciiart.eu/gallery

Usage:
  python3 portrait_picker.py list                         # all types
  python3 portrait_picker.py list --type cat              # cat portraits
  python3 portrait_picker.py show --id cat_sitting        # display one
  python3 portrait_picker.py pick --type cat              # pick random
  python3 portrait_picker.py save --id cat_sitting --slug mimi  # save to pet
  python3 portrait_picker.py save-custom --slug mimi --file /tmp/portrait.txt  # save custom
  python3 portrait_picker.py examples --type cat          # show examples for LLM reference
  python3 portrait_picker.py gen-prompt --type cat        # generate LLM prompt
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
GALLERY_PATH = os.path.join(PROJECT_DIR, "portraits", "gallery.json")


def load_gallery():
    with open(GALLERY_PATH, encoding="utf-8") as f:
        return json.load(f)


def cmd_list(args):
    gallery = load_gallery()
    animal_type = getattr(args, "type", None)

    if animal_type:
        types = [animal_type] if animal_type in gallery else []
    else:
        types = list(gallery.keys())

    if not types:
        print(f"Unknown type: {animal_type}", file=sys.stderr)
        print(f"Available: {', '.join(gallery.keys())}")
        sys.exit(1)

    for t in types:
        portraits = gallery[t]
        print(f"\n=== {t} ({len(portraits)} portraits) ===")
        for p in portraits:
            print(f"  {p['id']:25s}  {p['name']}  [{p['style']}]")


def cmd_show(args):
    gallery = load_gallery()
    for portraits in gallery.values():
        for p in portraits:
            if p["id"] == args.id:
                print(f"[{p['name']}]  ({p['id']})\n")
                print("\n".join(p["art"]))
                return
    print(f"Portrait not found: {args.id}", file=sys.stderr)
    sys.exit(1)


def cmd_pick(args):
    gallery = load_gallery()
    animal_type = getattr(args, "type", None) or "generic"
    portraits = gallery.get(animal_type, gallery.get("generic", []))
    if not portraits:
        print(f"No portraits for type: {animal_type}", file=sys.stderr)
        sys.exit(1)

    style = getattr(args, "style", None)
    if style:
        filtered = [p for p in portraits if p["style"] == style]
        if filtered:
            portraits = filtered

    chosen = random.choice(portraits)
    print(f"[{chosen['name']}]  ({chosen['id']})\n")
    print("\n".join(chosen["art"]))

    if getattr(args, "json", False):
        print("\n---JSON---")
        print(json.dumps(chosen, ensure_ascii=False, indent=2))


def cmd_save(args):
    gallery = load_gallery()
    portrait = None
    for portraits in gallery.values():
        for p in portraits:
            if p["id"] == args.id:
                portrait = p
                break

    if not portrait:
        print(f"Portrait not found: {args.id}", file=sys.stderr)
        sys.exit(1)

    pet_dir = os.path.join(PROJECT_DIR, "pets", args.slug)
    os.makedirs(pet_dir, exist_ok=True)
    portrait_path = os.path.join(pet_dir, "portrait.txt")

    art_text = "\n".join(portrait["art"])
    with open(portrait_path, "w", encoding="utf-8") as f:
        f.write(art_text + "\n")

    meta_path = os.path.join(pet_dir, "meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
        meta["portrait_id"] = portrait["id"]
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"Portrait '{portrait['name']}' saved to {portrait_path}")


def cmd_save_custom(args):
    """Save a custom (LLM-generated) portrait to a pet's profile."""
    slug = args.slug

    if args.file:
        with open(args.file, encoding="utf-8") as f:
            art_text = f.read().rstrip("\n")
    elif args.text:
        art_text = args.text.replace("\\n", "\n")
    else:
        print("Error: provide --file or --text", file=sys.stderr)
        sys.exit(1)

    pet_dir = os.path.join(PROJECT_DIR, "pets", slug)
    os.makedirs(pet_dir, exist_ok=True)
    portrait_path = os.path.join(pet_dir, "portrait.txt")

    with open(portrait_path, "w", encoding="utf-8") as f:
        f.write(art_text + "\n")

    meta_path = os.path.join(pet_dir, "meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
        meta["portrait_id"] = "custom"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    lines = art_text.split("\n")
    print(f"Custom portrait saved to {portrait_path}")
    print(f"Size: {max(len(l) for l in lines)}w x {len(lines)}h\n")
    print(art_text)


def cmd_examples(args):
    """Show all portraits of a type as formatted examples for LLM reference."""
    gallery = load_gallery()
    animal_type = getattr(args, "type", None) or "cat"
    portraits = gallery.get(animal_type, [])

    if not portraits:
        print(f"No portraits for type: {animal_type}", file=sys.stderr)
        sys.exit(1)

    print(f"=== {animal_type} reference examples ({len(portraits)} portraits) ===\n")
    for p in portraits:
        print(f"### {p['name']} ({p['id']}) [{p['style']}]")
        print("\n".join(p["art"]))
        print()


def cmd_gen_prompt(args):
    """Build a complete LLM prompt for generating a portrait."""
    gallery = load_gallery()
    animal_type = getattr(args, "type", None) or "cat"
    description = getattr(args, "description", None) or ""
    portraits = gallery.get(animal_type, gallery.get("generic", []))

    examples_text = ""
    for p in portraits[:3]:
        examples_text += f"### {p['name']} [{p['style']}]\n"
        examples_text += "\n".join(p["art"])
        examples_text += "\n\n"

    prompt_path = os.path.join(PROJECT_DIR, "prompts", "portrait_generator.md")
    with open(prompt_path, encoding="utf-8") as f:
        template = f.read()

    prompt = template.replace("{animal_type}", animal_type)
    prompt = prompt.replace("{user_description}", description or "(无特殊要求)")
    prompt = prompt.replace("{examples}", examples_text.strip())

    print(prompt)


def cmd_types(args):
    gallery = load_gallery()
    for t in gallery:
        print(f"  {t:12s}  ({len(gallery[t])} portraits)")


def main():
    parser = argparse.ArgumentParser(description="ASCII pet portrait picker")
    sub = parser.add_subparsers(dest="command")

    p_list = sub.add_parser("list", help="List available portraits")
    p_list.add_argument("--type", help="Filter by animal type")

    p_show = sub.add_parser("show", help="Display a portrait by ID")
    p_show.add_argument("--id", required=True)

    p_pick = sub.add_parser("pick", help="Pick a random portrait")
    p_pick.add_argument("--type", help="Animal type")
    p_pick.add_argument("--style", choices=["simple", "medium", "detailed"])
    p_pick.add_argument("--json", action="store_true", help="Also output JSON")

    p_save = sub.add_parser("save", help="Save portrait to a pet's profile")
    p_save.add_argument("--id", required=True, help="Portrait ID")
    p_save.add_argument("--slug", required=True, help="Pet slug")

    p_save_custom = sub.add_parser("save-custom", help="Save a custom portrait")
    p_save_custom.add_argument("--slug", required=True, help="Pet slug")
    p_save_custom.add_argument("--file", help="Path to portrait text file")
    p_save_custom.add_argument("--text", help="Portrait text (use \\n for newlines)")

    p_examples = sub.add_parser("examples", help="Show examples for LLM reference")
    p_examples.add_argument("--type", help="Animal type")

    p_gen = sub.add_parser("gen-prompt", help="Build LLM prompt for portrait generation")
    p_gen.add_argument("--type", help="Animal type")
    p_gen.add_argument("--description", help="User description of desired portrait")

    p_types = sub.add_parser("types", help="List available animal types")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    {"list": cmd_list, "show": cmd_show, "pick": cmd_pick,
     "save": cmd_save, "save-custom": cmd_save_custom,
     "examples": cmd_examples, "gen-prompt": cmd_gen_prompt,
     "types": cmd_types}[args.command](args)


if __name__ == "__main__":
    main()
