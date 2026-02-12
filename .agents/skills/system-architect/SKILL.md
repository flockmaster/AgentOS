---
name: system-architect
description: A specialist skill focused on decomposing complex PRDs into atomic architecture, task manifests, and DAGs.
---

# System Architect Skill (Phase 2)

## 1. Overview
This skill acts as the **System Architect**. It takes a Rough PRD (validated by Review) and breaks it down into clear, atomic engineering tasks (`T-xxx`). It is responsible for the **Manifest** and the **Global Architecture**.

## 2. Input
- **Rough PRD**: `docs/prd/[name]-rough.md` (The source of truth).
- **Project Structure**: `lib/` and `test/` (To respect existing patterns).

## 3. Actions

### Step 1: Global Architecture (The Map)
- **Identify Structure**: Which packages/modules are touched?
- **Define DAG**: What depends on what? (e.g., API first, then Models, then UI).
- **Create Diagram**: Draw a `graph TD` showing the technical flow.

### Step 2: Task Decomposition (The Atoms)
- **Granularity**: Tasks should represent a single cohesive unit of work (e.g., "Login Screen UI", "Auth Repository").
- **Constraints**: > 1 file change, < 1 day of work.
- **Naming**: `T-{ID}` (e.g., `T-001`).

### Step 3: Manifest Generation
- **Create Folder**: `docs/tasks/[feature/id]/`.
- **Create Manifest**: `docs/tasks/[feature/id]/manifest.md`.

## 4. Output Logic (Manifest)

**File**: `docs/tasks/[feature/id]/manifest.md`

```markdown
# Task Manifest: [Feature Name]

## 1. Architecture Map (Global Context)
```mermaid
graph TD
  [Start] --> [Component A]
```

## 2. Task List (DAG)
> Checklist format. Order implies dependency.

- [ ] **T-101: [Title]**
  - Path: `docs/tasks/[feature/id]/sub_prds/[snake_case_name].md`
  - Context: [Brief Description]
  - Depends On: [None | T-xxx]

- [ ] **T-102: [Title]**
  - Path: `docs/tasks/[feature/id]/sub_prds/[snake_case_name].md`
  - Context: [Description]
  - Depends On: T-101
```

## 5. Usage Example
**Input**: PRD for "Login".

**Output**: `docs/tasks/login-v1/manifest.md` with:
- T-001: Auth Repository (API + Local Storage).
- T-002: Login Bloc/Provider (State Management).
- T-003: Login Screen (UI).
