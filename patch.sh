#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "=================================================="
echo "  IVAR-MODS 6.8.0013 One-Click Termux Patcher"
echo "=================================================="

# 1. Setup storage & directory
cd /storage/emulated/0/Download

APK_FILE="IVAR MODS_6.8.0013.apk"
ZIP_FILE="IVAR-MODS_6.8.0013.apk-main.zip"

if [ ! -f "$APK_FILE" ]; then
    echo "[-] Error: $APK_FILE not found in /storage/emulated/0/Download!"
    exit 1
fi

if [ ! -f "$ZIP_FILE" ]; then
    echo "[-] Error: $ZIP_FILE not found in /storage/emulated/0/Download!"
    exit 1
fi

echo "[+] Step 1: Installing required tools (Java, Python, Zip)..."
pkg update -y
pkg install -y openjdk-17 zip unzip wget python apksigner

echo "[+] Step 2: Running patcher..."
python3 -c '
import os, sys, zipfile, shutil

work_dir = "/storage/emulated/0/Download"
apk_name = "IVAR MODS_6.8.0013.apk"
main_zip = "IVAR-MODS_6.8.0013.apk-main.zip"

temp_dir = os.path.join(work_dir, "ivar_temp")
os.makedirs(temp_dir, exist_ok=True)

smali_jar = os.path.join(temp_dir, "smali.jar")
if not os.path.exists(smali_jar):
    print("[*] Downloading smali assembler...")
    os.system(f"curl -L -o \"{smali_jar}\" \"https://bitbucket.org/JesusFreke/smali/downloads/smali-2.5.2.jar\" || wget -O \"{smali_jar}\" \"https://bitbucket.org/JesusFreke/smali/downloads/smali-2.5.2.jar\"")

print("[*] Extracting repository files...")
with zipfile.ZipFile(os.path.join(work_dir, main_zip), "r") as z:
    for n in z.namelist():
        if n.endswith("smali.zip"):
            z.extract(n, temp_dir)
            inner_zip = os.path.join(temp_dir, n)
            break

c88 = os.path.join(temp_dir, "smali_c88")
c89 = os.path.join(temp_dir, "smali_c89")
os.makedirs(c88, exist_ok=True)
os.makedirs(c89, exist_ok=True)

print("[*] Extracting classes88 and classes89 smali files...")
with zipfile.ZipFile(inner_zip, "r") as z:
    for item in z.infolist():
        if item.filename.endswith(".smali"):
            first = z.open(item).readline().decode("utf-8", errors="ignore").strip()
            if first == "# classes88.dex":
                z.extract(item, c88)
            elif first == "# classes89.dex":
                z.extract(item, c89)

print("[*] Compiling classes88.dex...")
os.system(f"java -jar \"{smali_jar}\" a \"{c88}\" -o \"{os.path.join(temp_dir, \"classes88.dex\")}\"")

print("[*] Compiling classes89.dex...")
os.system(f"java -jar \"{smali_jar}\" a \"{c89}\" -o \"{os.path.join(temp_dir, \"classes89.dex\")}\"")

print("[*] Updating APK with modified DEX files...")
cwd = os.getcwd()
os.chdir(temp_dir)
apk_path = os.path.join(work_dir, apk_name)
os.system(f"zip -u \"{apk_path}\" classes88.dex classes89.dex")
os.chdir(cwd)

print("[*] Cleaning up temporary files...")
shutil.rmtree(temp_dir, ignore_errors=True)

print("\n[+] SUCCESS! Both classes88.dex and classes89.dex were compiled and updated inside your APK!")
print(f"[+] Your modded APK: {apk_path}")
'

echo "=================================================="
echo "  DONE! APK is now fully modded and ready to use! "
echo "=================================================="
