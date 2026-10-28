# שלב 14 — קריית גת: הסניף של IPv6

<div dir="rtl">

> ⏱ ‏4 שיעורים · 🎯 דרישות משרד החינוך 7, ‏10 (overload), ‏17, ‏20.x, ‏22.11 (בחירת התלמיד)\
> 📁 מתחילים מ: `my-work/step13.pkt`\
> 💾 שומרים בשם: `my-work/step14.pkt`

</div>

<div dir="rtl">

> ✅ **לפני שמתחילים:** כל הסעיפים בנקודת הביקורת של שלב 13 מסומנים, ועשיתם את
> תרגיל ה-🔁 שלו בפרויקט שלכם. אל תדלגו על שלבים — כל שלב בנוי על הקובץ של השלב הקודם.

</div>

## 🗺 המשימות שלכם בשלב הזה
**שיעור 1 — יסודות IPv6 ובנייה**
- [ ] **משימה 1** — חימום IPv6 על דף (15 דקות)
- [ ] **משימה 2** — פותחים את שלב 13, שומרים בשם שלב 14, מציבים את המכשירים (15 דקות)
- [ ] **משימה 3** — מחברים את הסניף בכבלים (15 דקות)
- [ ] **משימה 4** — גורמים למתגים לדבר IPv6 (תבנית SDM) ‏(10 דקות)

**שיעור 2 — מתגי ה-distribution**
- [ ] **משימה 5** — ‏DIST1, חלק 1: הקשחה, ‏VLANים, ‏STP, ‏trunks ‏(10 דקות)
- [ ] **משימה 6** — ‏DIST1, חלק 2: ‏DHCPv6, ‏OSPFv3, קישור כלפי מעלה, שערי המשתמשים (15 דקות)
- [ ] **משימה 7** — ‏DIST1, חלק 3: ‏MGMT, שרתים, ‏VLAN מדור קודם, ניהול (10 דקות)
- [ ] **משימה 8** — ‏DIST2: תמונת המראה של DIST1 ‏(25 דקות)

**שיעור 3 — ‏access, נתב קצה, שרתים**
- [ ] **משימה 9** — שלושת מתגי ה-access ‏(25 דקות)
- [ ] **משימה 10** — ‏SW-KG-SRV ‏(5 דקות)
- [ ] **משימה 11** — ‏R-KG-EDGE והנתיב אצל הספק (20 דקות)
- [ ] **משימה 12** — שרתים ומכשירי קצה (IPv6 לחיצה אחרי לחיצה) (20 דקות)

**שיעור 4 — בודקים**
- [ ] **משימה 13** — בדיקות (15 דקות)
- [ ] **משימה 14** — ‏failover של HSRPv6 ‏(10 דקות)
- [ ] **תרגילים** א ו-ב
- [ ] **🛠 הפרויקט שלכם**

## מה יהיה לכם בסוף השלב
הסניף השלישי מריץ **IPv6** לכל המשתמשים, השרתים והניהול: כתובות אוטומטיות (SLAAC + ‏stateless
DHCPv6), ניתוב **OSPFv3**, ‏**HSRP ל-IPv6**. ‏VLAN ‏IPv4 קטן אחד "מדור קודם" (legacy) מגיע לאינטרנט דרך
**PAT ‏(overload)** — סוג ה-NAT השלישי.

```
                          R-ISPC-PE (ISP-C, dual-stack)
                                │ 2001:DB8:C:1::/64 + 200.3.1.0/30
                           R-KG-EDGE    (OSPFv3, static defaults, PAT for VLAN 199)
                    Gi0/0 ╱         ╲ Gi0/2
          SWL3-KG-DIST1 ════ trunk ════ SWL3-KG-DIST2      OSPFv3 area 0, HSRPv6
           ╱    │    │   ╲            ╱    │    │   ╲
        ACC1  ACC2  ACC3  SW-KG-SRV   (each with a cable to BOTH DIST switches)
```
(‏R-KG-EDGE מחובר ל-ISP-C ‏(dual-stack) ומריץ OSPFv3, נתיבי ברירת מחדל סטטיים ו-PAT ל-VLAN 199. מתחתיו
‏DIST1 ו-DIST2, מחוברים ב-trunk, עם OSPFv3 ‏area 0 ו-HSRPv6. לכל מתג access ולמתג השרתים יש כבל לשני
מתגי ה-DIST.)

## חלק 1 — קודם מבינים (בשפה פשוטה)

### 1.1 למה IPv6?
ל-IPv4 יש בערך 4 מיליארד כתובות — והעולם גמר אותן. בגלל זה צריך כתובות פרטיות ו-NAT. ל-**IPv6** יש
340 אנדסיליון כתובות (מספר בן 39 ספרות): לכל מכשיר יכולה להיות כתובת **ציבורית וייחודית**. לא צריך
NAT. משרד החינוך דורש שסניף אחד יהיה כולו IPv6 (דרישה 7).

### 1.2 איך קוראים כתובת IPv6
‏128 ביט, שנכתבים כ-**8 קבוצות** של 4 ספרות הקסדצימליות (0–9, ‏A–F), מופרדות ב-‎`:`‎.
```
2001:0DB8:0030:0031:0000:0000:0000:0002
```
שני כללי קיצור:
1. משמיטים **אפסים מובילים** בכל קבוצה: ‎`0DB8 → DB8`, ‏‎`0030 → 30`, ‏‎`0002 → 2`.
2. מחליפים רצף **אחד** של קבוצות שכולן אפסים ב-‎`::`‎.
```
2001:DB8:30:31::2          (the same address)
```
(אותה כתובת.)
- ‏‎`/64` — כמו ‎`/24` ב-IPv4, אבל זה התקן ל**כל** רשת מקומית: ‏64 הביטים הראשונים הם הרשת, ו-64
  האחרונים הם המכשיר.
- ‏‎`2001:DB8::/32` הוא הטווח ששמור לתיעוד ולמעבדות (כמו 192.0.2.x).

### 1.3 התוכנית שלנו: מספר ה-VLAN נמצא בכתובת
לקריית גת שייך ‎`2001:DB8:30::/48`. כל VLAN מקבל ‎/64 שה**קבוצה הרביעית** שלו = **מספר ה-VLAN**:
‏VLAN 31 ‏←‏ ‎`2001:DB8:30:31::/64`, ‏VLAN 99 ‏←‏ ‎`2001:DB8:30:99::/64`. קל לקרוא.

<div dir="rtl">

| ‎‏VLAN | שם | ‎‏Prefix | ‎‏DIST1 | ‎‏DIST2 | שער |
|---|---|---|---|---|---|
| ‎31 | ‎FAB-OPS | ‎2001:DB8:30:31::/64 | ‎::2 | ‎::3 | ‎FE80::1 |
| ‎32 | ‎QUALITY | ‎2001:DB8:30:32::/64 | ‎::2 | ‎::3 | ‎FE80::1 |
| ‎33 | ‎MAINTENANCE | ‎2001:DB8:30:33::/64 | ‎::2 | ‎::3 | ‎FE80::1 |
| ‎34 | ‎SAFETY | ‎2001:DB8:30:34::/64 | ‎::2 | ‎::3 | ‎FE80::1 |
| ‎35 | ‎PLANNING | ‎2001:DB8:30:35::/64 | ‎::2 | ‎::3 | ‎FE80::1 |
| ‎36 | ‎TRAINING | ‎2001:DB8:30:36::/64 | ‎::2 | ‎::3 | ‎FE80::1 |
| ‎99 | ‎MGMT | ‎2001:DB8:30:99::/64 | ‎::2 | ‎::3 | ‎FE80::1 |
| ‎100 | ‎SERVERS | ‎2001:DB8:30:100::/64 | ‎::2 | ‎::3 | ‎FE80::1 |
| ‎199 | ‎LEGACY-IPV4 | ‎**10.30.199.0/24** | ‎.1 | ‎— | ‎10.30.199.1 |

</div>

### 1.4 כתובות link-local — ‏`FE80::`‎
לכל ממשק IPv6 יש אוטומטית כתובת **link-local** שמתחילה ב-`FE80`. היא עובדת רק על הקישור שלה (אף פעם
לא מנותבת). ‏IPv6 משתמש בהן לגילוי שכנים וככתובת של **שער ברירת המחדל**. אנחנו קובעים את השער
הווירטואלי לכתובת הקלה `FE80::1` בכל VLAN.

### 1.5 איך מחשב מקבל כתובת IPv6 בלי להקליד — SLAAC
1. הנתב שולח **Router Advertisements ‏(RA)**: "הרשת כאן היא 2001:DB8:30:31::/64, ואני השער שלך".
2. המחשב בונה לעצמו כתובת: ה-prefix + חלק מכשיר שהוא מייצר בעצמו.
זה **SLAAC** ‏(Stateless Address Auto-Configuration). לא צריך שרת DHCP בשביל הכתובת.

אבל SLAAC לא אומר למחשב מהו שרת ה-**DNS**. לכן מוסיפים **stateless DHCPv6**: ה-RA נושא דגל ("O-flag" =
‏*other information*) שאומר למחשבים: "בקשו מ-DHCPv6 את התוספות (DNS, דומיין)".
‏←‏ הבחירה של קריית גת ל-DHCP (דרישה 22.11, "סניף שלישי: בחירת התלמיד") = **SLAAC + ‏stateless DHCPv6
במתגי ה-distribution**.

### 1.6 ‏OSPFv3 ו-HSRP ל-IPv6
- **‏OSPFv3** = ‏OSPF ל-IPv6. אותם רעיונות (שכנים, מפה, areas); הגדרה אחרת: מפעילים אותו **על כל ממשק**
  (`ipv6 ospf 1 area 0`), לא עם שורות `network`. הוא צריך router-ID שנכתב כמו כתובת IPv4 ‏(3.3.3.1) —
  אין כתובת IPv4 שאפשר "לשאול" ממנה.
- **‏HSRP ל-IPv6** — רק גרסה 2; השער המשותף הוא כתובת **link-local** ‏(`FE80::1`).

### 1.7 שונה בכוונה

<div dir="rtl">

| | חיפה | ירושלים | **קריית גת** |
|---|---|---|---|
| ‎‏VTP | ‎‏server/client | ‎‏server/client | **‏transparent** (כל מתג מחזיק את ה-VLANים שלו) |
| ‎‏EtherChannel | ‎‏LACP | ‎‏PAgP | **אין** (trunk יחיד בין מתגי ה-DIST) |
| ‎‏NAT | ‎‏static ‏(+PAT) | ‎‏dynamic | ‎**‏PAT ‏(overload)** |

</div>

### 1.8 למה עדיין יש קצת IPv4
‏NAT קיים רק ב-IPv4. משרד החינוך מבקש סניף IPv6 אחד **וגם** NAT בכל סניף. התשובה שלנו: **‏VLAN 199**
אחד "מדור קודם" למכשירים ישנים שמדברים רק IPv4 (קוראי כרטיסים, מצלמות). רק הוא משתמש ב-PAT כדי להגיע
לאינטרנט. כל השאר IPv6. **אשרו את הפרשנות הזו עם המנחה שלכם.**

### 1.9 כתובות הקישורים

<div dir="rtl">

| קישור | ‎‏IPv6 | ‎‏IPv4 |
|---|---|---|
| ‎R-KG-EDGE Gi0/0 ↔ DIST1 Gi1/1/1 | ‎2001:DB8:30:FF01::1 / ::2 (/64) | ‎10.30.4.1 / 10.30.4.2 (/30) |
| ‎R-KG-EDGE Gi0/2 ↔ DIST2 Gi1/1/1 | ‎2001:DB8:30:FF02::1 / ::2 (/64) | ‎— |
| ‎R-KG-EDGE Gi0/1 ↔ R-ISPC-PE Gi0/1 | ‎2001:DB8:C:1::2 / ::1 (/64) | ‎200.3.1.2 / 200.3.1.1 (/30) |

</div>

<div dir="rtl">

| מכשיר | ‏router-ID של OSPFv3 | כתובת ניהול IPv6 |
|---|---|---|
| ‎R-KG-EDGE | ‎3.3.3.1 | ‎2001:DB8:30:FF01::1 |
| ‎SWL3-KG-DIST1 / DIST2 | ‎3.3.3.2 / 3.3.3.3 | ‎2001:DB8:30:99::2 / ::3 |
| ‎SW-KG-ACC1 / ACC2 / ACC3 / SRV | ‎— | ‎2001:DB8:30:99::11 / ::12 / ::13 / ::14 |
| ‎PC-KG-ADMIN-01 | ‎— | ‎2001:DB8:30:99::100 |

</div>

<div dir="rtl">

> ⌨️ **מקלידים IPv6:** אותיות גדולות או קטנות — שתיהן עובדות (`FE80::1` = `fe80::1`). קראו כל
> כתובת קבוצה אחרי קבוצה לפני שלוחצים Enter — ‏‎`:`‎ חסר הוא הטעות מספר 1 בשלב הזה.

</div>

---

## משימה 1 — חימום IPv6 על דף
קצרו את הכתובות האלה (התשובות מוסתרות):

1. ‏‎`2001:0DB8:0030:0099:0000:0000:0000:0011`
2. ‏‎`2001:0DB8:000C:0001:0000:0000:0000:0002`
3. ‏`FE80:0000:0000:0000:0000:0000:0000:0001`

<details dir="rtl"><summary>✔ תשובות</summary>

1. ‏‎`2001:DB8:30:99::11`
2. ‏‎`2001:DB8:C:1::2`
3. ‏`FE80::1`
</details>

4. איזה VLAN זה ‎`2001:DB8:30:35::/64`? איזו מחלקה?

<details dir="rtl"><summary>✔ תשובה</summary>

הקבוצה הרביעית היא ‎`35` ‏←‏ ‏VLAN 35, ‏PLANNING.
</details>

---

## משימה 2 — פותחים את שלב 13, שומרים בשם שלב 14, מציבים את המכשירים (איך? ‏←‏ M1, ‏M2, ‏M4, ‏M8)
‏**File → Open** ‏←‏ `my-work/step13.pkt` ‏←‏ **File → Save As** ‏←‏ `my-work/step14.pkt`.
ציירו מלבן עם התווית `KIRYAT GAT BRANCH (IPv6)`‎.

<div dir="rtl">

| דגם | ‎Display Name |
|---|---|
| ‎2911 | ‎`R-KG-EDGE` |
| ‎3650-24PS | ‎`SWL3-KG-DIST1`, `SWL3-KG-DIST2` |
| ‎2960 | ‎`SW-KG-ACC1`, `SW-KG-ACC2`, `SW-KG-ACC3`, `SW-KG-SRV` |
| ‎Server ×4 | ‎`SRV-KG-DNS`, `SRV-KG-MAIL`, `SRV-KG-SYSLOG`, `SRV-KG-AAA` |
| ‎PC ×12 | ‎`PC-KG-FAB-01/02`, `PC-KG-QUA-01/02`, `PC-KG-MNT-01/02`, `PC-KG-SAF-01/02`, `PC-KG-PLN-01/02`, `PC-KG-TRN-01/02` |
| ‎PC ×3 | ‎`PC-KG-ADMIN-01`, `PC-KG-LEGACY-01`, `PC-KG-LEGACY-02` |
| ‎Printer ×2 | ‎`PRN-KG-ACC2-01`, `PRN-KG-ACC3-01` |
| Server ×1 — מציבים אותו ליד **SW-ISPC-HOME** (הרשת הביתית של ISP-C) | ‎`SRV-ISPC-WEB6` |

</div>

⚠️ ספקי כוח (M8):
- [ ] ‏DIST1
- [ ] ‏DIST2

---

## משימה 3 — מחברים את הסניף בכבלים (איך? ‏←‏ M5)

### 3א — ציוד רשת

<div dir="rtl">

| ‎# | כבל | לוחצים קודם על | פורט | לוחצים אחר כך על | פורט |
|---|---|---|---|---|---|
| ‎1 | ‎Cross-Over | ‎SWL3-KG-DIST1 | ‎Gi1/0/1 | ‎SW-KG-ACC1 | ‎Gi0/1 |
| ‎2 | ‎Cross-Over | ‎SWL3-KG-DIST2 | ‎Gi1/0/1 | ‎SW-KG-ACC1 | ‎Gi0/2 |
| ‎3 | ‎Cross-Over | ‎SWL3-KG-DIST1 | ‎Gi1/0/2 | ‎SW-KG-ACC2 | ‎Gi0/1 |
| ‎4 | ‎Cross-Over | ‎SWL3-KG-DIST2 | ‎Gi1/0/2 | ‎SW-KG-ACC2 | ‎Gi0/2 |
| ‎5 | ‎Cross-Over | ‎SWL3-KG-DIST1 | ‎Gi1/0/3 | ‎SW-KG-ACC3 | ‎Gi0/1 |
| ‎6 | ‎Cross-Over | ‎SWL3-KG-DIST2 | ‎Gi1/0/3 | ‎SW-KG-ACC3 | ‎Gi0/2 |
| ‎7 | ‎Cross-Over | ‎SWL3-KG-DIST1 | ‎Gi1/0/4 | ‎SW-KG-SRV | ‎Gi0/1 |
| ‎8 | ‎Cross-Over | ‎SWL3-KG-DIST2 | ‎Gi1/0/4 | ‎SW-KG-SRV | ‎Gi0/2 |
| ‎9 | ‎Cross-Over | ‎SWL3-KG-DIST1 | ‎Gi1/0/24 | ‎SWL3-KG-DIST2 | ‎Gi1/0/24 |
| ‎10 | ‎Straight | ‎SWL3-KG-DIST1 | ‎Gi1/1/1 | ‎R-KG-EDGE | ‎Gi0/0 |
| ‎11 | ‎Straight | ‎SWL3-KG-DIST2 | ‎Gi1/1/1 | ‎R-KG-EDGE | ‎Gi0/2 |
| ‎12 | ‎Cross-Over | ‎R-KG-EDGE | ‎Gi0/1 | ‎R-ISPC-PE | ‎Gi0/1 |
| ‎13 | ‎Straight | ‎SRV-ISPC-WEB6 | ‎Fa0 | ‎SW-ISPC-HOME | ‎Fa0/2 |

</div>

### 3ב — מכשירי קצה (כולם Straight-Through)

<div dir="rtl">

| מכשיר | מתג | פורט |
|---|---|---|
| ‎PC-KG-FAB-01 / 02 | ‎SW-KG-ACC1 | ‎Fa0/1 / Fa0/2 |
| ‎PC-KG-QUA-01 / 02 | ‎SW-KG-ACC1 | ‎Fa0/11 / Fa0/12 |
| ‎PC-KG-LEGACY-01 / 02 | ‎SW-KG-ACC1 | ‎Fa0/21 / Fa0/22 |
| ‎PC-KG-ADMIN-01 | ‎SW-KG-ACC1 | ‎Fa0/23 |
| ‎PC-KG-MNT-01 / 02 | ‎SW-KG-ACC2 | ‎Fa0/1 / Fa0/2 |
| ‎PC-KG-SAF-01 / 02 | ‎SW-KG-ACC2 | ‎Fa0/11 / Fa0/12 |
| ‎PRN-KG-ACC2-01 | ‎SW-KG-ACC2 | ‎Fa0/21 |
| ‎PC-KG-PLN-01 / 02 | ‎SW-KG-ACC3 | ‎Fa0/1 / Fa0/2 |
| ‎PC-KG-TRN-01 / 02 | ‎SW-KG-ACC3 | ‎Fa0/11 / Fa0/12 |
| ‎PRN-KG-ACC3-01 | ‎SW-KG-ACC3 | ‎Fa0/21 |
| ‎SRV-KG-DNS / MAIL / SYSLOG / AAA | ‎SW-KG-SRV | ‎Fa0/1 / 2 / 3 / 4 |

</div>

✅ ‏13 + 21 כבלים. ‏**File → Save**.

---

## משימה 4 — גורמים למתגים לדבר IPv6 (תבנית SDM)
🧠 **למה:** חלק מהמתגים ב-PT מתחילים עם תבנית זיכרון ש**אין בה מקום ל-IPv6**. אז כל פקודת
‏`ipv6 ...`‎ עונה ‎`% Invalid input`.

### 4א — בודקים 3650 אחד ו-2960 אחד
1. ‏**SWL3-KG-DIST1** ‏←‏ CLI ‏←‏ **Enter** ‏←‏ `enable` ‏←‏ `configure terminal` ‏←‏ `ipv6 unicast-routing`.
2. ‏**SW-KG-ACC1** ‏←‏ CLI ‏←‏ **Enter** ‏←‏ `enable` ‏←‏ `configure terminal` ‏←‏ `interface vlan 1` ‏←‏
   ‏`ipv6 address 2001:DB8::1/64`.

✅ **שתיהן התקבלו?** ממשיכים. ב-SW-KG-ACC1 מוחקים את כתובת הבדיקה: `no ipv6 address 2001:DB8::1/64`
‏←‏ `end`. מדלגים על 4ב.

❌ **נדחו?** עושים את 4ב ב**כל** מתג של הסניף הזה (6 מתגים).

### 4ב — משנים את התבנית (רק אם 4א נדחה), פעם אחת לכל מתג
⌨️ מקלידים:
```
configure terminal
sdm prefer dual-ipv4-and-ipv6 default
end
copy running-config startup-config
reload
```
לוחצים **Enter** כדי לאשר את האתחול. מחכים שהמתג יעלה שוב (לוחצים Fast Forward Time).
סמנו:
- [ ] ‏DIST1
- [ ] ‏DIST2
- [ ] ‏ACC1
- [ ] ‏ACC2
- [ ] ‏ACC3
- [ ] ‏SRV

---

## משימה 5 — ‏DIST1, חלק 1: הקשחה, ‏VLANים, ‏STP, ‏trunks
👉 **איפה:** ‏**SWL3-KG-DIST1** ‏←‏ CLI ‏←‏ `Switch>`‎ (או `Switch(config)#`‎ אם הגעתם ממשימה 4 —
קודם מקלידים `end`).

⌨️ מקלידים:
```
enable
configure terminal
hostname SWL3-KG-DIST1
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
ip routing
ipv6 unicast-routing
vtp mode transparent
vlan 31
 name FAB-OPS
vlan 32
 name QUALITY
vlan 33
 name MAINTENANCE
vlan 34
 name SAFETY
vlan 35
 name PLANNING
vlan 36
 name TRAINING
vlan 99
 name MGMT
vlan 100
 name SERVERS
vlan 199
 name LEGACY-IPV4
vlan 998
 name NATIVE
vlan 999
 name PARKING
 exit
spanning-tree mode rapid-pvst
spanning-tree vlan 31-36,99,100,199 root primary
interface range gi1/0/1 - 4
 description TRUNK to access switch
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 31-36,99,100,199,998
 switchport nonegotiate
 spanning-tree guard root
 no shutdown
interface gi1/0/24
 description TRUNK to SWL3-KG-DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 31-36,99,100,199,998
 switchport nonegotiate
 no shutdown
interface range gi1/0/5 - 23
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 exit
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`ipv6 unicast-routing` | "נתב IPv6 ושלח Router Advertisements" |

</div>

🔍 **בודקים עכשיו:** ‏`do show vlan brief` ‏←‏ ‏11 VLANים.

---

## משימה 6 — ‏DIST1, חלק 2: ‏DHCPv6, ‏OSPFv3, קישור כלפי מעלה, שערי המשתמשים
👉 **איפה:** ‏DIST1, שורת הפקודה `SWL3-KG-DIST1(config)#`‎.

### 6א — מאגר stateless DHCPv6, תהליך OSPFv3, קישור כלפי מעלה
⌨️ מקלידים:
```
ipv6 dhcp pool KG-STATELESS
 dns-server 2001:DB8:30:100::10
 domain-name intel.lab
 exit
ipv6 router ospf 1
 router-id 3.3.3.2
 exit
interface gi1/1/1
 description to R-KG-EDGE Gi0/0
 no switchport
 ip address 10.30.4.2 255.255.255.252
 ipv6 address 2001:DB8:30:FF01::2/64
 ipv6 ospf 1 area 0
 no shutdown
 exit
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`ipv6 dhcp pool KG-STATELESS` + `dns-server` | התוספות ש-stateless DHCPv6 מחלק |
| ‎`ipv6 router ospf 1` / `router-id 3.3.3.2` | הפעל OSPFv3, עם המזהה הזה |
| ‎`ipv6 address 2001:DB8:30:FF01::2/64` | כתובת ה-IPv6 של הממשק הזה |
| ‎`ipv6 ospf 1 area 0` | "הממשק הזה מצטרף לתהליך OSPFv3 מספר 1, ‏area 0" |

</div>

<div dir="rtl">

> לקישור כלפי מעלה יש גם כתובת IPv4 ‏(10.30.4.2) — רק בשביל ה-VLAN מדור קודם 199.

</div>

### 6ב — השערים של שש ה-VLANים של המשתמשים
כל בלוק הוא אותן 9 שורות; רק **מספר ה-VLAN** משתנה (ב-4 מקומות: `vlan 31`, ‏‎`:31::2`,
‏`standby 31` ×3).

⌨️ מקלידים:
```
interface vlan 31
 description GW FAB-OPS
 ipv6 address 2001:DB8:30:31::2/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 31 ipv6 FE80::1
 standby 31 priority 110
 standby 31 preempt
 no shutdown
interface vlan 32
 description GW QUALITY
 ipv6 address 2001:DB8:30:32::2/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 32 ipv6 FE80::1
 standby 32 priority 110
 standby 32 preempt
 no shutdown
interface vlan 33
 description GW MAINTENANCE
 ipv6 address 2001:DB8:30:33::2/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 33 ipv6 FE80::1
 standby 33 priority 110
 standby 33 preempt
 no shutdown
interface vlan 34
 description GW SAFETY
 ipv6 address 2001:DB8:30:34::2/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 34 ipv6 FE80::1
 standby 34 priority 110
 standby 34 preempt
 no shutdown
interface vlan 35
 description GW PLANNING
 ipv6 address 2001:DB8:30:35::2/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 35 ipv6 FE80::1
 standby 35 priority 110
 standby 35 preempt
 no shutdown
interface vlan 36
 description GW TRAINING
 ipv6 address 2001:DB8:30:36::2/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 36 ipv6 FE80::1
 standby 36 priority 110
 standby 36 preempt
 no shutdown
 exit
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`ipv6 nd other-config-flag` | מדליק את ה-**O-flag** ב-RAs: "בקש מ-DHCPv6 את ה-DNS" |
| ‎`ipv6 dhcp server KG-STATELESS` | "ענה לשאלות DHCPv6 ב-VLAN הזה" |
| ‎`standby 31 ipv6 FE80::1` | ‏HSRP ל-IPv6: שער משותף FE80::1 |

</div>

❌ **‏`standby 31 ipv6 FE80::1` נדחה?** השתמשו במקום זה ב-`standby 31 ipv6 autoconfig`, וראו "אם משהו
לא עובד".

---

## משימה 7 — ‏DIST1, חלק 3: ‏MGMT, שרתים, ‏VLAN מדור קודם, ניהול

### 7א — ‏MGMT ו-SERVERS (שם הכתובות סטטיות, ולכן אין DHCPv6)
⌨️ מקלידים:
```
interface vlan 99
 description GW MGMT
 ipv6 address 2001:DB8:30:99::2/64
 ipv6 ospf 1 area 0
 standby version 2
 standby 99 ipv6 FE80::1
 standby 99 priority 110
 standby 99 preempt
 no shutdown
interface vlan 100
 description GW SERVERS (+ OSPFv3 peering DIST1-DIST2)
 ipv6 address 2001:DB8:30:100::2/64
 ipv6 ospf 1 area 0
 standby version 2
 standby 100 ipv6 FE80::1
 standby 100 priority 110
 standby 100 preempt
 no shutdown
```

### 7ב — ה-VLAN מדור קודם של IPv4 (רק ב-DIST1) ו-OSPFv3 passive
⌨️ מקלידים:
```
interface vlan 199
 description GW LEGACY-IPV4
 ip address 10.30.199.1 255.255.255.0
 no shutdown
 exit
ip route 0.0.0.0 0.0.0.0 10.30.4.1
ipv6 router ospf 1
 passive-interface default
 no passive-interface gi1/1/1
 no passive-interface vlan 100
 exit
```

### 7ג — ניהול (רשימת אורחים ב-IPv6)
⌨️ מקלידים:
```
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
‏←‏ עונים **‎`1024`** ‏←‏ ואז:
```
ip ssh version 2
login block-for 120 attempts 3 within 60
ipv6 access-list MGMT6
 permit ipv6 2001:DB8:30:99::/64 any
 deny ipv6 any any log
 exit
line vty 0 15
 transport input ssh
 login local
 ipv6 access-class MGMT6 in
 exec-timeout 5 0
line console 0
 login local
 logging synchronous
 exit
service timestamps log datetime msec
logging host ipv6 2001:DB8:30:100::12
ntp server 200.1.10.4
 end
copy running-config startup-config
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`ipv6 access-class MGMT6 in` | רשימת האורחים של IPv6 לקווי ה-VTY |
| ‎`ntp server 200.1.10.4` | ‏NTP של הסניף: מסתנכרן לשרת ה-NTP הציבורי של חיפה (static NAT, שלב 12) ב-IPv4 |

</div>

<div dir="rtl">

> ‏`logging host ipv6 ...`‎ נדחה? נסו `logging 2001:DB8:30:100::12`.

</div>

🔍 **בודקים עכשיו:** ‏`show ipv6 interface brief` ‏←‏ ‏Vlan31–36, ‏99, ‏100, לכל אחד ‎`2001:DB8:30:x::2`
(ושורת `FE80::`‎). ייתכן שהם `down` עד שמגדירים את מתגי ה-access.

---

## משימה 8 — ‏DIST2: תמונת המראה של DIST1
👉 **איפה:** ‏**SWL3-KG-DIST2** ‏←‏ CLI.

<div dir="rtl">

| | ‎DIST1 | ‎**DIST2** |
|---|---|---|
| ‎hostname | ‎SWL3-KG-DIST1 | ‎**SWL3-KG-DIST2** |
| ‎`ip routing` | כן (בשביל VLAN 199) | **לא** |
| ‎STP | ‎root **primary** | ‎root **secondary** |
| router-id של OSPFv3 | ‎3.3.3.2 | ‎**3.3.3.3** |
| ‎Gi1/1/1 | ‎10.30.4.2 + 2001:DB8:30:FF01::2 | **רק 2001:DB8:30:FF02::2** |
| כתובות SVI | ‎`::2` | **‎`::3`** |
| עדיפות HSRP | ‎110 | ‎**90** |
| ‏SVI של VLAN 199 + נתיב ברירת מחדל IPv4 | כן | **לא** |
| שורת שרת NTP | כן | **לא** |

</div>

### 8א — הקשחה, ‏VLANים, ‏STP, ‏trunks
⌨️ מקלידים:
```
enable
configure terminal
hostname SWL3-KG-DIST2
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
ipv6 unicast-routing
vtp mode transparent
vlan 31
 name FAB-OPS
vlan 32
 name QUALITY
vlan 33
 name MAINTENANCE
vlan 34
 name SAFETY
vlan 35
 name PLANNING
vlan 36
 name TRAINING
vlan 99
 name MGMT
vlan 100
 name SERVERS
vlan 199
 name LEGACY-IPV4
vlan 998
 name NATIVE
vlan 999
 name PARKING
 exit
spanning-tree mode rapid-pvst
spanning-tree vlan 31-36,99,100,199 root secondary
interface range gi1/0/1 - 4
 description TRUNK to access switch
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 31-36,99,100,199,998
 switchport nonegotiate
 spanning-tree guard root
 no shutdown
interface gi1/0/24
 description TRUNK to SWL3-KG-DIST1
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 31-36,99,100,199,998
 switchport nonegotiate
 no shutdown
interface range gi1/0/5 - 23
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 exit
```

### 8ב — ‏DHCPv6, ‏OSPFv3, קישור כלפי מעלה
⌨️ מקלידים:
```
ipv6 dhcp pool KG-STATELESS
 dns-server 2001:DB8:30:100::10
 domain-name intel.lab
 exit
ipv6 router ospf 1
 router-id 3.3.3.3
 exit
interface gi1/1/1
 description to R-KG-EDGE Gi0/2
 no switchport
 ipv6 address 2001:DB8:30:FF02::2/64
 ipv6 ospf 1 area 0
 no shutdown
```

### 8ג — שערים
⌨️ מקלידים:
```
interface vlan 31
 description GW FAB-OPS
 ipv6 address 2001:DB8:30:31::3/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 31 ipv6 FE80::1
 standby 31 priority 90
 standby 31 preempt
 no shutdown
interface vlan 32
 description GW QUALITY
 ipv6 address 2001:DB8:30:32::3/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 32 ipv6 FE80::1
 standby 32 priority 90
 standby 32 preempt
 no shutdown
interface vlan 33
 description GW MAINTENANCE
 ipv6 address 2001:DB8:30:33::3/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 33 ipv6 FE80::1
 standby 33 priority 90
 standby 33 preempt
 no shutdown
interface vlan 34
 description GW SAFETY
 ipv6 address 2001:DB8:30:34::3/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 34 ipv6 FE80::1
 standby 34 priority 90
 standby 34 preempt
 no shutdown
interface vlan 35
 description GW PLANNING
 ipv6 address 2001:DB8:30:35::3/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 35 ipv6 FE80::1
 standby 35 priority 90
 standby 35 preempt
 no shutdown
interface vlan 36
 description GW TRAINING
 ipv6 address 2001:DB8:30:36::3/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 36 ipv6 FE80::1
 standby 36 priority 90
 standby 36 preempt
 no shutdown
interface vlan 99
 description GW MGMT
 ipv6 address 2001:DB8:30:99::3/64
 ipv6 ospf 1 area 0
 standby version 2
 standby 99 ipv6 FE80::1
 standby 99 priority 90
 standby 99 preempt
 no shutdown
interface vlan 100
 description GW SERVERS (+ OSPFv3 peering DIST1-DIST2)
 ipv6 address 2001:DB8:30:100::3/64
 ipv6 ospf 1 area 0
 standby version 2
 standby 100 ipv6 FE80::1
 standby 100 priority 90
 standby 100 preempt
 no shutdown
 exit
ipv6 router ospf 1
 passive-interface default
 no passive-interface gi1/1/1
 no passive-interface vlan 100
 exit
```

### 8ד — ניהול
⌨️ מקלידים:
```
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
‏←‏ עונים **‎`1024`** ‏←‏ ואז:
```
ip ssh version 2
login block-for 120 attempts 3 within 60
ipv6 access-list MGMT6
 permit ipv6 2001:DB8:30:99::/64 any
 deny ipv6 any any log
 exit
line vty 0 15
 transport input ssh
 login local
 ipv6 access-class MGMT6 in
 exec-timeout 5 0
line console 0
 login local
 logging synchronous
 exit
service timestamps log datetime msec
logging host ipv6 2001:DB8:30:100::12
 end
copy running-config startup-config
```

---

## משימה 9 — שלושת מתגי ה-access
⚠️ ‏VTP הוא **transparent**: כל מתג access יוצר **רק את ה-VLANים שהוא משתמש בהם**.

<div dir="rtl">

| מתג | ה-VLANים שלו | ‎Fa0/1–10 | ‎Fa0/11–20 | ‎Fa0/21 | ‎Fa0/22 | ‎Fa0/23 | IPv6 ניהול |
|---|---|---|---|---|---|---|---|
| ‎SW-KG-ACC1 | ‎31, 32, 99, 199 | ‎31 | ‎32 | ‎199 legacy | ‎199 legacy | 99 מחשב המנהל | ‎::11 |
| ‎SW-KG-ACC2 | ‎33, 34, 99 | ‎33 | ‎34 | 33 מדפסת | לא בשימוש | לא בשימוש | ‎::12 |
| ‎SW-KG-ACC3 | ‎35, 36, 99 | ‎35 | ‎36 | 35 מדפסת | לא בשימוש | לא בשימוש | ‎::13 |

</div>

### 9א — ‏SW-KG-ACC1 (Fab-Ops, ‏Quality, ‏legacy, מחשב המנהל)
👉 **איפה:** ‏**SW-KG-ACC1** ‏←‏ CLI.

⌨️ **הקשחה, ‏VLANים, פורטים:**
```
enable
configure terminal
hostname SW-KG-ACC1
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vlan 31
 name FAB-OPS
vlan 32
 name QUALITY
vlan 99
 name MGMT
vlan 199
 name LEGACY-IPV4
vlan 998
 name NATIVE
vlan 999
 name PARKING
 exit
spanning-tree mode rapid-pvst
interface range gi0/1 - 2
 description TRUNK uplink to DIST1 / DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 31-36,99,100,199,998
 switchport nonegotiate
 no shutdown
interface range fa0/1 - 10
 description FAB-OPS users
 switchport mode access
 switchport access vlan 31
interface range fa0/11 - 20
 description QUALITY users
 switchport mode access
 switchport access vlan 32
interface range fa0/21 - 22
 description LEGACY IPv4 devices
 switchport mode access
 switchport access vlan 199
interface fa0/23
 description PC-KG-ADMIN-01 (management)
 switchport mode access
 switchport access vlan 99
interface range fa0/1 - 23
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
 no cdp enable
interface fa0/24
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
interface vlan 99
 description MANAGEMENT
 ipv6 address 2001:DB8:30:99::11/64
 no shutdown
 exit
```
⌨️ **ניהול:**
```
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
‏←‏ עונים **‎`1024`** ‏←‏ ואז:
```
ip ssh version 2
login block-for 120 attempts 3 within 60
ipv6 access-list MGMT6
 permit ipv6 2001:DB8:30:99::/64 any
 deny ipv6 any any log
 exit
line vty 0 15
 transport input ssh
 login local
 ipv6 access-class MGMT6 in
 exec-timeout 5 0
line console 0
 login local
 logging synchronous
 exit
service timestamps log datetime msec
logging host ipv6 2001:DB8:30:100::12
 end
copy running-config startup-config
```

<div dir="rtl">

> מתג שכבה 2 לומד את שער ה-IPv6 שלו מה-Router Advertisements — לא צריך שורת `default-gateway`.
> ‏DHCP snooping הוא רק ל-IPv4, ולכן כאן פורטי ה-access מוגנים על ידי port-security, ‏BPDU Guard
> וה-VLAN של החניה. (מתגים אמיתיים מוסיפים **RA Guard** ו-**DHCPv6 Guard** — לא קיים ב-PT. ציינו
> את זה בספר.)

</div>

### 9ב — ‏SW-KG-ACC2 (Maintenance, ‏Safety, מדפסת)
👉 **איפה:** ‏**SW-KG-ACC2** ‏←‏ CLI.

⌨️ **הקשחה, ‏VLANים, פורטים:**
```
enable
configure terminal
hostname SW-KG-ACC2
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vlan 33
 name MAINTENANCE
vlan 34
 name SAFETY
vlan 99
 name MGMT
vlan 998
 name NATIVE
vlan 999
 name PARKING
 exit
spanning-tree mode rapid-pvst
interface range gi0/1 - 2
 description TRUNK uplink to DIST1 / DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 31-36,99,100,199,998
 switchport nonegotiate
 no shutdown
interface range fa0/1 - 10
 description MAINTENANCE users
 switchport mode access
 switchport access vlan 33
interface range fa0/11 - 20
 description SAFETY users
 switchport mode access
 switchport access vlan 34
interface fa0/21
 description PRN-KG-ACC2-01
 switchport mode access
 switchport access vlan 33
interface range fa0/1 - 21
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
 no cdp enable
interface range fa0/22 - 24
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
interface vlan 99
 description MANAGEMENT
 ipv6 address 2001:DB8:30:99::12/64
 no shutdown
 exit
```
⌨️ **ניהול:** אותו בלוק כמו ב-9א (מ-`ip domain-name intel.lab` ועד
`copy running-config startup-config`).

### 9ג — ‏SW-KG-ACC3 (Planning, ‏Training, מדפסת)
👉 **איפה:** ‏**SW-KG-ACC3** ‏←‏ CLI.

⌨️ **הקשחה, ‏VLANים, פורטים:**
```
enable
configure terminal
hostname SW-KG-ACC3
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vlan 35
 name PLANNING
vlan 36
 name TRAINING
vlan 99
 name MGMT
vlan 998
 name NATIVE
vlan 999
 name PARKING
 exit
spanning-tree mode rapid-pvst
interface range gi0/1 - 2
 description TRUNK uplink to DIST1 / DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 31-36,99,100,199,998
 switchport nonegotiate
 no shutdown
interface range fa0/1 - 10
 description PLANNING users
 switchport mode access
 switchport access vlan 35
interface range fa0/11 - 20
 description TRAINING users
 switchport mode access
 switchport access vlan 36
interface fa0/21
 description PRN-KG-ACC3-01
 switchport mode access
 switchport access vlan 35
interface range fa0/1 - 21
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
 no cdp enable
interface range fa0/22 - 24
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
interface vlan 99
 description MANAGEMENT
 ipv6 address 2001:DB8:30:99::13/64
 no shutdown
 exit
```
⌨️ **ניהול:** אותו בלוק כמו ב-9א.

🔍 **בודקים עכשיו (בכל אחד):** ‏`show vlan brief` ‏←‏ הפורטים נמצאים ב-VLANים של הטבלה למעלה.

---

## משימה 10 — ‏SW-KG-SRV
👉 **איפה:** ‏**SW-KG-SRV** ‏←‏ CLI.

⌨️ מקלידים:
```
enable
configure terminal
hostname SW-KG-SRV
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vlan 99
 name MGMT
vlan 100
 name SERVERS
vlan 998
 name NATIVE
vlan 999
 name PARKING
 exit
spanning-tree mode rapid-pvst
interface range gi0/1 - 2
 description TRUNK uplink to DIST1 / DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 31-36,99,100,199,998
 switchport nonegotiate
 no shutdown
interface range fa0/1 - 4
 description servers
 switchport mode access
 switchport access vlan 100
 spanning-tree portfast
 spanning-tree bpduguard enable
interface range fa0/5 - 24
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
interface vlan 99
 description MANAGEMENT
 ipv6 address 2001:DB8:30:99::14/64
 no shutdown
 exit
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
‏←‏ עונים **‎`1024`** ‏←‏ ואז:
```
ip ssh version 2
login block-for 120 attempts 3 within 60
ipv6 access-list MGMT6
 permit ipv6 2001:DB8:30:99::/64 any
 deny ipv6 any any log
 exit
line vty 0 15
 transport input ssh
 login local
 ipv6 access-class MGMT6 in
 exec-timeout 5 0
line console 0
 login local
 exit
logging host ipv6 2001:DB8:30:100::12
 end
copy running-config startup-config
```

---

## משימה 11 — ‏R-KG-EDGE והנתיב אצל הספק

### 11א — ‏R-KG-EDGE: ממשקים ו-OSPFv3
👉 **איפה:** ‏**R-KG-EDGE** ‏←‏ CLI ‏←‏ `no` לשאלה ‏←‏ `Router>`‎.

⌨️ מקלידים:
```
enable
configure terminal
hostname R-KG-EDGE
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
ipv6 unicast-routing
ipv6 router ospf 1
 router-id 3.3.3.1
 exit
interface gi0/0
 description to SWL3-KG-DIST1
 ip address 10.30.4.1 255.255.255.252
 ip nat inside
 ipv6 address 2001:DB8:30:FF01::1/64
 ipv6 ospf 1 area 0
 no shutdown
interface gi0/2
 description to SWL3-KG-DIST2
 ipv6 address 2001:DB8:30:FF02::1/64
 ipv6 ospf 1 area 0
 no shutdown
interface gi0/1
 description WAN to R-ISPC-PE (dual-stack)
 ip address 200.3.1.2 255.255.255.252
 ip nat outside
 ipv6 address 2001:DB8:C:1::2/64
 no shutdown
 exit
```
לחצו **Fast Forward Time**.\
🔍 **בודקים עכשיו:** ‏`do show ipv6 ospf neighbor` ‏←‏ ‎`3.3.3.2` ו-‎`3.3.3.3`, שניהם `FULL`.

### 11ב — נתיבים סטטיים לכיוון ה-WAN, בשתי גרסאות ה-IP
⌨️ מקלידים:
```
ipv6 route ::/0 2001:DB8:C:1::1
ip route 0.0.0.0 0.0.0.0 200.3.1.1
ip route 10.30.199.0 255.255.255.0 10.30.4.2
ipv6 router ospf 1
 default-information originate
 exit
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`ipv6 route ::/0 2001:DB8:C:1::1` | נתיב ברירת מחדל ב-IPv6 ‏(‎`::/0` = הכול) |
| ‎`ip route 10.30.199.0 ... 10.30.4.2` | ה-VLAN מדור קודם נמצא מאחורי DIST1 |

</div>

### 11ג — ‏PAT ל-VLAN מדור קודם, ומסנן IPv6 נכנס
⌨️ מקלידים:
```
access-list 1 permit 10.30.199.0 0.0.0.255
access-list 1 permit 10.30.4.0 0.0.0.3
ip nat inside source list 1 interface gi0/1 overload
ipv6 access-list WAN6-IN
 remark --- ICMPv6 is required by IPv6 itself (neighbour discovery) ---
 permit icmp any any
 remark --- replies from web and DNS servers ---
 permit tcp any eq www any
 permit udp any eq domain any
 deny ipv6 any any log
 exit
interface gi0/1
 ipv6 traffic-filter WAN6-IN in
 exit
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`ip nat inside source list 1 interface gi0/1 overload` | ‏**PAT** — כל המכשירים מדור קודם (וה-NTP של DIST1) חולקים את 200.3.1.2 |
| ‎`ipv6 traffic-filter WAN6-IN in` | מפעיל ACL של IPv6 על ממשק |

</div>

### 11ד — ניהול
⌨️ מקלידים:
```
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
‏←‏ עונים **‎`1024`** ‏←‏ ואז:
```
ip ssh version 2
login block-for 120 attempts 3 within 60
ipv6 access-list MGMT6
 permit ipv6 2001:DB8:30:99::/64 any
 deny ipv6 any any log
 exit
line vty 0 15
 transport input ssh
 login local
 ipv6 access-class MGMT6 in
 exec-timeout 5 0
line console 0
 login local
 exit
service timestamps log datetime msec
logging host ipv6 2001:DB8:30:100::12
 end
copy running-config startup-config
```

### 11ה — ‏R-ISPC-PE: מנתבים את בלוק ה-IPv6 של קריית גת
👉 **איפה:** ‏**R-ISPC-PE** ‏←‏ CLI ‏←‏ `enable` ‏←‏ סיסמה `Intel#En4ble`.

⌨️ מקלידים:
```
configure terminal
ipv6 route 2001:DB8:30::/48 2001:DB8:C:1::2
end
copy running-config startup-config
```

<div dir="rtl">

> אין NAT ל-IPv6: הספק פשוט מנתב את כל ה-‎/48 לנתב הקצה שלנו.

</div>

---

## משימה 12 — שרתים ומכשירי קצה (IPv6 לחיצה אחרי לחיצה)

### 12א — איפה נמצאות הגדרות ה-IPv6
שרת או מחשב ‏←‏ **Desktop** ‏←‏ **IP Configuration**. בחלון יש שני חלקים: **IPv4** למעלה,
ו-**IPv6 Configuration** מתחתיו. במכשירים שהם IPv6 בלבד, משאירים את שדות ה-**IPv4** **ריקים**.

<div dir="rtl">

| מכשיר | הגדרת IPv6 | ‎IPv6 Address / prefix | ‎IPv6 Gateway | ‎IPv6 DNS Server |
|---|---|---|---|---|
| ‎SRV-KG-DNS | ‎Static | ‎2001:DB8:30:100::10 / 64 | ‎FE80::1 | ‎2001:DB8:30:100::10 |
| ‎SRV-KG-MAIL | ‎Static | ‎2001:DB8:30:100::11 / 64 | ‎FE80::1 | ‎2001:DB8:30:100::10 |
| ‎SRV-KG-SYSLOG | ‎Static | ‎2001:DB8:30:100::12 / 64 | ‎FE80::1 | ‎2001:DB8:30:100::10 |
| ‎SRV-KG-AAA | ‎Static | ‎2001:DB8:30:100::13 / 64 | ‎FE80::1 | ‎2001:DB8:30:100::10 |
| ‎PC-KG-ADMIN-01 | ‎Static | ‎2001:DB8:30:99::100 / 64 | ‎FE80::1 | ‎2001:DB8:30:100::10 |
| ‎SRV-ISPC-WEB6 | ‎Static | ‎2001:DB8:C:50::80 / 64 | ‎FE80::1 | ‎— |
| כל 12 המחשבים של המחלקות | לוחצים **Automatic** | ‏(SLAAC ממלא) | | |

</div>

<div dir="rtl">

> בתיבה IPv6 Address מקלידים רק את הכתובת; ה-‎`64` נכנס לתיבה הקטנה שאחרי ה-‎`/`‎.

</div>

### 12ב — מחשבים מדור קודם ומדפסות
- **מחשבים מדור קודם (IPv4 בלבד):** ‏PC-KG-LEGACY-01 ‏‎`10.30.199.10`, ‏PC-KG-LEGACY-02 ‏‎`10.30.199.11`,
  mask ‏‎`255.255.255.0`, ‏gateway ‏‎`10.30.199.1`, ‏DNS ‏‎`200.1.100.10`.
- **מדפסות:** ‏Config ‏←‏ FastEthernet0 ‏←‏ IPv6 ‏←‏ **Automatic** ‏(SLAAC).

### 12ג — שירותים
- ‏**SRV-KG-DNS** ‏←‏ DNS **On** ‏←‏ רשומות מסוג **AAAA Record** (לא A!):
  ‏`mail.kg.intel.lab → 2001:DB8:30:100::11`, ‏`www6.isp-web.com → 2001:DB8:C:50::80`.
- ‏**SRV-KG-MAIL** ‏←‏ EMAIL ‏←‏ דומיין `kg.intel.lab` ‏←‏ Set (המשתמשים בשלב 16).
- ‏**SRV-KG-SYSLOG** ‏←‏ SYSLOG **On**.
- ‏**SRV-KG-AAA** ‏←‏ AAA **On** (ראו את ההערה למטה).
- ‏**SRV-ISPC-WEB6** ‏←‏ HTTP ‏←‏ עורכים את `index.html` ‏←‏ ‎`<h1>IPv6 works!</h1>`‎ ‏←‏ Save.
- בכל שרת מכבים את השירותים שלא צריך.

<div dir="rtl">

> **‏AAA על IPv6 ב-Packet Tracer.** התמיכה של PT ב-TACACS+/RADIUS על IPv6 מוגבלת, ולכן המכשירים של
> קריית גת למעלה משתמשים במסד המשתמשים ה**מקומי** (`login local`). שרת ה-AAA קיים בסניף (דרישה
> 20.10). אם גרסת ה-PT שלכם מקבלת את זה, נסו במתג:
> ‏`aaa new-model` ‏←‏ `tacacs server KG-AAA` ‏←‏ `address ipv6 2001:DB8:30:100::13` ‏←‏ `key Intel#Tac`
> ‏←‏ `exit` ‏←‏ `aaa authentication login default group tacacs+ local`, ורשמו את המתג
> ב-SRV-KG-AAA לפי כתובת ה-IPv6 שלו. כתבו בספר איזו דרך עבדה.

</div>

🔍 **בודקים עכשיו:** ‏PC-KG-FAB-01 ‏←‏ Command Prompt ‏←‏ `ipconfig /all` ‏←‏ כתובת IPv6
‏‎`2001:DB8:30:31:…`‎, ‏gateway ‏`FE80::1`, ‏DNS ‏‎`2001:DB8:30:100::10`.

❌ **יש רק כתובת `FE80::`‎:** לחצו שוב **Automatic**; בדקו שה-SVI של VLAN 31 למעלה ב-DIST1
(`show ipv6 interface brief`).

---

## משימה 13 — בדיקות

### 13א — במתגים ובנתב הקצה

<div dir="rtl">

| ‎# | איפה | מקלידים | ✅ אמורים לראות |
|---|---|---|---|
| ‎1 | ‎DIST1 | ‎`show ipv6 interface brief` | כל VLAN למעלה עם ה-‎`2001:DB8:30:x::2` שלו |
| ‎2 | ‎DIST1 | ‎`show standby brief` | `Vl31 31 110 P Active local FE80::... FE80::1` (ושאר ה-VLANים) |
| ‎3 | ‎DIST1 | ‎`show ipv6 ospf neighbor` | ‏3.3.3.1 (נתב הקצה) ו-3.3.3.3 ‏(DIST2) במצב FULL |
| ‎4 | ‎DIST2 | ‎`show ipv6 route` | `OE2 ::/0 [110/1] via FE80::..., GigabitEthernet1/1/1` — ברירת המחדל מנתב הקצה |
| ‎5 | ‎R-KG-EDGE | `show ip nat translations` (אחרי בדיקה 5 למטה) | ‎`200.3.1.2:port  10.30.199.10:port` |

</div>

### 13ב — ממכשירי הקצה

<div dir="rtl">

| ‎# | מאיפה | עושים | צפוי |
|---|---|---|---|
| ‎1 | ‎PC-KG-FAB-01 | ‎`ping 2001:DB8:30:36::2` | ✅ ניתוב בין VLANים ב-IPv6 |
| ‎2 | ‎PC-KG-FAB-01 | ‎`ping 2001:DB8:30:100::10` | ✅ שרת ה-DNS |
| ‎3 | ‎PC-KG-FAB-01 | ‎‏Web Browser ‏←‏ `http://www6.isp-web.com` | ‎✅ ‏"IPv6 works!" |
| ‎4 | ‎PC-KG-FAB-01 | ‎`ssh -l admin 2001:DB8:30:99::11` | ❌ נדחה (MGMT6) |
| ‎5 | ‎PC-KG-LEGACY-01 | ‎`ping 200.1.100.11` | ✅ דרך PAT |
| ‎6 | ‎PC-KG-ADMIN-01 | ‎`ssh -l admin 2001:DB8:30:99::11` | ‎✅ |
| ‎7 | ‎SWL3-KG-DIST1 | ‎`show ntp status` | מסונכרן ל-200.1.10.4 (אחרי Fast Forward) |

</div>

---

## משימה 14 — ‏failover של HSRPv6
1. קודם **File → Save**.
2. ‏PC-KG-FAB-01 ‏←‏ Command Prompt ‏←‏ `ping -t 2001:DB8:30:100::10`.
3. מוחקים את **SWL3-KG-DIST1** (הכלי **Delete**).
4. מסתכלים: כמה תשובות הולכות לאיבוד, ואז הפינגים ממשיכים. ב-DIST2: ‏`show standby brief` ‏←‏
   ‏**Active** עבור `FE80::1`.
5. ‏**File → Open** לקובץ ששמרתם (עונים **No** לשמירה) כדי להחזיר את DIST1.

💾 ‏`copy running-config startup-config` בכל מקום ‏←‏ **File → Save**.

---

## נקודת ביקורת
- [ ] המחשבים מקבלים כתובות IPv6 אוטומטית, עם שער FE80::1 ושרת DNS
- [ ] שכני OSPFv3 במצב FULL; למתגי ה-DIST יש את נתיב ברירת המחדל ‎`::/0`
- [ ] גלישה ב-IPv6 ל-www6.isp-web.com עובדת
- [ ] מחשבי ה-legacy מגיעים לאינטרנט דרך PAT
- [ ] ה-failover של HSRPv6 עובד

## אם משהו לא עובד

<div dir="rtl">

| בעיה | פתרון |
|---|---|
| פקודות `ipv6 ...`‎ נדחות במתג | משימה 4ב — ‏`sdm prefer dual-ipv4-and-ipv6 default` + ‏reload |
| ‏OSPFv3 לא מתחיל | אין `router-id` תחת `ipv6 router ospf 1` |
| המחשבים מקבלים רק כתובת `FE80::`‎ | חסר `ipv6 unicast-routing` ‏←‏ אין RAs; או שה-SVI של ה-VLAN למטה |
| למחשבים אין DNS | חסר `ipv6 nd other-config-flag` / ‏`ipv6 dhcp server`; או הקלידו את ה-DNS ידנית |
| ‏`standby 31 ipv6 FE80::1` נדחה | השתמשו ב-`standby 31 ipv6 autoconfig`, קראו את הכתובת הווירטואלית עם `show standby brief`, והשתמשו בה כשער של השרתים |
| ‏HSRP ל-IPv6 לא נתמך בכלל | ל-IPv6 יש יתירות שער משלו: שני מתגי ה-DIST שולחים RAs והמחשבים לומדים שני שערים. כתבו את זה בספר הפרויקט |
| כל ה-IPv6 מת אחרי ה-ACL בנתב הקצה | חסרה השורה `permit icmp any any` ‏(IPv6 צריך ICMPv6) |
| למחשב legacy אין אינטרנט | ‏`ip route 10.30.199.0 ...`‎ בנתב הקצה, ‏`ip route 0.0.0.0 ... 10.30.4.1` ב-DIST1, ‏NAT inside/outside |
| הפורטים של VLAN אחד מתים במתג access | ‏VTP הוא transparent — ה-VLAN הזה לא נוצר **במתג הזה** |

</div>

---

## 🏋 תרגילים

### תרגיל א — למה אין את האתר של חיפה? ⭐⭐
- 🎯 **המשימה:** למחשב בקריית גת יש אינטרנט, אבל הוא לא מצליח לפתוח את `http://www.intel.lab`
  (האתר של חיפה). גלו למה והציעו שני פתרונות מהעולם האמיתי.
- 📁 **מתחילים מ:** ‏`step14.pkt` שלכם (לא משנים כלום).
- 👣 **צעדים:**
  1. ‏PC-KG-FAB-01 ‏←‏ Web Browser ‏←‏ `http://www.intel.lab`.
  2. ‏`ipconfig /all` במחשב — אילו גרסאות IP יש לו?
  3. אילו כתובות יש ל-`www.intel.lab` (שלב 11, שלב 12)?
- ✅ **גמרתם כש**כתבתם את הסיבה במשפט אחד ושני פתרונות.

<details dir="rtl"><summary>💡 רמז</summary>

האם טלפון שמדבר רק עברית יכול להתקשר למישהו שמדבר רק אנגלית בלי מתורגמן?
</details>
<details dir="rtl"><summary>✔ תשובה</summary>

ל-`www.intel.lab` יש רק כתובת **IPv4** ‏(200.1.10.3 ציבורית / 10.10.200.13 פרטית), והמחשבים בקריית גת
מדברים **רק IPv6**. מחשב שהוא IPv6 בלבד לא יכול לדבר עם שרת שהוא IPv4 בלבד בלי מתרגם. פתרונות
אמיתיים: (1) **NAT64 + ‏DNS64** בנתב הקצה של קריית גת; (2) להפוך את ה-DMZ של חיפה ל-**dual-stack**
(כתובת IPv6 + רשומת AAAA לשרת ה-web); (3) ‏reverse proxy. ‏PT לא תומך ב-NAT64 — תעדו את זה כפשרה
תכנונית שנובעת מהדרישה "סניף אחד כולו IPv6".
</details>

### תרגיל ב — מורידים את ה-O-flag ⭐
- 🎯 **המשימה:** לראות מה `ipv6 nd other-config-flag` באמת נותן למחשב.
- 📁 **מתחילים מ:** ‏`step14.pkt` ‏←‏ **Save As** ‏`step14-exB.pkt`.
- 👣 **צעדים:**
  1. ב-**DIST1 וגם ב-DIST2**: ‏`configure terminal` ‏←‏ `interface vlan 32` ‏←‏
     ‏`no ipv6 nd other-config-flag` ‏←‏ `end`.
  2. ‏PC-KG-QUA-01 ‏←‏ IP Configuration ‏←‏ IPv6 ‏←‏ לוחצים **Static**, ואז שוב **Automatic**.
  3. ‏`ipconfig /all`.
- ✅ **גמרתם כש**אתם יודעים לומר מה עוד יש למחשב ומה הוא איבד.

<details dir="rtl"><summary>✔ תשובה</summary>

המחשב עדיין מקבל כתובת IPv6 ושער (SLAAC, מה-RA) — אבל **אין לו שרת DNS**. בלי ה-O-flag המחשב אף
פעם לא מבקש מ-DHCPv6 את התוספות, ולכן שמות כמו `www6.isp-web.com` מפסיקים לעבוד, ו-ping לפי כתובת
עדיין עובד.
</details>

---

## 🛠 הפרויקט שלכם

עשיתם את השלב הזה על הדוגמה של אינטל. עכשיו עשו אותו שוב בפרויקט **שלכם**, עם הערכים
מהתוכנית **שלכם** (`my-project/plan.md`). הפקודות זהות — רק הערכים משתנים.

זה **סניף ה-IPv6** של הדוגמה. בנו את האתר השלישי **שלכם** מתוך חלקים ג–ה בתוכנית:

- [ ] פותחים את `my-project/step13.pkt` ‏←‏ **Save As** ‏`my-project/step14.pkt`
- [ ] קודם כותבים את טבלאות ה-IPv6 שלכם (כמו 1.3 ו-1.9)
- [ ] מציבים (ספקי כוח!), מחברים, בודקים את תבנית ה-SDM
- [ ] שני מתגי ה-DIST: ‏VLANים, ‏OSPFv3, שערים עם HSRPv6, ‏stateless DHCPv6
- [ ] מתגי ה-access (כל אחד יוצר את ה-VLANים שלו!), מתג השרתים
- [ ] נתב הקצה: ‏OSPFv3, ברירות מחדל סטטיות, ‏PAT ל-VLAN מדור קודם, מסנן IPv6; נתיב אצל הספק
- [ ] שרתים, מחשבים על Automatic; הבדיקות של משימה 13; ‏failover

<div dir="rtl">

| בדוגמה | בפרויקט שלכם — לוקחים מ |
|---|---|
| ‏‎`2001:DB8:30::/48`, הכלל "מספר ה-VLAN = הקבוצה הרביעית" | תוכנית, חלק ג (ה-‎/48 שלכם — שמרו על כלל פשוט כמו זה) |
| ‏VLANים 31–36, ‏99, ‏100 | תוכנית, חלק ד (אתר 3) |
| ‏router-IDs של OSPFv3 ‏3.3.3.x | router-IDs משלכם |
| ‏HSRP ל-IPv6, שער וירטואלי `FE80::1` | להשאיר את השיטה, הקבוצות שלכם |
| ‎‏SLAAC / ‏stateless DHCPv6 | תוכנית, חלק ה (שורת ה-DHCP) |
| ‏VLAN ‏199 של IPv4 מדור קודם עם PAT | תוכנית, חלק ה (שורת ה-NAT) — בדקו את הפרשנות הזו עם המנחה, כמו שאומרת הערת התכנון ב-design.md |

</div>

משרד החינוך דורש אתר אחד שהוא **כולו IPv6** (דרישה 7).

**בדיקה:** ‏`show ipv6 ospf neighbor`; המחשבים מקבלים כתובת IPv6 מה-prefix שלכם; ‏ping מהאתר הזה לשרת
IPv6 באינטרנט עובד.

💾 שמרו בשם `my-project/step14.pkt`.

---

## 🎓 מסבירים לבוחן

בבחינה, הבוחן מצביע על הפרויקט **שלכם** ומבקש **להסביר** ו**להראות**. תרגלו כל שאלה
**בקול**, ואז הראו את התשובה בפרויקט שלכם — לא בדוגמה. כסו את התשובה, ענו בעצמכם, ורק אז
פתחו והשוו.

★1–★3 = שאלה ממאגר השאלות של משרד החינוך (רמת קושי 1–3).
◆ = לא במאגר, אבל בוחנים שואלים אותה לעיתים קרובות.

**1. ◆ מהם הסוגים העיקריים של כתובות IPv6?**

<details dir="rtl"><summary>תשובה</summary>

‏Global unicast ‏(‎`2000::/3`, ניתנת לניתוב באינטרנט), ‏link-local ‏(`FE80::/10`, רק על הקישור — משמשת
פרוטוקולי ניתוב וכשער), ‏multicast ‏(`FF00::/8`). ב-IPv6 אין broadcast.

**איפה מראים:** `show ipv6 interface brief`
</details>

**2. ◆ מה ההבדל בין SLAAC, ‏stateless DHCPv6 ו-stateful DHCPv6?**

<details dir="rtl"><summary>תשובה</summary>

‏SLAAC: המחשב בונה לעצמו כתובת מה-prefix של הנתב (Router Advertisement). ‏Stateless DHCPv6: הכתובת
מ-SLAAC, אבל מידע נוסף (DNS) משרת DHCPv6 (‏`ipv6 nd other-config-flag`). ‏Stateful DHCPv6: השרת עצמו
מחלק את הכתובת.

**איפה מראים:** מחשב ‏←‏ IP Configuration ‏←‏ IPv6 ‏(Automatic)
</details>

**3. ◆ במה OSPFv3 שונה מ-OSPFv2?**

<details dir="rtl"><summary>תשובה</summary>

הוא מנתב IPv6, מופעל **על כל ממשק** (`ipv6 ospf 1 area 0`) במקום עם פקודות `network`, משתמש בכתובות
link-local לשכנים, ועדיין צריך router-ID של 32 ביט שמוגדר ידנית כשאין כתובת IPv4.

**איפה מראים:** `show ipv6 ospf neighbor`, `show ipv6 route`
</details>

**4. ◆ איך HSRP עובד ב-IPv6?**

<details dir="rtl"><summary>תשובה</summary>

כמו ב-IPv4 (חובה `standby version 2`), אבל השער הווירטואלי הוא כתובת **link-local** (כאן `FE80::1`),
שהמחשבים לומדים כשער ברירת המחדל שלהם.

**איפה מראים:** `show standby brief`
</details>

**5. ★1 מהו PAT? למה יש בכלל NAT באתר IPv6?**

<details dir="rtl"><summary>תשובה</summary>

‏PAT מאפשר להרבה מחשבים פנימיים לחלוק כתובת IPv4 ציבורית אחת בעזרת מספרי פורט. ‏IPv6 לא צריך NAT
(יש מספיק כתובות); האתר הזה שומר VLAN ‏IPv4 קטן אחד מדור קודם, ורק הוא עובר PAT — כדי לעמוד בדרישה
ל-NAT בכל אתר (דרישה 10).

**איפה מראים:** `show ip nat translations`
</details>

---

## 🔁 עושים שוב — בלי המדריך

הבוחן יכול לבקש מכם להגדיר משהו שוב, מולו. תצליחו רק אם עשיתם את זה **בלי המדריך** לפני כן.
עשו את התרגיל הזה בפרויקט שלכם:

בעותק של הקובץ שלכם, מחקו את כתובות ה-IPv6 ואת OSPFv3 ממתג distribution אחד. בלי העמוד הזה, הגדירו
אותם שוב מתוך התוכנית שלכם. יעד: **‏15 דקות**. אחר כך הראו מחשב עם כתובת IPv6 מה-prefix שלכם ואת
`show ipv6 ospf neighbor`.

---

## 👩‍🏫 הערות למורה
- **שיעור 1:** ‏IPv6 — למה, איך קוראים ומקצרים כתובות (תרגלו 10 על הלוח), ‏‎/64, ‏link-local, תוכנית
  מספרי ה-VLAN שלנו ‏←‏ בנייה וחיווט.
- **שיעור 2:** ‏SLAAC + ‏stateless DHCPv6 (הראו את ה-RA ואת ה-DHCPv6 במצב Simulation, מסננים **ICMPv6**
  ו-**DHCPv6**), ‏OSPFv3, ‏HSRPv6 ‏←‏ ‏DIST1 ו-DIST2 (בזוגות: אחד מקליד את DIST1, השני את DIST2).
- **שיעור 3:** מתגי ה-access, מתג השרתים, נתב הקצה, השרתים.
- **שיעור 4:** בדיקות, ‏failover, ה-VLAN מדור קודם ו-PAT, הדיון בתרגיל א (דו-קיום של IPv4 ו-IPv6).
- **שאלות נפוצות של תלמידים**
  - *"איפה מסיכת הרשת?"* — ה-‎`/64` הוא המסיכה. ב-IPv6 תמיד כותבים את אורך ה-prefix.
  - *"למה FE80::1 כשער ולא 2001:…::1?"* — נתבים מפרסמים את עצמם בכתובות link-local; היא אף פעם לא
    משתנה, גם אם ה-prefix הגלובלי משתנה.
  - *"בלי NAT בכלל?"* — לא צריך: כל כתובת IPv6 ייחודית. האבטחה באה מחומות אש ומ-ACLs.
- **טעויות אופייניות:** שכחת תבנית ה-SDM + ה-reload; שגיאות כתיב בכתובות IPv6 ארוכות (אפסים); ‏OSPFv3
  בלי router-ID; שכחת `permit icmp` ב-ACLs של IPv6.
