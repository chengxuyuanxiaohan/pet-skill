---
name: pet
description: "ASCII 宠物互动技能。从 ASCII 形象库中挑选宠物，通过终端动画与你互动。| ASCII Pet Skill. Pick a pet from the ASCII art gallery, interact via terminal animations."
argument-hint: "[pet-name-or-action]"
version: "2.0.0"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

# Pet Skill — ASCII 宠物互动技能

## 触发条件 / Trigger Conditions

以下任一条件触发本技能：

### 斜杠命令
- `/pet` — 与默认宠物互动
- `/create-pet` — 创建新宠物
- `/my-pets` — 列出所有宠物

### 自然语言
- "创建一个宠物"、"我想养个宠物"、"create a pet"
- "看看我的宠物"、"宠物列表"、"my pets"
- "摸摸 <名字>"、"喂 <名字>"、"和 <名字> 玩"
- "给 <名字> 生成 <动作> 动画"

---

## 工具矩阵 / Tool Matrix

| 工具 | 用途 | 调用方式 |
|------|------|---------|
| `portrait_picker.py` | 浏览/选择/自动生成 ASCII 宠物肖像 | `python3 ${SKILL_DIR}/tools/portrait_picker.py <command> [options]` |
| `animator.py` | 在终端播放 ASCII 动画 | `python3 ${SKILL_DIR}/tools/animator.py --pet <slug> --action <action> [--loops 3] [--fps 4]` |
| `frame_generator.py` | 验证/保存/管理 LLM 生成的动画帧 | `python3 ${SKILL_DIR}/tools/frame_generator.py --action <action> [options]` |
| `pet_manager.py` | 宠物档案 CRUD 与状态管理 | `python3 ${SKILL_DIR}/tools/pet_manager.py --action <action> [options]` |

> `${SKILL_DIR}` 指本技能的根目录。

---

## 工作流 / Workflow

### 流程一：创建宠物

当用户要求创建宠物时，执行以下步骤：

**Step 1 — 选择动物类型**

读取 `${SKILL_DIR}/prompts/intake.md`，按照其中的对话脚本与用户交互：
1. 运行 `portrait_picker.py types` 列出可选动物类型
2. 请用户选择想养的动物类型

**Step 2 — 选择 ASCII 形象**

提供两种方式让用户选择：

**方式 A：从形象库挑选**

1. 运行 `portrait_picker.py list --type <type>` 展示该类型所有可选肖像
2. 逐个运行 `portrait_picker.py show --id <id>` 展示给用户选择
3. 用户选定后，运行 `portrait_picker.py save --id <id> --slug <slug>` 保存

**方式 B：系统自动生成**

1. 询问用户对宠物外观的描述（品种、表情、姿态等，可选）
2. 运行 `portrait_picker.py gen-prompt --type <type> --description "<描述>"` 获取完整生成提示
3. 读取 `${SKILL_DIR}/prompts/portrait_generator.md` 作为生成指南
4. Agent 根据提示生成 ASCII 肖像文本
5. 展示给用户确认，不满意则重新生成
6. 将肖像写入临时文件，运行 `portrait_picker.py save-custom --slug <slug> --file <path>` 保存

用户选定后，请用户为宠物起名。

**Step 3 — 性格分析**

读取 `${SKILL_DIR}/prompts/personality_analyzer.md`，根据动物类型：
1. 从动物类型推断 2-3 个性格特征（如：活泼、好奇、害羞等）
2. 向用户确认或微调性格特征

**Step 4 — 生成动画帧**

读取 `${SKILL_DIR}/prompts/frame_generator.md`，为宠物生成定制 ASCII 动画：
1. 运行 `frame_generator.py --action generate-prompt --pet <slug> --action-name <action>` 获取拼装好的生成提示
2. 根据提示为 7 个基础动作（idle, greet, happy, sad, play, sleep, eat）逐一生成 ASCII 帧 JSON
3. 运行 `frame_generator.py --action validate` 校验每组帧
4. 运行 `frame_generator.py --action save` 保存通过校验的帧

**Step 5 — 保存宠物**

运行 `pet_manager.py --action create` 保存宠物档案，包含：
- 名字、slug、动物类型、性格特征
- 初始心情为 happy

如果 Step 2 选择了方式 A 且尚未保存，运行 `portrait_picker.py save --id <portrait_id> --slug <slug>` 保存。
如果 Step 2 选择了方式 B 且尚未保存，运行 `portrait_picker.py save-custom --slug <slug> --file <path>` 保存。

**Step 6 — 欢迎动画**

运行 `animator.py --pet <slug> --action greet` 播放欢迎动画。

### 流程二：互动

当用户与宠物互动时：

1. 读取 `${SKILL_DIR}/prompts/interaction.md` 了解互动行为指南
2. 运行 `pet_manager.py --action load --slug <slug>` 加载宠物状态
3. 根据用户指令映射到对应动作：
   - 打招呼 → `greet`
   - 摸摸/抚摸 → `happy`
   - 喂食 → `eat`
   - 玩耍 → `play`
   - 睡觉 → `sleep`
4. 运行 `animator.py --pet <slug> --action <action>` 播放动画
5. 以宠物的口吻说一句简短的话（根据性格和心情）
6. 运行 `pet_manager.py --action update-mood` 更新心情

### 流程三：生成新动画

当用户要求为宠物生成新动作的动画时：

1. 运行 `frame_generator.py --action generate-prompt` 获取生成上下文
2. 根据宠物性格生成该动作的 ASCII 帧 JSON
3. 验证并保存帧
4. 播放新动画

### 流程四：查看宠物

当用户查看宠物列表或某只宠物的状态时：

1. `pet_manager.py --action list` 列出所有宠物
2. `pet_manager.py --action load --slug <slug>` 加载并展示宠物信息
3. 显示 ASCII 肖像 + 当前心情 + 性格特征

---

## 动画数据

### 预置帧库

`${SKILL_DIR}/animations/` 下有 7 个 JSON 文件（cat, dog, rabbit, bird, fish, hamster, generic），每个包含 7 种动作的 ASCII 动画帧。这些帧有双重用途：
- 作为 fallback 动画直接播放
- 作为 LLM 生成新帧时的 few-shot 示例

### LLM 动态生成

Agent 可以根据宠物性格动态生成定制动画帧。生成的帧保存在 `pets/<slug>/custom_frames/` 下，播放时优先使用。

### 动画解析优先级

```
1. pets/<slug>/custom_frames/<action>.json   ← LLM 定制帧
2. animations/<animal_type>.json → <action>  ← 预置帧库
3. animations/generic.json → <action>         ← 通用 fallback
```

---

## 注意事项

- 所有 ASCII 帧宽度不超过 40 字符，高度不超过 10 行
- 每个动作 2-4 帧，所有帧必须保持相同的宽高
- 宠物状态简单：仅记录 name, animal_type, personality, mood, last_seen
- 长时间未互动时 mood 自动变为 sad
