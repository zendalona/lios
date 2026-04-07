# LIOS Test Suite - By Zendalona

Automated unit and integration tests for the **Linux-Intelligent-OCR-Solution (LIOS)** backend.

---

## Quick Start

The best way to run the tests is to use a local Python virtual environment inside your cloned repository so it doesn't interfere with your system packages.

```bash
# 1. Clone the repository and switch to the test branch
git clone https://github.com/MrSpideyNihal/lios.git
cd lios
git checkout LIOS-test

# 2. Create and activate a local virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install testing dependencies
pip install pytest pytest-cov pytest-xvfb Pillow pyenchant PyGObject

# 4. Run all tests locally sandboxed
PYTHONPATH=. pytest Tests/
```

---

## How to Run

*Note: Ensure your virtual environment is active (`source venv/bin/activate`) before running.*

### All tests (with coverage)
```bash
PYTHONPATH=. pytest Tests/
```
Coverage report is printed in the terminal and saved as HTML to `Tests/coverage_html/index.html`.

### All tests (fast, no coverage)
```bash
PYTHONPATH=. pytest Tests/ --no-cov
```

### A single file
```bash
PYTHONPATH=. pytest Tests/test_ocr_engine_base.py -v
```

### A single test class or test
```bash
PYTHONPATH=. pytest Tests/test_ocr_engines.py::TestOcrEngineTesseract -v
PYTHONPATH=. pytest Tests/test_ocr_engines.py::TestOcrEngineTesseract::test_name_attribute -v
```

### Useful flags
| Flag | Effect |
|---|---|
| `-v` | Show each test name |
| `--tb=short` | Shorter tracebacks on failure |
| `-x` | Stop after first failure |
| `-k "tesseract"` | Filter tests by name |
| `-s` | Show `print()` / logging output |

---

## Test Files

### Backend / OCR Tests
| File | What It Tests |
|---|---|
| `test_macros.py` | Global constants, path resolution, `set_datadir`, mixed-case combos |
| `test_image_logics.py` | Rectangle overlap detection, box ordering, index finding |
| `test_ocr_engine_base.py` | `OcrEngineBase` abstract contract, all 3 language setters, edge cases |
| `test_ocr_engines.py` | All 6 concrete engines (Tesseract, Cuneiform, Gocr, Ocrad, ABBYY 9 & 11) — fully mocked |
| `test_tesseract_path_finder.py` | `FastTessdataFinder`: init, caching, env vars, glob matching, validation |
| `test_ocr_init.py` | `get_available_engines()` return type and filtering, all engine class imports |
| `test_text_to_audio.py` | `text_to_audio_converter` setters (volume/pitch/speed/voice) with mocked espeak |
| `test_mp_compat.py` | Multiprocessing compatibility: version detection, fork workaround, decorator |
| `test_dictionary.py` | Language name → code mapping correctness |
| `test_ocr_integration.py` | **Real** Tesseract OCR on actual PNG images *(auto-skipped if tesseract absent)* |
| `test_scanner_driver_base.py` | `DriverBase` abstract contract, `SCAN_AREA_*` constants |
| `test_scanner_sane_driver.py` | `DriverSane` with fully mocked `sane` module |
| `test_scanner_scanimage_driver.py` | `DriverScanimage` with mocked subprocess/os calls |

### GTK UI Tests (headless via `pytest-xvfb`)
| File | What It Tests |
|---|---|
| `test_gtk_text_view.py` | `TextView`: set/get text, insert positions, line ops, cursor, find/replace, highlights |
| `test_gtk_widgets.py` | `Entry`, `Label`, `Button`, `SpinButton`, `ComboBox`, `ListView`, `Statusbar`, etc. |
| `test_gtk_containers.py` | `Grid`, `ScrollBox`, `NoteBook`, `Frame`, `Paned`, `Box` |
| `test_gtk_window.py` | `Window` title/connections, `Dialog` content area + button IDs |

---

## Integration Tests (Real Tesseract)

`test_ocr_integration.py` runs real OCR — **no mocks**. It auto-skips if tesseract is not installed.

To install tesseract:
```bash
# Ubuntu / Debian
sudo apt install tesseract-ocr

# Arch
sudo pacman -S tesseract
```

---

## What These Tests Will Catch

- ✅ Breaking the `OcrEngineBase` language setter contract
- ✅ A new engine not implementing required methods
- ✅ Malformed tesseract shell commands (multi-lang `+` joining)
- ✅ Scanner device filtering broken (picks up webcams)
- ✅ Scan area calculations wrong (FULL/HALF/QUARTER)
- ✅ Import chain failures across the `lios.ocr` package
- ✅ Multiprocessing fork workaround wrongly applied

## What These Tests Won't Catch

- ❌ Real scanner hardware failures
- ❌ Performance regressions
- ❌ Complex multi-window GTK workflows (e.g. drag-and-drop between panels)

---

## Coverage

After running, open the HTML coverage report:
```bash
xdg-open Tests/coverage_html/index.html
```

Key module coverage:
- `lios/ocr/__init__.py` → **100%**
- `lios/ocr/ocr_engine_cuneiform.py` → **90%**
- `lios/ocr/ocr_engine_gocr.py` → **87%**
- `lios/ocr/ocr_engine_base.py` → **78%**
- `lios/scanner/sane_driver.py` → **65%**
- `lios/scanner/scanimage_driver.py` → **67%**
- `lios/ui/gtk/text_view.py` → **tested** (via pytest-xvfb)
- `lios/ui/gtk/widget.py` → **tested** (via pytest-xvfb)

---

## How to Add New Tests

When you add a new function or feature to LIOS, add a corresponding test to keep the suite up to date.

### Naming Convention
- File: `Tests/test_<module_name>.py`
- Class: `TestClassName` (matches the class you're testing)
- Method: `test_what_it_does`

### Template: Backend / Logic Test
```python
import pytest
from unittest.mock import patch, MagicMock

class TestMyNewFeature:
    def test_basic_behavior(self):
        from lios.my_module import my_function
        result = my_function("input")
        assert result == "expected_output"

    @patch("lios.my_module.os.system")
    def test_shell_command(self, mock_sys):
        from lios.my_module import run_tool
        run_tool("file.png")
        mock_sys.assert_called_once()
        cmd = mock_sys.call_args[0][0]
        assert "file.png" in cmd
```

### Template: GTK Widget Test
```python
import pytest

@pytest.fixture(scope="module")
def gtk_init():
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    Gtk.init([])

class TestMyWidget:
    def test_widget_property(self, gtk_init):
        from lios.ui.gtk.my_widget import MyWidget
        w = MyWidget()
        w.set_text("Hello")
        assert w.get_text() == "Hello"
```

> **Important:** Always import GTK modules *inside* the test function or fixture, never at the top of the file. This lets `pytest-xvfb` set up the virtual display first.

### Running Your New Test
```bash
# Run just your new file
PYTHONPATH=. pytest Tests/test_my_module.py -v

# Run the full suite to make sure nothing else broke
PYTHONPATH=. pytest Tests/ --no-cov
```
