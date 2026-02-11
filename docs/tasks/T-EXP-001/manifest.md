# Task Manifest: Codex Dispatcher Experiment (T-EXP-001)

## 任务目标
测试 Codex 在不同场景下的行为模式，以便优化 `codex-dispatch.md` 的调度逻辑。

## 实验清单

### EXP-01: 基础命令执行与输出
- [ ] **Case A**: 执行简单的 `echo "Hello World"`，验证 `json` 输出格式。
- [ ] **Case B**: 执行耗时操作 `start-process sleep 5`，验证异步等待机制。

### EXP-02: 文件操作与 Side Effects
- [ ] **Case A**: 创建文件 `test_file.txt`。
- [ ] **Case B**: 修改文件内容（追加文本）。
- [ ] **Case C**: 删除文件。
- **验证点**: 检查 `--dangerously-bypass-approvals-and-sandbox` 是否真的绕过了交互确认。

### EXP-03: 长时间运行与交互
- [ ] **Case A**: 执行一个需要用户输入的脚本（模拟 Worker 提问）。
- [ ] **Case B**: 验证 PM 能否通过 `send_command_input` 回复。

### EXP-04: 错误处理与 Exit Code
- [ ] **Case A**: 执行一个必定失败的脚本 (`exit 1`)。
- [ ] **Case B**: 验证 `--json` 输出中的 `error` 事件及最终 Exit Code。

## 结论产出
根据实验结果，更新 `codex-dispatch.md` 中的最佳实践部分。
