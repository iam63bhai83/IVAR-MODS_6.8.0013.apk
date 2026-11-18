import os
import sys
import glob
import zipfile
import shutil

work_dir = "/storage/emulated/0/Download"
if not os.path.exists(work_dir):
    work_dir = os.getcwd()

print("[*] Working Directory:", work_dir)

# 1. Find APK
apks = glob.glob(os.path.join(work_dir, "*IVAR*.apk"))
if not apks:
    apks = glob.glob(os.path.join(work_dir, "*.apk"))
if not apks:
    print("[-] Error: No APK file found in " + work_dir)
    sys.exit(1)
apk_path = apks[0]
print("[+] Found APK:", os.path.basename(apk_path))

# 2. Find ZIP
zips = glob.glob(os.path.join(work_dir, "*IVAR*.zip"))
if not zips:
    zips = glob.glob(os.path.join(work_dir, "*main*.zip"))
if not zips:
    print("[-] Error: No ZIP file found in " + work_dir)
    sys.exit(1)
zip_path = zips[0]
print("[+] Found ZIP:", os.path.basename(zip_path))

temp_dir = os.path.join(work_dir, "ivar_temp")
os.makedirs(temp_dir, exist_ok=True)

# 3. Download smali.jar
smali_jar = os.path.join(temp_dir, "smali.jar")
if not os.path.exists(smali_jar) or os.path.getsize(smali_jar) < 1000000:
    print("[*] Downloading smali compiler...")
    url1 = "https://bitbucket.org/JesusFreke/smali/downloads/smali-2.5.2.jar"
    url2 = "https://github.com/google/smali/releases/download/v2.5.2/smali-2.5.2.jar"
    os.system('curl -L -o "' + smali_jar + '" "' + url1 + '" || wget -O "' + smali_jar + '" "' + url1 + '" || curl -L -o "' + smali_jar + '" "' + url2 + '"')

# 4. Extract repository zip
print("[*] Extracting repository files...")
inner_zip = None
with zipfile.ZipFile(zip_path, "r") as z:
    for n in z.namelist():
        if n.endswith("smali.zip"):
            z.extract(n, temp_dir)
            inner_zip = os.path.join(temp_dir, n)
            break

if not inner_zip or not os.path.exists(inner_zip):
    inner_zip = zip_path

# 5. Extract classes88 and classes89
c88_dir = os.path.join(temp_dir, "smali_c88")
c89_dir = os.path.join(temp_dir, "smali_c89")
os.makedirs(c88_dir, exist_ok=True)
os.makedirs(c89_dir, exist_ok=True)

print("[*] Sorting smali files for classes88 and classes89...")
count88 = 0
count89 = 0
with zipfile.ZipFile(inner_zip, "r") as z:
    for item in z.infolist():
        if item.filename.endswith(".smali"):
            first = z.open(item).readline().decode("utf-8", errors="ignore").strip()
            if first == "# classes88.dex":
                z.extract(item, c88_dir)
                count88 += 1
            elif first == "# classes89.dex":
                z.extract(item, c89_dir)
                count89 += 1

print("[+] Extracted " + str(count88) + " files for classes88, " + str(count89) + " files for classes89")

# 5.5 Auto-fix register constraints on 30s dispatchers
print("[*] Applying register safety fixes...")
for n in ["94", "95", "96", "97"]:
    p1 = os.path.join(c89_dir, "com/ivar/mods/ai/DashboardActivity$" + n + "$4$1.smali")
    if os.path.exists(p1):
        with open(p1, "r") as f:
            c = f.read()
        c = c.replace("invoke-virtual {p1, v11}", "move-object/from16 v12, p1\n    invoke-virtual {v12, v11}")
        with open(p1, "w") as f:
            f.write(c)

    p2 = os.path.join(c89_dir, "com/ivar/mods/ai/DashboardActivity$" + n + "$4$2.smali")
    if os.path.exists(p2):
        with open(p2, "r") as f:
            c = f.read()
        c = c.replace("invoke-virtual {p1, v9}", "move-object/from16 v10, p1\n    invoke-virtual {v10, v9}")
        with open(p2, "w") as f:
            f.write(c)

# 6. Compile DEX files
dex88 = os.path.join(temp_dir, "classes88.dex")
dex89 = os.path.join(temp_dir, "classes89.dex")

print("[*] Compiling classes88.dex...")
os.system('java -jar "' + smali_jar + '" a "' + c88_dir + '" -o "' + dex88 + '"')

print("[*] Compiling classes89.dex...")
os.system('java -jar "' + smali_jar + '" a "' + c89_dir + '" -o "' + dex89 + '"')

if not os.path.exists(dex88) or not os.path.exists(dex89):
    print("[-] Error: DEX compilation failed!")
    sys.exit(1)

# 7. Update APK
print("[*] Injecting DEX into APK...")
cwd = os.getcwd()
os.chdir(temp_dir)
os.system('zip -u "' + apk_path + '" classes88.dex classes89.dex')
os.chdir(cwd)

# 8. Clean up
shutil.rmtree(temp_dir, ignore_errors=True)

print("\n==================================================")
print("[+] SUCCESS! Both classes88.dex and classes89.dex updated in APK!")
print("[+] Modded APK is ready: " + apk_path)
print("==================================================")
