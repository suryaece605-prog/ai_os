# AI OS

An AI-first operating system you can build and boot from your Windows laptop.

**What it is:** a bootable Linux (Debian 13 + XFCE desktop) that opens straight into an AI assistant. You type what you want ("find my biggest files", "open Firefox", "write a README in my Documents folder") and the assistant does it, asking your permission before it changes anything. It can use the **Claude API** or a **local model (Ollama)**, and you can switch between them.

**What it is not:** a kernel written from scratch. Real operating systems take big teams years; this builds on Debian, which is how most "custom OS" projects work. It runs **live from a USB stick or a virtual machine and never touches your Windows install**.

## Parts

| Path | What it does |
|---|---|
| `aios_core.py` | The brain: provider switching, tools, approval + safety rules |
| `aios_gui.py` | Desktop window (also starts automatically on the ISO) |
| `aios.py` | Terminal chat, `setup`, `status` |
| `windows/*.bat` | Double-click launchers to try it on Windows right now |
| `iso/` | Recipe that builds the bootable ISO |
| `.github/workflows/build-iso.yml` | Builds the ISO online, no Linux needed |
| `tests/` | `python -m unittest discover -s tests` |

## 1. Try it on Windows first (5 minutes)

1. Install Python 3 from python.org (tick **Add Python to PATH**).
2. Unzip this folder. Double-click `windows\setup-aios.bat`, pick `claude`, paste your API key.
3. Double-click `windows\run-aios-gui.bat`.

No API key? Install [Ollama](https://ollama.com), run `ollama pull llama3.2:3b`, then pick `ollama` in the window.

## 2. Build the bootable ISO

**Option A: online (easiest from Windows)**
1. Put this folder in a GitHub repository and push it.
2. Open the repo's **Actions** tab, choose **Build AI OS ISO**, click **Run workflow**.
3. When it finishes, download `aios-iso` from the run's **Artifacts** and unzip it to get the `.iso`.

**Option B: on your laptop with WSL2**
1. In PowerShell: `wsl --install -d Debian` (restart if asked).
2. Copy this folder into the Linux side (`cp -r /mnt/c/Users/YOU/Downloads/ai-os ~/ai-os`). Do not build under `/mnt/c`, it breaks permissions.
3. `cd ~/ai-os && sudo bash iso/build.sh`. It takes 20-40 minutes and downloads about 1.5 GB.
4. The ISO is at `iso/build/aios-amd64.hybrid.iso`. Copy it back to Windows.

## 3. Boot it

**Safest first: a virtual machine.** In VirtualBox create a Linux (Debian 64-bit) VM with 4 GB RAM, attach the ISO as the CD, start it. It logs in on its own and opens the assistant.

**Real laptop:** write the ISO to a USB stick with [Rufus](https://rufus.ie) (DD mode if asked) or [Ventoy](https://ventoy.net), then pick the USB in the boot menu (usually F12 / F2 / Esc at power-on). If it won't start, try turning Secure Boot off in the BIOS. Running live does not change your internal drive; nothing is written to it unless you run the installer (section 4).

Live-session facts: the login user is `user`, changes are lost on shutdown, and Wi-Fi is set up from the network icon in the tray. In the assistant window click **Claude key...** and paste your key (in live mode it's gone after shutdown; once installed it stays).

## 4. Install it on your old laptop

Check first: a **64-bit** CPU (Debian 13 has no 32-bit version), 4 GB RAM recommended (2 GB minimum), 20 GB free disk, and Wi-Fi or a LAN cable.

1. **Boot the USB in live mode first** and make sure the screen, keyboard, Wi-Fi and the assistant all work. Nothing is changed yet.
2. **Back up anything you want to keep** from that laptop. "Erase disk" wipes the whole drive.
3. In the live session open the menu and choose **Install AI OS to this laptop** (or run `aios-install` in a terminal). Follow the installer, pick **Erase disk** for a clean install on a spare machine, and create your own username and password.
4. When it finishes, reboot and remove the USB. AI OS opens after you log in, and from now on your files, settings and Claude key are kept after shutdown.

Keep Windows on that laptop? Choose "install alongside" in the installer instead. A clean erase is simpler on a spare machine.

## 5. Local model on the ISO

Open a terminal and run `aios-install-ollama`. A live session keeps everything in RAM, so use a small model and a laptop with 8 GB or more. If that's tight, use the Claude API instead; it needs almost no memory.

## Safety

- **Reading** folders/files happens automatically. **Writing files, running commands and opening apps** each pop up a Yes/No box showing exactly what will happen. Default answer is No.
- A built-in filter refuses obviously destructive commands (wiping the disk, `rm -rf /`, piping downloads into a shell, touching `.ssh` or the AI OS config). It is a **best-effort filter, not a sandbox**: read each approval prompt before you say yes.
- The file tools refuse to read your saved API key and the command filter blocks the obvious ways to get at it, but a command you approve could still reach it, so only approve what you understand. Text found inside files or command output is treated as data, not instructions.
- Your key is stored in `%APPDATA%\aios\config.json` on Windows (`~/.config/aios/config.json` on Linux). You can also use the `ANTHROPIC_API_KEY` environment variable instead.

## Status of this build

- Tested: the assistant core (18 automated tests against fake Claude and Ollama servers), the terminal program, script syntax.
- **Not tested:** the desktop window on a real screen, the ISO build and boot, and the installer (the riskiest part: bootloader setup on real hardware). They were written from the standard Debian live-build recipe but have not been run. If the first ISO build or boot fails, send me the end of `iso/build.log` (or a photo of the boot screen) and I'll fix it.

## Ideas for next steps

Voice input, more tools (web search, calendar), custom boot splash and branding, a persistence partition for people who stay on live USB.
