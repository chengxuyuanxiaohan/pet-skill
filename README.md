# Pet Skill — ASCII 宠物互动技能

从 ASCII 形象库中挑选你的宠物，通过终端 ASCII 动画与它互动。

形象库参考 [ASCII Art Gallery](https://www.asciiart.eu/gallery) 风格。

## 功能

- **ASCII 形象库** — 内置多种动物的 ASCII 肖像，风格来自 asciiart.eu
- **终端动画** — 使用 ANSI 转义序列在终端播放逐帧 ASCII 动画
- **性格系统** — 根据动物类型分析性格特征，影响动画风格和台词
- **LLM 动态生成** — 根据宠物性格，由 LLM 动态生成定制 ASCII 动画帧
- **简单状态** — 记录宠物名字、心情，长时间不互动宠物会变得伤心

## 支持的动物

| 动物 | 可选形象 | 预置动画 | 默认性格 |
|------|---------|---------|---------|
| 猫 (cat) | 7 款 | 7 组 | 好奇 + 安静 |
| 狗 (dog) | 6 款 | 7 组 | 活泼 + 好奇 |
| 兔子 (rabbit) | 4 款 | 7 组 | 害羞 + 好奇 |
| 鸟 (bird) | 4 款 | 7 组 | 好奇 + 活泼 |
| 鱼 (fish) | 4 款 | 7 组 | 安静 + 好奇 |
| 仓鼠 (hamster) | 3 款 | 7 组 | 好奇 + 活泼 |
| 乌龟 (turtle) | 2 款 | 7 组 | 安静 + 好奇 |
| 蛇 (snake) | 2 款 | 7 组 | 安静 + 好奇 |
| 通用 (generic) | 2 款 | 7 组 | 好奇 + 安静 |

## 安装

```bash
pip install -r requirements.txt
```

依赖：
- `pypinyin` — 中文名转拼音 slug（可选）

## 使用方式

### 作为 AI 技能

将本目录放入技能目录（如 `.cursor/skills/pet/` 或 `.claude/skills/pet/`），然后：

- 说 "创建一个宠物" 选择动物和形象
- 说 "摸摸咪咪" / "和咪咪玩" 等进行互动
- 说 "给咪咪生成一个跳舞动画" 让 LLM 创作新动画

### 命令行工具

```bash
# 查看可选动物类型
python3 tools/portrait_picker.py types

# 列出某类型所有形象
python3 tools/portrait_picker.py list --type cat

# 展示某个形象
python3 tools/portrait_picker.py show --id cat_sitting

# 随机选一个形象
python3 tools/portrait_picker.py pick --type dog

# 保存形象到宠物档案
python3 tools/portrait_picker.py save --id cat_classic --slug mi_mi

# 创建宠物
python3 tools/pet_manager.py --action create --name 咪咪 --type cat --personality "curious,mischievous"

# 播放动画
python3 tools/animator.py --pet mi_mi --action happy

# 列出宠物
python3 tools/pet_manager.py --action list

# 验证 LLM 生成的帧
python3 tools/frame_generator.py --action validate --frames frames.json

# 保存自定义帧
python3 tools/frame_generator.py --action save --pet mi_mi --action-name dance --frames frames.json
```

## 项目结构

```
pet-skill/
├── SKILL.md              # 技能入口
├── README.md
├── requirements.txt
├── prompts/              # Agent 提示词
│   ├── intake.md         # 创建宠物对话流程
│   ├── personality_analyzer.md  # 性格分析
│   ├── frame_generator.md      # LLM 帧生成指南
│   └── interaction.md          # 互动行为指南
├── portraits/            # ASCII 形象库
│   └── gallery.json      # 所有动物的 ASCII 肖像
├── tools/                # Python 工具
│   ├── portrait_picker.py     # 形象浏览/选择/保存
│   ├── animator.py             # 终端动画引擎
│   ├── frame_generator.py      # 帧验证/保存/管理
│   └── pet_manager.py          # 宠物档案管理
├── animations/           # 预置动画帧库
│   ├── cat.json
│   ├── dog.json
│   ├── rabbit.json
│   ├── bird.json
│   ├── fish.json
│   ├── hamster.json
│   └── generic.json
└── pets/                 # 用户宠物数据
    └── example_mimi/     # 示例宠物
```

## 动画帧格式

每个动画动作的帧数据为 JSON 格式：

```json
{
  "frames": [
    "  /\\_/\\  \n ( ^.^ ) \n  > ^ <  ",
    "  /\\_/\\  \n ( ^.^ ) \n  > ^ < ~"
  ],
  "fps": 3,
  "default_loops": 3
}
```

约束：
- 帧宽度 <= 40 字符
- 帧高度 <= 10 行
- 每动作 2-6 帧
- 所有帧行数一致

## 性格特征

| 性格 | 对动画的影响 |
|------|------------|
| 活泼 (energetic) | 动作大、节奏快 |
| 安静 (calm) | 微动、节奏慢 |
| 好奇 (curious) | 探索、东张西望 |
| 害羞 (shy) | 躲藏、犹豫 |
| 调皮 (mischievous) | 不规则、出其不意 |

## 许可

MIT License
