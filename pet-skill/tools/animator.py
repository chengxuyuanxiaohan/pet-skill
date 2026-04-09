#!/usr/bin/env python3
"""Terminal ASCII animation engine with ANSI escape sequence rendering."""

import argparse
import json
import os
import sys
import time
import random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
ANIMATIONS_DIR = os.path.join(PROJECT_DIR, "animations")
PETS_DIR = os.path.join(PROJECT_DIR, "pets")

PERSONALITY_FPS_MODIFIER = {
    "energetic": 1.5,
    "calm": 0.5,
    "curious": 1.0,
    "shy": 0.7,
    "mischievous": 1.3,
}

PERSONALITY_LOOPS_MODIFIER = {
    "energetic": 1.5,
    "calm": 1.0,
    "curious": 1.0,
    "shy": 0.8,
    "mischievous": 1.2,
}

PET_LINES = {
    "idle": {
        "default": ["...", "~", "(发呆中)"],
        "energetic": ["坐不住了!", "想出去玩~", "嗯?嗯?"],
        "calm": ["...", "~", "（安静地看着你）"],
        "curious": ["那是什么?", "嗯...?", "（东张西望）"],
        "shy": ["...", "（偷偷看你）", "（低头）"],
        "mischievous": ["嘿嘿嘿...", "（在打什么主意）", "~"],
    },
    "greet": {
        "default": ["你好呀!", "嗨~", "你来啦!"],
        "energetic": ["你来啦你来啦!", "太开心了!!", "终于等到你!"],
        "calm": ["你好~", "来了呀", "嗯~"],
        "curious": ["你今天做了什么?", "带了什么好东西?", "嗯?"],
        "shy": ["...你好", "（小声）嗨", "（躲了一下又出来）"],
        "mischievous": ["嘿! 你来得正好~", "嘿嘿，等你很久了", "有个惊喜给你!"],
    },
    "happy": {
        "default": ["开心~", "♥", "嘿嘿~"],
        "energetic": ["太棒了!!!", "开心到转圈!", "耶耶耶!"],
        "calm": ["嗯...舒服~", "（满足地眯眼）", "♥"],
        "curious": ["这个感觉真好!", "还有还有!", "♥!"],
        "shy": ["...谢谢", "（脸红）", "嗯...♥"],
        "mischievous": ["嘿嘿嘿~", "再来再来!", "摸到我了~哼!"],
    },
    "sad": {
        "default": ["呜...", "（委屈）", "..."],
        "energetic": ["不好玩...", "为什么...", "我不开心!"],
        "calm": ["...", "（叹气）", "...嗯"],
        "curious": ["怎么了?", "为什么会这样...", "（疑惑又难过）"],
        "shy": ["...", "（缩成一团）", "（不想说话）"],
        "mischievous": ["哼!", "不理你了!", "...（假装没事）"],
    },
    "play": {
        "default": ["玩玩玩!", "接住!", "嘿!"],
        "energetic": ["再来再来!", "看我的!", "冲冲冲!"],
        "calm": ["好吧~", "（慢悠悠地玩）", "嗯~"],
        "curious": ["这个怎么玩?", "让我看看!", "有意思~"],
        "shy": ["（小心翼翼地玩）", "这样...对吗?", "...好玩"],
        "mischievous": ["看你能不能接住!", "哈哈抢到了!", "来追我呀~"],
    },
    "sleep": {
        "default": ["z Z z...", "（呼噜）", "...zzz"],
        "energetic": ["不...不困...(倒头就睡)", "zzz...（梦里还在跑）", "嗯...五分钟..."],
        "calm": ["晚安~", "z Z z...", "（安静地入睡）"],
        "curious": ["明天...再去探索...zzz", "嗯...好困...", "z Z z..."],
        "shy": ["（悄悄睡着了）", "...zzz", "（卷成一团）"],
        "mischievous": ["才不困呢...zzz", "（嘴角带笑地睡着）", "嘿嘿...zzz"],
    },
    "eat": {
        "default": ["好吃!", "嗯~", "谢谢投喂!"],
        "energetic": ["好吃好吃!", "还有吗还有吗?!", "吃饱了有力气玩!"],
        "calm": ["嗯...不错~", "（细细品味）", "好吃~"],
        "curious": ["这是什么味道?", "第一次吃这个!", "嗯...?好吃!"],
        "shy": ["...谢谢", "（偷偷吃）", "好吃..."],
        "mischievous": ["这个我先吃了!", "哼哼,好吃~", "还想要!"],
    },
}


def load_pet_meta(slug: str):
    meta_path = os.path.join(PETS_DIR, slug, "meta.json")
    if not os.path.exists(meta_path):
        return None
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_frames(slug: str, action: str, animal_type: str = "generic"):
    """Resolve animation frames with priority: custom > prebuilt > generic."""
    custom_path = os.path.join(PETS_DIR, slug, "custom_frames", f"{action}.json")
    if os.path.exists(custom_path):
        with open(custom_path, "r", encoding="utf-8") as f:
            return json.load(f)

    prebuilt_path = os.path.join(ANIMATIONS_DIR, f"{animal_type}.json")
    if os.path.exists(prebuilt_path):
        with open(prebuilt_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        anims = data.get("animations", {})
        if action in anims:
            return anims[action]

    generic_path = os.path.join(ANIMATIONS_DIR, "generic.json")
    if os.path.exists(generic_path):
        with open(generic_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        anims = data.get("animations", {})
        if action in anims:
            return anims[action]

    return None


def get_pet_line(action, personality):
    action_lines = PET_LINES.get(action, PET_LINES["idle"])
    for trait in personality:
        if trait in action_lines:
            return random.choice(action_lines[trait])
    return random.choice(action_lines["default"])


def apply_personality_modifiers(fps, loops, personality):
    fps_mod = 1.0
    loops_mod = 1.0
    for trait in personality:
        fps_mod *= PERSONALITY_FPS_MODIFIER.get(trait, 1.0)
        loops_mod *= PERSONALITY_LOOPS_MODIFIER.get(trait, 1.0)
    return fps * fps_mod, max(1, int(loops * loops_mod))


def play_animation(
    frames,
    fps: float = 3,
    loops: int = 3,
    pet_name: str = "",
    pet_line: str = "",
):
    if not frames:
        print("No frames to play.")
        return

    interval = 1.0 / fps
    max_lines = max(frame.count("\n") + 1 for frame in frames)
    max_width = max(
        len(line) for frame in frames for line in frame.split("\n")
    )

    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    try:
        total_frames = loops * len(frames)
        for i in range(total_frames):
            frame = frames[i % len(frames)]
            lines = frame.split("\n")

            while len(lines) < max_lines:
                lines.append("")

            if i > 0:
                sys.stdout.write(f"\033[{max_lines}A")

            for line in lines:
                padded = line.ljust(max_width)
                sys.stdout.write(padded + "\n")

            sys.stdout.flush()
            time.sleep(interval)

        if pet_name or pet_line:
            line_text = f"\n{pet_name}: {pet_line}" if pet_name else f"\n{pet_line}"
            sys.stdout.write(line_text + "\n")

    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(description="Play ASCII animations in terminal")
    parser.add_argument("--pet", required=True, help="Pet slug")
    parser.add_argument("--action", required=True, help="Animation action (idle, greet, happy, etc.)")
    parser.add_argument("--loops", type=int, help="Number of animation loops (overrides default)")
    parser.add_argument("--fps", type=float, help="Frames per second (overrides default)")
    parser.add_argument("--no-line", action="store_true", help="Don't print pet dialogue line")

    args = parser.parse_args()

    meta = load_pet_meta(args.pet)
    if meta is None:
        print(f"Error: Pet '{args.pet}' not found.", file=sys.stderr)
        sys.exit(1)

    animal_type = meta.get("animal_type", "generic")
    personality = meta.get("personality", [])
    pet_name = meta.get("name", args.pet)

    frame_data = resolve_frames(args.pet, args.action, animal_type)
    if frame_data is None:
        print(f"Error: No animation '{args.action}' found for pet '{args.pet}'.", file=sys.stderr)
        print(f"Available actions: idle, greet, happy, sad, play, sleep, eat", file=sys.stderr)
        sys.exit(1)

    frames = frame_data.get("frames", [])
    fps = args.fps or frame_data.get("fps", 3)
    loops = args.loops or frame_data.get("default_loops", 3)

    fps, loops = apply_personality_modifiers(fps, loops, personality)

    pet_line = "" if args.no_line else get_pet_line(args.action, personality)

    play_animation(frames, fps, loops, pet_name, pet_line)


if __name__ == "__main__":
    main()
