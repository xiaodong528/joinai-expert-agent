---
name: video-s5-tts
description: "豆包 TTS 异步长文本合成 + 字幕时间戳生成。Triggers on TTS, voice synthesis, text to speech, subtitle."
---

# Stage 5: TTS 语音合成 + 字幕生成 (Async)

## 用途

使用豆包 TTS 异步长文本合成 API 为每个场景合成旁白音频，同时通过 `enable_subtitle` 获取句级字幕时间戳，直接生成 SRT 文件。
此阶段为**可选** — 短剧（带旁白/配音）必需；宣传片/广告和创意短视频跳过。
在 GasTown 中跨所有场景并行运行（Wave 3，与 Stage 4 和 Stage 6 并行）。

## 输入/输出契约

**输入**
- `Video-Producer-output/{project_id}/scripts/storyboard.yaml` — 包含每个场景的：
  - `台词` 或 `旁白`：口语文本
  - `speaker`：可选 2.0 音色 ID（默认 `zh_male_ruyayichen_uranus_bigtts`）

**输出**
- `Video-Producer-output/{project_id}/audio/tts-{01..N}.mp3` — 每个场景的语音文件
- `Video-Producer-output/{project_id}/subtitles/scene-{01..N}.srt` — 每个场景的 SRT 字幕文件（含精确时间戳）
- `Video-Producer-output/{project_id}/audio/tts-manifest.json` — 时长清单（供 Stage 7 对齐）

## API 详情

- **模型**：豆包语音合成 2.0 大模型（`seed-tts-2.0`）
- **平台**：火山引擎 OpenSpeech
- **协议**：HTTP REST V3（异步提交 + 轮询）
- **认证**：`TTS_APP_ID` + `TTS_TOKEN` 环境变量

### 端点

| 操作 | 方法 | URL |
|------|------|-----|
| 提交任务 | `POST` | `https://openspeech.bytedance.com/api/v3/tts/submit` |
| 轮询结果 | `POST` | `https://openspeech.bytedance.com/api/v3/tts/query` |

### 请求头

```
Content-Type: application/json
X-Api-App-Id: {TTS_APP_ID}
X-Api-Access-Key: {TTS_TOKEN}
X-Api-Resource-Id: seed-tts-2.0
X-Api-Request-Id: {UUID}
```

### 关键参数

| 参数 | 值 | 说明 |
|------|-----|------|
| `appid` | `TTS_APP_ID` 环境变量 | 豆包语音应用 ID |
| `reqid` | UUID（20-64 字符） | 唯一请求 ID |
| `text` | 场景台词/旁白 | 最大 10 万字符 |
| `format` | `mp3` | 输出格式 |
| `speaker` | `zh_male_ruyayichen_uranus_bigtts`（默认） | 儒雅逸辰 2.0，视频配音推荐 |
| `enable_timestamp` | `true` | 返回句级+字级时间戳（秒 float） |

### 2.0 音色完整列表

**通用场景**

| speaker | 名称 | 语种 |
|---------|------|------|
| `zh_female_vv_uranus_bigtts` | vivi 2.0 | cn |
| `zh_female_xiaohe_uranus_bigtts` | 小何 | cn |
| `zh_male_m191_uranus_bigtts` | 云舟 | cn |
| `zh_male_taocheng_uranus_bigtts` | 小天 | cn |
| `zh_male_liufei_uranus_bigtts` | 刘飞 2.0 | zh |
| `zh_male_sophie_uranus_bigtts` | 魅力苏菲 2.0 | zh |
| `zh_female_qingxinnvsheng_uranus_bigtts` | 清新女声 2.0 | zh |
| `zh_female_tianmeixiaoyuan_uranus_bigtts` | 甜美小源 2.0 | zh |
| `zh_female_tianmeitaozi_uranus_bigtts` | 甜美桃子 2.0 | zh |
| `zh_female_shuangkuaisisi_uranus_bigtts` | 爽快思思 2.0 | zh |
| `zh_female_linjianvhai_uranus_bigtts` | 邻家女孩 2.0 | zh |
| `zh_male_shaonianzixin_uranus_bigtts` | 少年梓辛/Brayan 2.0 | zh |
| `zh_female_meilinvyou_uranus_bigtts` | 魅力女友 2.0 | zh |

**视频配音（推荐用于旁白）**

| speaker | 名称 | 语种 |
|---------|------|------|
| `zh_male_ruyayichen_uranus_bigtts` | **儒雅逸辰 2.0（默认）** | zh |
| `zh_male_dayi_uranus_bigtts` | 大壹 2.0 | zh |
| `zh_female_peiqi_uranus_bigtts` | 佩奇猪 2.0 | zh |
| `zh_male_sunwukong_uranus_bigtts` | 猴哥 2.0 | zh |
| `zh_female_mizai_uranus_bigtts` | 黑猫侦探社咪仔 2.0 | zh |
| `zh_female_jitangnv_uranus_bigtts` | 鸡汤女 2.0 | zh |
| `zh_female_liuchangnv_uranus_bigtts` | 流畅女声 2.0 | zh |

**角色扮演**

| speaker | 名称 | 语种 |
|---------|------|------|
| `zh_female_cancan_uranus_bigtts` | 知性灿灿 2.0 | zh |
| `zh_female_sajiaoxuemei_uranus_bigtts` | 撒娇学妹 2.0 | zh |
| `saturn_zh_female_cancan_tob` | 知性灿灿 | cn |
| `saturn_zh_female_keainvsheng_tob` | 可爱女生 | cn |
| `saturn_zh_female_tiaopigongzhu_tob` | 调皮公主 | cn |
| `saturn_zh_male_shuanglangshaonian_tob` | 爽朗少年 | cn |
| `saturn_zh_male_tiancaitongzhuo_tob` | 天才同桌 | cn |

**专业场景**

| speaker | 名称 | 场景 | 语种 |
|---------|------|------|------|
| `zh_female_yingyujiaoxue_uranus_bigtts` | Tina老师 2.0 | 教育 | zh |
| `zh_female_kefunvsheng_uranus_bigtts` | 暖阳女声 2.0 | 客服 | zh |
| `zh_female_xiaoxue_uranus_bigtts` | 儿童绘本 2.0 | 有声阅读 | zh |

**英文音色**

| speaker | 名称 | 语种 |
|---------|------|------|
| `en_male_tim_uranus_bigtts` | Tim | en |
| `en_female_dacey_uranus_bigtts` | Dacey | en |
| `en_female_stokie_uranus_bigtts` | Stokie | en |

### 字幕返回格式（`enable_timestamp: true`）

```json
{
  "sentences": [
    {
      "text": "深夜十一点，城市的喧嚣早已褪去。",
      "startTime": 0.28,
      "endTime": 6.07,
      "words": [{"word": "深", "startTime": 0.28, "endTime": 0.42, "confidence": 0.8}]
    }
  ]
}
```

时间单位：**秒（float64）**。V3 API 使用 `startTime`/`endTime`（驼峰），非 V1 的 `begin_time`/`end_time`。

### 异步模式

```
submit → task_id
poll every 3s (POST /api/v3/tts/query) → task_status: 1(Running) / 2(Success) / 3(Failure)
on success → download audio_url + 提取 sentences[] 字幕时间戳
timeout: 120 seconds
```

## 脚本

```bash
python .opencode/skills/video-s5-tts/scripts/stage5_tts.py \
  --project-id <project_id> \
  --storyboard Video-Producer-output/<project_id>/scripts/storyboard.yaml \
  --speaker zh_male_ruyayichen_uranus_bigtts
```

每个场景的完整流程：TTS 提交→轮询→下载 MP3→生成 SRT→FFmpeg 混合嵌入到视频。

> **重要设计决策**：
> - FFmpeg 使用 `amix` 将 TTS 旁白（volume=1.0）与视频原音/Seedance 环境音效（volume=0.3）**混合**，而非替换。TTS 结束后只剩环境音效。
> - **不使用 `-shortest`**，保持视频原始时长（如 12 秒），不裁剪视频画面。
> - 旁白建议控制在 8 秒左右（约 35-40 字），视频保持完整 12 秒，TTS 结束后有 4 秒纯环境音画面过渡。
> - 生成的 `-tts-sub.mp4` 片段已包含 TTS 音频，Stage 7 拼接时**不再单独混合 TTS**，仅额外添加 BGM。

## 严格并行调度模式（必须遵守）

**Stage 5 并行执行时，必须使用子智能体（每个场景一个）。** 每个子智能体独立完成 TTS→SRT→FFmpeg 嵌入的完整流程：

```bash
# 子智能体 1: 处理场景 1
python .opencode/skills/video-s5-tts/scripts/stage5_tts.py \
  --project-id {id} --storyboard ... --scene 1

# 子智能体 N: 处理场景 N（全部同时启动）
python .opencode/skills/video-s5-tts/scripts/stage5_tts.py \
  --project-id {id} --storyboard ... --scene {N}
```

## 验证清单

- [ ] 所有 `tts-{01..N}.mp3` 文件存在于 `Video-Producer-output/{project_id}/audio/`
- [ ] 所有 `scene-{01..N}.srt` 文件存在于 `Video-Producer-output/{project_id}/subtitles/`
- [ ] 所有 `scene-{01..N}-tts-sub.mp4` 存在于 `Video-Producer-output/{project_id}/clips/`
- [ ] 每个 `-tts-sub.mp4` 包含 video + audio + subtitle 三轨道
- [ ] `tts-manifest.json` 已写入，包含每个场景的时长和文本
- [ ] 每个 MP3 > 5 KB（非空白）
- [ ] 各片段音色一致（同一 speaker）
- [ ] SRT 字幕时间戳与音频对齐
- [ ] 时长与文本长度合理匹配（中文约 3-5 字/秒）

## 错误处理

- HTTP 401：检查 `TTS_APP_ID` 和 `TTS_TOKEN` 是否正确设置
- 任务失败（task_status=2）：记录错误信息，重试一次
- 轮询超时（120s）：记录 scene_id，继续处理其他场景
- 无字幕数据：音频仍保存，跳过 SRT 生成

## 备注

- `TTS_TOKEN` 是豆包语音应用的 Access Token，**不是** `ARK_API_KEY`（火山方舟）
- voice_type 在同一项目的所有场景中必须保持一致
- Stage 9（字幕烧录）直接使用本阶段生成的 SRT 文件，无需 ASR 识别
- 若跳过 TTS（非短剧视频类型），Stage 7 仅使用 BGM，Stage 9 跳过
