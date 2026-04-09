---
illustration_id: 02
type: framework
style: china-mobile-corporate
references:
  - ref_id: 01
    filename: 01-ref-content-template.png
    usage: direct
---

JAS 三层架构 — 层级关系图

STRUCTURE: hierarchical (top-to-bottom, 3 layers)

NODES:
- Layer 1 (Top, largest): "编排层 — GasTown Mayor" — Large rounded rectangle in #0066B3 blue with white text. Contains icons: calendar(调度), shield(质量门控), arrows(Wave分发). Label: "统筹调度 · Wave 并行分发 · 质量门控"
- Layer 2 (Middle): "逻辑层 — OpenCode Agent: video-generation-orchestrator" — Medium rounded rectangle in #00A651 green with white text. Contains icons: scissors(裁剪), fork(派发), list(串行). Label: "管线裁剪 · 子智能体派发 · 串行收尾"
- Layer 3 (Bottom, widest): "执行层 — 11 个 Stage Skill" — Wide rounded rectangle in #00B4D8 teal with white text. Inside: 11 small square tiles labeled S0-S10, each with a tiny icon. Label: "每个 Skill 独立自包含 · Python 脚本 + API 客户端"

RELATIONSHIPS:
- Thick downward arrows connecting Layer 1 → Layer 2 → Layer 3
- Layer 1 to Layer 2: labeled "调度指令"
- Layer 2 to Layer 3: labeled "任务分发" with multiple arrows fanning out to different Skill tiles

LABELS: GasTown Mayor, OpenCode Agent, 11 Stage Skill, 编排层, 逻辑层, 执行层
COLORS (China Mobile Official Brand):
- Primary Blue: #0078D4 (中国移动蓝)
- Accent Teal: #00A4A6 (青绿色)
- Gradient Green: #00C853 (渐变终点绿)
- Background: #FFFFFF pure white
- Text: #333333 dark gray
- Secondary Text: #666666 gray

BRAND ELEMENTS (match reference template exactly):
- Top-right corner: China Mobile logo — a blue-green gradient sphere icon with swoosh lines, next to "中国移动 China Mobile" text in blue
- Bottom decoration: Flowing smooth blue-green gradient wave pattern starting from bottom-left corner, curving gracefully across approximately 60% of the bottom edge. Colors transition from blue (#0078D4) through teal (#00A4A6) to light green (#00C853)
- Background: Pure white #FFFFFF
- Content area: Main content centered in page middle 70%, leaving top-right 15% clear for logo and bottom 15% clear for wave decoration
- Overall feel: Clean, corporate, professional — matches China Mobile internal presentation template

STYLE: Clean corporate infographic. Flat vector illustration with bold geometric shapes. No gradients except subtle background. Black outlines on elements. Generous white space. Modern, professional, highly readable. Chinese text labels in bold sans-serif font.
ASPECT: 16:9
