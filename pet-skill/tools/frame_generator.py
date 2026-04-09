#!/usr/bin/env python3
"""Validate, save, and manage LLM-generated ASCII animation frames."""

import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
ANIMATIONS_DIR = os.path.join(PROJECT_DIR, "animations")
PETS_DIR = os.path.join(PROJECT_DIR, "pets")
PROMPT_TEMPLATE = os.path.join(PROJECT_DIR, "prompts", "frame_generator.md")

MAX_FRAME_WIDTH = 40
MAX_FRAME_HEIGHT = 10
MIN_FRAMES = 2
MAX_FRAMES = 6


def load_pet_meta(slug: str) -> dict:
    meta_path = os.path.join(PETS_DIR, slug, "meta.json")
    if not os.path.exists(meta_path):
        print(f"Error: Pet '{slug}' not found at {meta_path}", file=sys.stderr)
        sys.exit(1)
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_prebuilt_animations(animal_type: str) -> dict:
    anim_path = os.path.join(ANIMATIONS_DIR, f"{animal_type}.json")
    if not os.path.exists(anim_path):
        anim_path = os.path.join(ANIMATIONS_DIR, "generic.json")
    with open(anim_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_frames(frames_data):
    """Validate frame data and return list of error messages (empty = valid)."""
    errors = []

    if "frames" not in frames_data:
        errors.append("Missing 'frames' key")
        return errors

    frames = frames_data["frames"]
    if not isinstance(frames, list):
        errors.append("'frames' must be a list")
        return errors

    if len(frames) < MIN_FRAMES:
        errors.append(f"Too few frames: {len(frames)} (minimum {MIN_FRAMES})")
    if len(frames) > MAX_FRAMES:
        errors.append(f"Too many frames: {len(frames)} (maximum {MAX_FRAMES})")

    line_counts = []
    for i, frame in enumerate(frames):
        if not isinstance(frame, str):
            errors.append(f"Frame {i}: must be a string")
            continue

        lines = frame.split("\n")
        line_counts.append(len(lines))

        if len(lines) > MAX_FRAME_HEIGHT:
            errors.append(f"Frame {i}: too tall ({len(lines)} lines, max {MAX_FRAME_HEIGHT})")

        for j, line in enumerate(lines):
            if len(line) > MAX_FRAME_WIDTH:
                errors.append(f"Frame {i}, line {j}: too wide ({len(line)} chars, max {MAX_FRAME_WIDTH})")

    if line_counts and len(set(line_counts)) > 1:
        errors.append(f"Inconsistent frame heights: {line_counts}")

    if "fps" in frames_data:
        fps = frames_data["fps"]
        if not isinstance(fps, (int, float)) or fps <= 0:
            errors.append(f"Invalid fps: {fps}")

    if "default_loops" in frames_data:
        loops = frames_data["default_loops"]
        if not isinstance(loops, int) or loops <= 0:
            errors.append(f"Invalid default_loops: {loops}")

    return errors


def action_validate(args):
    frames_input = args.frames
    if os.path.isfile(frames_input):
        with open(frames_input, "r", encoding="utf-8") as f:
            frames_input = f.read()

    try:
        data = json.loads(frames_input)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    errors = validate_frames(data)
    if errors:
        print("Validation FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)
    else:
        print("Validation passed.")
        print(f"  Frames: {len(data['frames'])}")
        lines = data["frames"][0].split("\n")
        print(f"  Frame height: {len(lines)} lines")
        max_w = max(len(line) for frame in data["frames"] for line in frame.split("\n"))
        print(f"  Max width: {max_w} chars")
        print(f"  FPS: {data.get('fps', 'not set')}")
        print(f"  Loops: {data.get('default_loops', 'not set')}")


def action_save(args):
    slug = args.pet
    action_name = args.action_name
    frames_input = args.frames

    if os.path.isfile(frames_input):
        with open(frames_input, "r", encoding="utf-8") as f:
            frames_input = f.read()

    try:
        data = json.loads(frames_input)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    errors = validate_frames(data)
    if errors:
        print("Validation FAILED, cannot save:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    custom_dir = os.path.join(PETS_DIR, slug, "custom_frames")
    os.makedirs(custom_dir, exist_ok=True)

    out_path = os.path.join(custom_dir, f"{action_name}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved {action_name} frames to {out_path}")
    print(f"  Frames: {len(data['frames'])}, FPS: {data.get('fps', 3)}")


def action_list(args):
    slug = args.pet
    custom_dir = os.path.join(PETS_DIR, slug, "custom_frames")

    if not os.path.exists(custom_dir):
        print(f"No custom frames for pet '{slug}'")
        return

    files = sorted(f for f in os.listdir(custom_dir) if f.endswith(".json"))
    if not files:
        print(f"No custom frames for pet '{slug}'")
        return

    print(f"Custom frames for '{slug}':")
    for f in files:
        action_name = f.replace(".json", "")
        fpath = os.path.join(custom_dir, f)
        with open(fpath, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        n_frames = len(data.get("frames", []))
        fps = data.get("fps", "?")
        print(f"  {action_name}: {n_frames} frames, {fps} fps")


def action_generate_prompt(args):
    slug = args.pet
    action_name = args.action_name

    meta = load_pet_meta(slug)
    animal_type = meta.get("animal_type", "generic")
    personality = ", ".join(meta.get("personality", ["unknown"]))
    mood = meta.get("mood", "neutral")

    prebuilt = load_prebuilt_animations(animal_type)
    anims = prebuilt.get("animations", {})

    example_actions = []
    if action_name in anims:
        example_actions.append(action_name)
    for a in ["idle", "happy", "play"]:
        if a not in example_actions and a in anims:
            example_actions.append(a)
        if len(example_actions) >= 3:
            break

    example_text = ""
    for ea in example_actions:
        anim_data = anims[ea]
        example_text += f"\n### {ea}\n```json\n{json.dumps(anim_data, ensure_ascii=False, indent=2)}\n```\n"

    with open(PROMPT_TEMPLATE, "r", encoding="utf-8") as f:
        template = f.read()

    prompt = template.replace("{animal_type}", animal_type)
    prompt = prompt.replace("{personality}", personality)
    prompt = prompt.replace("{mood}", mood)
    prompt = prompt.replace("{action_name}", action_name)
    prompt = prompt.replace("{example_frames}", example_text)

    print(prompt)


def main():
    parser = argparse.ArgumentParser(description="Manage LLM-generated ASCII animation frames")
    parser.add_argument(
        "--action",
        required=True,
        choices=["validate", "save", "list", "generate-prompt"],
        help="Action to perform",
    )
    parser.add_argument("--pet", help="Pet slug")
    parser.add_argument("--action-name", help="Animation action name (e.g. happy, play)")
    parser.add_argument("--frames", help="JSON string or file path containing frame data")

    args = parser.parse_args()

    if args.action == "validate":
        if not args.frames:
            parser.error("--frames is required for validate")
        action_validate(args)

    elif args.action == "save":
        if not args.pet or not args.action_name or not args.frames:
            parser.error("--pet, --action-name, and --frames are required for save")
        action_save(args)

    elif args.action == "list":
        if not args.pet:
            parser.error("--pet is required for list")
        action_list(args)

    elif args.action == "generate-prompt":
        if not args.pet or not args.action_name:
            parser.error("--pet and --action-name are required for generate-prompt")
        action_generate_prompt(args)


if __name__ == "__main__":
    main()
