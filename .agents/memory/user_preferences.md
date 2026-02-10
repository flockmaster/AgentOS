---
last_updated: 2026-02-10
---

# User Preferences (长期记忆 - 偏好设置)

这里记录用户显式提出的、在所有项目中都应遵守的个人偏好。
**更新机制**: 仅在用户明确说 "以后都要/不要..." 时添加。
**遗忘机制**: 用户说 "改一下习惯" 时修改，或由于长期不使用而标记为 [Deprecated]。
**规范来源**: 本偏好提炼自 `flutter-ai-advanced-template`（用户长期实践的开发规范）。

## 1. 沟通风格
- **语言**: 强制中文 (Chinese Mandatory)。
- **啰嗦程度**: 极简 (Extreme Briefness)。
  - 禁止解释标准库用法 (如 `Container` 是什么)。
  - 禁止复述显而易见的代码变更。
  - 直接输出 `diff` 或 `code`，除非有高风险操作需要警告。
- **反馈**: 遇到模糊需求强制反问（需求澄清门禁）。
- **疑问即停顿**: 遇到业务歧义、视觉细节疑问、架构不确定时，必须先停下来问我，禁止猜测。

## 2. 开发流程习惯
- **PRD**: 生成 PRD 后必须等待确认 (Gate 1)。
- **Git**: 编译成功必须自动提交 (Gate 2)。
- **测试**: 原子任务完成后必须自测。
- **Flutter 开发**: 开始 Flutter 功能开发前，先执行 `/use-flutter-template`，并遵守模板规范。
- **先读后写**: 写代码前必须先读取相关模板文件（如 ViewModel 模板），禁止凭记忆动手。
- **异常 Step 0**: 遇到任何报错，必须先记录到 `exception_history.md` 再修复，禁止直接改代码。同一错误出现 3 次自动晋升为 `prevention_rules.md`。
- **核心文件保护**: 修改基类 / `.rules` / 网络层等核心文件前，必须先向我陈述理由并获得同意。

## 3. 技术栈偏好
- **框架**: Flutter (强制)。
- **架构**: Stacked Framework (MVVM)。ViewModel 必须继承 `BaicBaseViewModel`，View 必须用 `ViewModelBuilder<T>.reactive()` 构建。
- **状态管理**: Stacked（`notifyListeners`）。
- **依赖注入**: Get_it (`locator<T>()`)。
- **网络层**: Dio + `ApiClient`。Mock 数据通过 `MockInterceptor` 拦截，业务代码零感知。
- **JSON**: `json_serializable`。
- **导航**: 页面跳转只用 `MapsTo()`，ViewModel 中禁止出现 `BuildContext` / `Navigator` / `showDialog`。

## 4. UI / 视觉规范（铁律级别）
- **颜色**: 禁止 `Color(0xFF...)` 硬编码，唯一来源 `AppColors.xxx`。
- **圆角**: 禁止 `BorderRadius.circular(裸数字)`，唯一来源 `AppDimensions.radiusXS/S/M/L/Full`。
  - XS=4 / S=8 / M=12 / L=16 / Full=999
- **间距**: 禁止 `EdgeInsets.all(裸数字)`，唯一来源 `AppDimensions.spaceXS/S/M/ML/L/XL/XXL`。
- **字体**: 数字用机械字体 `AppTypography.dataDisplayXXX`，价格用 `AppTypography.priceMain`。
- **交互**: 所有可点击元素必须用 `BaicBounceButton` 包裹。
- **自检**: 代码里出现裸数字（除 0/1/0.5 等基础比例外）即违规，必须替换为设计系统常量。

## 5. 代码文档规范
- **中文备注**: 所有 Model 字段、ViewModel 方法、Service 接口必须有完整中文注释。
- **业务意图**: 备注说明字段的业务含义、方法的触发场景、异常处理意图。
- **自检**: "离了 AI，人类开发者看这段备注能瞬间明白业务意图吗？"

## 6. 数据层规范
- **接口先行**: 所有数据获取必须通过 `ApiClient` 网络请求。
- **禁止本地 Mock**: Service 里禁止 `if (mock) return localData`，用 `MockInterceptor` 代替。
- **自检**: "如果明天换成真实后端，这行代码需要删吗？"需要删就是违规。

## 7. 原型驱动开发
- **原型即真理**: 有原型时，`prototypes/` 中的 React 组件是 UI 和业务逻辑的唯一参考源。
- **禁止脑补**: 禁止凭空想象 UI，必须严格参考原型。
- **转换规则**: React → Flutter 转换严格适配 Stacked 架构 + BAIC 视觉规范。
