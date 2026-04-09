# 性格分析指南

根据动物类型和图片中的表现，为宠物分配 2-3 个性格特征。

## 可用性格特征

| 特征 | 英文 | 描述 |
|------|------|------|
| 活泼 | energetic | 精力旺盛，喜欢运动，反应快 |
| 安静 | calm | 沉稳、温和，喜欢安静的环境 |
| 好奇 | curious | 对一切感兴趣，喜欢探索新事物 |
| 害羞 | shy | 谨慎、内向，需要时间适应 |
| 调皮 | mischievous | 爱搞小动作，出其不意，幽默感强 |

## 动物类型→默认性格映射

以下是每种动物的典型性格组合，可根据图片中的实际表现调整：

### 猫 (cat)
- 默认: curious + calm
- 橘猫变体: curious + mischievous（橘猫天生调皮）
- 布偶变体: calm + shy
- 小猫变体: energetic + curious

### 狗 (dog)
- 默认: energetic + curious
- 大型犬变体: calm + curious
- 小型犬变体: energetic + mischievous
- 老犬变体: calm + shy

### 兔子 (rabbit)
- 默认: shy + curious
- 荷兰垂耳变体: calm + shy
- 侏儒兔变体: energetic + curious

### 鸟 (bird)
- 默认: curious + energetic
- 鹦鹉变体: mischievous + energetic
- 文鸟变体: shy + calm

### 鱼 (fish)
- 默认: calm + curious
- 金鱼变体: calm + energetic
- 热带鱼变体: curious + energetic

### 仓鼠 (hamster)
- 默认: curious + energetic
- 变体: shy + curious

### 通用 (generic)
- 默认: curious + calm

## 分析步骤

1. 确定动物类型
2. 查看上方的默认映射
3. 根据图片中动物的姿态/表情微调：
   - 张嘴/伸舌 → 偏 energetic
   - 蜷缩/闭眼 → 偏 calm 或 shy
   - 歪头/盯着看 → 偏 curious
   - 动作夸张/翻肚皮 → 偏 mischievous
4. 选择 2-3 个最合适的特征
5. 用中文向用户展示分析结果

## 输出格式

向 pet_manager.py 传递时使用英文逗号分隔：
```
--personality "curious,mischievous"
```

向用户展示时使用中文：
```
性格分析：好奇 + 调皮
- 好奇：喜欢东张西望，对新事物充满兴趣
- 调皮：爱搞小动作，给你带来意想不到的惊喜
```
