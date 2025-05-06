# Ninoxator

##  Features

- Runs various internal flows using a keyboard-based GUI.

##  Setup

### 1. Clone & Create Virtual Environment

```bash
git clone https://github.com/spearuav/ninoxator
cd ninoxator
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```
### DroneKit Fix (Ubuntu/Linux only)
If you're using Ubuntu/Linux, you may need to patch dronekit due to compatibility with Python 3.10+:

1. Locate the package:
```bash
pip show dronekit
```
- Look for Location: and go to .../site-packages/dronekit/.
- Edit __init__.py in that folder and add the following lines at the very top:
```python
import collections.abc
collections.MutableMapping = collections.abc.MutableMapping
```

## Running

```bash
python gui/ninoxator_console_gui.py
```

## Building Executable

### Requirements

- Python 3.9
- [PyInstaller](https://pyinstaller.org/)

Install PyInstaller in your virtualenv:

```bash
pip install pyinstaller
```

### Build Using Spec File

```bash
pyinstaller ninoxator_console_gui.spec
```

Result will be placed under `dist/ninoxator_console_gui(.exe)`.

---

##  Vendorized Dependencies

We use a **vendored version** of `consolemenu` placed under `vendor/consolemenu` to avoid packaging/import issues.

**Do not install `consolemenu` via pip**.

To update:
1. Copy the full `consolemenu` package from `site-packages` into `vendor/`.
2. Ensure all expected files are present (e.g., `menu_item.py`).
3. Avoid modifying your imports – keep using:

```python
from consolemenu import ConsoleMenu, MenuFormatBuilder
```

## To create a packagem use:
https://github.com/spearuav/spear-version-packer

## When running the local version:
- Copy ninoxator_console_gui.exe to the local PC.
- Create the folder app/configurations and place the config.ini file inside it.
- In config.ini, make sure the packed_versions_dir key points to the directory containing the .tar.gz software package.
- Place the software package (.tar.gz) in that directory.

## 📝 License

Internal use only – property of SpearUAV.