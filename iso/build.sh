#!/usr/bin/env bash
# Builds the AI OS live ISO (Debian 13 "trixie" + XFCE + the AI OS assistant).
# Run as root on Debian/Ubuntu, a Debian container, or WSL2 (inside the Linux
# filesystem, e.g. ~/ai-os, NOT under /mnt/c).
#
#   sudo bash iso/build.sh
#
# Result: iso/build/aios-amd64.hybrid.iso
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"

if [ "$(id -u)" -ne 0 ]; then
  echo "Please run as root:  sudo bash iso/build.sh" >&2
  exit 1
fi

apt-get update
apt-get install -y live-build debootstrap debian-archive-keyring

rm -rf "$HERE/build"
mkdir -p "$HERE/build"
cd "$HERE/build"

lb config \
  --distribution trixie \
  --architectures amd64 \
  --binary-images iso-hybrid \
  --debian-installer none \
  --archive-areas "main contrib non-free-firmware" \
  --bootappend-live "boot=live components quiet" \
  --iso-application "AI OS" \
  --iso-volume "AI_OS" \
  --image-name aios

# Our package list, login/autostart config and launcher scripts.
cp -a "$HERE/overlay/." config/

# The assistant itself.
mkdir -p config/includes.chroot/opt/aios
cp "$ROOT/aios_core.py" "$ROOT/aios.py" "$ROOT/aios_gui.py" config/includes.chroot/opt/aios/

chmod +x config/includes.chroot/usr/local/bin/* || true

lb build 2>&1 | tee "$HERE/build.log"

echo
ls -lh "$HERE"/build/*.iso
