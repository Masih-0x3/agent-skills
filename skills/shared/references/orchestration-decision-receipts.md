# Orchestration Decision Receipts

Use this receipt whenever a planning, audit, or implementation skill chooses parent-only, worker/subagent, or visible-thread execution.

```text
Orchestration decision:
- Mode: <parent-only | lightweight workers | full worker run | visible-thread handoff>
- Worker count:
- Decision reason:
- Independent surfaces:
- Workers used or skipped:
- Thread decision:
- Token/context rationale:
- Reconsider trigger:
```

## Worker/Subagent vs Visible Thread Policy

- Workers/subagents are for parallel evidence, implementation support, audit coverage, or validation inside one parent-owned task.
- User-visible Codex threads are for explicit user-owned lanes, long-lived handoffs, separate worktrees, or follow-ups the user will manage directly.
- Do not create visible threads as hidden scratch space or as a generic context-limit workaround.
- More context is useful only when the subtask has an independent contract and the parent can synthesize the result.
- Parent accountability remains: verify, deduplicate, and integrate worker/thread output before relying on it.

## Closeout Receipt

```text
Orchestration closeout:
- Workers actually used:
- Worker scopes:
- Worker results accepted/rejected/unverified:
- Parent verification:
- Gaps that would benefit from more workers:
- Visible thread considered:
```

