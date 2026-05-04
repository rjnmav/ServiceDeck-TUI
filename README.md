# 🛠️ ServiceDeck TUI
**A professional-grade Terminal User Interface for seamless systemd service management.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Built with Textual](https://img.shields.io/badge/Built%20with-Textual-ff69b4.svg)](https://textual.textualize.io/)

ServiceDeck TUI provides a powerful, real-time interface for monitoring and controlling systemd units across both System and Session (User) D-Buses. Designed for power users and sysadmins, it simplifies complex service management into a clean, keyboard-driven experience.


## ✨ Key Features

- **Dual Bus Support**: Effortlessly toggle between `System` and `Session` (User) buses.
- **Real-time Monitoring**: Instant visibility into unit states (`Active`, `Sub State`, and `Enabled`).
- **Live Log Viewer**: Press `l` to tail `journalctl` logs for any service with an automatic 2-second refresh interval.
- **Comprehensive Control**: Start, Stop, Restart, Enable, Disable, Mask, and Unmask services with single keypresses.
- **Modern TUI**: Built on the robust **Textual** framework for a beautiful and responsive terminal experience.

## 🚀 Getting Started

### Prerequisites

ServiceDeck requires **Python 3.8+** and specific system libraries to interface with D-Bus and the Systemd Journal.

#### Debian/Ubuntu
```bash
sudo apt update
sudo apt install libgirepository1.0-dev libcairo2-dev pkg-config python3-dev libsystemd-dev
```

#### Fedora/RHEL
```bash
sudo dnf install gobject-introspection-devel cairo-devel pkgconf-pkg-config python3-devel systemd-devel
```

#### Arch Linux
```bash
sudo pacman -S gobject-introspection cairo pkgconf python systemd
```


### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rjnmav/ServiceDeck-TUI.git
   cd ServiceDeck-TUI
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Usage

### Running the Application
Launch the TUI by executing the main entry point:
```bash
python main.py
```

### Keyboard Shortcuts

| Key | Action |
|:---:|:---|
| `q` | **Quit** the application |
| `escape` | **Back** to service list from logs |
| `t` | **Toggle** between System and User bus |
| `f` | **Refresh** the service list manually |
| `l` | **View Logs** for selected unit |
| `s` | **Start** the selected unit |
| `x` | **Stop** the selected unit |
| `r` | **Restart** the selected unit |
| `e` | **Enable** the selected unit |
| `d` | **Disable** the selected unit |
| `m` | **Mask** the selected unit |
| `u` | **Unmask** the selected unit |


## 🏗️ Architecture

ServiceDeck is built using a clean **Model-View-Controller (MVC)** pattern:
- **Model**: Interfaces with `org.freedesktop.systemd1` over D-Bus and retrieves logs via `systemd.journal`.
- **View**: A reactive TUI layout powered by `Textual` with dedicated `DataTable` and `RichLog` components.
- **Controller**: Manages the state transition, event flow, and auto-refresh timers between the Model and View.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
