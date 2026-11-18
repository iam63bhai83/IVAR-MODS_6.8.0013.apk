import os
import sys
import glob
import zipfile
import shutil

# Search locations for files
search_dirs = [
    "/storage/emulated/0/Download",
    os.getcwd(),
    os.path.abspath(os.path.join(os.getcwd(), ".."))
]

work_dir = "/storage/emulated/0/Download"
if not os.path.exists(work_dir):
    work_dir = os.getcwd()

print("[*] Primary Directory:", work_dir)

# 1. Find APK (specifically checking for 'IVAR MODS_6.8.0013.apk')
apk_path = None
for d in search_dirs:
    exact = os.path.join(d, "IVAR MODS_6.8.0013.apk")
    if os.path.isfile(exact):
        apk_path = exact
        break

if not apk_path:
    for d in search_dirs:
        if os.path.exists(d):
            apks = [f for f in glob.glob(os.path.join(d, "*IVAR*.apk")) if os.path.isfile(f)]
            if apks:
                apk_path = apks[0]
                break
            apks = [f for f in glob.glob(os.path.join(d, "*.apk")) if os.path.isfile(f)]
            if apks:
                apk_path = apks[0]
                break

if not apk_path:
    print("[-] Error: 'IVAR MODS_6.8.0013.apk' not found in:")
    for d in search_dirs:
        print("    - " + d)
    sys.exit(1)

print("[+] Target APK:", apk_path)

# 2. Find ZIP (checking for 'IVAR-MODS_6.8.0013.apk-main.zip' or 'smali.zip')
zip_path = None
inner_zip = None

# Check for direct smali.zip first
for d in search_dirs:
    smali_f = os.path.join(d, "smali.zip")
    if os.path.isfile(smali_f):
        inner_zip = smali_f
        zip_path = smali_f
        print("[+] Found smali.zip directly at:", smali_f)
        break

if not inner_zip:
    for d in search_dirs:
        exact = os.path.join(d, "IVAR-MODS_6.8.0013.apk-main.zip")
        if os.path.isfile(exact):
            zip_path = exact
            break

if not zip_path:
    for d in search_dirs:
        if os.path.exists(d):
            zips = [f for f in glob.glob(os.path.join(d, "*IVAR*.zip")) if os.path.isfile(f)]
            if zips:
                zip_path = zips[0]
                break
            zips = [f for f in glob.glob(os.path.join(d, "*main*.zip")) if os.path.isfile(f)]
            if zips:
                zip_path = zips[0]
                break
            zips = [f for f in glob.glob(os.path.join(d, "*.zip")) if os.path.isfile(f) and not f.endswith("smali.zip")]
            if zips:
                zip_path = zips[0]
                break

if not zip_path:
    print("[-] Error: 'IVAR-MODS_6.8.0013.apk-main.zip' not found in:")
    for d in search_dirs:
        print("    - " + d)
    sys.exit(1)

print("[+] Source ZIP:", zip_path)

temp_dir = os.path.join(os.path.dirname(apk_path), "ivar_temp")
os.makedirs(temp_dir, exist_ok=True)

# 3. Extract smali.zip from main zip if needed
if not inner_zip:
    print("[*] Extracting repository files from " + os.path.basename(zip_path) + "...")
    with zipfile.ZipFile(zip_path, "r") as z:
        for n in z.namelist():
            if n.endswith("smali.zip"):
                z.extract(n, temp_dir)
                inner_zip = os.path.join(temp_dir, n)
                break
    if not inner_zip or not os.path.exists(inner_zip):
        inner_zip = zip_path

# 4. Download smali.jar compiler if needed
smali_jar = os.path.join(temp_dir, "smali.jar")
if not os.path.exists(smali_jar) or os.path.getsize(smali_jar) < 1000000:
    print("[*] Downloading smali compiler...")
    url1 = "https://bitbucket.org/JesusFreke/smali/downloads/smali-2.5.2.jar"
    url2 = "https://github.com/google/smali/releases/download/v2.5.2/smali-2.5.2.jar"
    os.system('curl -L -o "' + smali_jar + '" "' + url1 + '" || wget -O "' + smali_jar + '" "' + url1 + '" || curl -L -o "' + smali_jar + '" "' + url2 + '"')

# 5. Extract classes88 and classes89
c88_dir = os.path.join(temp_dir, "smali_c88")
c89_dir = os.path.join(temp_dir, "smali_c89")
os.makedirs(c88_dir, exist_ok=True)
os.makedirs(c89_dir, exist_ok=True)

print("[*] Sorting smali files for classes88.dex and classes89.dex...")
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

# 6. Auto-fix register constraints on 30s dispatchers
print("[*] Verifying register safety constraints...")
for n in ["94", "95", "96", "97"]:
    p1 = os.path.join(c89_dir, "com/ivar/mods/ai/DashboardActivity$" + n + "$4$1.smali")
    if os.path.exists(p1):
        with open(p1, "r") as f:
            c = f.read()
        if "move-object/from16" not in c:
            c = c.replace("invoke-virtual {p1, v11}", "move-object/from16 v12, p1\n    invoke-virtual {v12, v11}")
            with open(p1, "w") as f:
                f.write(c)

    p2 = os.path.join(c89_dir, "com/ivar/mods/ai/DashboardActivity$" + n + "$4$2.smali")
    if os.path.exists(p2):
        with open(p2, "r") as f:
            c = f.read()
        if "move-object/from16" not in c:
            c = c.replace("invoke-virtual {p1, v9}", "move-object/from16 v10, p1\n    invoke-virtual {v10, v9}")
            with open(p2, "w") as f:
                f.write(c)

# 7. Compile DEX files
dex88 = os.path.join(temp_dir, "classes88.dex")
dex89 = os.path.join(temp_dir, "classes89.dex")

print("[*] Compiling classes88.dex...")
os.system('java -jar "' + smali_jar + '" a "' + c88_dir + '" -o "' + dex88 + '"')

print("[*] Compiling classes89.dex...")
os.system('java -jar "' + smali_jar + '" a "' + c89_dir + '" -o "' + dex89 + '"')

if not os.path.exists(dex88) or not os.path.exists(dex89):
    print("[-] Error: DEX compilation failed! Make sure openjdk-17 is installed (pkg install openjdk-17).")
    sys.exit(1)

# 8. Update APK
print("[*] Injecting modified DEX files into " + os.path.basename(apk_path) + "...")
cwd = os.getcwd()
os.chdir(temp_dir)
os.system('zip -u "' + apk_path + '" classes88.dex classes89.dex')
os.chdir(cwd)

# 9. Clean up
shutil.rmtree(temp_dir, ignore_errors=True)

print("\n==================================================")
print("[+] SUCCESS! Both classes88.dex and classes89.dex updated in APK!")
print("[+] Crash prevention: All anti-tamper & exit checks eliminated!")
print("[+] Direct Launch: Bypasses login & Google sign-in directly to Dashboard!")
print("[+] Modded APK is ready: " + apk_path)
print("==================================================")
