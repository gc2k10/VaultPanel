# Offline checks

Run from the repository root in an isolated Python environment installed from `requirements-alpha.txt`:

```sh
python -m unittest discover -s tests -v
node --test tests/*.test.mjs
```

The mdraid suite uses synthetic text and mocked file reads, never a NAS connection. API tests independently vary BTRFS and RAID membership. JavaScript tests exercise both layouts, unavailable states, degradation, maintenance and conflicting arrays. Hardware writes stay disabled.

CI also runs distribution smoke checks, four Python/platform combinations including ARM64/Python 3.13.5, fixture-only application browser checks and the standalone demo browser matrix. See `docs/demo-validation.md` for demo coverage. None of these tests validate physical sensors, actual storage topology or recovery.
