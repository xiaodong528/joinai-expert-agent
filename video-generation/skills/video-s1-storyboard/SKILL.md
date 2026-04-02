---
name: video-s1-storyboard
description: "从 story.yaml 创意简报生成结构化分镜脚本 YAML。输出包含文生图和图生视频提示词的场景记录。Triggers on storyboard, scene breakdown, script generation."
---

# Stage 1: 分镜脚本生成 (Storyboard Generation)

将 Stage 0 的创意策划（`story.yaml`）转换为 N 个结构化分镜记录（`storyboard.yaml`），每个分镜包含图像生成和视频生成所需的完整提示词。

---

## 输入契约

从 `output/{project_id}/scripts/story.yaml` 读取以下字段：

| 字段 | 用途 |
|------|------|
| `视频类型` | 决定哪些字段必填（短剧需台词，创意短视频可省略） |
| `主线内容` | 故事主线，分镜的叙事依据 |
| `目标时长` | 计算场景数量 |
| `单镜时长` | 每个分镜的默认时长（通常 12 秒） |
| `目标画幅` | 16:9 或 9:16 |
| `角色` | 角色 DNA 卡片列表（可能为空） |
| `世界观与场景设定.主要场景` | 场景列表及其氛围描述 |
| `风格锁定.统一风格前缀` | 必须前置到每个生成提示词 |
| `风格锁定.负面提示词` | 每个图像生成调用的统一排除项 |

---

## 输出契约

输出文件：`output/{project_id}/scripts/storyboard.yaml`

### 文件顶层结构

```yaml
# storyboard.yaml
元信息:
  项目ID: "{project_id}"
  生成日期: "YYYY-MM-DD"
  场景总数: N
  目标总时长: "XX秒"
  画幅: "16:9"

风格锁定:
  统一风格前缀: "{从 story.yaml 原样复制}"
  负面提示词: "{从 story.yaml 原样复制}"

分镜列表:
  - # 场景 1
    ...
  - # 场景 2
    ...
```

### 每个分镜的字段定义

```yaml
- 编号: 1                    # 从 1 开始连续递增
  时长: "12秒"                # ≤12秒，单位必须写"秒"
  景别: "中景"               # 远景/全景/中景/近景/特写
  情绪: "宁静壮丽"           # 该分镜的情感基调

  文生图提示词: |
    # 用于 Stage 3 关键帧生成（Seedream txt2img / img2img）
    # 描述该分镜的【静态首帧画面】
    # 必须包含：风格前缀 + 角色完整外貌(如有) + 场景 + 构图 + 光线
    {完整提示词}

  末帧图提示词: |
    # 用于 Stage 3 尾帧生成（Seedream img2img，锚定自首帧）
    # 描述该分镜【结束瞬间的静态画面】— 角色位移后的位置、光线/氛围变化
    # 规则同 文生图提示词：风格前缀前置(R2) + 角色DNA完整(R1) + 禁止运动词(R5)
    # 此字段可选 — 若省略，Stage 3 仅生成首帧，Stage 4 使用单帧模式
    {完整提示词}

  图生视频提示词: |
    # 用于 Stage 4 图生视频（Seedance 首尾帧模式）
    # 描述从首帧到尾帧的【动态变化过程】
    # 包含：镜头运动 + 角色动作 + 环境变化 + 时长（默认 12 seconds）
    {完整提示词}

  台词: ""                   # 角色对白，用于 Stage 5 TTS
  旁白: ""                   # 旁白文本，用于 Stage 5 TTS
  音效提示: ""               # 环境音/音效描述，用于 Stage 6 参考
```

---

## 强制规则（5 条）

### R1: 角色 DNA 完整重复

每个分镜的 `文生图提示词` 必须包含角色的**完整外貌描述**，从 DNA 卡片逐字复制，**禁止省略、缩写或引用**。

**WRONG** — 省略外貌：
```yaml
文生图提示词: |
  cinematic photorealistic, the protagonist standing at a rooftop,
  looking at the sunset, warm lighting
```

**CORRECT** — 完整 DNA 重复：
```yaml
文生图提示词: |
  cinematic photorealistic, warm desaturated color grading,
  golden hour backlit, subtle film grain, 16:9 aspect ratio,
  a 25-year-old young man with short messy black hair,
  sharp jawline, deep-set dark brown eyes, lean athletic build,
  wearing a dark navy wool trench coat over a white crew-neck t-shirt,
  black slim-fit jeans, silver wristwatch on left wrist,
  standing at a rain-soaked city rooftop at dusk,
  looking out at the skyline, hands in coat pockets,
  warm golden light from the setting sun casting long shadows
```

> 如果 `角色` 列表为空（如创意短视频），此规则不适用，直接跳过角色描述部分。

### R2: 风格前缀前置

`统一风格前缀` 必须作为每个 `文生图提示词` 和 `图生视频提示词` 的**第一段文字**，原样复制，不得改写或省略任何词。

**WRONG** — 风格前缀被改写：
```yaml
文生图提示词: |
  realistic cinematic style, a city skyline at sunset...
```

**CORRECT** — 风格前缀原样前置：
```yaml
文生图提示词: |
  cinematic photorealistic, warm desaturated color grading,
  golden hour backlit, subtle film grain, shallow depth of field,
  16:9 aspect ratio, 1920x1080 resolution,
  a sprawling city skyline at sunset...
```

### R3: 相邻分镜视觉连贯

相邻分镜必须保持以下要素一致：
- **光线方向**: 不能场景 1 是日落、场景 2 突然变成正午
- **天气状况**: 不能场景 1 晴天、场景 2 突然下雨（除非剧情需要）
- **时间流向**: 时间必须单调递进（日落→黄昏→夜晚），不可回退
- **色温趋势**: 渐变过渡，不能跳变

### R4: 场景数量计算

```
场景数 N = ceil(目标时长(秒) ÷ 单镜时长(秒))
```

- 每个分镜时长 **≤ 12 秒**
- 如果 `单镜时长` 未指定，默认 12 秒
- 示例：目标时长 24 秒，单镜 12 秒 → N = 2

### R6: 音频提示词规则

每个 `图生视频提示词` 末尾必须附加以下英文指令：
```
ambient sounds only, no character speech or dialogue audio
```
确保 Seedance 只生成环境音效（脚步声、雨声、门声等），不生成人物说话的声音。角色语音由 Stage 5 TTS 独立控制。

### R5: 静态首帧 vs 动态变化

两类提示词有明确分工，**不可混淆**：

| 字段 | 描述内容 | 用于阶段 | 时态 |
|------|---------|---------|------|
| `文生图提示词` | 该分镜的**起始瞬间**画面（静态） | Stage 3 首帧 | 现在时 |
| `末帧图提示词` | 该分镜的**结束瞬间**画面（静态，可选） | Stage 3 尾帧 | 现在时 |
| `图生视频提示词` | 从首帧到尾帧的**运动过程**（动态） | Stage 4 图生视频 | 进行时 |

**WRONG** — 文生图包含动态描述：
```yaml
文生图提示词: |
  ..., camera slowly pans across the skyline as the sun sets...
```

**CORRECT** — 文生图只描述静态画面：
```yaml
文生图提示词: |
  ..., a wide-angle view of a city skyline,
  the sun hovering just above the horizon,
  sky painted in gradients of orange and purple,
  glass skyscrapers reflecting warm golden light

图生视频提示词: |
  slow pan from left to right across the skyline,
  the sun gradually descends below the horizon,
  sky colors shift from orange to deep purple,
  city lights begin to flicker on, 12 seconds
```

---

## 提示词工程指南

### 图像提示词结构

按以下顺序组织 `文生图提示词`：

```
[1. 统一风格前缀（原样复制）]
[2. 角色完整外貌（从DNA卡片复制，如有角色）]
[3. 场景环境描述]
[4. 角色动作/姿态（静态瞬间）]
[5. 构图/景别]
[6. 光线/氛围]
```

### 末帧提示词结构（可选）

按以下顺序组织 `末帧图提示词`（结构同 `文生图提示词`，但描述场景结束时的状态）：

```
[1. 统一风格前缀（原样复制）]
[2. 角色完整外貌（从DNA卡片复制，如有角色）]
[3. 场景环境描述（反映时间/光线变化后的状态）]
[4. 角色动作/姿态（场景结束时的位置）]
[5. 构图/景别]
[6. 光线/氛围（变化后的状态）]
```

> 省略 `末帧图提示词` 时，Stage 3 仅生成首帧，Stage 4 使用单帧模式（Seedance 自行生成运动）。

### 视频提示词结构

按以下顺序组织 `图生视频提示词`：

```
[1. 镜头运动指令]
[2. 角色动作描述]
[3. 环境变化描述]
[4. 时长提示（默认 "12 seconds"）]
```

### 镜头运动词汇表

| 中文 | 英文 | 适用场景 |
|------|------|---------|
| 推镜 | push in / dolly in | 逐渐靠近主体，增强紧张感 |
| 拉镜 | pull out / dolly out | 逐渐远离，揭示全景 |
| 左摇/右摇 | pan left / pan right | 水平扫视场景 |
| 上摇/下摇 | tilt up / tilt down | 垂直移动视角 |
| 跟拍 | tracking shot | 跟随运动主体 |
| 航拍俯冲 | aerial dive | 无人机视角快速下降 |
| 环绕 | orbit / arc shot | 围绕主体旋转 |
| 固定 | static / locked | 无镜头运动 |
| 缓慢变焦 | slow zoom | 微妙推进，电影感 |
| 手持晃动 | handheld | 临场感、纪实感 |

### 景别映射

| 中文 | 英文 | 画面范围 |
|------|------|---------|
| 远景 | extreme wide shot | 环境为主，人物极小 |
| 全景 | wide shot / full shot | 人物全身可见 |
| 中景 | medium shot | 人物腰部以上 |
| 近景 | close-up | 人物胸部以上 |
| 特写 | extreme close-up | 面部或细节 |

---

## 视频类型差异处理

### 创意短视频（无角色）

- `角色` 列表为空 → 跳过 R1（DNA 重复规则）
- `台词` 和 `旁白` 通常为空
- 聚焦视觉构图和氛围变化
- `音效提示` 可包含环境音描述

### 短剧（完整链路）

- 必须严格执行 R1（DNA 完整重复）
- `台词` 是必填字段（驱动 Stage 5 TTS 和 Stage 8 Lip-Sync）
- 每个有台词的分镜需要考虑嘴型匹配
- `情绪` 字段影响 TTS 的 emotion 参数

### 宣传片/广告

- 可能有也可能没有角色
- `旁白` 通常是主要文本输出（而非台词）
- 聚焦产品/品牌展示
- `音效提示` 偏向品牌音效

---

## 输出验证

生成 storyboard.yaml 后，加载 `video-validate-storyboard` Skill 执行完整验证。
详见该 Skill 的 13 项检查清单和结构化报告格式。

---

## 完整示例：L1 创意短视频（城市日落延时，3 场景）

### 输入 story.yaml 摘要

```yaml
视频类型: 创意短视频
目标时长: 24秒
单镜时长: 12秒
角色: []  # 无角色
风格锁定:
  统一风格前缀: >-
    cinematic photorealistic, warm desaturated color grading,
    golden hour backlit, subtle film grain, shallow depth of field,
    16:9 aspect ratio, 1920x1080 resolution
```

### 输出 storyboard.yaml

```yaml
元信息:
  项目ID: "test-001"
  生成日期: "2026-03-20"
  场景总数: 3
  目标总时长: "24秒"
  画幅: "16:9"

风格锁定:
  统一风格前缀: >-
    cinematic photorealistic, warm desaturated color grading,
    golden hour backlit, subtle film grain, shallow depth of field,
    16:9 aspect ratio, 1920x1080 resolution
  负面提示词: >-
    blurry, deformed, cartoon, anime, painting, illustration,
    overexposed, underexposed, text, watermark, logo,
    low quality, low resolution, extra limbs, disfigured

分镜列表:
  - 编号: 1
    时长: "12秒"
    景别: "远景"
    情绪: "壮丽宁静"

    文生图提示词: |
      cinematic photorealistic, warm desaturated color grading,
      golden hour backlit, subtle film grain, shallow depth of field,
      16:9 aspect ratio, 1920x1080 resolution,
      a sweeping wide-angle view of a modern East Asian city skyline,
      dozens of glass skyscrapers catching the last rays of a setting sun,
      the sky painted in layered gradients of burnt orange and soft purple,
      thin wisps of clouds streaked across the horizon,
      the sun hovering just above the skyline casting long golden shadows,
      a sense of vast urban expanse and quiet grandeur

    末帧图提示词: |
      cinematic photorealistic, warm desaturated color grading,
      golden hour backlit, subtle film grain, shallow depth of field,
      16:9 aspect ratio, 1920x1080 resolution,
      a sweeping wide-angle view of the same city skyline,
      the sun now touching the horizon line with its lower edge,
      sky colors deepened to crimson and early purple,
      a few lower-floor windows beginning to glow with warm interior light,
      long shadows stretching across the urban landscape,
      the transition from day to dusk captured in a single still moment

    图生视频提示词: |
      slow pan from left to right across the entire skyline,
      the sun gradually descends touching the horizon line,
      sky colors deepen from orange to crimson and then purple,
      shadows on the buildings elongate subtly,
      a few distant lights begin to twinkle on the lower floors,
      12 seconds

    台词: ""
    旁白: ""
    音效提示: "轻柔的城市环境音，远处汽车声，微风"

  - 编号: 2
    时长: "12秒"
    景别: "中景"
    情绪: "温暖感性"

    文生图提示词: |
      cinematic photorealistic, warm desaturated color grading,
      golden hour backlit, subtle film grain, shallow depth of field,
      16:9 aspect ratio, 1920x1080 resolution,
      a busy city crosswalk at dusk seen from street level,
      silhouettes of pedestrians mid-stride backlit by the warm glow
      of a deep orange sky, neon shop signs beginning to glow
      in soft pink and blue on both sides of the street,
      wet asphalt reflecting the warm sky colors,
      the overall mood is cinematic and warmly melancholic

    图生视频提示词: |
      static camera with subtle handheld sway,
      pedestrians walk across the crosswalk in both directions,
      their silhouettes shift and overlap against the bright sky,
      neon signs gradually intensify in brightness,
      reflections on the wet road shimmer with each passing step,
      12 seconds

    台词: ""
    旁白: ""
    音效提示: "行人脚步声，红绿灯提示音，霓虹灯嗡鸣"

  - 编号: 3
    时长: "12秒"
    景别: "特写"
    情绪: "诗意收束"

    文生图提示词: |
      cinematic photorealistic, warm desaturated color grading,
      golden hour backlit, subtle film grain, shallow depth of field,
      16:9 aspect ratio, 1920x1080 resolution,
      an extreme close-up of a modern glass curtain wall
      on a skyscraper facade, the glass panels reflecting
      a vivid sunset sky with swirling clouds of orange and deep blue,
      faint interior office lights visible behind the glass,
      water droplets from recent rain dotting the surface,
      each droplet catching a tiny reflection of the colorful sky

    图生视频提示词: |
      slow push in toward the glass surface,
      the reflected sunset colors shift and morph
      as the viewing angle changes slightly,
      interior lights behind the glass grow brighter
      as the sky darkens, water droplets catch light
      and sparkle momentarily, a poetic closing composition,
      12 seconds

    台词: ""
    旁白: ""
    音效提示: "安静的环境音，偶尔水滴滑落声，远处城市低鸣渐弱"
```

### 验证检查

| 检查项 | 结果 |
|--------|------|
| 场景数 = ceil(24/8) = 3 | PASS |
| 每个文生图以风格前缀开头 | PASS (均以 "cinematic photorealistic" 开头) |
| 角色 DNA 完整重复 | N/A (创意短视频无角色) |
| 文生图仅静态描述 | PASS (无镜头运动词) |
| 图生视频含镜头运动 | PASS (slow pan / static + handheld / slow push in) |
| 时间连贯: 日落→黄昏→夜幕初降 | PASS |
| 光线连贯: 金色→暖橙→橙蓝交融 | PASS |
