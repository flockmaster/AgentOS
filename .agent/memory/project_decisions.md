---
project_name: Test Flutter App
last_updated: 2026-02-10
---

# Project Decisions (长期记忆 - 架构决策)

## 1. 技术栈
- SDK: Flutter (Core App)
- Website: Vanilla HTML5/CSS3/JS (Branding Site)
- Style: Tailwind CSS (Utility classes)

## 2. 架构设计
- App: MVVM
- Site: Component-based Vanilla JS

## 3. 编码规范
- Lint: flutter_lints
- Formatting: dart format / Prettier (JS)

## 4. 第三方库 (白名单)
| 库名 | 用途 | 添加日期 |
|------|------|---------|
| Lucide | 图标库 | 2026-02-10 |

## 5. 已知问题 (错误模式学习)
| 日期 | 错误类型 | 根因分析 | 修复方案 | 影响范围 |
|------|---------|---------|---------|---------|

## 6. Deprecated (废弃决策归档)

## 7. 🎨 UI/UX Standards (Mandatory)
- **Official Design System**: `d:\Baic-Flutter-APP\test-agent-install\design-system\antigravity-agent-os-landing\MASTER.md`
- **Design Philosophy**: Glassmorphism + Scroll-Triggered Storytelling.
- **Icon Set**: Lucide SVG only.
- **Verification**: Every UI change must be verified against the Master.md checklist by PM (Antigravity).
