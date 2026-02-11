# 🔄 PRD: Antigravity Agent OS 官网 (研发版)

> **版本**: 1.0 | **日期**: 2026-02-10 | **状态**: 已确认

## 1. 技术背景
- **项目路径**: `branding-site/`
- **技术栈**: Vanilla HTML5, CSS3, JavaScript (ES6+)
- **设计基准**: `design-system/antigravity-agent-os-landing/MASTER.md`
- **核心目标**: 实现高性能、玻璃拟态、滚动叙事动画的单页官网。

## 2. 任务拆解 (第1层 - 原子化交付)

| ID | 任务 | 状态 | 描述 | 预估 | 依赖 |
|----|------|------|------|-----|------|
| T-001 | 项目初始化与目录结构 | ✅ DONE | 创建 `branding-site/` 及其基本目录 (css, js, assets, index.html) | 0.5h | - |
| T-002 | 设计系统 CSS 变量注入 | ✅ DONE | 根据 `MASTER.md` 实现 CSS 根变量、字体导入和重置样式 | 0.5h | T-001 |
| T-003 | 基础布局框架实现 | ✅ DONE | 实现 Flex/Grid 基础结构，包含固定的浮动 Navbar (Glassmorphism) | 1h | T-002 |
| T-004 | Hero Section 实现 | ✅ DONE | 包含主标题、副标题及 CTA 按钮，应用初级入场动画 | 2h | T-003 |
| T-005 | 滚动叙事引擎 (Scroll Engine) | ✅ DONE | 使用 Intersection Observer 实现滚动进度监听及 Section 活动状态切换 | 2h | T-001 |
| T-006 | 功能便当盒组件 (Bento Grid) | ✅ DONE | 实现玻璃拟态卡片，展示记忆系统、技能矩阵、自进化引擎 | 2h | T-003 |
| T-007 | 动态视觉终端组件 | ✅ DONE | 模拟 `/start` 启动流程的打字机效果及视觉反馈 | 1.5h | T-003 |
| [x] T-008 | 全局滚动动画调优 | ✅ DONE | 对各 Section 增加背景视差、元素位移、透明度等 Scroll-Triggered 效果 | 2h | T-005 |
| [x] T-009 | 响应式适配与 A11y 优化 | ✅ DONE | 适配 375px/1440px，确保交互元素 cursor-pointer 及焦点可见 | 1h | T-008 |
| T-010 | 性能审计与成品提交 | ⏳ PENDING | 优化加载速度，完成 UI/UX Checklist 最终检查 | 0.5h | T-009 |

## 3. 执行协议 (Worker Protocol)
1. **SSOT**: 以 `design-system/antigravity-agent-os-landing/MASTER.md` 为唯一视觉事实来源。
2. **原子提交**: 每完成一个任务 (T-XXX)，执行 Git Commit。
3. **自检查**: 提交前必须对照 `MASTER.md` 的 Pre-Delivery Checklist。

---
**提示**: 输入 `/feature-flow` 开始执行 T-001。
