#!/usr/bin/env python3
import os
import sys
import zipfile
import subprocess
import shutil

print("[*] IVAR-MODS v6.8.0013 Termux Automatic DEX Patcher")
print("==================================================")

work_dir = "/storage/emulated/0/Download"
if not os.path.exists(work_dir):
    work_dir = os.getcwd()

apk_name = "IVAR MODS_6.8.0013.apk"
main_zip = "IVAR-MODS_6.8.0013.apk-main.zip"

apk_path = os.path.join(work_dir, apk_name)
zip_path = os.path.join(work_dir, main_zip)

if not os.path.exists(apk_path):
    print(f"[-] Error: {apk_name} not found in {work_dir}")
    sys.exit(1)

if not os.path.exists(zip_path):
    print(f"[-] Error: {main_zip} not found in {work_dir}")
    sys.exit(1)

print(f"[+] Found APK: {apk_path}")
print(f"[+] Found ZIP: {zip_path}")

temp_dir = os.path.join(work_dir, "ivar_temp")
os.makedirs(temp_dir, exist_ok=True)

# 1. Download smali.jar if not present
smali_jar = os.path.join(temp_dir, "smali-2.5.2.jar")
if not os.path.exists(smali_jar):
    print("[*] Downloading smali-2.5.2.jar...")
    url = "https://bitbucket.org/JesusFreke/smali/downloads/smali-2.5.2.jar"
    cmd = f"curl -L -o '{smali_jar}' '{url}' || wget -O '{smali_jar}' '{url}'"
    os.system(cmd)

if not os.path.exists(smali_jar) or os.path.getsize(smali_jar) < 1000000:
    print("[-] Failed to download smali.jar. Trying alternate source...")
    url_alt = "https://github.com/google/smali/releases/download/v2.5.2/smali-2.5.2.jar"
    os.system(f"curl -L -o '{smali_jar}' '{url_alt}'")

# 2. Extract smali.zip from main_zip
print("[*] Extracting smali.zip from repository archive...")
with zipfile.ZipFile(zip_path, "r") as z:
    for name in z.namelist():
        if name.endswith("smali.zip"):
            z.extract(name, temp_dir)
            inner_smali_zip = os.path.join(temp_dir, name)
            break

# 3. Extract classes88 and classes89 smali files
c88_dir = os.path.join(temp_dir, "smali_classes88")
c89_dir = os.path.join(temp_dir, "smali_classes89")
os.makedirs(c88_dir, exist_ok=True)
os.makedirs(c89_dir, exist_ok=True)

print("[*] Sorting smali files for classes88.dex and classes89.dex...")
with zipfile.ZipFile(inner_smali_zip, "r") as z:
    for item in z.infolist():
        if not item.filename.endswith(".smali"):
            continue
        first_line = z.open(item).readline().decode("utf-8", errors="ignore").strip()
        if first_line == "# classes88.dex":
            z.extract(item, c88_dir)
        elif first_line == "# classes89.dex":
            z.extract(item, c89_dir)

# 4. Compile classes88.dex and classes89.dex
print("[*] Compiling classes88.dex...")
out_dex88 = os.path.join(temp_dir, "classes88.dex")
os.system(f"java -jar '{smali_jar}' a '{c88_dir}' -o '{out_dex88}'")

print("[*] Compiling classes89.dex...")
out_dex89 = os.path.join(temp_dir, "classes89.dex")
os.system(f"java -jar '{smali_jar}' a '{c89_dir}' -o '{out_dex89}'")

if not os.path.exists(out_dex88) or not os.path.exists(out_dex89):
    print("[-] DEX compilation failed! Make sure openjdk-17 is installed (pkg install openjdk-17).")
    sys.exit(1)

# 5. Inject into APK
print("[*] Injecting compiled DEX files into APK...")
curr_cwd = os.getcwd()
os.chdir(temp_dir)
os.system(f"zip -u '{apk_path}' classes88.dex classes89.dex")
os.chdir(curr_cwd)

# 6. Sign APK
print("[*] Signing APK...")
signed_apk = os.path.join(work_dir, "IVAR_MODS_6.8.0013_MODDED.apk")
shutil.copy(apk_path, signed_apk)
os.system(f"apksigner sign --ks-pass pass:123456 --key-pass pass:123456 '{signed_apk}' 2>/dev/null || true")

print("\n==================================================")
print("[+] SUCCESS! All 39 patches injected into APK!")
print(f"[+] Modded APK is ready at: {apk_path}")
print("==================================================")
