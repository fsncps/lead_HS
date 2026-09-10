# Run state machine

Source of truth: 20_DESIGN/MASTER/architecture.md (run state machine)
and 20_DESIGN/MASTER/interfaces.md (run semantics). Rendered with
--type state_machine.

## States

- planned: run row created, deterministic run_key assigned
- running: adapter probing this source
- done: findings + documents written (access blocks recorded as findings + notes)
- failed: unrecoverable network error (exit 2)
- blocked: source wholly inaccessible
- aborted: user interrupt; inserted findings persist

## Transitions

- planned → running on start
- running → done on all findings written
- running → failed on unrecoverable network error
- running → blocked on source wholly inaccessible
- running → aborted on interrupt (Ctrl-C)
- failed → planned on re-run as a NEW run (old findings stay)
- blocked → planned on re-run as a NEW run (manual fallback recorded)
- aborted → planned on re-run as a NEW run (old findings persist)

```
planned ──▶ running ──▶ done
              │  ▲
          error│  │ re-run (NEW run id; old findings stay)
              ▼  │
        failed/blocked/aborted
```
