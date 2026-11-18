#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "=================================================="
echo "  IVAR-MODS 6.8.0013 One-Click Termux Patcher"
echo "=================================================="

# 1. Setup storage & directory
cd /storage/emulated/0/Download

echo "[+] Step 1: Installing required tools (Java, Python, Zip)..."
pkg update -y
pkg install -y openjdk-17 zip unzip wget python apksigner

echo "[+] Step 2: Running patcher..."
python3 patch.py

echo "=================================================="
echo "  DONE! APK is now fully modded and ready to use! "
echo "=================================================="
