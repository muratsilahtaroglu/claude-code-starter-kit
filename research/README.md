# research/ — external research evidence trail (opt-in, rules.md §8)

Filled **only when the user opts in** (offered at bootstrap §0d, or via the `/keel-research` skill). One
subfolder per source platform; each holds a distilled `findings.md` and (optionally) raw downloads.

```
research/
├── github/          # repos, code patterns
│   ├── findings.md      # distilled, cited notes (committed)
│   ├── downloads/       # raw clones/files (git-ignored — large/copyrighted)
│   └── local/           # notes kept on THIS machine only (git-ignored)
├── articles/        # blog posts, papers/preprints
├── linkedin/        # posts, expert opinions
├── huggingface/     # models, datasets, model cards
└── web/             # everything else
```

Rules:
- **Cite everything.** Each claim in a `findings.md` carries its **source URL** + a confidence note;
  flag low-signal or paywalled sources.
- **Verify, don't trust** (rules.md §4) — sub-agent/web output is sanity-checked before it drives a decision.
- **Raw downloads are git-ignored** (`research/**/downloads/`); only `findings.md` + this README are committed.
- **`research/<platform>/local/` is git-ignored too** — working notes the owner keeps on one machine
  and has not (yet) promoted into the tracked `findings.md`. Use it when a research pass should inform
  the work without entering the shared evidence trail; promote the parts that end up justifying a
  decision, since an ADR may only cite something the repo actually carries.
- `research/` is evidence, **not** the final architecture — conclusions that drive a decision go into an
  ADR (`docs/adr/`) or `docs/`.
- Platforms above are examples — add/remove subfolders per project (prune at bootstrap if unused).
