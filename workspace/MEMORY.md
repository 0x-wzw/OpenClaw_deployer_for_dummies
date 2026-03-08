# Memory

Sessions are stored as JSONL files under `sessions/<session_id>.jsonl`.
Each line is one message object: `{"role": "user"|"assistant"|"tool", "content": "..."}`.

On startup the gateway loads the last N lines of the relevant session file to
restore context (N is controlled by the `CONTEXT_WINDOW_LINES` env var,
default 50).

Long-term facts that should survive session rotation can be appended here
manually or by the agent using the `memory_write` skill.
