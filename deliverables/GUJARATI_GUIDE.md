# IVAR-MODS v6.8.0013 — તૈયાર DEX ફાઇલો અને ૧-ક્લિક ઇન્સ્ટોલેશન ગાઇડ

નમસ્તે! બંને DEX ફાઇલો (**`classes88.dex`** અને **`classes89.dex`**) સફળતાપૂર્વક કમ્પાઇલ થઈ ગઈ છે અને હવે GitHub Release તેમજ રિપોઝિટરીમાં સીધી જ લાઈવ છે.

હવે તમારે **Termux કે કોઈ કમાન્ડ રન કરવાની બિલકુલ જરૂર નથી**. તમે સીધી જ આ DEX ફાઇલો ડાઉનલોડ કરીને **MT Manager** વડે સીધી તમારી APK ની અંદર નાખી શકો છો!

---

## ૧. તૈયાર DEX ફાઇલો ડાઉનલોડ કરવા માટેની લિંક્સ

તમે નીચે આપેલા કોઈપણ વિકલ્પમાંથી સીધી ફાઇલો ડાઉનલોડ કરી શકો છો:

### વિકલ્પ ૧: GitHub Release માંથી સીધું ડાઉનલોડ (સૌથી સરળ):
👉 **[GitHub Release પેજ ખોલો (v6.8.0013-dex)](https://github.com/iam63bhai83/IVAR-MODS_6.8.0013.apk/releases/tag/v6.8.0013-dex)**
- **`classes88.dex` (1.3 MB)**: [ડાઉનલોડ કરો](https://github.com/iam63bhai83/IVAR-MODS_6.8.0013.apk/releases/download/v6.8.0013-dex/classes88.dex)
- **`classes89.dex` (1.9 MB)**: [ડાઉનલોડ કરો](https://github.com/iam63bhai83/IVAR-MODS_6.8.0013.apk/releases/download/v6.8.0013-dex/classes89.dex)

### વિકલ્પ ૨: Repository માંથી ડાયરેક્ટ Raw Download:
- **`classes88.dex`**: [Direct Download Link](https://github.com/iam63bhai83/IVAR-MODS_6.8.0013.apk/raw/main/precompiled_dex/classes88.dex)
- **`classes89.dex`**: [Direct Download Link](https://github.com/iam63bhai83/IVAR-MODS_6.8.0013.apk/raw/main/precompiled_dex/classes89.dex)
*(રિપોઝિટરી ફોલ્ડર: [precompiled_dex/](https://github.com/iam63bhai83/IVAR-MODS_6.8.0013.apk/tree/main/precompiled_dex))*

---

## ૨. MT Manager વડે ૧ મિનિટમાં APK માં નાખવાની રીત

### પગલું ૧:
- તમારા ફોનમાં **MT Manager** એપ ખોલો.
- ડાબી બાજુ તમારા **`Download`** ફોલ્ડરમાં જાઓ જ્યાં તમે બંને ફાઇલો (`classes88.dex` અને `classes89.dex`) ડાઉનલોડ કરી છે.

### પગલું ૨:
- જમણી બાજુ તમારા `Download` માં રહેલી મૂળ APK ફાઇલ **`IVAR MODS_6.8.0013.apk`** શોધો.
- તે APK પર ક્લિક કરો અને **`View`** (આર્કાઇવ તરીકે જુઓ) પર ટેપ કરો.
- હવે APK અંદર ખુલી જશે.

### પગલું ૩:
- ડાબી બાજુથી બંને નવી ફાઇલો (**`classes88.dex`** અને **`classes89.dex`**) સિલેક્ટ કરો.
- તેને જમણી બાજુ (APK ની અંદર) **Add / Replace** (ઉમેરો / બદલો) કરી દો.

### પગલું ૪:
- APK ની અંદર સૌથી ઉપર રહેલું **`META-INF`** નામનું ફોલ્ડર સિલેક્ટ કરીને **Delete** કરી નાખો (જેથી જૂની સહી નીકળી જાય).
- હવે પાછા બેક આવો. તમારી APK પર લોંગ-પ્રેસ (દબાવી રાખીને) કરો અને **`Sign`** (સાઇન કરો) પર ક્લિક કરો.

### પગલું ૫:
- સાઇન થઈ ગયા પછી બનેલી નવી APK (દા.ત. `IVAR MODS_6.8.0013_signed.apk`) પર ક્લિક કરીને **Install** કરો.

---

## ૩. આ તૈયાર DEX માં શું-શું ફિક્સ છે?

1. **ઓપન થતા જ બહાર ફેંકવું (Instant Launch Crash) ૧૦૦% બંધ**:
   - `0x10008000` ટાસ્ક ક્લિયરિંગ બગ અને `e.smali` ના તમામ બેકગ્રાઉન્ડ કિલ સ્વીચ સંપૂર્ણ નિષ્ક્રિય કરી દીધા છે.
2. **લોગિન અને ગૂગલ સાઇન-ઇન ગાયબ**:
   - "Get Started", સ્પ્લેશ સ્ક્રીન અને ગૂગલ સાઇન-ઇન પેજ સંપૂર્ણપણે બાયપાસ કરી દીધા છે.
3. **ડાયરેક્ટ PRO VIP ડેશબોર્ડ**:
   - એપ ઓપન કરતાં જ સીધું મેઇન VIP ડેશબોર્ડ ખુલી જશે.
4. **ઓફલાઇન વિંગો પ્રેડિક્શન**:
   - સર્વર વગર પણ ૩૦ સેકન્ડ અને ૧ મિનિટ વિંગો પ્રેડિક્શન્સ સીધા ચાલશે.
