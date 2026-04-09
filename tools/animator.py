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


def is_interactive_terminal():
    """Check if stdout is a real interactive terminal."""
    return sys.stdout.isatty()


def play_animation_interactive(frames, fps, loops, max_lines, max_width):
    """Play animation with ANSI escape codes in a real terminal."""
    interval = 1.0 / fps

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
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()


def play_animation_static(frames, pet_name, action, portrait_path=None):
    """Output animation as static text for non-interactive environments (e.g. AI agent shell)."""
    if portrait_path and os.path.exists(portrait_path):
        print("╭─── 宠物肖像 ───╮")
        with open(portrait_path, "r", encoding="utf-8") as f:
            portrait = f.read().rstrip("\n")
        for line in portrait.split("\n"):
            print(f"  {line}")
        print("╰────────────────╯")
        print()

    print(f"▶ 动作: {action}  ({len(frames)} 帧)")
    print()

    unique_frames = []
    seen = set()
    for frame in frames:
        if frame not in seen:
            unique_frames.append(frame)
            seen.add(frame)

    for i, frame in enumerate(unique_frames):
        if len(unique_frames) > 1:
            print(f"  [帧 {i + 1}/{len(unique_frames)}]")
        for line in frame.split("\n"):
            print(f"  {line}")
        if i < len(unique_frames) - 1:
            print()


def _load_fonts():
    """Load monospace font for ASCII and CJK font for dialogue."""
    from PIL import ImageFont

    mono_font = None
    for fp in [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.dfont",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]:
        if os.path.exists(fp):
            try:
                mono_font = ImageFont.truetype(fp, 16)
                break
            except Exception:
                continue
    if mono_font is None:
        mono_font = ImageFont.load_default()

    cjk_font = None
    for fp in [
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
        "/System/Library/Fonts/PingFang.ttc",
    ]:
        if os.path.exists(fp):
            try:
                cjk_font = ImageFont.truetype(fp, 16)
                break
            except Exception:
                continue
    if cjk_font is None:
        cjk_font = mono_font

    return mono_font, cjk_font


def render_gif(frames, fps, loops, pet_name, pet_line, portrait_path, output_path):
    """Render ASCII animation frames to an animated GIF file."""
    from PIL import Image, ImageDraw

    mono_font, cjk_font = _load_fonts()

    char_bbox = mono_font.getbbox("M")
    char_w = char_bbox[2] - char_bbox[0]
    char_h = int((char_bbox[3] - char_bbox[1]) * 1.4)

    portrait_lines = []
    if portrait_path and os.path.exists(portrait_path):
        with open(portrait_path, "r", encoding="utf-8") as f:
            portrait_lines = f.read().rstrip("\n").split("\n")

    all_frame_lines = [frame.split("\n") for frame in frames]
    max_frame_w = max(len(line) for fl in all_frame_lines for line in fl)
    max_frame_h = max(len(fl) for fl in all_frame_lines)

    dialogue = f"{pet_name}: {pet_line}" if pet_name and pet_line else ""

    content_width = max(
        max((len(l) for l in portrait_lines), default=0),
        max_frame_w,
        30,
    )

    padding = 20
    img_w = content_width * char_w + padding * 2
    portrait_h = len(portrait_lines) * char_h if portrait_lines else 0
    gap = char_h if portrait_lines else 0
    frame_area_h = max_frame_h * char_h
    dialogue_h = char_h * 2 if dialogue else 0
    img_h = padding + portrait_h + gap + frame_area_h + dialogue_h + padding

    bg_color = (30, 30, 30)
    art_color = (0, 230, 118)
    dialogue_color = (255, 214, 102)

    pil_frames = []
    frame_sequence = []
    for _ in range(loops):
        frame_sequence.extend(frames)

    for frame_text in frame_sequence:
        img = Image.new("RGB", (img_w, img_h), bg_color)
        draw = ImageDraw.Draw(img)

        y = padding
        for line in portrait_lines:
            draw.text((padding, y), line, fill=art_color, font=mono_font)
            y += char_h

        y += gap
        for line in frame_text.split("\n"):
            draw.text((padding, y), line, fill=art_color, font=mono_font)
            y += char_h

        if dialogue:
            y = img_h - padding - char_h
            draw.text((padding, y), dialogue, fill=dialogue_color, font=cjk_font)

        pil_frames.append(img)

    duration = int(1000 / fps)
    pil_frames[0].save(
        output_path,
        save_all=True,
        append_images=pil_frames[1:],
        duration=duration,
        loop=0,
    )
    return output_path


OVERLAY_PID_FILE = "/tmp/pet_overlay.pid"
OVERLAY_CMD_FILE = "/tmp/pet_overlay_cmd.json"


def _overlay_running():
    """Check if a pet overlay process is already alive."""
    if not os.path.exists(OVERLAY_PID_FILE):
        return False
    try:
        with open(OVERLAY_PID_FILE) as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)
        return True
    except (ValueError, OSError):
        return False


def _send_overlay_cmd(slug, action):
    """Write a command file for the running overlay to pick up."""
    with open(OVERLAY_CMD_FILE, "w") as f:
        json.dump({"pet": slug, "action": action, "ts": time.time()}, f)


def play_overlay(slug, action):
    """Launch the overlay or update the existing one (single-window singleton)."""
    meta = load_pet_meta(slug)
    if meta is None:
        print(f"Error: Pet '{slug}' not found.", file=sys.stderr)
        sys.exit(1)

    _send_overlay_cmd(slug, action)

    if _overlay_running():
        print(f"Overlay updated: {meta.get('name', slug)} → {action}")
        return

    _run_overlay(slug, action)


def _run_overlay(initial_slug, initial_action):
    """Start the persistent singleton overlay window."""
    try:
        import tkinter as tk
        import tkinter.font as tkfont
    except ImportError:
        print("Error: tkinter not available. Use python3.9:", file=sys.stderr)
        sys.exit(1)

    BG = "#000000"

    with open(OVERLAY_PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    root = tk.Tk()
    root.title("")
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.config(bg=BG)

    mono = tkfont.Font(root=root, family="Menlo", size=14)
    cjk = None
    for fam in ("PingFang SC", "STHeiti", "Hiragino Sans GB", "Songti SC"):
        try:
            cjk = tkfont.Font(root=root, family=fam, size=13)
            break
        except Exception:
            continue
    if cjk is None:
        cjk = mono

    canvas = tk.Canvas(root, highlightthickness=0, bg=BG)
    canvas.pack(fill="both", expand=True)

    FIXED_LOOPS = 5
    FRAME_REPEAT = 3

    state = {
        "padded": [], "fps": 3.0, "pet_name": "", "personality": [],
        "action": "", "slug": "", "idx": 0, "last_cmd_ts": 0.0,
        "anim_id": None, "dialogue_id": None,
        "animating": False, "frames_played": 0, "loops_total": 0,
        "portrait_text": "",
    }

    def load_and_render(slug, action):
        meta = load_pet_meta(slug)
        if not meta:
            return
        animal_type = meta.get("animal_type", "generic")
        personality = meta.get("personality", [])
        pet_name = meta.get("name", slug)

        frame_data = resolve_frames(slug, action, animal_type)
        if not frame_data:
            return

        raw = frame_data.get("frames", [])
        fps_val = frame_data.get("fps", 3)
        fps_val, _ = apply_personality_modifiers(fps_val, 3, personality)

        all_fl = [f.split("\n") for f in raw]
        max_fh = max(len(fl) for fl in all_fl)
        max_fw = max(len(line) for fl in all_fl for line in fl)

        padded = []
        for f in raw:
            lines = f.split("\n")
            while len(lines) < max_fh:
                lines.append("")
            padded.append("\n".join(l.ljust(max_fw) for l in lines))

        portrait_path = os.path.join(PETS_DIR, slug, "portrait.txt")
        portrait_text = ""
        if os.path.exists(portrait_path):
            with open(portrait_path, "r", encoding="utf-8") as f:
                portrait_text = f.read().rstrip("\n")

        portrait_lines = portrait_text.split("\n") if portrait_text else []
        portrait_w = max((len(l) for l in portrait_lines), default=0)
        portrait_h_lines = len(portrait_lines) if portrait_lines else 0

        content_chars = max(max_fw, portrait_w, 16)

        padded = padded * FRAME_REPEAT
        state["padded"] = padded
        state["fps"] = fps_val
        state["pet_name"] = pet_name
        state["personality"] = personality
        state["action"] = action
        state["slug"] = slug
        state["idx"] = 0
        state["animating"] = True
        state["frames_played"] = 0
        state["loops_total"] = FIXED_LOOPS * len(padded)
        state["portrait_text"] = portrait_text

        pet_line = get_pet_line(action, personality)

        char_w = mono.measure("M")
        char_h = mono.metrics()["linespace"]
        cjk_h = cjk.metrics()["linespace"]
        pad = 18
        gap = 8

        display_h = max(max_fh, portrait_h_lines)

        y = pad
        anim_y = y
        y += display_h * char_h + gap + 2
        dialogue_y = y
        y += cjk_h + pad
        total_w = content_chars * char_w + pad * 2
        total_h = y

        canvas.delete("all")
        canvas.config(width=total_w, height=total_h)

        state["anim_id"] = canvas.create_text(
            pad, anim_y, text=padded[0],
            font=mono, fill="#00e676", anchor="nw",
        )
        state["dialogue_id"] = canvas.create_text(
            pad, dialogue_y, text=f"{pet_name}: {pet_line}",
            font=cjk, fill="#ffd54f", anchor="nw",
        )

        root.geometry(f"{total_w}x{total_h}")

    def poll_commands():
        try:
            if os.path.exists(OVERLAY_CMD_FILE):
                mtime = os.path.getmtime(OVERLAY_CMD_FILE)
                if mtime > state["last_cmd_ts"]:
                    state["last_cmd_ts"] = mtime
                    with open(OVERLAY_CMD_FILE) as f:
                        cmd = json.load(f)
                    if cmd.get("action") == "close":
                        root.quit()
                        return
                    load_and_render(cmd["pet"], cmd["action"])
        except Exception:
            pass
        root.after(400, poll_commands)

    def check_orphan():
        if os.getppid() == 1:
            root.quit()
            return
        root.after(10000, check_orphan)

    def animate():
        if state["animating"] and state["padded"] and state["anim_id"]:
            canvas.itemconfig(state["anim_id"], text=state["padded"][state["idx"]])
            state["idx"] = (state["idx"] + 1) % len(state["padded"])
            state["frames_played"] += 1
            if state["frames_played"] >= state["loops_total"]:
                state["animating"] = False
                still = state["portrait_text"] if state["portrait_text"] else state["padded"][0]
                canvas.itemconfig(state["anim_id"], text=still)
                idle_line = get_pet_line("idle", state["personality"])
                canvas.itemconfig(
                    state["dialogue_id"],
                    text=f"{state['pet_name']}: {idle_line}",
                )
        interval = int(1000 / state["fps"]) if state["fps"] > 0 else 333
        root.after(interval, animate)

    drag = {"x": 0, "y": 0}

    def on_press(e):
        drag["x"] = e.x_root - root.winfo_x()
        drag["y"] = e.y_root - root.winfo_y()

    def on_drag(e):
        root.geometry(f"+{e.x_root - drag['x']}+{e.y_root - drag['y']}")

    canvas.bind("<Button-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)

    load_and_render(initial_slug, initial_action)
    state["last_cmd_ts"] = time.time()

    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    ww = root.winfo_width()
    wh = root.winfo_height()
    root.geometry(f"+{sw - ww - 50}+{sh - wh - 100}")

    root.after(200, animate)
    root.after(1000, poll_commands)
    root.after(10000, check_orphan)

    print("Overlay started.")
    root.mainloop()

    try:
        root.destroy()
    except Exception:
        pass
    for p in (OVERLAY_PID_FILE, OVERLAY_CMD_FILE):
        try:
            os.remove(p)
        except OSError:
            pass


def play_animation(
    frames,
    fps: float = 3,
    loops: int = 3,
    pet_name: str = "",
    pet_line: str = "",
    action: str = "",
    portrait_path: str = "",
    force_static: bool = False,
):
    if not frames:
        print("No frames to play.")
        return

    max_lines = max(frame.count("\n") + 1 for frame in frames)
    max_width = max(
        len(line) for frame in frames for line in frame.split("\n")
    )

    use_static = force_static or not is_interactive_terminal()

    if use_static:
        play_animation_static(frames, pet_name, action, portrait_path)
    else:
        play_animation_interactive(frames, fps, loops, max_lines, max_width)

    if pet_name or pet_line:
        print()
        if pet_name:
            print(f"{pet_name}: {pet_line}")
        else:
            print(pet_line)


def main():
    parser = argparse.ArgumentParser(description="Play ASCII animations in terminal")
    parser.add_argument("--pet", help="Pet slug")
    parser.add_argument("--action", help="Animation action (idle, greet, happy, etc.)")
    parser.add_argument("--loops", type=int, help="Number of animation loops (overrides default)")
    parser.add_argument("--fps", type=float, help="Frames per second (overrides default)")
    parser.add_argument("--no-line", action="store_true", help="Don't print pet dialogue line")
    parser.add_argument("--static", action="store_true", help="Force static output (no ANSI animation)")
    parser.add_argument("--overlay", action="store_true",
                        help="Show as floating desktop sticker (always-on-top)")
    parser.add_argument("--overlay-close", action="store_true",
                        help="Close the running overlay window")
    parser.add_argument("--gif", metavar="OUTPUT",
                        help="Render animation to an animated GIF file")

    args = parser.parse_args()

    if args.overlay_close:
        _send_overlay_cmd("", "close")
        print("Overlay close signal sent.")
        return

    if args.overlay:
        if not args.pet or not args.action:
            parser.error("--pet and --action are required with --overlay")
        play_overlay(args.pet, args.action)
        return

    if not args.pet or not args.action:
        parser.error("--pet and --action are required")

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
    portrait_path = os.path.join(PETS_DIR, args.pet, "portrait.txt")

    if args.gif:
        out = render_gif(frames, fps, loops, pet_name, pet_line,
                         portrait_path, args.gif)
        print(f"GIF saved: {out}")
    else:
        play_animation(
            frames, fps, loops, pet_name, pet_line,
            action=args.action,
            portrait_path=portrait_path,
            force_static=args.static,
        )


if __name__ == "__main__":
    main()
