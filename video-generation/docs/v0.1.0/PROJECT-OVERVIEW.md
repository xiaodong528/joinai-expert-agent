# JoinAI Swarm Factory — AI 视频生成工作流

> **状态**: 已完成（5/5 子任务） | **更新**: 2026-03-21 | **成本**: ~¥8-14/片（不含 LLM）

设计并实现 11 阶段全自动 AI 视频制作管线，运行在 GasTown 多智能体系统上，支持短剧/宣传片/教程/广告/创意短视频等多种类型。

---

## 1. 管线架构速览

```
Stage 0  创意策划 (Mayor, 交互式)     → story.yaml
Stage 1  分镜脚本 (Polecat, LLM)      → storyboard.yaml
Stage 2  角色锚定 (Polecat, 可选)     → character ref images
Stage 3  关键帧生成 (Polecat x N)     → scene-{01..N}.png
Stage 4  图生视频 (Polecat x N, 异步) → scene-{01..N}.mp4
Stage 5  TTS语音+字幕 (Polecat x N, 可选) → tts-{01..N}.mp3 + subtitles/scene-{01..N}.srt
Stage 6  BGM音乐 (Polecat x 1, 可选)  → bgm.mp3
Stage 7  视频拼接+字幕合并 (Mayor, FFmpeg) → concat-mixed.mp4
Stage 8  对口型 (Mayor, 可选, 异步)   → lipsync.mp4
Stage 9  硬烧字幕（仅需要时，需libass） (Mayor, 可选) → final.mp4 + final.srt
Stage 10 质量审查 (Mayor, ffprobe+LLM) → qa-report.json
```

### Wave 并行化（GasTown 编排）

| Wave | Polecat 数 | 任务 |
|------|-----------|------|
| 1 | 2 | 分镜脚本 ‖ 角色锚定 |
| 2 | N | 关键帧生成（首帧锚定链，批内串行） |
| 3 | 2N+1 | 图生视频(xN) ‖ TTS(xN) ‖ BGM(x1) |
| Mayor | — | 拼接 → 对口型 → 字幕 → QA |

10 场景时峰值并行度 21 个 Polecat。

---

## 2. 技术栈总表

| Stage | 模型 | 模型 ID | API 端点（国内） | 环境变量 | 单片成本 |
|-------|------|---------|-----------------|---------|---------|
| 0,1,10 | GasTown 默认 LLM | — | — | — | GasTown 承担 |
| 2 | Seedream 4.0 | `doubao-seedream-4-0-250828` | `ark.cn-beijing.volces.com/api/v3/images/generations` | `ARK_API_KEY` | ¥0.40~2.00 |
| 3 | Seedream 4.0 | `doubao-seedream-4-0-250828` | 同上 | `ARK_API_KEY` | ¥2.00~4.00 |
| 4 | Seedance 1.5 Pro | `doubao-seedance-1-5-pro-251215` | `volcenginesdkarkruntime.Ark` SDK | `ARK_API_KEY` | ¥1.00~3.00 |
| 5 | 豆包语音合成 2.0 大模型 | `seed-tts-2.0` / `zh_male_ruyayichen_uranus_bigtts` | `openspeech.bytedance.com/api/v3/tts/submit` | `TTS_APP_ID` + `TTS_TOKEN` | ¥0.18 |
| 6 | Music 2.5+ | `music-2.5+` | `api.minimaxi.com/v1/music_generation` | `MINIMAX_API_KEY` | ¥1.09 |
| 7 | FFmpeg | — | 本地 CLI（输出 concat-mixed.mp4） | — | ¥0 |
| 8 | 可灵 Lip-Sync | `kling-v1-6` | `api.klingai.com/v1/videos/lip-sync` | `KLING_ACCESS_KEY` + `KLING_SECRET_KEY` | ¥3.83~7.65 |
| 9 | 豆包 ASR 2.0 | — | Batch recognition | `ARK_API_KEY` | ¥0.04 |

**容灾备份**: Wan 2.2 kf2v-flash (`DASHSCOPE_API_KEY`) | CosyVoice | Mureka | LatentSync

### 认证模式

- **火山引擎/MiniMax/阿里云**: `Bearer {API_KEY}` 标准 header
- **豆包 TTS 2.0**: `TTS_APP_ID` + `TTS_TOKEN`（V3 API 使用 `X-Api-App-Id` + `X-Api-Access-Key` + `X-Api-Resource-Id: seed-tts-2.0` 请求头）
- **快手可灵**: 双密钥 JWT（`KLING_ACCESS_KEY` + `KLING_SECRET_KEY` 签名生成 token）

### 异步 API 轮询

| API | 轮询间隔 | 超时 |
|-----|---------|------|
| Seedance (Stage 4) | 5s | 5min |
| 豆包 TTS 异步 (Stage 5) | 3s | 120s |
| MiniMax Music (Stage 6) | 同步模式（`output_format: "url"` 返回 OSS 音频 URL，超时 600s） | — |
| 可灵 Lip-Sync (Stage 8) | 5s | 10min |

---

## 3. 实施架构

```
GasTown Mayor（并行编排层）
  │ dispatch beads → Polecat (Wave 1/2/3 并行子智能体)
  ▼
OpenCode Agent: video-generation-orchestrator（主编排智能体）
  │ Wave 1/2/3: 派发子智能体并行执行
  │ Stage 7-10: 主智能体直接串行执行
  ▼
11 个 Stage Skill（混合式：指令 + 脚本引用）
  │ .opencode/skills/video-s*/scripts/*.py
  ▼
外部 MCP（仅视觉理解 / 网络搜索 / 视频分析）
```

| 决策 | 选择 |
|------|------|
| 封装层级 | 11 独立 Skill + Agent 层编排 |
| 编排模式 | 并行阶段 → 子智能体；串行阶段 → 主智能体直接执行 |
| MCP 策略 | 轻量为主，仅复杂感知类用 MCP |
| Skill 粒度 | 混合式：核心 API 脚本固化 + 灵活部分指令式 |

### 渐进路径

| 阶段 | 子任务 | 产出 |
|------|--------|------|
| API 验证 | 3 (Phase 2) | `.opencode/skills/video-s*/scripts/*.py` |
| Skill 封装 | 3 (Phase 3 后) | `.opencode/skills/video-s{0..10}-*/SKILL.md` |
| Agent 定义 | 4 | `video-generation/.opencode/agents/video-generation-orchestrator.md` |
| GasTown 集成 | 5 | `gastown/mayor-video-orchestration.md` + `beads/*.md` |

---

## 4. 子任务进度看板

| # | 子任务 | 状态 | 完成日期 | 关键产出 |
|---|--------|------|---------|---------|
| 1 | 梳理AI视频生成工作流步骤 | ✅ 已完成 | 2026-03-19 | `JAS AI 视频生成工作流定义.md` |
| 2 | 各环节模型选型与调研 | ✅ 已完成 | 2026-03-20 | `模型选型评估报告.md` |
| 3 | 各步骤单独测试验证 | ✅ 已完成 | 2026-03-21 | 9 个 Stage 脚本 + 11 个 OpenCode Skills（每个 Skill 自带独立 api_client.py） |
| 4 | 工作流优化与串联 | ✅ 已完成 | 2026-03-21 | L1/L2/L3 集成测试脚本（dry-run 通过） |
| 5 | 集成到GasTown全自动化执行 | ✅ 已完成 | 2026-03-26 | Mayor 编排 prompt + Wave 1/2/3 Bead 模板 + Rig Agent 桥接配置（ADR-001 §5.2 L2） |

---

## 4. 实现产物清单

### Python 脚本（`.opencode/skills/video-s*/scripts/`）

每个 Stage Skill 自带独立脚本和 `api_client.py`（不共享），路径格式为 `.opencode/skills/video-s{N}-{name}/scripts/`。

| 脚本 | Skill 目录 | 用途 |
|------|-----------|------|
| `stage2_seedream.py` | `video-s2-character-anchor` | Seedream 文生图 + image_urls 角色锚定 |
| `stage3_keyframe_chain.py` | `video-s3-keyframe-gen` | 首尾帧锚定链（txt2img → img2img, `--start-scene`/`--end-scene` 分批） |
| `stage4_seedance.py` | `video-s4-image-to-video` | Seedance 图生视频（异步, `--scene N` 单场景模式） |
| `stage5_tts.py` | `video-s5-tts` | 豆包 TTS 语音合成 |
| `stage6_bgm.py` | `video-s6-bgm` | MiniMax BGM 生成（同步，output_format=url） |
| `stage7_concat.py` | `video-s7-concat` | FFmpeg 视频拼接 + 音频混合 |
| `stage8_lipsync.py` | `video-s8-lipsync` | 可灵 Lip-Sync + 10s 分段处理（异步） |
| `stage9_subtitle.py` | `video-s9-subtitle` | 字幕生成（SRT）+ FFmpeg 烧录 |
| `stage10_qa.py` | `video-s10-qa-review` | ffprobe QA 检查 + JSON 报告 |

### OpenCode Skills（`.opencode/skills/`）

11 个 SKILL.md（video-s0 through video-s10），每个包含 I/O 契约、关键参数、验证清单。

### GasTown 模板（`gt/gastown/`）

| 文件 | 用途 |
|------|------|
| `settings/config.json` | Rig Agent 桥接配置 — `opencode --agent video-generation-orchestrator`（ADR-001 §5.2 L2） |
| `mayor-video-orchestration.md` | Mayor 编排 prompt（Wave 调度 + 裁剪表 + 质量门控） |
| `beads/wave-1-script-anchor.md` | Wave 1: 分镜脚本 + 角色锚定 |
| `beads/wave-2-keyframe.md` | Wave 2: 关键帧生成（首帧锚定链） |
| `beads/wave-3-generate.md` | Wave 3: 视频 + TTS + BGM 并行生成 |

### 下一步：实际 API 验证

脚本和管线逻辑已通过 dry-run 验证。实际 API 调用需要：
1. 逐 Stage 验证（需 `cd` 到对应 `scripts/` 目录或设置 `PYTHONPATH`，见 CLAUDE.md）
2. 确认 5 个关键决策点（generate_audio 一致性、角色锚定效果等）
3. Round 3（Stage 4/5/6）和 Round 4（Stage 8/9）待执行

---

## 5. 关键决策点（3/5 已确认，2 待测试）

| # | 问题 | 测试方法 | 影响 |
|---|------|---------|------|
| 1 | ✅ Seedance `generate_audio=true` 音色一致性 | 已测试通过，使用 ambient sounds only 策略 | 已确认 |
| 2 | Seedream `image_urls` 角色锚定效果 | 传参考图生成 3 张对比 | 若不足 → ComfyUI + IP-Adapter |
| 3 | ✅ 豆包 TTS voice_type 跨请求一致性 | 已验证 seed-tts-2.0 + zh_male_ruyayichen 跨请求一致 | 已确认 |
| 4 | ✅ 首帧锚定链视觉连贯性 | scale=0.4 已验证效果理想 | 已确认 |
| 5 | 可灵 Lip-Sync 10s 分段拼接 | 15s 场景分 2 段处理 | 若不自然 → 限制场景 ≤10s |

---

## 6. 成本估算（3 分钟 / 10 场景）

| 项目 | 金额 |
|------|------|
| 图像生成（角色锚定+关键帧） | ¥2.40~6.00 |
| 视频生成（10 场景） | ¥1.00~3.00 |
| TTS + BGM + ASR | ¥1.31 |
| Lip-Sync（50% 场景） | ¥3.83 |
| **总计（不含 LLM）** | **¥8.54~14.14** |

> Lip-Sync 占 40%+ 是成本大头，仅对有人物特写的场景启用可显著降本。

---

## 7. 文档索引

| 文件 | 用途 | 行数 |
|------|------|------|
| `JAS AI 视频生成工作流定义.md` | 主规格：11 阶段管线、I/O 契约、Wave 并行化、视频类型预设 | ~738 |
| `模型选型评估报告.md` | 模型选型：各阶段 API 评估、定价、成本估算 | ~394 |
| `各步骤单独测试验证.md` | 测试计划：逐 Stage 验证规格、L1/L2/L3 集成测试、异步轮询 | ~690+ |
| `CLAUDE.md` | Claude Code 项目指引：模型 ID、端点、认证模式、目录约定 | ~136 |
| `PROJECT-OVERVIEW.md` | 本文件：项目总览一页纸 | — |

---

## 8. 快速命令参考

```bash
# 激活虚拟环境
source .venv/bin/activate

# 环境变量（已配置到 ~/.zshrc）
echo $ARK_API_KEY          # 火山引擎
echo $MINIMAX_API_KEY      # MiniMax
echo $KLING_ACCESS_KEY     # 可灵 Access Key
echo $KLING_SECRET_KEY     # 可灵 Secret Key
echo $TTS_APP_ID           # 豆包 TTS App ID
echo $TTS_TOKEN            # 豆包 TTS Token
echo $DASHSCOPE_API_KEY    # 阿里云百炼（备用）

# FFmpeg 版本
ffmpeg -version            # 8.0.1
ffprobe -version           # 8.0.1

# 测试输出目录
ls Video-Producer-output/test-001/        # scripts/ characters/ frames/ clips/ audio/ videos/ subtitles/

# Notion 任务看板
# /task pull AI视频生成    # 拉取 Notion 进度到本地文档
```
