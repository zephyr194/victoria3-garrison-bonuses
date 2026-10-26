# Development contract

- Read README.md and DESIGN.md before changes.
- User changed scope on 2026-10-26: positive effects include lower turmoil penalties, fewer radicals and more loyalists; costs include infrastructure; research permanent facilities.
- Current experimental implementation is a **dedicated fixed local security workforce**, not field armies, barracks recruitment, or a fictional exact army-to-state mapping.
- No UI redesign is requested. Use existing in-game building and modifier surfaces.
- Namespace all custom engine keys with gs_. Never override vanilla files or use replace_path.
- balance.json is the single source for model and generated numeric script values. Run tools/generate.py then tools/validate.py.
- Do not invent engine keys. Record source provenance, exact document version and uncertainty in docs/SOURCES.md and evidence/bindings.json.
- Runtime targets are 1.13.x and 1.14.x. Available documentation snapshots are 1.13.11 and 1.14.5-openbeta, not proof of current 1.14 stable compatibility.
- Engine scripts are experimental until tested in the actual game. Static checks and model tests do not validate engine loading or performance.
- v0.3 uses separate security/civic qualification and resets old schema progress. Qualified-neutral loyalty targets are model-only until a verified runtime adapter exists. The negative radical gate stays off by default until bookkeeping is game-tested.
- Supply uses the verified building shortage boolean. Monthly observations are not proof of continuous uptime; do not claim either graded supply or perfect toggle prevention.
- Long-term political effects may persist after closure; current order modifiers expire or are replaced. Document this distinction.
- Keep design, implementation and validation docs updated in place; do not accumulate SPEC files.
- Use scripts/package.py only for explicitly experimental packages while compatibility is unverified. Never label them stable or tested.
