# xmind_compress

A command-line utility that shrinks the embedded screenshots inside [XMind](https://www.xmind.net/) files. XMind files are ZIP archives; this tool extracts the images from the `resources/` directory, resizes and recompresses them, and repackages the file — often cutting file size by 50–80% with no visible quality loss.

## Features

- Resizes images that exceed a configurable maximum dimension (default: 1440 px)
- Recompresses JPEG images at a configurable quality level (default: 80)
- Optimizes PNG images losslessly
- Processes a single file, multiple files, or wildcard patterns (e.g. `*.xmind`)
- Writes a new `-compressed` copy by default; also supports `--in-place` and `--output` modes
- Shows per-image and per-file size reduction statistics with `--verbose`

## Requirements

| Requirement | Version |
|-------------|---------|
| Python      | 3.8+    |
| Pillow      | 9.0+    |

No other dependencies are needed.

---

## Installation

### macOS

#### Option A — run the install script

Save and run `install_mac.sh` (see [Scripts](#scripts) below):

```bash
chmod +x install_mac.sh
./install_mac.sh
```

This installs Homebrew Python (if needed), Pillow, and copies the script to `/usr/local/bin`.

#### Option B — manual steps

1. **Install Python 3** via [Homebrew](https://brew.sh/):
   ```bash
   brew install python
   ```
   Or download the macOS installer from [python.org](https://www.python.org/downloads/).

2. **Install Pillow:**
   ```bash
   pip3 install Pillow
   ```

3. **Install the script** (optional — makes it runnable from anywhere):
   ```bash
   chmod +x xmind_compress.py
   sudo cp xmind_compress.py /usr/local/bin/xmind_compress
   ```

4. **Run:**
   ```bash
   xmind_compress notes.xmind
   # or, without installing to PATH:
   python3 xmind_compress.py notes.xmind
   ```

> **Apple Silicon note:** Homebrew installs Python to `/opt/homebrew/bin/python3`. The script shebang already points there. If you installed Python differently, edit line 1 of the script or invoke it explicitly with `python3 xmind_compress.py`.

---

### Windows

#### Option A — run the install script

Save `install_windows.ps1` (see [Scripts](#scripts) below) and run it in PowerShell (run as Administrator):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\install_windows.ps1
```

This installs Python 3 via `winget` (if needed), installs Pillow, and copies the script to `C:\Tools\` (added to your PATH).

#### Option B — manual steps

1. **Install Python 3** from [python.org](https://www.python.org/downloads/).
   During setup, check **"Add Python to PATH"**.

2. **Install Pillow** in a Command Prompt or PowerShell window:
   ```powershell
   pip install Pillow
   ```

3. **Run the script:**
   ```powershell
   python xmind_compress.py notes.xmind
   ```

   To run it from any directory without typing `python`, copy `xmind_compress.py` to a folder on your `PATH` (e.g. `C:\Tools\`) and create a wrapper `xmind_compress.bat` alongside it:
   ```batch
   @echo off
   python "%~dp0xmind_compress.py" %*
   ```

---

### Linux

#### Option A — run the install script

Save and run `install_linux.sh` (see [Scripts](#scripts) below):

```bash
chmod +x install_linux.sh
./install_linux.sh
```

This installs Python 3 and Pillow via your distro's package manager, then copies the script to `/usr/local/bin`.

#### Option B — manual steps

**Debian / Ubuntu:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip
pip3 install Pillow
```

**Fedora / RHEL / CentOS:**
```bash
sudo dnf install -y python3 python3-pip
pip3 install Pillow
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip
pip install Pillow
```

After installing dependencies:
```bash
chmod +x xmind_compress.py
sudo cp xmind_compress.py /usr/local/bin/xmind_compress
```

---

## Scripts

### `install_mac.sh` / `install_linux.sh`

```bash
#!/usr/bin/env bash
# install_mac.sh  — macOS installer
# install_linux.sh — Linux installer (edit PACKAGE_MANAGER as needed)
set -euo pipefail

SCRIPT_SRC="xmind_compress.py"
INSTALL_DIR="/usr/local/bin"
INSTALL_NAME="xmind_compress"

# ── macOS: ensure Python via Homebrew ──────────────────────────────────────
if [[ "$(uname)" == "Darwin" ]]; then
    if ! command -v brew &>/dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    if ! command -v python3 &>/dev/null; then
        echo "Installing Python via Homebrew..."
        brew install python
    fi
fi

# ── Linux: ensure Python ───────────────────────────────────────────────────
if [[ "$(uname)" == "Linux" ]]; then
    if ! command -v python3 &>/dev/null; then
        if command -v apt &>/dev/null; then
            sudo apt update && sudo apt install -y python3 python3-pip
        elif command -v dnf &>/dev/null; then
            sudo dnf install -y python3 python3-pip
        elif command -v pacman &>/dev/null; then
            sudo pacman -S --noconfirm python python-pip
        else
            echo "ERROR: Cannot detect package manager. Install Python 3 manually." >&2
            exit 1
        fi
    fi
fi

# ── Install Pillow ─────────────────────────────────────────────────────────
echo "Installing Pillow..."
python3 -m pip install --upgrade Pillow

# ── Copy script to PATH ────────────────────────────────────────────────────
echo "Installing $SCRIPT_SRC to $INSTALL_DIR/$INSTALL_NAME..."
chmod +x "$SCRIPT_SRC"
sudo cp "$SCRIPT_SRC" "$INSTALL_DIR/$INSTALL_NAME"

echo ""
echo "Done. Run:  xmind_compress --help"
```

### `install_windows.ps1`

```powershell
# install_windows.ps1 — Windows installer (run as Administrator in PowerShell)

$ErrorActionPreference = "Stop"
$InstallDir = "C:\Tools"
$ScriptSrc  = "xmind_compress.py"

# ── Ensure Python ──────────────────────────────────────────────────────────
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Python via winget..."
    winget install --id Python.Python.3 --source winget --accept-package-agreements --accept-source-agreements
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path","User")
}

# ── Install Pillow ─────────────────────────────────────────────────────────
Write-Host "Installing Pillow..."
python -m pip install --upgrade Pillow

# ── Copy script and create wrapper ────────────────────────────────────────
if (-not (Test-Path $InstallDir)) { New-Item -ItemType Directory -Path $InstallDir | Out-Null }
Copy-Item $ScriptSrc "$InstallDir\xmind_compress.py" -Force

$wrapper = "@echo off`r`npython `"%~dp0xmind_compress.py`" %*`r`n"
Set-Content "$InstallDir\xmind_compress.bat" $wrapper -Encoding ASCII

# ── Add C:\Tools to PATH if not already there ─────────────────────────────
$machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
if ($machinePath -notlike "*$InstallDir*") {
    [System.Environment]::SetEnvironmentVariable("Path", "$machinePath;$InstallDir", "Machine")
    Write-Host "Added $InstallDir to system PATH. Restart your terminal to apply."
}

Write-Host ""
Write-Host "Done. Run:  xmind_compress --help"
```

---

## Usage

```
usage: xmind_compress [-h] [--output FILE] [--in-place] [--suffix SUFFIX]
                      [--quality 1-95] [--max-dim PIXELS] [--verbose]
                      FILE [FILE ...]
```

### Examples

```bash
# Compress one file → creates notes-compressed.xmind
xmind_compress notes.xmind

# Compress all .xmind files in the current directory
xmind_compress *.xmind

# Overwrite the original file
xmind_compress notes.xmind --in-place

# Write to a specific output file
xmind_compress notes.xmind --output notes-small.xmind

# Higher quality, larger maximum image dimension
xmind_compress notes.xmind --quality 90 --max-dim 2560

# Show per-image statistics
xmind_compress notes.xmind --verbose
```

### Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--output FILE` | `-o` | — | Output path (single-file mode only) |
| `--in-place` | `-i` | off | Overwrite the source file |
| `--suffix SUFFIX` | `-s` | `-compressed` | Suffix inserted before `.xmind` extension |
| `--quality 1-95` | `-q` | `80` | JPEG compression quality |
| `--max-dim PIXELS` | `-d` | `1440` | Max width or height; larger images are scaled down |
| `--verbose` | `-v` | off | Print size reduction for every image |

---

## How it works

XMind files are standard ZIP archives. `xmind_compress`:

1. Extracts the archive to a temporary directory.
2. Finds all JPEG and PNG files under `resources/`.
3. Resizes any image whose width or height exceeds `--max-dim` (aspect ratio preserved, Lanczos filter).
4. Re-saves JPEGs with the specified `--quality` and `optimize=True`; PNGs are saved with `optimize=True` (lossless).
5. Repackages the directory back into a ZIP with `ZIP_DEFLATED` compression.
6. Atomically replaces the output file.

The map structure, links, and all non-image content are untouched.

---

## License

MIT
