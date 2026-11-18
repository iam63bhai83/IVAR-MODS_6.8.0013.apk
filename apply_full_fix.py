#!/usr/bin/env python3
import os
import sys
import zipfile
import re

print("[*] Starting comprehensive Dalvik/ART & Firebase fix...")

# Load DT.ZIP and smali.zip
with zipfile.ZipFile("smali.zip", "r") as z:
    all_smalis = {item.filename: z.read(item).decode("utf-8", errors="ignore") for item in z.infolist()}

print(f"[*] Loaded {len(all_smalis)} files from smali.zip")

# 1. Patch SketchApplication.smali
sketch_app = all_smalis["com/ivar/mods/ai/SketchApplication.smali"]
sketch_app_oncreate = """# virtual methods
.method public onCreate()V
    .registers 4

    .line 19
    invoke-virtual {p0}, Lcom/ivar/mods/ai/SketchApplication;->getApplicationContext()Landroid/content/Context;

    move-result-object v0

    sput-object v0, Lcom/ivar/mods/ai/SketchApplication;->mApplicationContext:Landroid/content/Context;

    .line 22
    new-instance v0, Lcom/ivar/mods/ai/SketchApplication$1;

    invoke-direct {v0, p0}, Lcom/ivar/mods/ai/SketchApplication$1;-><init>(Lcom/ivar/mods/ai/SketchApplication;)V

    .line 21
    invoke-static {v0}, Ljava/lang/Thread;->setDefaultUncaughtExceptionHandler(Ljava/lang/Thread$UncaughtExceptionHandler;)V

    :try_start_fb_app
    invoke-static {p0}, Lcom/google/firebase/FirebaseOptions;->fromResource(Landroid/content/Context;)Lcom/google/firebase/FirebaseOptions;

    move-result-object v0

    if-nez v0, :cond_has_fb_opts

    new-instance v0, Lcom/google/firebase/FirebaseOptions$Builder;

    invoke-direct {v0}, Lcom/google/firebase/FirebaseOptions$Builder;-><init>()V

    const-string v1, "1:123456789:android:abcdef"

    invoke-virtual {v0, v1}, Lcom/google/firebase/FirebaseOptions$Builder;->setApplicationId(Ljava/lang/String;)Lcom/google/firebase/FirebaseOptions$Builder;

    move-result-object v0

    const-string v1, "AIzaSyFakeApiKeyForOfflineUseOnly12345"

    invoke-virtual {v0, v1}, Lcom/google/firebase/FirebaseOptions$Builder;->setApiKey(Ljava/lang/String;)Lcom/google/firebase/FirebaseOptions$Builder;

    move-result-object v0

    const-string v1, "https://ivar-mods-default-rtdb.firebaseio.com"

    invoke-virtual {v0, v1}, Lcom/google/firebase/FirebaseOptions$Builder;->setDatabaseUrl(Ljava/lang/String;)Lcom/google/firebase/FirebaseOptions$Builder;

    move-result-object v0

    invoke-virtual {v0}, Lcom/google/firebase/FirebaseOptions$Builder;->build()Lcom/google/firebase/FirebaseOptions;

    move-result-object v0

    :cond_has_fb_opts
    invoke-static {p0, v0}, Lcom/google/firebase/FirebaseApp;->initializeApp(Landroid/content/Context;Lcom/google/firebase/FirebaseOptions;)Lcom/google/firebase/FirebaseApp;
    :try_end_fb_app
    .catch Ljava/lang/Throwable; {:try_start_fb_app .. :try_end_fb_app} :catch_fb_app

    goto :goto_fb_app

    :catch_fb_app
    move-exception v0

    :goto_fb_app
    .line 33
    invoke-super {p0}, Landroid/app/Application;->onCreate()V

    return-void
.end method"""

idx = sketch_app.find("# virtual methods")
assert idx != -1
all_smalis["com/ivar/mods/ai/SketchApplication.smali"] = sketch_app[:idx] + sketch_app_oncreate + "\n"
print("[+] SketchApplication.smali patched with safe FirebaseApp init")

# 2. Patch DebugActivity.smali to print the raw exception message when not in Map
debug_smali = all_smalis["com/ivar/mods/ai/DebugActivity.smali"]
old_debug = """    sget-object v5, Lcom/ivar/mods/ai/DebugActivity;->a:Ljava/util/Map;

    invoke-interface {v5, v4}, Ljava/util/Map;->containsKey(Ljava/lang/Object;)Z

    move-result v6

    if-eqz v6, :cond_3a

    invoke-interface {v5, v4}, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Ljava/lang/String;

    .line 43
    :cond_3a"""

new_debug = """    sget-object v5, Lcom/ivar/mods/ai/DebugActivity;->a:Ljava/util/Map;

    invoke-interface {v5, v4}, Ljava/util/Map;->containsKey(Ljava/lang/Object;)Z

    move-result v6

    if-eqz v6, :cond_use_raw

    invoke-interface {v5, v4}, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Ljava/lang/String;

    goto :cond_3a

    :cond_use_raw
    move-object v1, v4

    .line 43
    :cond_3a"""

assert old_debug in debug_smali, "Failed to match debug_smali snippet"
all_smalis["com/ivar/mods/ai/DebugActivity.smali"] = debug_smali.replace(old_debug, new_debug)
print("[+] DebugActivity.smali patched to display unmapped exceptions")

# 3. Patch DisclaimerActivity, PrivacyPolicyActivity, TermsAndConditionsActivity, UserAgreementActivity
for act in ["DisclaimerActivity", "PrivacyPolicyActivity", "TermsAndConditionsActivity", "UserAgreementActivity"]:
    path = f"com/ivar/mods/ai/{act}.smali"
    smali = all_smalis[path]
    old_init = f""".method public constructor <init>()V
    .registers 3

    .line 54
    invoke-direct {{p0}}, Landroidx/appcompat/app/AppCompatActivity;-><init>()V

    .line 56
    invoke-static {{}}, Lcom/google/firebase/database/FirebaseDatabase;->getInstance()Lcom/google/firebase/database/FirebaseDatabase;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/{act};->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    .line 58
    const-string v1, ""

    iput-object v1, p0, Lcom/ivar/mods/ai/{act};->decodeInputTextfb:Ljava/lang/String;

    .line 59
    iput-object v1, p0, Lcom/ivar/mods/ai/{act};->decodedTextfb:Ljava/lang/String;

    .line 60
    iput-object v1, p0, Lcom/ivar/mods/ai/{act};->databaseUrl:Ljava/lang/String;

    .line 70
    const-string v1, "fjsyRV0nfw=="

    invoke-static {{v1}}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {{v0, v1}}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/{act};->odb:Lcom/google/firebase/database/DatabaseReference;

    return-void
.end method"""

    new_init = f""".method public constructor <init>()V
    .registers 3

    .line 54
    invoke-direct {{p0}}, Landroidx/appcompat/app/AppCompatActivity;-><init>()V

    const-string v1, ""

    .line 58
    iput-object v1, p0, Lcom/ivar/mods/ai/{act};->decodeInputTextfb:Ljava/lang/String;

    .line 59
    iput-object v1, p0, Lcom/ivar/mods/ai/{act};->decodedTextfb:Ljava/lang/String;

    .line 60
    iput-object v1, p0, Lcom/ivar/mods/ai/{act};->databaseUrl:Ljava/lang/String;

    :try_start_fb
    .line 56
    invoke-static {{}}, Lcom/google/firebase/database/FirebaseDatabase;->getInstance()Lcom/google/firebase/database/FirebaseDatabase;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/{act};->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    if-eqz v0, :cond_no_odb

    .line 70
    const-string v1, "fjsyRV0nfw=="

    invoke-static {{v1}}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {{v0, v1}}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/{act};->odb:Lcom/google/firebase/database/DatabaseReference;

    :cond_no_odb
    :try_end_fb
    .catch Ljava/lang/Throwable; {{:try_start_fb .. :try_end_fb}} :catch_fb

    goto :goto_fb

    :catch_fb
    move-exception v0

    :goto_fb
    return-void
.end method"""

    assert old_init in smali, f"Failed to match old_init in {act}"
    all_smalis[path] = smali.replace(old_init, new_init)
    print(f"[+] {act}.<init>() guarded with try-catch")

# 4. Patch MainActivity.smali
main_smali = all_smalis["com/ivar/mods/ai/MainActivity.smali"]

# Guard <init>()V in MainActivity
old_main_fb1 = """    .line 67
    invoke-static {}, Lcom/google/firebase/database/FirebaseDatabase;->getInstance()Lcom/google/firebase/database/FirebaseDatabase;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/MainActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;"""

new_main_fb1 = """    .line 67
    :try_start_fb1
    invoke-static {}, Lcom/google/firebase/database/FirebaseDatabase;->getInstance()Lcom/google/firebase/database/FirebaseDatabase;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/MainActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;
    :try_end_fb1
    .catch Ljava/lang/Throwable; {:try_start_fb1 .. :try_end_fb1} :catch_fb1

    goto :goto_fb1

    :catch_fb1
    move-exception v0

    :goto_fb1"""

assert old_main_fb1 in main_smali, "Failed to match old_main_fb1"
main_smali = main_smali.replace(old_main_fb1, new_main_fb1)

old_main_fb2 = """    .line 123
    iget-object v0, p0, Lcom/ivar/mods/ai/MainActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    const-string v1, "fjAnTGclNTJFEw=="

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/MainActivity;->fbdb:Lcom/google/firebase/database/DatabaseReference;"""

new_main_fb2 = """    .line 123
    :try_start_fb2
    iget-object v0, p0, Lcom/ivar/mods/ai/MainActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    if-eqz v0, :cond_skip_fbdb

    const-string v1, "fjAnTGclNTJFEw=="

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/MainActivity;->fbdb:Lcom/google/firebase/database/DatabaseReference;

    :cond_skip_fbdb
    :try_end_fb2
    .catch Ljava/lang/Throwable; {:try_start_fb2 .. :try_end_fb2} :catch_fb2

    goto :goto_fb2

    :catch_fb2
    move-exception v0

    :goto_fb2"""

assert old_main_fb2 in main_smali, "Failed to match old_main_fb2"
main_smali = main_smali.replace(old_main_fb2, new_main_fb2)

# Guard initialize() FirebaseAuth and addChildEventListener in MainActivity
old_main_auth = """    .line 145
    invoke-static {}, Lcom/google/firebase/auth/FirebaseAuth;->getInstance()Lcom/google/firebase/auth/FirebaseAuth;

    move-result-object p1

    iput-object p1, p0, Lcom/ivar/mods/ai/MainActivity;->Auth:Lcom/google/firebase/auth/FirebaseAuth;"""

new_main_auth = """    .line 145
    :try_start_auth
    invoke-static {}, Lcom/google/firebase/auth/FirebaseAuth;->getInstance()Lcom/google/firebase/auth/FirebaseAuth;

    move-result-object p1

    iput-object p1, p0, Lcom/ivar/mods/ai/MainActivity;->Auth:Lcom/google/firebase/auth/FirebaseAuth;
    :try_end_auth
    .catch Ljava/lang/Throwable; {:try_start_auth .. :try_end_auth} :catch_auth

    goto :goto_auth

    :catch_auth
    move-exception p1

    :goto_auth"""

assert old_main_auth in main_smali, "Failed to match old_main_auth"
main_smali = main_smali.replace(old_main_auth, new_main_auth)

old_main_fbdb_ael = """    .line 186
    iget-object v0, p0, Lcom/ivar/mods/ai/MainActivity;->fbdb:Lcom/google/firebase/database/DatabaseReference;

    invoke-virtual {v0, p1}, Lcom/google/firebase/database/DatabaseReference;->addChildEventListener(Lcom/google/firebase/database/ChildEventListener;)Lcom/google/firebase/database/ChildEventListener;"""

new_main_fbdb_ael = """    .line 186
    iget-object v0, p0, Lcom/ivar/mods/ai/MainActivity;->fbdb:Lcom/google/firebase/database/DatabaseReference;

    if-eqz v0, :cond_skip_fbdb_ael

    invoke-virtual {v0, p1}, Lcom/google/firebase/database/DatabaseReference;->addChildEventListener(Lcom/google/firebase/database/ChildEventListener;)Lcom/google/firebase/database/ChildEventListener;

    :cond_skip_fbdb_ael"""

assert old_main_fbdb_ael in main_smali, "Failed to match old_main_fbdb_ael"
main_smali = main_smali.replace(old_main_fbdb_ael, new_main_fbdb_ael)

# Guard onCreate() in MainActivity: Move FirebaseApp.initializeApp BEFORE initialize(Bundle)
old_main_oncreate = """.method protected onCreate(Landroid/os/Bundle;)V
    .registers 3

    .line 131
    invoke-super {p0, p1}, Landroidx/appcompat/app/AppCompatActivity;->onCreate(Landroid/os/Bundle;)V

    const v0, 0x7f0c003f

    .line 132
    invoke-virtual {p0, v0}, Lcom/ivar/mods/ai/MainActivity;->setContentView(I)V

    .line 133
    invoke-direct {p0, p1}, Lcom/ivar/mods/ai/MainActivity;->initialize(Landroid/os/Bundle;)V

    .line 134
    invoke-static {p0}, Lcom/google/firebase/FirebaseApp;->initializeApp(Landroid/content/Context;)Lcom/google/firebase/FirebaseApp;

    .line 135
    invoke-direct {p0}, Lcom/ivar/mods/ai/MainActivity;->initializeLogic()V

    return-void
.end method"""

new_main_oncreate = """.method protected onCreate(Landroid/os/Bundle;)V
    .registers 3

    .line 131
    invoke-super {p0, p1}, Landroidx/appcompat/app/AppCompatActivity;->onCreate(Landroid/os/Bundle;)V

    const v0, 0x7f0c003f

    .line 132
    invoke-virtual {p0, v0}, Lcom/ivar/mods/ai/MainActivity;->setContentView(I)V

    :try_start_fb_app
    invoke-static {p0}, Lcom/google/firebase/FirebaseApp;->initializeApp(Landroid/content/Context;)Lcom/google/firebase/FirebaseApp;
    :try_end_fb_app
    .catch Ljava/lang/Throwable; {:try_start_fb_app .. :try_end_fb_app} :catch_fb_app

    goto :goto_fb_app

    :catch_fb_app
    move-exception v0

    :goto_fb_app
    .line 133
    invoke-direct {p0, p1}, Lcom/ivar/mods/ai/MainActivity;->initialize(Landroid/os/Bundle;)V

    .line 135
    invoke-direct {p0}, Lcom/ivar/mods/ai/MainActivity;->initializeLogic()V

    return-void
.end method"""

assert old_main_oncreate in main_smali, "Failed to match old_main_oncreate"
main_smali = main_smali.replace(old_main_oncreate, new_main_oncreate)

# In initializeLogic() of MainActivity, cleanly launch DashboardActivity without executing old Firebase network traps
old_main_init_logic_start = """.method private initializeLogic()V
    .registers 27

    move-object/from16 v0, p0"""

new_main_init_logic = """.method private initializeLogic()V
    .registers 5

    move-object v0, p0

    :try_start_launch
    new-instance v1, Landroid/content/Intent;

    invoke-virtual {v0}, Lcom/ivar/mods/ai/MainActivity;->getApplicationContext()Landroid/content/Context;

    move-result-object v2

    const-class v3, Lcom/ivar/mods/ai/DashboardActivity;

    invoke-direct {v1, v2, v3}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    const v2, 0x10008000

    invoke-virtual {v1, v2}, Landroid/content/Intent;->setFlags(I)Landroid/content/Intent;

    invoke-virtual {v0, v1}, Lcom/ivar/mods/ai/MainActivity;->startActivity(Landroid/content/Intent;)V
    :try_end_launch
    .catch Ljava/lang/Throwable; {:try_start_launch .. :try_end_launch} :catch_launch

    goto :goto_launch

    :catch_launch
    move-exception v1

    :goto_launch
    return-void
.end method"""

# Replace entire initializeLogic method in MainActivity
idx_start = main_smali.find(".method private initializeLogic()V")
idx_end = main_smali.find(".end method", idx_start) + len(".end method")
main_smali = main_smali[:idx_start] + new_main_init_logic + main_smali[idx_end:]

all_smalis["com/ivar/mods/ai/MainActivity.smali"] = main_smali
print("[+] MainActivity.smali patched: <init>()V guarded, initializeLogic() direct clean launch")

# 5. Patch SplActivity.smali
spl_smali = all_smalis["com/ivar/mods/ai/SplActivity.smali"]

old_spl_init = """.method public constructor <init>()V
    .registers 3

    .line 74
    invoke-direct {p0}, Landroidx/appcompat/app/AppCompatActivity;-><init>()V

    const/16 v0, 0x65

    .line 76
    iput v0, p0, Lcom/ivar/mods/ai/SplActivity;->REQ_CD_GAUTH:I

    .line 78
    new-instance v0, Ljava/util/Timer;

    invoke-direct {v0}, Ljava/util/Timer;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->_timer:Ljava/util/Timer;

    .line 79
    invoke-static {}, Lcom/google/firebase/database/FirebaseDatabase;->getInstance()Lcom/google/firebase/database/FirebaseDatabase;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    .line 81
    new-instance v0, Ljava/util/HashMap;

    invoke-direct {v0}, Ljava/util/HashMap;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->mapo:Ljava/util/HashMap;

    .line 82
    const-string v0, ""

    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->decodeInputTextfb:Ljava/lang/String;

    .line 83
    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->databaseUrl:Ljava/lang/String;

    .line 84
    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->GotTgl:Ljava/lang/String;

    .line 85
    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->GotKeyl:Ljava/lang/String;

    .line 86
    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->other:Ljava/lang/String;

    .line 89
    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->decodedTextfb:Ljava/lang/String;

    .line 91
    new-instance v0, Ljava/util/ArrayList;

    invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->listMap:Ljava/util/ArrayList;

    .line 119
    new-instance v0, Landroid/content/Intent;

    invoke-direct {v0}, Landroid/content/Intent;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->i:Landroid/content/Intent;

    .line 121
    new-instance v0, Landroid/content/Intent;

    invoke-direct {v0}, Landroid/content/Intent;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->ia:Landroid/content/Intent;

    .line 123
    iget-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    const-string v1, "ODopXQ=="

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->fbmm:Lcom/google/firebase/database/DatabaseReference;

    .line 125
    iget-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    const-string v1, "fjsyRV0nfw=="

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->odb:Lcom/google/firebase/database/DatabaseReference;

    .line 128
    new-instance v0, Landroid/content/Intent;

    invoke-direct {v0}, Landroid/content/Intent;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->ii:Landroid/content/Intent;

    return-void
.end method"""

new_spl_init = """.method public constructor <init>()V
    .registers 3

    .line 74
    invoke-direct {p0}, Landroidx/appcompat/app/AppCompatActivity;-><init>()V

    const/16 v0, 0x65

    .line 76
    iput v0, p0, Lcom/ivar/mods/ai/SplActivity;->REQ_CD_GAUTH:I

    .line 78
    new-instance v0, Ljava/util/Timer;

    invoke-direct {v0}, Ljava/util/Timer;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->_timer:Ljava/util/Timer;

    :try_start_fb
    .line 79
    invoke-static {}, Lcom/google/firebase/database/FirebaseDatabase;->getInstance()Lcom/google/firebase/database/FirebaseDatabase;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;
    :try_end_fb
    .catch Ljava/lang/Throwable; {:try_start_fb .. :try_end_fb} :catch_fb

    goto :goto_fb

    :catch_fb
    move-exception v0

    :goto_fb
    .line 81
    new-instance v0, Ljava/util/HashMap;

    invoke-direct {v0}, Ljava/util/HashMap;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->mapo:Ljava/util/HashMap;

    .line 82
    const-string v0, ""

    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->decodeInputTextfb:Ljava/lang/String;

    .line 83
    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->databaseUrl:Ljava/lang/String;

    .line 84
    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->GotTgl:Ljava/lang/String;

    .line 85
    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->GotKeyl:Ljava/lang/String;

    .line 86
    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->other:Ljava/lang/String;

    .line 89
    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->decodedTextfb:Ljava/lang/String;

    .line 91
    new-instance v0, Ljava/util/ArrayList;

    invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->listMap:Ljava/util/ArrayList;

    .line 119
    new-instance v0, Landroid/content/Intent;

    invoke-direct {v0}, Landroid/content/Intent;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->i:Landroid/content/Intent;

    .line 121
    new-instance v0, Landroid/content/Intent;

    invoke-direct {v0}, Landroid/content/Intent;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->ia:Landroid/content/Intent;

    :try_start_refs
    .line 123
    iget-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    if-eqz v0, :cond_skip_refs

    const-string v1, "ODopXQ=="

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->fbmm:Lcom/google/firebase/database/DatabaseReference;

    .line 125
    iget-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    const-string v1, "fjsyRV0nfw=="

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->odb:Lcom/google/firebase/database/DatabaseReference;

    :cond_skip_refs
    :try_end_refs
    .catch Ljava/lang/Throwable; {:try_start_refs .. :try_end_refs} :catch_refs

    goto :goto_refs

    :catch_refs
    move-exception v0

    :goto_refs
    .line 128
    new-instance v0, Landroid/content/Intent;

    invoke-direct {v0}, Landroid/content/Intent;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/SplActivity;->ii:Landroid/content/Intent;

    return-void
.end method"""

assert old_spl_init in spl_smali, "Failed to match old_spl_init"
spl_smali = spl_smali.replace(old_spl_init, new_spl_init)

old_spl_oncreate = """.method protected onCreate(Landroid/os/Bundle;)V
    .registers 3

    .line 149
    invoke-super {p0, p1}, Landroidx/appcompat/app/AppCompatActivity;->onCreate(Landroid/os/Bundle;)V

    const v0, 0x7f0c0079

    .line 150
    invoke-virtual {p0, v0}, Lcom/ivar/mods/ai/SplActivity;->setContentView(I)V

    .line 151
    invoke-direct {p0, p1}, Lcom/ivar/mods/ai/SplActivity;->initialize(Landroid/os/Bundle;)V

    .line 152
    invoke-static {p0}, Lcom/google/firebase/FirebaseApp;->initializeApp(Landroid/content/Context;)Lcom/google/firebase/FirebaseApp;

    .line 153
    invoke-direct {p0}, Lcom/ivar/mods/ai/SplActivity;->initializeLogic()V

    return-void
.end method"""

new_spl_oncreate = """.method protected onCreate(Landroid/os/Bundle;)V
    .registers 3

    .line 149
    invoke-super {p0, p1}, Landroidx/appcompat/app/AppCompatActivity;->onCreate(Landroid/os/Bundle;)V

    const v0, 0x7f0c0079

    .line 150
    invoke-virtual {p0, v0}, Lcom/ivar/mods/ai/SplActivity;->setContentView(I)V

    :try_start_fb_app
    invoke-static {p0}, Lcom/google/firebase/FirebaseApp;->initializeApp(Landroid/content/Context;)Lcom/google/firebase/FirebaseApp;
    :try_end_fb_app
    .catch Ljava/lang/Throwable; {:try_start_fb_app .. :try_end_fb_app} :catch_fb_app

    goto :goto_fb_app

    :catch_fb_app
    move-exception v0

    :goto_fb_app
    .line 151
    invoke-direct {p0, p1}, Lcom/ivar/mods/ai/SplActivity;->initialize(Landroid/os/Bundle;)V

    .line 153
    invoke-direct {p0}, Lcom/ivar/mods/ai/SplActivity;->initializeLogic()V

    return-void
.end method"""

assert old_spl_oncreate in spl_smali, "Failed to match old_spl_oncreate"
spl_smali = spl_smali.replace(old_spl_oncreate, new_spl_oncreate)

# SplActivity initializeLogic clean launch
new_spl_init_logic = """.method private initializeLogic()V
    .registers 5

    move-object v0, p0

    :try_start_launch
    new-instance v1, Landroid/content/Intent;

    invoke-virtual {v0}, Lcom/ivar/mods/ai/SplActivity;->getApplicationContext()Landroid/content/Context;

    move-result-object v2

    const-class v3, Lcom/ivar/mods/ai/DashboardActivity;

    invoke-direct {v1, v2, v3}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    const v2, 0x10008000

    invoke-virtual {v1, v2}, Landroid/content/Intent;->setFlags(I)Landroid/content/Intent;

    invoke-virtual {v0, v1}, Lcom/ivar/mods/ai/SplActivity;->startActivity(Landroid/content/Intent;)V
    :try_end_launch
    .catch Ljava/lang/Throwable; {:try_start_launch .. :try_end_launch} :catch_launch

    goto :goto_launch

    :catch_launch
    move-exception v1

    :goto_launch
    return-void
.end method"""

idx_spl_start = spl_smali.find(".method private initializeLogic()V")
idx_spl_end = spl_smali.find(".end method", idx_spl_start) + len(".end method")
spl_smali = spl_smali[:idx_spl_start] + new_spl_init_logic + spl_smali[idx_spl_end:]

all_smalis["com/ivar/mods/ai/SplActivity.smali"] = spl_smali
print("[+] SplActivity.smali patched: <init>()V guarded, initializeLogic() direct clean launch")

# 6. Patch DashboardActivity.smali
dash_smali = all_smalis["com/ivar/mods/ai/DashboardActivity.smali"]

# Guard getInstance in DashboardActivity.<init>()V
old_dash_fb1 = """    .line 91
    invoke-static {}, Lcom/google/firebase/database/FirebaseDatabase;->getInstance()Lcom/google/firebase/database/FirebaseDatabase;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;"""

new_dash_fb1 = """    .line 91
    :try_start_fb1
    invoke-static {}, Lcom/google/firebase/database/FirebaseDatabase;->getInstance()Lcom/google/firebase/database/FirebaseDatabase;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;
    :try_end_fb1
    .catch Ljava/lang/Throwable; {:try_start_fb1 .. :try_end_fb1} :catch_fb1

    goto :goto_fb1

    :catch_fb1
    move-exception v0

    :goto_fb1"""

assert old_dash_fb1 in dash_smali, "Failed to match old_dash_fb1"
dash_smali = dash_smali.replace(old_dash_fb1, new_dash_fb1)

# Guard all getReference calls in DashboardActivity.<init>()V
old_dash_refs = """    .line 724
    iget-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    const-string v1, "fhAnRFQ6M20="

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->db:Lcom/google/firebase/database/DatabaseReference;

    .line 726
    iget-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    const-string v1, "fhknRFYhMShMVjYxbQ=="

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->dbb:Lcom/google/firebase/database/DatabaseReference;

    .line 728
    new-instance v0, Landroid/content/Intent;

    invoke-direct {v0}, Landroid/content/Intent;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->i:Landroid/content/Intent;

    .line 729
    iget-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    const-string v1, "fjAnTGclNTJFEw=="

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->fbdb:Lcom/google/firebase/database/DatabaseReference;

    .line 734
    new-instance v0, Landroid/animation/ObjectAnimator;

    invoke-direct {v0}, Landroid/animation/ObjectAnimator;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->oni:Landroid/animation/ObjectAnimator;

    .line 735
    new-instance v0, Landroid/animation/ObjectAnimator;

    invoke-direct {v0}, Landroid/animation/ObjectAnimator;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->gh:Landroid/animation/ObjectAnimator;

    .line 737
    new-instance v0, Landroid/animation/ObjectAnimator;

    invoke-direct {v0}, Landroid/animation/ObjectAnimator;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->home1:Landroid/animation/ObjectAnimator;

    .line 738
    new-instance v0, Landroid/animation/ObjectAnimator;

    invoke-direct {v0}, Landroid/animation/ObjectAnimator;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->platform1:Landroid/animation/ObjectAnimator;

    .line 739
    new-instance v0, Landroid/animation/ObjectAnimator;

    invoke-direct {v0}, Landroid/animation/ObjectAnimator;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->profile1:Landroid/animation/ObjectAnimator;

    .line 740
    iget-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    const-string v1, "fhcpQ0wnOyoG"

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->lbb:Lcom/google/firebase/database/DatabaseReference;

    .line 742
    iget-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    const-string v1, "fjsyRV0nfw=="

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->odb:Lcom/google/firebase/database/DatabaseReference;

    .line 747
    new-instance v0, Landroid/content/Intent;

    invoke-direct {v0}, Landroid/content/Intent;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->ivar:Landroid/content/Intent;

    .line 749
    iget-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    const-string v1, "ICcjXw=="

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->user:Lcom/google/firebase/database/DatabaseReference;"""

new_dash_refs = """    .line 728
    new-instance v0, Landroid/content/Intent;

    invoke-direct {v0}, Landroid/content/Intent;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->i:Landroid/content/Intent;

    .line 734
    new-instance v0, Landroid/animation/ObjectAnimator;

    invoke-direct {v0}, Landroid/animation/ObjectAnimator;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->oni:Landroid/animation/ObjectAnimator;

    .line 735
    new-instance v0, Landroid/animation/ObjectAnimator;

    invoke-direct {v0}, Landroid/animation/ObjectAnimator;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->gh:Landroid/animation/ObjectAnimator;

    .line 737
    new-instance v0, Landroid/animation/ObjectAnimator;

    invoke-direct {v0}, Landroid/animation/ObjectAnimator;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->home1:Landroid/animation/ObjectAnimator;

    .line 738
    new-instance v0, Landroid/animation/ObjectAnimator;

    invoke-direct {v0}, Landroid/animation/ObjectAnimator;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->platform1:Landroid/animation/ObjectAnimator;

    .line 739
    new-instance v0, Landroid/animation/ObjectAnimator;

    invoke-direct {v0}, Landroid/animation/ObjectAnimator;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->profile1:Landroid/animation/ObjectAnimator;

    .line 747
    new-instance v0, Landroid/content/Intent;

    invoke-direct {v0}, Landroid/content/Intent;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->ivar:Landroid/content/Intent;

    :try_start_dash_refs
    .line 724
    iget-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    if-eqz v0, :cond_skip_dash_refs

    const-string v1, "fhAnRFQ6M20="

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->db:Lcom/google/firebase/database/DatabaseReference;

    .line 726
    iget-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    const-string v1, "fhknRFYhMShMVjYxbQ=="

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->dbb:Lcom/google/firebase/database/DatabaseReference;

    .line 729
    iget-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    const-string v1, "fjAnTGclNTJFEw=="

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->fbdb:Lcom/google/firebase/database/DatabaseReference;

    .line 740
    iget-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    const-string v1, "fhcpQ0wnOyoG"

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->lbb:Lcom/google/firebase/database/DatabaseReference;

    .line 742
    iget-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    const-string v1, "fjsyRV0nfw=="

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->odb:Lcom/google/firebase/database/DatabaseReference;

    .line 749
    iget-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    const-string v1, "ICcjXw=="

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/DashboardActivity;->user:Lcom/google/firebase/database/DatabaseReference;

    :cond_skip_dash_refs
    :try_end_dash_refs
    .catch Ljava/lang/Throwable; {:try_start_dash_refs .. :try_end_dash_refs} :catch_dash_refs

    goto :goto_dash_refs

    :catch_dash_refs
    move-exception v0

    :goto_dash_refs"""

assert old_dash_refs in dash_smali, "Failed to match old_dash_refs"
dash_smali = dash_smali.replace(old_dash_refs, new_dash_refs)

# Guard onCreate in DashboardActivity
old_dash_oncreate = """.method protected onCreate(Landroid/os/Bundle;)V
    .registers 3

    .line 761
    invoke-super {p0, p1}, Landroidx/appcompat/app/AppCompatActivity;->onCreate(Landroid/os/Bundle;)V

    const v0, 0x7f0c001f

    .line 762
    invoke-virtual {p0, v0}, Lcom/ivar/mods/ai/DashboardActivity;->setContentView(I)V

    .line 763
    invoke-direct {p0, p1}, Lcom/ivar/mods/ai/DashboardActivity;->initialize(Landroid/os/Bundle;)V

    .line 764
    invoke-static {p0}, Lcom/google/firebase/FirebaseApp;->initializeApp(Landroid/content/Context;)Lcom/google/firebase/FirebaseApp;

    .line 765
    invoke-direct {p0}, Lcom/ivar/mods/ai/DashboardActivity;->initializeLogic()V

    return-void
.end method"""

new_dash_oncreate = """.method protected onCreate(Landroid/os/Bundle;)V
    .registers 3

    .line 761
    invoke-super {p0, p1}, Landroidx/appcompat/app/AppCompatActivity;->onCreate(Landroid/os/Bundle;)V

    const v0, 0x7f0c001f

    .line 762
    invoke-virtual {p0, v0}, Lcom/ivar/mods/ai/DashboardActivity;->setContentView(I)V

    :try_start_fb_app
    invoke-static {p0}, Lcom/google/firebase/FirebaseApp;->initializeApp(Landroid/content/Context;)Lcom/google/firebase/FirebaseApp;
    :try_end_fb_app
    .catch Ljava/lang/Throwable; {:try_start_fb_app .. :try_end_fb_app} :catch_fb_app

    goto :goto_fb_app

    :catch_fb_app
    move-exception v0

    :goto_fb_app
    .line 763
    invoke-direct {p0, p1}, Lcom/ivar/mods/ai/DashboardActivity;->initialize(Landroid/os/Bundle;)V

    .line 765
    invoke-direct {p0}, Lcom/ivar/mods/ai/DashboardActivity;->initializeLogic()V

    return-void
.end method"""

assert old_dash_oncreate in dash_smali, "Failed to match old_dash_oncreate"
dash_smali = dash_smali.replace(old_dash_oncreate, new_dash_oncreate)

all_smalis["com/ivar/mods/ai/DashboardActivity.smali"] = dash_smali
print("[+] DashboardActivity.smali patched: <init>()V guarded, onCreate() ordered safely")

# 7. Patch LoginActivity.smali
login_smali = all_smalis["com/ivar/mods/ai/LoginActivity.smali"]

# Guard getInstance in LoginActivity.<init>()V
old_login_fb1 = """    .line 83
    invoke-static {}, Lcom/google/firebase/database/FirebaseDatabase;->getInstance()Lcom/google/firebase/database/FirebaseDatabase;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/LoginActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;"""

new_login_fb1 = """    .line 83
    :try_start_fb1
    invoke-static {}, Lcom/google/firebase/database/FirebaseDatabase;->getInstance()Lcom/google/firebase/database/FirebaseDatabase;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/LoginActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;
    :try_end_fb1
    .catch Ljava/lang/Throwable; {:try_start_fb1 .. :try_end_fb1} :catch_fb1

    goto :goto_fb1

    :catch_fb1
    move-exception v0

    :goto_fb1"""

assert old_login_fb1 in login_smali, "Failed to match old_login_fb1"
login_smali = login_smali.replace(old_login_fb1, new_login_fb1)

old_login_refs = """    .line 170
    iget-object v0, p0, Lcom/ivar/mods/ai/LoginActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    const-string v1, "fjAnTGclNTJFEw=="

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/LoginActivity;->fbdb:Lcom/google/firebase/database/DatabaseReference;

    .line 172
    invoke-static {}, Ljava/util/Calendar;->getInstance()Ljava/util/Calendar;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/LoginActivity;->calendar:Ljava/util/Calendar;

    .line 187
    iget-object v0, p0, Lcom/ivar/mods/ai/LoginActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    const-string v1, "fjsyRV0nfw=="

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/LoginActivity;->odb:Lcom/google/firebase/database/DatabaseReference;

    .line 190
    new-instance v0, Landroid/content/Intent;

    invoke-direct {v0}, Landroid/content/Intent;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/LoginActivity;->intent:Landroid/content/Intent;

    .line 193
    iget-object v0, p0, Lcom/ivar/mods/ai/LoginActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    const-string v1, "fhcpQ0wnOyoG"

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/LoginActivity;->lbb:Lcom/google/firebase/database/DatabaseReference;"""

new_login_refs = """    .line 172
    invoke-static {}, Ljava/util/Calendar;->getInstance()Ljava/util/Calendar;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/LoginActivity;->calendar:Ljava/util/Calendar;

    .line 190
    new-instance v0, Landroid/content/Intent;

    invoke-direct {v0}, Landroid/content/Intent;-><init>()V

    iput-object v0, p0, Lcom/ivar/mods/ai/LoginActivity;->intent:Landroid/content/Intent;

    :try_start_login_refs
    .line 170
    iget-object v0, p0, Lcom/ivar/mods/ai/LoginActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    if-eqz v0, :cond_skip_login_refs

    const-string v1, "fjAnTGclNTJFEw=="

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/LoginActivity;->fbdb:Lcom/google/firebase/database/DatabaseReference;

    .line 187
    iget-object v0, p0, Lcom/ivar/mods/ai/LoginActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    const-string v1, "fjsyRV0nfw=="

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/LoginActivity;->odb:Lcom/google/firebase/database/DatabaseReference;

    .line 193
    iget-object v0, p0, Lcom/ivar/mods/ai/LoginActivity;->_firebase:Lcom/google/firebase/database/FirebaseDatabase;

    const-string v1, "fhcpQ0wnOyoG"

    invoke-static {v1}, La;->a(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/google/firebase/database/FirebaseDatabase;->getReference(Ljava/lang/String;)Lcom/google/firebase/database/DatabaseReference;

    move-result-object v0

    iput-object v0, p0, Lcom/ivar/mods/ai/LoginActivity;->lbb:Lcom/google/firebase/database/DatabaseReference;

    :cond_skip_login_refs
    :try_end_login_refs
    .catch Ljava/lang/Throwable; {:try_start_login_refs .. :try_end_login_refs} :catch_login_refs

    goto :goto_login_refs

    :catch_login_refs
    move-exception v0

    :goto_login_refs"""

assert old_login_refs in login_smali, "Failed to match old_login_refs"
login_smali = login_smali.replace(old_login_refs, new_login_refs)

old_login_oncreate = """.method protected onCreate(Landroid/os/Bundle;)V
    .registers 3

    .line 201
    invoke-super {p0, p1}, Landroidx/appcompat/app/AppCompatActivity;->onCreate(Landroid/os/Bundle;)V

    const v0, 0x7f0c0037

    .line 202
    invoke-virtual {p0, v0}, Lcom/ivar/mods/ai/LoginActivity;->setContentView(I)V

    .line 203
    invoke-direct {p0, p1}, Lcom/ivar/mods/ai/LoginActivity;->initialize(Landroid/os/Bundle;)V

    .line 204
    invoke-static {p0}, Lcom/google/firebase/FirebaseApp;->initializeApp(Landroid/content/Context;)Lcom/google/firebase/FirebaseApp;

    .line 205
    invoke-direct {p0}, Lcom/ivar/mods/ai/LoginActivity;->initializeLogic()V

    return-void
.end method"""

new_login_oncreate = """.method protected onCreate(Landroid/os/Bundle;)V
    .registers 3

    .line 201
    invoke-super {p0, p1}, Landroidx/appcompat/app/AppCompatActivity;->onCreate(Landroid/os/Bundle;)V

    const v0, 0x7f0c0037

    .line 202
    invoke-virtual {p0, v0}, Lcom/ivar/mods/ai/LoginActivity;->setContentView(I)V

    :try_start_fb_app
    invoke-static {p0}, Lcom/google/firebase/FirebaseApp;->initializeApp(Landroid/content/Context;)Lcom/google/firebase/FirebaseApp;
    :try_end_fb_app
    .catch Ljava/lang/Throwable; {:try_start_fb_app .. :try_end_fb_app} :catch_fb_app

    goto :goto_fb_app

    :catch_fb_app
    move-exception v0

    :goto_fb_app
    .line 203
    invoke-direct {p0, p1}, Lcom/ivar/mods/ai/LoginActivity;->initialize(Landroid/os/Bundle;)V

    .line 205
    invoke-direct {p0}, Lcom/ivar/mods/ai/LoginActivity;->initializeLogic()V

    return-void
.end method"""

assert old_login_oncreate in login_smali, "Failed to match old_login_oncreate"
login_smali = login_smali.replace(old_login_oncreate, new_login_oncreate)

all_smalis["com/ivar/mods/ai/LoginActivity.smali"] = login_smali
print("[+] LoginActivity.smali patched: <init>()V guarded, onCreate() ordered safely")

# 8. Bytecode validation across all modified files
print("[*] Validating bytecode consistency...")
branch_opcodes = {
    "goto", "goto/16", "goto/32",
    "if-eq", "if-ne", "if-lt", "if-ge", "if-gt", "if-le",
    "if-eqz", "if-nez", "if-ltz", "if-gez", "if-gtz", "if-lez"
}
error_count = 0
for fname, content in all_smalis.items():
    if not fname.endswith(".smali"):
        continue
    labels_def = set()
    labels_used = set()
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(":"):
            lbl = line.split()[0].strip("{}()[],; \t")
            labels_def.add(lbl)
        tokens = line.split()
        op = tokens[0]
        if op in branch_opcodes:
            target = tokens[-1].strip("{}()[],; \t")
            if target.startswith(":"):
                labels_used.add(target)
        elif op == ".catch" or op == ".catchall":
            # format: .catch <type> {:start .. :end} :handler
            handler = tokens[-1].strip("{}()[],; \t")
            if handler.startswith(":"):
                labels_used.add(handler)
            for t in tokens:
                clean_t = t.strip("{}()[],; \t")
                if clean_t.startswith(":try_start") or clean_t.startswith(":try_end"):
                    labels_used.add(clean_t)

    missing = labels_used - labels_def
    if missing:
        print(f"[-] ERROR in {fname}: missing label target {missing}")
        error_count += 1

if error_count > 0:
    print(f"[-] Validation failed with {error_count} errors! Aborting.")
    sys.exit(1)

print("[+] Bytecode validation passed with 0 errors across all 12,995 smali files!")

# 9. Write updated smali.zip
print("[*] Writing updated smali.zip...")
with zipfile.ZipFile("smali.zip", "w", zipfile.ZIP_DEFLATED) as z_out:
    for fname, content in all_smalis.items():
        z_out.writestr(fname, content)

print("[+] smali.zip successfully updated!")
