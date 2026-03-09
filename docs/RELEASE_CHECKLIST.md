# Release Checklist

Run this before zipping or publishing the repository.

## 1. Clean disposable caches

Dry run:

```bash
python scripts/release_clean.py --dry-run
```

Apply cleanup:

```bash
python scripts/release_clean.py
```

This removes:

- `__pycache__/`
- `.pytest_cache/`
- `.mypy_cache/`
- `.ruff_cache/`
- bytecode files such as `.pyc`

It preserves scientific artifacts, reports, and bundled task assets by default.

## 2. Run safety scans

Development scan:

```bash
python scripts/check_public_safety.py --mode dev
```

Release scan:

```bash
python scripts/check_public_safety.py --mode release
```

Release mode scans `artifacts/` in addition to docs, configs, manifests, logs, and result files.

## 3. Run lightweight regression checks

```bash
pytest -q
```

## 4. Confirm release framing

- Layer A remains the main exact mechanism-validation layer.
- Layer B remains a bundled mechanistic probe layer.
- Negative and mixed findings remain visible.
- Any local structured-output confounds are still documented.
