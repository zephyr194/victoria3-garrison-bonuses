# Experimental install and game test · v0.3

No engine-verified release exists. Default runtime benefits are order relief and qualification records; negative radical effects are gated off and direct loyalty targeting remains unimplemented.

1. Python 3.11+: run `python3 tools/generate.py`, `python3 tools/validate.py`, and `python3 -m unittest discover -s tests -v`.
2. Run `python3 scripts/package.py --target 1.13 --experimental` or target 1.14. This declares an intended target, not compatibility.
3. Extract `gs_garrison/` and `gs_garrison.mod` together into your own `Documents/Paradox Interactive/Victoria 3/mod/`.
4. Use a separate test playset and a copied save/new game. Enable debug logs; check `error.log` before advancing.
5. Build a garrison. Verify 950 soldier + 50 officer jobs/level, actual government payroll, no field battalions, and 2 infrastructure reserved/level.
6. Test Standing Garrison, Civic Service and Mothballed Compound. Civic adds grain5/fabric2/paper2/services5 per fully staffed level beyond normal inputs. It does not yet directly add loyalists.
7. Inspect coverage, one order tier and state variables `gs_service_months`, `gs_civic_months`, `gs_interruption_months`. Test 20%/50% boundaries and monthly qualification decay/reset.
8. Test shortages, ownership/control changes, upgrading a v0.2 save, split states, police/decrees and reload. See VALIDATION.md.
9. For deliberate negative-effect development tests only, set `experimental_radical_effects_enabled=true` in a separate copy of balance.json, regenerate and validate, then use the copied test save. Record all three attitude pools before changing defaults. The shipped regression suite asserts default safety.
10. Do not substitute a broad state loyalist effect for the missing qualified-neutral adapter.

Fill VALIDATION.md per exact patch/build. Do not set game_verified merely to bypass the release gate. Some legacy v0.2 attitude changes may already be present in an old save and cannot be undone simply by this migration.
