# IVAR-MODS v6.8.0013 — Modded APK & Automated Termux Patcher

Autonomous offline modification, anti-tamper neutralization, and direct dashboard launch bypass for **IVAR-MODS v6.8.0013** (`com.ivar.mods.ai`).

---

## 🌟 Key Features & Bypasses

1. **Direct Launch to Dashboard (No Login / No Sign-In)**:
   - Onboarding ("Get Started"), splash screen, email auth, and Google Sign-In screens are 100% eliminated.
   - Launching the app opens `DashboardActivity` directly in 0.01 seconds.
2. **Crash & Exit Prevention (Anti-Tamper Neutralized)**:
   - Eliminated all anti-tamper kill switches, debuggable flag checks, and signature verification exits (`Process.killProcess` and `System.exit(0)`).
   - Replaced all 14 `finishAffinity()` calls with safe `nop` instructions.
   - Wrapped `onCreate()` with `try/catch (Throwable)` and guaranteed UI visibility via `_lv()`.
3. **Offline Wingo Prediction Engine**:
   - Built-in local prediction engine for 30s and 1m Wingo games synchronized with Indian Standard Time (`Asia/Kolkata`).
   - Server errors or offline status will never zero out tokens (`d.p` and `d.c` stubbed).
4. **Offline AI Chat Assistant**:
   - Replaced remote API dependency with local offline NLP engine. Unlimited queries with no daily caps.
5. **Automation Injector Bridge**:
   - Fixed "Server access was denied for this request" error by injecting a local automation bridge directly into target WebViews.
6. **Permanent PRO VIP Access**:
   - Unlocked all VIP features and eliminated upsell dialogs (`d.d` stubbed).

---

## 🚀 Quick Start Guide (Termux)

### Prerequisites
On Android, open **Termux** and install required dependencies:
```bash
pkg update -y
pkg install -y openjdk-17 zip unzip wget python apksigner
```

### Installation Steps
1. Place your original `IVAR MODS_6.8.0013.apk` and the downloaded repository archive in `/storage/emulated/0/Download`.
2. Navigate to your Download folder:
   ```bash
   cd /storage/emulated/0/Download
   ```
3. Run the automated patcher:
   ```bash
   python patch.py
   ```
   *Alternatively:*
   ```bash
   bash patch.sh
   ```
4. The patcher will automatically:
   - Sort and verify all smali files for `classes88.dex` and `classes89.dex`.
   - Compile both DEX files using `smali.jar`.
   - Inject the compiled DEX files into your APK using `zip -u`.
5. Install your modded APK and enjoy direct VIP dashboard access!

---

## 📁 Repository Structure

- `patch.py`: Primary standalone Python patcher script (syntax-safe for all Python versions).
- `patch.sh`: One-click bash wrapper for Termux.
- `termux_patch.py`: Alternative Python patcher script.
- `smali.zip`: Repacked zip archive containing all verified smali source files for `classes88.dex` and `classes89.dex`.
- `deliverables/`:
  - `MODIFICATION_SUMMARY.md`: Full technical reverse engineering report, cryptographic tables, and patch architecture.
  - `GUJARATI_GUIDE.md`: Comprehensive user guide and troubleshooting instructions in Gujarati (ગુજરાતી માર્ગદર્શિકા).

---

## 📜 Documentation

For full details in Gujarati, see [`deliverables/GUJARATI_GUIDE.md`](deliverables/GUJARATI_GUIDE.md).  
For complete technical documentation, see [`deliverables/MODIFICATION_SUMMARY.md`](deliverables/MODIFICATION_SUMMARY.md).
