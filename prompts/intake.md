# 创建宠物 — 对话流程

本文件指导 Agent 完成宠物创建的对话交互。按顺序执行每个步骤。

---

## Step 1: 选择动物类型

运行命令获取可选类型：
```bash
python3 ${SKILL_DIR}/tools/portrait_picker.py types
```

向用户说：

> 想创建一只 ASCII 宠物吗？请选择你想养的动物类型：
>
> 🐱 猫 (cat) · 🐶 狗 (dog) · 🐰 兔子 (rabbit)
> 🐦 鸟 (bird) · 🐠 鱼 (fish) · 🐹 仓鼠 (hamster)
> 🐢 乌龟 (turtle) · 🐍 蛇 (snake) · ✨ 其他 (generic)

等待用户选择。如果用户用自然语言描述（如"我想养一只猫"），提取动物类型。

## Step 2: 选择 ASCII 形象

向用户提供两种选择：

> 你想如何获得宠物形象？
>
> **A. 从形象库挑选** — 有多款经典 ASCII 形象可选
> **B. 系统自动生成** — AI 为你量身定制独一无二的 ASCII 肖像

等待用户选择。

---

### 如果选择 A：从形象库挑选

运行命令展示该类型所有可选肖像：
```bash
python3 ${SKILL_DIR}/tools/portrait_picker.py list --type <animal_type>
```

然后逐个展示肖像让用户挑选：
```bash
python3 ${SKILL_DIR}/tools/portrait_picker.py show --id <portrait_id>
```

向用户展示所有可选形象，例如：

> 以下是猫咪的可选 ASCII 形象：
>
> **1. 经典猫咪** (cat_classic)
> ```
>   /\_/\
>  ( o.o )
>   > ^ <
> ```
>
> **2. 猫脸** (cat_face)
> ...
>
> 请选择一个形象（输入编号或名称）

用户选定后，跳转到 Step 3。

---

### 如果选择 B：系统自动生成

询问用户对宠物外观的描述：

> 请描述你想要的宠物形象（可选，直接回车跳过）：
> 例如：一只戴着蝴蝶结的布偶猫、一只趴着的柴犬、一只吐舌头的狗...

获取描述后，生成肖像：

1. 运行获取参考示例和生成提示：
```bash
python3 ${SKILL_DIR}/tools/portrait_picker.py gen-prompt --type <animal_type> --description "<用户描述>"
```

2. 读取 `${SKILL_DIR}/prompts/portrait_generator.md` 作为生成指南

3. 根据提示和指南，生成一个 ASCII 肖像（纯文本，不要代码块包裹）

4. 向用户展示并确认：

> 为你生成了这个形象：
>
> ```
> [生成的 ASCII 肖像]
> ```
>
> 满意吗？（回复"好的"确认，或告诉我你想调整什么）

5. 如果用户不满意，根据反馈重新生成

6. 用户确认后，将肖像文本写入临时文件 `/tmp/pet_portrait_<slug>.txt`

7. 运行保存：
```bash
python3 ${SKILL_DIR}/tools/portrait_picker.py save-custom --slug <slug> --file /tmp/pet_portrait_<slug>.txt
```

跳转到 Step 3。

---

## Step 3: 起名字

> 请给你的宠物起个名字吧？

等待用户回复名字。名字可以是中文或英文。

## Step 4: 性格分析

读取 `${SKILL_DIR}/prompts/personality_analyzer.md`，根据动物类型分析性格特征。

向用户展示并确认：

> **[名字]** 的性格分析：
> - [特征1]（解释）
> - [特征2]（解释）
>
> 你觉得合适吗？想调整哪个性格特征？（直接回复"好的"表示确认）

如果用户想调整，根据用户反馈修改性格特征。

## Step 5: 保存 & 生成动画

确认后：

1. 运行 `pet_manager.py --action create` 创建宠物档案
2. 如果选择了方式 A 且尚未保存：运行 `portrait_picker.py save --id <portrait_id> --slug <slug>`
3. 如果选择了方式 B 且尚未保存：运行 `portrait_picker.py save-custom --slug <slug> --file <path>`
4. 使用 `frame_generator.py --action generate-prompt` + Agent 为 7 个基础动作生成定制帧
5. 用 `frame_generator.py --action validate` 和 `--action save` 保存每组帧

向用户展示：

> **[名字]** 诞生啦！
> 形象：[portrait_name 或 "自动生成"]
> 性格：[特征列表]
> 已生成 7 组专属动画

## Step 6: 欢迎动画

运行：
```bash
python3 ${SKILL_DIR}/tools/animator.py --pet <slug> --action greet
```

完成宠物创建。
