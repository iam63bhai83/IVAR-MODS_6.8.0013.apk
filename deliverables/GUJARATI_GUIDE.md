# IVAR-MODS v6.8.0013 — તમામ Finish/Kill સ્વીચ ફિક્સ અને તૈયાર DEX ગાઇડ

નમસ્તે! તમે જે ૧૧૭ `finish` રિઝલ્ટ્સ MT Manager માં જોયા હતા, તે જ એપને બહાર ફેંકી દેવા (Crash) નું અસલી મૂળ કારણ હતું!

મૂળ એપમાં ડેવલપરે `DashboardActivity`, `DashboardActivity$88` ("Start Checking" બટન), `MainActivity`, અને `SplActivity` ની અંદર કુલ **૧૦૩ જગ્યાએ `finishAffinity()`** અને **`System.exit()`** મૂકેલા હતા. જ્યારે પણ એપમાં સિગ્નેચર બદલાય, રૂટ/MT Manager ડિટેક્ટ થાય, ત્યારે તે તરત જ `finishAffinity()` કોલ કરીને એપ બંધ કરી દેતું હતું.

હવે **તમામે તમામ ૧૦૩ `finishAffinity()` અને `System.exit()` કાયમ માટે નિષ્ક્રિય (Neutralize) કરી દેવામાં આવ્યા છે**, જેથી એપ ક્યારેય બંધ કે બહાર ફેંકી ન શકે! સાથે જ તમારા **`DT.ZIP`** માં રહેલી તમામ સુવિધાઓ અને ટેલિગ્રામ લિંક પણ સાચવી લેવામાં આવી છે.

---

## ૧. નવી તૈયાર DEX ફાઇલો ડાઉનલોડ કરો

નીચે આપેલી લિંક્સ પરથી ૧૦૦% ફિક્સ થયેલી નવી ફાઇલો ડાઉનલોડ કરો:

### વિકલ્પ ૧: GitHub Release (સૌથી સરળ):
👉 **[GitHub Release v6.8.0013-dex ખોલો](https://github.com/iam63bhai83/IVAR-MODS_6.8.0013.apk/releases/tag/v6.8.0013-dex)**
- **`classes88.dex` (1.3 MB)**: [ડાઉનલોડ કરો](https://github.com/iam63bhai83/IVAR-MODS_6.8.0013.apk/releases/download/v6.8.0013-dex/classes88.dex)
- **`classes89.dex` (1.9 MB)**: [ડાઉનલોડ કરો](https://github.com/iam63bhai83/IVAR-MODS_6.8.0013.apk/releases/download/v6.8.0013-dex/classes89.dex)

### વિકલ્પ ૨: Repository માંથી Direct Raw Download:
- **`classes88.dex`**: [Direct Download Link](https://github.com/iam63bhai83/IVAR-MODS_6.8.0013.apk/raw/main/precompiled_dex/classes88.dex)
- **`classes89.dex`**: [Direct Download Link](https://github.com/iam63bhai83/IVAR-MODS_6.8.0013.apk/raw/main/precompiled_dex/classes89.dex)
*(રિપોઝિટરી ફોલ્ડર: [precompiled_dex/](https://github.com/iam63bhai83/IVAR-MODS_6.8.0013.apk/tree/main/precompiled_dex))*

---

## ૨. MT Manager વડે APK માં નાખવાની રીત (૧ મિનિટ)

1. **MT Manager** ખોલો.
2. ડાબી બાજુ તમારા **`Download`** ફોલ્ડરમાં જાઓ જ્યાં તમે બંને ફાઇલો (`classes88.dex` અને `classes89.dex`) ડાઉનલોડ કરી છે.
3. જમણી બાજુ તમારા `Download` માં રહેલી મૂળ APK **`IVAR MODS_6.8.0013.apk`** પર ક્લિક કરો અને **`View`** (આર્કાઇવ તરીકે જુઓ) પર ટેપ કરો.
4. ડાબી બાજુથી બંને નવી ફાઇલો (**`classes88.dex`** અને **`classes89.dex`**) સિલેક્ટ કરીને અંદર **Add / Replace** (ઉમેરો / બદલો) કરી દો.
5. APK ની અંદરનું **`META-INF`** ફોલ્ડર સિલેક્ટ કરીને **Delete** કરો (જેથી જૂની સહી નીકળી જાય).
6. બેક આવીને APK પર લોંગ-પ્રેસ કરો અને **`Sign`** (સાઇન કરો) પર ક્લિક કરો.
7. બનેલી નવી સાઇન થયેલી APK ઇન્સ્ટોલ કરી લો!

---

## ૩. આ નવા અપડેટમાં શું-શું ફિક્સ થયું છે?

1. **૧૦૩ `finishAffinity()` અને `System.exit()` બંધ**:
   - `DashboardActivity.initializeLogic()` અને `$88` (Start Checking) માં રહેલા તમામ કિલ સ્વીચ નિષ્ક્રિય કરી દીધા છે.
   - હવે તમે કોઈ પણ બટન દબાવશો તો પણ એપ ક્યારેય બંધ કે બહાર નહીં ફેંકે!
2. **`onCreate` માંથી `finish()` હટાવ્યું**:
   - `MainActivity` અને `SplActivity` માંથી `finish()` હટાવી દીધું છે જેથી એન્ડ્રોઇડ ટાસ્ક ક્યારેય મરે નહીં.
3. **DT.ZIP ની તમામ વસ્તુઓ અને ટેલિગ્રામ લિંક કાયમ**:
   - તમારા `DT.ZIP` ની ટેલિગ્રામ લિંક્સ (`https://t.me/+Y55ZXBe9pWAzMDA1`) અને તમામ ફીચર્સ સંપૂર્ણ જાળવી રાખ્યા છે.
4. **ઓફલાઇન પ્રેડિક્શન અને VIP અનલૉક**:
   - ૩૦ સેકન્ડ અને ૧ મિનિટ વિંગો પ્રેડિક્શન્સ સર્વર વગર પણ સીધા ચાલશે.
