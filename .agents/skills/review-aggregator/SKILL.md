---
name: review-aggregator
description: Aggregates reviews from 5 experts, resolves conflicts, prioritizes content, and updates the PRD. Also syncs the result to Feishu Docs.
---

# Review Aggregator Skill

## 1. Overview
This skill acts as the **Lead PM**. It takes input from the Expert Review Board (UX, Product, Domain, Tech, Critic), resolves conflicts based on a strict hierarchy, and produces a finalized "Rough Design" PRD. It also ensures the documentation is synced to the cloud (Feishu).

## 2. Input
- **Original Draft**: `docs/prd/[name]-draft.md`
- **Review Artifacts**:
  - `review_ux.md`
  - `review_product.md`
  - `review_domain.md`
  - `review_tech.md`
  - `review_critic.md`

## 3. Conflict Resolution Hierarchy (The Gavel)
When experts disagree, use this priority order:
1.  🔴 **Safety & Security** (Critic): Non-negotiable.
2.  🔧 **Technical Feasibility** (Tech): Hard constraints.
3.  👔 **Strategic Alignment** (Product Director): P0/P1 scope.
4.  💰 **Business Value** (Domain): Logic correctness.
5.  ✨ **UX** (UX Director): Optimization.

## 4. Actions

### Step 1: Synthesis
- Merge all "Pass" and "Optimization" suggestions.
- For "Reject" or "Blocker" items, apply the hierarchy.
- Rewrite the `User Stories` and `Requirements` in the Draft.
- Update the `Flowchart` if logic changed.

### Step 2: Documentation (The Final Artifacts)
- **Summary**: Create `docs/reviews/[name]/summary.md` listing key decisions and discarded items.
- **Final Rough PRD**: Update `docs/prd/[name]-rough.md`. **Ensure the file name ends in `-rough.md`.**

### Step 3: Cloud Sync (Feishu)
- **Call Skill**: `feishu-doc-assistant` (or use `feishu-doc-creator`).
- **Action**: Create a new Feishu Doc named "PRD: [Feature Name] (Rough)".
- **Content**:
  - Title: [Feature Name]
  - Body: Combine `summary.md` + `rough.md`.
- **Output**: Get the visible URL.

## 5. Output Format

**File**: `docs/reviews/[name]/summary.md`

```markdown
# Review Summary: [Feature Name]

## 1. Key Decisions
- [Conflict]: Resolved by [Role] -> Decision

## 2. Scope Changes
- Removed: ...
- Added: ...

## 3. Feishu Link
- [Feishu Doc](URL)
```
