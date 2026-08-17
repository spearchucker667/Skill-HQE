# Python Diagnostic Guide

## 1. Project Orientation & Manifests
- **Project Configuration**: `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements.txt`, `Pipfile`, `environment.yml`.
- **Environment Tooling**: `uv`, `poetry`, `pipenv`, `hatch`, `flit`.

## 2. Common Defect Patterns
1. **Mutable Default Arguments**: `def append_item(item, target=[])` accumulating state across function invocations.
2. **Exception Handling Anti-Patterns**: Bare `except:` or `except Exception: pass` swallowing critical syntax errors, keyboard interrupts, or DB errors.
3. **GIL / Concurrency Pitfalls**: Using `threading` for CPU-bound tasks or unsynchronized shared state access.
4. **AsyncIO Anti-Patterns**: Blocking synchronous calls (`time.sleep()`, synchronous file I/O, `requests.get()`) executed inside async event loops.
5. **Path Traversal & Unsafe Deserialization**: Insecure use of `pickle.loads()`, `yaml.load()` without SafeLoader, or unsanitized `os.path.join()`.
6. **Resource Cleanup**: Missing context managers (`with open(...) as f:`) causing file descriptor exhaustion.

## 3. Verification & Validation Commands
```bash
# Type Checking
mypy .
pyright .

# Linting & Formatting
ruff check .
flake8 .

# Tests
pytest -v
python3 -m unittest discover
```
