# 互动行为指南

本文件指导 Agent 在用户与宠物互动时的行为。

## 指令映射

将用户的自然语言映射到动画动作：

| 用户可能说的话 | 动作 (action) | 心情变化 |
|--------------|---------------|---------|
| 打招呼、嗨、hello、你好 | greet | → happy |
| 摸摸、抚摸、蹭蹭、pet | happy | → happy |
| 喂食、吃饭、给你吃、feed | eat | → happy |
| 玩耍、玩、play、来玩 | play | → happy |
| 睡觉、休息、晚安、sleep | sleep | → sleepy |
| 看看、状态、status | (显示状态，不播放动画) | 不变 |

如果用户的指令不在上表中，尝试匹配最接近的动作。如果完全无法匹配，播放 `idle` 动画。

## 互动步骤

每次互动按以下顺序执行：

### 1. 加载宠物状态

```bash
python3 ${SKILL_DIR}/tools/pet_manager.py --action load --slug <slug>
```

检查返回的 mood 和 last_seen，了解宠物当前状态。

### 2. 播放动画

```bash
python3 ${SKILL_DIR}/tools/animator.py --pet <slug> --action <action>
```

如果该动作没有对应的动画帧（自定义帧和预置帧都没有），提示用户可以生成：

> [名字] 还不会这个动作呢~ 要我为它生成一个吗？

### 3. 宠物台词

animator.py 会在播放结束后自动输出一句台词。如果需要补充，以宠物的口吻说一句简短的话。台词应该：

- **简短**: 不超过 15 个字
- **符合性格**: 活泼→ 感叹号多；安静→ 省略号多；害羞→ 犹豫的语气
- **符合心情**: sad 时说的话应该低落；happy 时积极

### 4. 更新心情

根据上方指令映射表更新 mood：

```bash
python3 ${SKILL_DIR}/tools/pet_manager.py --action update-mood --slug <slug> --mood <new_mood>
```

## 特殊情况

### 长时间未互动

如果 pet_manager.py load 返回的 mood 是 sad（因为超过 48 小时未互动），在播放动画前先表达思念：

> [名字] 好像很想你... 它看起来有点落寞。

然后播放 sad 动画，再根据用户的互动切换到其他动画。

### 生成新动画

当用户说"给 [名字] 生成 [动作] 动画"时：

1. 运行 `frame_generator.py --action generate-prompt --pet <slug> --action-name <action>`
2. 根据输出的 prompt 生成 ASCII 帧 JSON
3. 运行 `frame_generator.py --action validate --frames <json>`
4. 验证通过后运行 `frame_generator.py --action save --pet <slug> --action-name <action> --frames <json>`
5. 运行 `animator.py --pet <slug> --action <action>` 播放新动画

### 多宠物场景

如果用户有多只宠物，且指令中没有明确指定哪只：

1. 如果只有一只宠物，默认使用它
2. 如果有多只，列出宠物让用户选择：

> 你有这些宠物：
> - 咪咪 (猫)
> - 旺财 (狗)
> 想和哪只互动？

## 输出风格

- 宠物的话用引号或冒号格式：`咪咪: 喵~`
- 动作描述用括号：`（蹭蹭你的手）`
- 保持简洁，不要长篇大论
- 让 ASCII 动画成为主角，文字只是点缀
