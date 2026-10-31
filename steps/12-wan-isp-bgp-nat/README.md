# שלב 12 — ה-WAN: ‏3 ספקי אינטרנט, ‏BGP, ‏NAT וגיבוי DSL

<div dir="rtl">

> ⏱ ‏3–4 שיעורים · 🎯 דרישות משרד החינוך 1, ‏3, ‏4, ‏9, ‏10 (static), ‏22.12, ‏22.17, ‏23.1, ‏23.2, ‏23.3\
> 📁 מתחילים מ: `my-work/step11.pkt`\
> 💾 שומרים בשם: `my-work/step12.pkt`

</div>

<div dir="rtl">

> ✅ **לפני שמתחילים:** כל הסעיפים בנקודת הביקורת של שלב 11 מסומנים, ועשיתם את
> תרגיל ה-🔁 שלו בפרויקט שלכם. אל תדלגו על שלבים — כל שלב בנוי על הקובץ של השלב הקודם.

</div>

## 🗺 המשימות שלכם בשלב הזה
**שיעור 1 — בונים, ו-ISP-A**
- [ ] **משימה 1** — פותחים את שלב 11, שומרים בשם שלב 12, מציירים את אזור ה-INTERNET ‏(3 דקות)
- [ ] **משימה 2** — מציבים את מכשירי ה-WAN ‏(10 דקות)
- [ ] **משימה 3** — מחברים את ה-WAN בכבלים (20 דקות)
- [ ] **משימה 4** — ‏ISP-A: ‏R-ISPA-BR ו-R-ISPA-PE ‏(20 דקות)

**שיעור 2 — ‏ISP-B, ‏ISP-C ו-BGP**
- [ ] **משימה 5** — ‏ISP-B: ‏R-ISPB-BR ו-R-ISPB-PE ‏(15 דקות)
- [ ] **משימה 6** — ‏ISP-C: ‏R-ISPC-BR ו-R-ISPC-PE ‏(15 דקות)
- [ ] **משימה 7** — בודקים BGP וקוראים את טבלת ה-BGP ‏(15 דקות)
- [ ] **משימה 8** — שרתי האינטרנט והמחשב הביתי (15 דקות)

**שיעור 3 — חיפה באינטרנט**
- [ ] **משימה 9** — ‏R-HFA-EDGE: קישור ה-WAN וניתוב (10 דקות)
- [ ] **משימה 10** — ‏R-HFA-EDGE: ‏PAT כדי שהעובדים יוכלו לגלוש (10 דקות)
- [ ] **משימה 11** — ‏R-HFA-EDGE: ‏static NAT + חורים ב-ASA, כדי שהאינטרנט יראה את האתר שלנו (15 דקות)

**שיעור 4 — קו הגיבוי**
- [ ] **משימה 12** — מודם ה-DSL והענן (15 דקות)
- [ ] **משימה 13** — בדיקות יתירות (15 דקות)
- [ ] **משימה 14** — תצוגה פיזית: עיר "Internet" לספקים (15 דקות)
- [ ] **תרגילים** א ו-ב
- [ ] **🛠 הפרויקט שלכם**

## מה יהיה לכם בסוף השלב
**אינטרנט** קטן: שלושה ספקים (ISPs) שמחליפים ביניהם נתיבים עם **BGP**, וכל אחד מריץ **OSPF**
בפנים. חיפה מחוברת: העובדים גולשים באינטרנט (**PAT**), האינטרנט יכול לפתוח את האתר של אינטל
(**static NAT**), ו**מודם DSL** הוא קו גיבוי.

```
          AS 100 (ISP-A)                AS 200 (ISP-B)               AS 300 (ISP-C)
   [R-ISPA-PE]─OSPF─[R-ISPA-BR]══eBGP══[R-ISPB-BR]─OSPF─[R-ISPB-PE]
     │      │             ╲               ╱                │     │
     │   internet          ╲════eBGP════[R-ISPC-BR]─OSPF─[R-ISPC-PE]
     │   servers            (eBGP B↔C too)               │      │
   R-HFA-EDGE ·········· DSL modem ····· cloud ──────────┘      home users
   (Haifa)          (backup line to ISP-B)           (Jerusalem — step 13) (Kiryat Gat — step 14)
```
(שלושה ספקים: ‏AS 100, ‏AS 200, ‏AS 300. בכל ספק נתב BR ונתב PE עם OSPF ביניהם, וה-BRs מחוברים
ב-eBGP במשולש. ‏R-HFA-EDGE (חיפה) מחובר ל-ISP-A, ובקו גיבוי דרך מודם DSL וענן ל-ISP-B. ירושלים
(שלב 13) מתחברת ל-ISP-B, וקריית גת (שלב 14) ומשתמשים ביתיים ל-ISP-C.)

## חלק 1 — קודם מבינים (בשפה פשוטה)

### 1.1 מה זה באמת "האינטרנט"
האינטרנט הוא אלפי רשתות ששייכות לחברות שונות (ספקים, אוניברסיטאות, Google…), וכולן מחוברות. כל
רשת כזו היא **AS — Autonomous System** (מערכת אוטונומית), עם מספר (כאן 100, ‏200, ‏300).

- **בתוך** AS, הנתבים משתמשים בפרוטוקול פנימי (**OSPF** או EIGRP) — כמו השלטים של העיר עצמה.
- **בין** ASים, הם משתמשים ב-**BGP** — הפרוטוקול של האינטרנט — כמו הסכמים בין מדינות על אילו
  כבישים מובילים לאן.

משרד החינוך מבקש בדיוק את זה: ‏WAN שמריץ BGP (דרישות 1, ‏3), עם OSPF/EIGRP בתוך הספקים (דרישה 4).

### 1.2 שלושת הספקים שלנו
לכל ספק יש שני נתבים:
- **‏BR ‏(border router, נתב גבול)** — מדבר **BGP** עם הספקים האחרים.
- **‏PE ‏(provider edge, נתב קצה של הספק)** — מחבר את ה**לקוחות** (הסניפים שלנו). מדבר רק OSPF בתוך
  הספק שלו.

<div dir="rtl">

| ספק | ‎‏AS | בלוק הכתובות שלו | לקוח |
|---|---|---|---|
| ‎ISP-A | ‎100 | ‎200.1.0.0/16 | חיפה (+ שרתי האינטרנט) |
| ‎ISP-B | ‎200 | ‎200.2.0.0/16 | ירושלים (+ גיבוי ה-DSL של חיפה) |
| ‎ISP-C | ‎300 | ‎200.3.0.0/16 | קריית גת (+ משתמשים ביתיים) |

</div>

שלושת ה-BRs מחוברים ב**משולש** — אם קישור אחד נשבר, ‏BGP משתמש בדרך השנייה (יתירות בין סניפים,
דרישה 23.1).

### 1.3 ‏BGP במילים פשוטות
- שכני BGP נכתבים **ידנית**: ‏`neighbor 200.0.12.2 remote-as 200` = "הנתב בכתובת הזו שייך ל-AS 200 —
  בוא נדבר".
- כל ספק **מפרסם את הבלוק שלו**: ‏`network 200.1.0.0 mask 255.255.0.0`.
- ‏BGP מפרסם רק בלוק ש**קיים בדיוק** בטבלת הניתוב. לכן מוסיפים נתיב "שומר מקום" ל-**Null0** (חור
  שחור): ‏`ip route 200.1.0.0 255.255.0.0 null0`. נתיבים אמיתיים ומפורטים יותר בתוך הבלוק עדיין
  מנצחים, כי הנתב תמיד מעדיף את **ההתאמה הארוכה ביותר** (longest match).

### 1.4 לקוחות משתמשים בנתיבים סטטיים
נתבי הקצה שלנו לא מריצים שום פרוטוקול ניתוב מול הספק. הם משתמשים ב**נתיב ברירת מחדל סטטי אחד**:
"כל מה שאני לא מכיר ‏←‏ לספק". כך אנחנו **אף פעם** לא מספרים לאינטרנט על הרשתות הפנימיות שלנו
(דרישה 22.17). הספק, מצידו, מחזיק נתיב סטטי לכיוון הכתובות הציבוריות של הלקוח.

### 1.5 ‏NAT — פרטי בפנים, ציבורי בחוץ
כתובות ה-10.x שלנו הן **פרטיות**: הן לא קיימות באינטרנט. **‏NAT** ‏(Network Address Translation,
תרגום כתובות) בנתב הקצה מחליף אותן בכתובות **ציבוריות** כשהחבילות יוצאות.

<div dir="rtl">

| סוג | איך זה עובד | השוואה | איפה |
|---|---|---|---|
| ‎**‏Static NAT** | כתובת פרטית אחת ↔ כתובת ציבורית אחת, קבוע | קו טלפון ישיר למשרד אחד | חיפה: שרת ה-web ‏‎`10.10.200.13 ↔ 200.1.10.3` |
| ‎**‏Dynamic NAT** | כתובות פרטיות מקבלות כתובת ציבורית מתוך **מאגר** (pool), אחת לכל אחת, כל עוד הן בשימוש | מאגר משותף של קווים חיצוניים | ירושלים (שלב 13) |
| ‎**‏PAT ‏(overload)** | כולם חולקים כתובת ציבורית **אחת**; הנתב מבדיל ביניהם לפי **מספר פורט** | מרכזיה של חברה: מספר ציבורי אחד, הרבה שלוחות | חיפה לגלישה; קריית גת (שלב 14) |

</div>

משרד החינוך רוצה את שלושתם, אחד לכל סניף (דרישה 10). **השיטה של חיפה היא static NAT**; היא גם
משתמשת ב-PAT כדי שהעובדים יוכלו לגלוש (דרישה 22.12).

‏Static NAT הוא הסיבה שהאינטרנט יכול להגיע לאתר שלנו: מבקר פותח `http://www.intel.lab` ‏←‏ ה-DNS של
האינטרנט אומר ‎`200.1.10.3` ‏←‏ החבילה מגיעה לנתב הקצה שלנו ‏←‏ ‏NAT מחליף אותה ל-‎`10.10.200.13` ‏←‏
ה-ASA מעביר אותה ל-DMZ.

אנחנו גם מפרסמים את שרת ה-NTP בכתובת ‎`200.1.10.4` (רק פורט 123) עבור קריית גת בשלב 14.

### 1.6 גיבוי DSL ו-floating static route
משרד החינוך רוצה ספק שמגיעים אליו דרך **מודם DSL** (דרישה 23.2). אנחנו משתמשים בו כקו ה**גיבוי** של
חיפה, דרך ספק אחר (ISP-B).

**‏Floating static route** (נתיב סטטי "צף") הוא נתיב גיבוי עם "ציון אמון" גרוע יותר (administrative
distance): ‏`ip route 0.0.0.0 0.0.0.0 200.2.9.1 10`. לנתיב הרגיל יש distance 1; לזה יש 10, ולכן הוא
**נשאר מוסתר** כל עוד הראשי עובד, ומופיע אוטומטית אם הראשי נעלם.

### 1.7 תוכנית הכתובות של ה-WAN
השאירו את הטבלה הזו פתוחה — כל משימה לוקחת ממנה את המספרים.

<div dir="rtl">

| נתב | ‎‏Gi0/0 | ‎‏Gi0/1 | ‎‏Gi0/2 |
|---|---|---|---|
| ‎R-ISPA-BR | ‎200.1.0.1/30 | ‎200.0.12.1/30 | ‎200.0.13.1/30 |
| ‎R-ISPA-PE | ‎200.1.0.2/30 | 200.1.1.1/30 לחיפה | 200.1.100.1/24 לשרתים |
| ‎R-ISPB-BR | ‎200.2.0.1/30 | ‎200.0.12.2/30 | ‎200.0.23.1/30 |
| ‎R-ISPB-PE | ‎200.2.0.2/30 | 200.2.1.1/30 לירושלים | 200.2.9.1/30 ל-DSL (גיבוי חיפה) |
| ‎R-ISPC-BR | ‎200.3.0.1/30 | ‎200.0.13.2/30 | ‎200.0.23.2/30 |
| ‎R-ISPC-PE | ‎200.3.0.2/30 | 200.3.1.1/30 לקריית גת | 200.3.50.1/24 למשתמשים ביתיים |
| ‎R-HFA-EDGE | ‎10.10.7.1/30 (ASA) | ‎**200.1.1.2/30** (ISP-A) | ‎**200.2.9.2/30** (DSL) |

</div>

### 1.8 לפני שמקלידים בנתב חדש כלשהו
- נתב חדש שואל `Would you like to enter the initial configuration dialog? [yes/no]:`‎ ‏←‏ הקלידו
  **`no`**, ‏Enter, ואז שוב Enter ‏←‏ `Router>`‎.
- פורטים של נתב מתחילים **כבויים** — כל בלוק של ממשק נגמר ב-`no shutdown`.
- נתבי הספקים שייכים ל"חברות אחרות", ולכן הם מקבלים רק את הבסיס: שם, ‏secret, ‏banner (משרד
  החינוך רוצה banner על **כל** הנתבים).

---

## משימה 1 — פותחים את שלב 11 ושומרים בשם שלב 12 (איך? ‏←‏ M1)
‏**File → Open** ‏←‏ `my-work/step11.pkt` ‏←‏ **File → Save As** ‏←‏ `my-work/step12.pkt`.
ציירו אליפסה גדולה מימין עם התווית `INTERNET / WAN` ‏(M19 — בחרו בכלי ה-**Ellipse** במקום המלבן).

---

## משימה 2 — מציבים את מכשירי ה-WAN (איך? ‏←‏ M2, ‏M4)

<div dir="rtl">

| איפה בסרגל המכשירים | דגם | ‎Display Name |
|---|---|---|
| ‎Network Devices → Routers | ‎**2911** ×6 | ‎`R-ISPA-BR`, `R-ISPA-PE`, `R-ISPB-BR`, `R-ISPB-PE`, `R-ISPC-BR`, `R-ISPC-PE` |
| ‎Network Devices → Switches | ‎**2960** ×2 | ‎`SW-ISPA-NET`, `SW-ISPC-HOME` |
| ‎End Devices | ‎**Server** ×3 | ‎`SRV-ISP-DNS`, `SRV-ISP-WEB1`, `SRV-ISP-WEB2` |
| ‎End Devices | ‎**PC** | ‎`PC-HOME-01` |
| ‎Network Devices → **WAN Emulation** | ‎**DSL-Modem** | ‎`DSL-HFA` |
| ‎Network Devices → **WAN Emulation** | ‎**Cloud** | ‎`CLOUD-DSL` |

</div>

💡 סדרו אותם כמו בשרטוט למעלה: ‏ISP-A משמאל, ‏ISP-B באמצע, ‏ISP-C מימין. שרטוט מסודר חוסך
טעויות חיווט.

✅ ‏14 מכשירים חדשים, לכולם שמות.

---

## משימה 3 — מחברים את ה-WAN בכבלים (איך? ‏←‏ M5)
נתב ↔ נתב = **Cross-Over**. נתב/שרת/מחשב ↔ מתג = **Straight-Through**.
את שורות 12–14 (‏DSL) משאירים למשימה 12.

<div dir="rtl">

| ‎# | כבל | לוחצים קודם על | פורט | לוחצים אחר כך על | פורט |
|---|---|---|---|---|---|
| ‎1 | ‎Cross-Over | ‎R-ISPA-BR | ‎Gi0/0 | ‎R-ISPA-PE | ‎Gi0/0 |
| ‎2 | ‎Cross-Over | ‎R-ISPB-BR | ‎Gi0/0 | ‎R-ISPB-PE | ‎Gi0/0 |
| ‎3 | ‎Cross-Over | ‎R-ISPC-BR | ‎Gi0/0 | ‎R-ISPC-PE | ‎Gi0/0 |
| ‎4 | ‎Cross-Over | ‎R-ISPA-BR | ‎Gi0/1 | ‎R-ISPB-BR | ‎Gi0/1 |
| ‎5 | ‎Cross-Over | ‎R-ISPA-BR | ‎Gi0/2 | ‎R-ISPC-BR | ‎Gi0/1 |
| ‎6 | ‎Cross-Over | ‎R-ISPB-BR | ‎Gi0/2 | ‎R-ISPC-BR | ‎Gi0/2 |
| ‎7 | ‎Cross-Over | ‎R-ISPA-PE | ‎Gi0/1 | ‎**R-HFA-EDGE** | ‎**Gi0/1** |
| ‎8 | ‎Straight | ‎R-ISPA-PE | ‎Gi0/2 | ‎SW-ISPA-NET | ‎Gi0/1 |
| ‎9a | ‎Straight | ‎SRV-ISP-DNS | ‎Fa0 | ‎SW-ISPA-NET | ‎Fa0/1 |
| ‎9b | ‎Straight | ‎SRV-ISP-WEB1 | ‎Fa0 | ‎SW-ISPA-NET | ‎Fa0/2 |
| ‎9c | ‎Straight | ‎SRV-ISP-WEB2 | ‎Fa0 | ‎SW-ISPA-NET | ‎Fa0/3 |
| ‎10 | ‎Straight | ‎R-ISPC-PE | ‎Gi0/2 | ‎SW-ISPC-HOME | ‎Gi0/1 |
| ‎11 | ‎Straight | ‎PC-HOME-01 | ‎Fa0 | ‎SW-ISPC-HOME | ‎Fa0/1 |

</div>

✅ ‏13 כבלים. הקצוות בצד הנתבים **אדומים** — זה תקין, פורטים של נתב כבויים עד שמגדירים אותם.
בדקו כל תווית (M6).

---

## משימה 4 — ‏ISP-A: ‏R-ISPA-BR ו-R-ISPA-PE

### 4א — ‏R-ISPA-BR: בסיס וממשקים
👉 **איפה:** ‏**R-ISPA-BR** ‏←‏ CLI ‏←‏ `no` לשאלה ‏←‏ `Router>`‎.

⌨️ מקלידים:
```
enable
configure terminal
hostname R-ISPA-BR
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  ISP-A (AS 100) - AUTHORIZED ACCESS ONLY  *
#
interface gi0/0
 description to R-ISPA-PE
 ip address 200.1.0.1 255.255.255.252
 no shutdown
interface gi0/1
 description eBGP to R-ISPB-BR (AS 200)
 ip address 200.0.12.1 255.255.255.252
 no shutdown
interface gi0/2
 description eBGP to R-ISPC-BR (AS 300)
 ip address 200.0.13.1 255.255.255.252
 no shutdown
 exit
```
🔍 **בודקים עכשיו:** ‏`do show ip interface brief` ‏←‏ ‏Gi0/0, ‏Gi0/1, ‏Gi0/2 עם הכתובות שלהם.
(‏Gi0/1 ו-Gi0/2 נשארים `down` עד שמגדירים את הספקים האחרים — זה בסדר.)

### 4ב — ‏R-ISPA-BR: ‏OSPF בפנים ו-BGP בחוץ
⌨️ מקלידים:
```
ip route 200.1.0.0 255.255.0.0 null0
router ospf 10
 router-id 1.1.1.1
 network 200.1.0.0 0.0.0.3 area 0
 default-information originate always
 exit
router bgp 100
 bgp router-id 1.1.1.1
 neighbor 200.0.12.2 remote-as 200
 neighbor 200.0.13.2 remote-as 300
 network 200.1.0.0 mask 255.255.0.0
 end
copy running-config startup-config
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`ip route 200.1.0.0 255.255.0.0 null0` | נתיב "שומר מקום", כדי שהבלוק יהיה קיים בטבלה |
| ‎`default-information originate always` | "ספר לשכני ה-OSPF שלי: שלחו אליי תעבורה לא מוכרת" |
| ‎`router bgp 100` | "הפעל BGP; אני AS 100" |
| ‎`neighbor 200.0.12.2 remote-as 200` | "הנתב ב-200.0.12.2 נמצא ב-AS 200 — היו שותפי BGP" |
| ‎`network 200.1.0.0 mask 255.255.0.0` | "פרסם את הבלוק שלי לעולם" |

</div>

### 4ג — ‏R-ISPA-PE
👉 **איפה:** ‏**R-ISPA-PE** ‏←‏ CLI ‏←‏ `no` ‏←‏ `Router>`‎.

⌨️ מקלידים:
```
enable
configure terminal
hostname R-ISPA-PE
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  ISP-A (AS 100) - AUTHORIZED ACCESS ONLY  *
#
interface gi0/0
 description to R-ISPA-BR
 ip address 200.1.0.2 255.255.255.252
 no shutdown
interface gi0/1
 description customer: Intel Haifa
 ip address 200.1.1.1 255.255.255.252
 no shutdown
interface gi0/2
 description internet services LAN
 ip address 200.1.100.1 255.255.255.0
 no shutdown
 exit
ip route 200.1.10.0 255.255.255.248 200.1.1.2
router ospf 10
 router-id 1.1.1.2
 passive-interface gi0/1
 passive-interface gi0/2
 network 200.1.0.0 0.0.0.3 area 0
 network 200.1.1.0 0.0.0.3 area 0
 network 200.1.100.0 0.0.0.255 area 0
 redistribute static subnets
 end
copy running-config startup-config
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`ip route 200.1.10.0 255.255.255.248 200.1.1.2` | "בלוק ה-static NAT הציבורי של אינטל חיפה נמצא מאחורי הנתב של הלקוח" |
| ‎`redistribute static subnets` | "שתף את הנתיבים הסטטיים שלי (בלוקי הלקוחות) בתוך OSPF" |

</div>

לחצו **Fast Forward Time**.

✅ ‏‎`%OSPF-5-ADJCHG: Process 10, Nbr 1.1.1.1 ... from LOADING to FULL`.\
🔍 **בודקים עכשיו:** ב-R-ISPA-PE ‏`ping 200.1.0.1` ‏←‏ ‎`!!!!!`‎; ‏`show ip route` ‏←‏ `O*E2 0.0.0.0/0`
(נתיב ברירת המחדל מה-BR).

---

## משימה 5 — ‏ISP-B: ‏R-ISPB-BR ו-R-ISPB-PE
אותו דפוס כמו ISP-A. ההבדלים: ‏AS **‏200**, בלוק **200.2.0.0/16**, ‏router-IDs **‏2.2.2.x**.

### 5א — ‏R-ISPB-BR
👉 **איפה:** ‏**R-ISPB-BR** ‏←‏ CLI ‏←‏ `no` ‏←‏ `Router>`‎.

⌨️ מקלידים:
```
enable
configure terminal
hostname R-ISPB-BR
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  ISP-B (AS 200) - AUTHORIZED ACCESS ONLY  *
#
interface gi0/0
 description to R-ISPB-PE
 ip address 200.2.0.1 255.255.255.252
 no shutdown
interface gi0/1
 description eBGP to R-ISPA-BR (AS 100)
 ip address 200.0.12.2 255.255.255.252
 no shutdown
interface gi0/2
 description eBGP to R-ISPC-BR (AS 300)
 ip address 200.0.23.1 255.255.255.252
 no shutdown
 exit
ip route 200.2.0.0 255.255.0.0 null0
router ospf 10
 router-id 2.2.2.1
 network 200.2.0.0 0.0.0.3 area 0
 default-information originate always
 exit
router bgp 200
 bgp router-id 2.2.2.1
 neighbor 200.0.12.1 remote-as 100
 neighbor 200.0.23.2 remote-as 300
 network 200.2.0.0 mask 255.255.0.0
 end
copy running-config startup-config
```
לחצו **Fast Forward Time** כמה פעמים.

✅ ‏‎`%BGP-5-ADJCHANGE: neighbor 200.0.12.1 Up` — **שותפות ה-BGP הראשונה** שלכם (ISP-A ↔ ISP-B).

### 5ב — ‏R-ISPB-PE
👉 **איפה:** ‏**R-ISPB-PE** ‏←‏ CLI ‏←‏ `no` ‏←‏ `Router>`‎.

⌨️ מקלידים:
```
enable
configure terminal
hostname R-ISPB-PE
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  ISP-B (AS 200) - AUTHORIZED ACCESS ONLY  *
#
interface gi0/0
 description to R-ISPB-BR
 ip address 200.2.0.2 255.255.255.252
 no shutdown
interface gi0/1
 description customer: Intel Jerusalem (step 13)
 ip address 200.2.1.1 255.255.255.252
 no shutdown
interface gi0/2
 description DSL customer: Intel Haifa backup
 ip address 200.2.9.1 255.255.255.252
 no shutdown
 exit
ip route 200.2.10.0 255.255.255.248 200.2.1.2
router ospf 10
 router-id 2.2.2.2
 passive-interface gi0/1
 passive-interface gi0/2
 network 200.2.0.0 0.0.0.3 area 0
 network 200.2.1.0 0.0.0.3 area 0
 network 200.2.9.0 0.0.0.3 area 0
 redistribute static subnets
 end
copy running-config startup-config
```

<div dir="rtl">

> ‏`ip route 200.2.10.0 ...`‎ מצביע על מאגר ה-dynamic NAT של ירושלים (שלב 13). ‏Gi0/1 ו-Gi0/2
> נשארים down עד שלב 12 (‏DSL) ושלב 13 — זה בסדר.

</div>

---

## משימה 6 — ‏ISP-C: ‏R-ISPC-BR ו-R-ISPC-PE
‏AS **‏300**, בלוק **200.3.0.0/16**, ‏router-IDs **‏3.3.0.x**.

### 6א — ‏R-ISPC-BR
👉 **איפה:** ‏**R-ISPC-BR** ‏←‏ CLI ‏←‏ `no` ‏←‏ `Router>`‎.

⌨️ מקלידים:
```
enable
configure terminal
hostname R-ISPC-BR
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  ISP-C (AS 300) - AUTHORIZED ACCESS ONLY  *
#
interface gi0/0
 description to R-ISPC-PE
 ip address 200.3.0.1 255.255.255.252
 no shutdown
interface gi0/1
 description eBGP to R-ISPA-BR (AS 100)
 ip address 200.0.13.2 255.255.255.252
 no shutdown
interface gi0/2
 description eBGP to R-ISPB-BR (AS 200)
 ip address 200.0.23.2 255.255.255.252
 no shutdown
 exit
ip route 200.3.0.0 255.255.0.0 null0
router ospf 10
 router-id 3.3.0.1
 network 200.3.0.0 0.0.0.3 area 0
 default-information originate always
 exit
router bgp 300
 bgp router-id 3.3.0.1
 neighbor 200.0.13.1 remote-as 100
 neighbor 200.0.23.1 remote-as 200
 network 200.3.0.0 mask 255.255.0.0
 end
copy running-config startup-config
```

### 6ב — ‏R-ISPC-PE (‏dual-stack: ‏IPv4 + ‏IPv6 לכיוון הלקוחות שלו)
👉 **איפה:** ‏**R-ISPC-PE** ‏←‏ CLI ‏←‏ `no` ‏←‏ `Router>`‎.

⌨️ מקלידים:
```
enable
configure terminal
hostname R-ISPC-PE
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  ISP-C (AS 300) - AUTHORIZED ACCESS ONLY  *
#
ipv6 unicast-routing
interface gi0/0
 description to R-ISPC-BR
 ip address 200.3.0.2 255.255.255.252
 no shutdown
interface gi0/1
 description customer: Intel Kiryat Gat (step 14)
 ip address 200.3.1.1 255.255.255.252
 ipv6 address 2001:DB8:C:1::1/64
 no shutdown
interface gi0/2
 description home users
 ip address 200.3.50.1 255.255.255.0
 ipv6 address 2001:DB8:C:50::1/64
 ipv6 address FE80::1 link-local
 no shutdown
 exit
router ospf 10
 router-id 3.3.0.2
 passive-interface gi0/1
 passive-interface gi0/2
 network 200.3.0.0 0.0.0.3 area 0
 network 200.3.1.0 0.0.0.3 area 0
 network 200.3.50.0 0.0.0.255 area 0
 end
copy running-config startup-config
```

<div dir="rtl">

> שורות ה-IPv6 מכינות את ISP-C לקריית גת בשלב 14. הקלידו אותן עכשיו; תשתמשו בהן בהמשך.

</div>

לחצו **Fast Forward Time** כמה פעמים (‏BGP איטי בהתחלה).

---

## משימה 7 — בודקים BGP וקוראים את טבלת ה-BGP
👉 **איפה:** ‏**R-ISPA-BR** (שורת הפקודה `R-ISPA-BR#`‎).

### 7א — האם השותפים מדברים?
⌨️ ‏`show ip bgp summary`
```
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
200.0.12.2      4   200      10      10        4    0    0 00:02:10        2
200.0.13.2      4   300      10      10        4    0    0 00:02:05        2
```
✅ ה**עמודה האחרונה היא מספר** ‏←‏ השותפות פעילה.\
❌ ‏`Active` או `Idle` = לא פעילה ‏←‏ קודם עשו ping לכתובת של השכן. אם הפינג נכשל: בעיה בכבל או
בממשק. אם הפינג עובד: ‏IP של `neighbor` או מספר AS שגויים.

עשו אותו דבר ב-**R-ISPB-BR** וב-**R-ISPC-BR**. סמנו (2 מספרים בכל אחד):
- [ ] ‏ISPA-BR
- [ ] ‏ISPB-BR
- [ ] ‏ISPC-BR

### 7ב — קוראים את טבלת ה-BGP
⌨️ ‏`show ip bgp`
```
   Network          Next Hop            Metric LocPrf Weight Path
*> 200.1.0.0/16     0.0.0.0                  0         32768 i
*> 200.2.0.0/16     200.0.12.2               0             0 200 i
*  200.3.0.0/16     200.0.12.2                             0 200 300 i
*>                  200.0.13.2               0             0 300 i
```
איך קוראים אותה:
- ‏‎`*>`‎ = הדרך ה**טובה ביותר** (זו שבשימוש).
- ‏`Path` = רשימת ה-ASים שבדרך. ‏`i` בסוף = "הגיע מתוך ה-AS הזה".
- ל-‎`200.3.0.0` יש **שתי** דרכים: ישירה (‎`300`) ודרך ISP-B ‏(‎`200 300`). הקצרה מנצחת; הארוכה היא
  הגיבוי.

📝 במחברת: "כדי להגיע ל-ISP-C, ‏ISP-A הולך ______; אם הקישור הזה נשבר הוא הולך ______."

---

## משימה 8 — שרתי האינטרנט והמחשב הביתי

### 8א — הגדרות IP (איך? ‏←‏ M14)
‏Desktop ‏←‏ IP Configuration ‏←‏ **Static**:

<div dir="rtl">

| מכשיר | ‎IP | ‎Mask | ‎Gateway | ‎DNS |
|---|---|---|---|---|
| ‎SRV-ISP-DNS | ‎200.1.100.10 | ‎255.255.255.0 | ‎200.1.100.1 | ‎200.1.100.10 |
| ‎SRV-ISP-WEB1 | ‎200.1.100.11 | ‎255.255.255.0 | ‎200.1.100.1 | ‎200.1.100.10 |
| ‎SRV-ISP-WEB2 | ‎200.1.100.12 | ‎255.255.255.0 | ‎200.1.100.1 | ‎200.1.100.10 |
| ‎PC-HOME-01 | ‎200.3.50.10 | ‎255.255.255.0 | ‎200.3.50.1 | ‎200.1.100.10 |

</div>

### 8ב — שירותים (איך? ‏←‏ M20)
- ‏**SRV-ISP-DNS** ‏←‏ Services ‏←‏ DNS **On** ‏←‏ מוסיפים רשומות A:

  | Name | Address |
  |---|---|
  | `www.isp-web1.com` | 200.1.100.11 |
  | `www.isp-web2.com` | 200.1.100.12 |
  | `www.intel.lab` | **‏200.1.10.3** ‏←‏ הכתובת ה**ציבורית** של האתר שלנו! |

  את שאר השירותים מעבירים ל-**Off**.
- ‏**SRV-ISP-WEB1** ‏←‏ Services ‏←‏ HTTP ‏←‏ `index.html` ‏←‏ **(edit)** ‏←‏ ‎`<h1>ISP Web Server 1</h1>`‎ ‏←‏ **Save**.
- ‏**SRV-ISP-WEB2** ‏←‏ אותו דבר עם ‎`<h1>ISP Web Server 2</h1>`‎.
- ‏`SW-ISPA-NET` ו-`SW-ISPC-HOME`: רק שמות — לא צריך הגדרות.

🔍 **בודקים עכשיו:** ‏PC-HOME-01 ‏←‏ **Web Browser** ‏←‏ `http://www.isp-web1.com` ‏←‏ **Go** ‏←‏
‏"ISP Web Server 1". ✅ האינטרנט עובד **דרך 3 ASים** (המחשב הביתי ב-AS 300, השרת ב-AS 100).

❌ **אם זה נכשל:** ‏`ping 200.1.100.11` מ-PC-HOME-01. הפינג נכשל ‏←‏ ‏BGP (משימה 7). הפינג עובד אבל
השם נכשל ‏←‏ רשומת ה-DNS או הגדרת ה-DNS של המחשב.

---

## משימה 9 — ‏R-HFA-EDGE: קישור ה-WAN וניתוב
👉 **איפה:** ‏**R-HFA-EDGE** ‏←‏ CLI ‏←‏ נכנסים (`admin` / `Intel#Adm1n`) ‏←‏ `R-HFA-EDGE#`‎.

⌨️ מקלידים:
```
configure terminal
interface gi0/1
 description PRIMARY to R-ISPA-PE
 ip address 200.1.1.2 255.255.255.252
 no shutdown
 exit
ip route 0.0.0.0 0.0.0.0 200.1.1.1
```
🔍 **בודקים עכשיו:** ‏`do ping 200.1.100.11` ‏←‏ ‎`!!!!!`‎ — נתב הקצה עצמו מגיע לאינטרנט.

אבל נסו ממחשב **Engineering**: ‏`ping 200.1.100.11` ‏←‏ ❌ ‏timed out.\
🧠 **למה?** החבילה יוצאת עם כתובת מקור ‎`10.10.16.x` — כתובת פרטית. לאינטרנט אין נתיב חזרה
ל-10.x. צריך NAT.

---

## משימה 10 — ‏R-HFA-EDGE: ‏PAT כדי שהעובדים יוכלו לגלוש
👉 **איפה:** ‏R-HFA-EDGE, שורת הפקודה `R-HFA-EDGE(config)#`‎.

### 10א — מסמנים את הצד הפנימי ואת הצד החיצוני
⌨️ מקלידים:
```
interface gi0/0
 ip nat inside
interface gi0/1
 ip nat outside
 exit
```

### 10ב — מי מתורגם, ולמה
⌨️ מקלידים:
```
ip access-list extended NAT-HFA
 remark --- remote-access VPN users are NOT translated (step 15) ---
 deny ip 10.10.0.0 0.0.255.255 172.16.250.0 0.0.0.255
 permit ip 10.10.0.0 0.0.255.255 any
 exit
ip nat inside source list NAT-HFA interface gi0/1 overload
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`ip nat inside` / `ip nat outside` | איזה צד של הנתב פרטי / ציבורי |
| ‎`ip nat inside source list NAT-HFA interface gi0/1 overload` | "תרגם את כל מי שברשימה לכתובת של Gi0/1, בעזרת פורטים" = **PAT** |

</div>

🔍 **בודקים עכשיו:**
1. ממחשב ENG: ‏`ping 200.1.100.11` ‏←‏ ✅ עכשיו יש תשובות.
2. ב-R-HFA-EDGE: ‏`do show ip nat translations` ‏←‏ שורה כמו
   ‏`icmp 200.1.1.2:5   10.10.16.11:5   200.1.100.11:5 ...`‎ — הכתובת הפנימית מימין, הכתובת
   הציבורית המשותפת משמאל.
3. מחשב ENG ‏←‏ Web Browser ‏←‏ `http://www.isp-web1.com` ‏←‏ ✅.

---

## משימה 11 — ‏Static NAT + חורים ב-ASA: האינטרנט רואה את האתר שלנו
🧠 **למה:** ‏PAT מאפשר רק **לנו** להתחיל שיחות. מבקר באינטרנט לא יכול להתחיל שיחה אל
10.10.200.13 — ולכן נותנים לשרת ה-web כתובת ציבורית קבועה.

### 11א — ב-R-HFA-EDGE
⌨️ מקלידים:
```
ip nat inside source static 10.10.200.13 200.1.10.3
ip nat inside source static udp 10.10.200.14 123 200.1.10.4 123
 end
copy running-config startup-config
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`ip nat inside source static 10.10.200.13 200.1.10.3` | "השרת הזה הוא תמיד הכתובת הציבורית הזו" = **static NAT** |
| ‎`... static udp 10.10.200.14 123 200.1.10.4 123` | מפרסמים רק את פורט 123 ‏(NTP) של שרת ה-NTP |

</div>

### 11ב — ב-ASA-HFA-FW1: פותחים את החורים
👉 **איפה:** ‏ASA ‏←‏ `enable` ‏←‏ סיסמה `Intel#En4ble` ‏←‏ `ASA-HFA-FW1#`‎.

⌨️ מקלידים:
```
configure terminal
access-list OUTSIDE_IN extended permit tcp any host 10.10.200.13 eq www
access-list OUTSIDE_IN extended permit udp any host 10.10.200.14 eq ntp
end
write memory
```

<div dir="rtl">

> ה-ASA רואה את הכתובת ה**אמיתית** של השרת — נתב הקצה כבר תרגם אותה בחזרה.

</div>

🔍 **בודקים עכשיו:**

<div dir="rtl">

| מאיפה | עושים | צפוי |
|---|---|---|
| ‎PC-HOME-01 | ‎‏Web Browser ‏←‏ `http://www.intel.lab` | ✅ ‏"Intel Israel - Intranet" — דרך 200.1.10.3 |
| ‎PC-HOME-01 | ‎`ping 10.10.16.1` | ❌ כתובות פרטיות לא קיימות באינטרנט |
| ‎LT-HFA-GUEST-01 | ‎‏Web Browser ‏←‏ `http://www.isp-web2.com` | ✅ לאורחים יש עכשיו אינטרנט (שלב 10) |
| ‎R-HFA-EDGE | ‎`show ip nat translations` | שורות PAT + שתי השורות הסטטיות (‎`200.1.10.3`, ‏‎`200.1.10.4`) |

</div>

❌ **אם המחשב הביתי לא מקבל דף:** בדקו בסדר הזה: רשומת ה-DNS של הספק (‎`200.1.10.3`);
‏`ip route 200.1.10.0 ...`‎ + ‏`redistribute static subnets` ב-R-ISPA-PE; שורת ה-`www` ב-ASA.

---

## משימה 12 — מודם ה-DSL והענן
🧠 **למה:** קו שני דרך ספק **אחר**. אם הקישור של ISP-A מת, לחיפה עדיין יש דרך החוצה.

### 12א — כבלים (זהירות: כבל הטלפון!)

<div dir="rtl">

| ‎# | כבל | לוחצים קודם על | פורט | לוחצים אחר כך על | פורט |
|---|---|---|---|---|---|
| ‎12 | ‎Straight | ‎R-HFA-EDGE | ‎**Gi0/2** | ‎DSL-HFA | ‎**Port 1** (Ethernet) |
| ‎13 | **Phone** (הקו השחור הדק ב-Connections) | ‎DSL-HFA | ‎**Port 0** | ‎CLOUD-DSL | ‎**Modem4** |
| ‎14 | ‎Straight | ‎CLOUD-DSL | ‎**Ethernet6** | ‎R-ISPB-PE | ‎**Gi0/2** |

</div>

### 12ב — אומרים לענן לחבר את המודם ל-ISP-B
👉 ‏CLOUD-DSL ‏←‏ לשונית **Config** ‏←‏ ברשימה משמאל **DSL** ‏←‏ *From Port* ‏**Modem4**, *To Port*
‏**Ethernet6** ‏←‏ **Add**.

✅ בטבלה מופיעה שורה `Modem4 ↔ Ethernet6`.

### 12ג — נתב הקצה: ממשק הגיבוי וה-floating static route
👉 **איפה:** ‏R-HFA-EDGE ‏←‏ `configure terminal`.

⌨️ מקלידים:
```
interface gi0/2
 description BACKUP via DSL to R-ISPB-PE
 ip address 200.2.9.2 255.255.255.252
 ip nat outside
 no shutdown
 exit
ip route 0.0.0.0 0.0.0.0 200.2.9.1 10
 end
copy running-config startup-config
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`ip route 0.0.0.0 0.0.0.0 200.2.9.1 10` | נתיב ברירת מחדל לגיבוי (floating static, ‏distance 10) |

</div>

🔍 **בודקים עכשיו:**
1. ‏`ping 200.2.9.1` ‏←‏ ‎`!!!!!`‎ (קו ה-DSL עובד).
2. ‏`show ip route static` ‏←‏ **רק** `S* 0.0.0.0/0 [1/0] via 200.1.1.1` — הגיבוי מוסתר. זה נכון:
   הוא מחכה.

❌ **אם קישור ה-DSL אדום:** המיפוי בענן (12ב) חסר, או שכבל הטלפון בפורט הלא נכון של המודם.

---

## משימה 13 — בדיקות יתירות

### 13א — המשולש של BGP
1. ב-**R-ISPA-BR**: ‏`configure terminal` ‏←‏ `interface gi0/2` ‏←‏ `shutdown` ‏←‏ `end`.
2. ‏Fast Forward Time (בערך דקה). ‏`show ip bgp` ‏←‏ ל-200.3.0.0/16 יש עכשיו רק ‎`200 300`.
3. ‏PC-HOME-01 ‏←‏ Web Browser ‏←‏ `http://www.intel.lab` ‏←‏ עדיין ✅ (הדרך הארוכה).
4. מחזירים: `configure terminal` ‏←‏ `interface gi0/2` ‏←‏ `no shutdown` ‏←‏ `end`.

### 13ב — גיבוי ה-DSL
1. ב-R-HFA-EDGE: ‏`ping 200.2.0.1 repeat 1000` (עוצרים אחר כך עם **Ctrl+Shift+6**).
2. שוברים את הקו הראשי: `configure terminal` ‏←‏ `interface gi0/1` ‏←‏ `shutdown` ‏←‏ `end`.
3. ‏`show ip route static` ‏←‏ `S* 0.0.0.0/0 [10/0] via 200.2.9.1` — הגיבוי השתלט, דרך המודם.
4. ‏`configure terminal` ‏←‏ `interface gi0/1` ‏←‏ `no shutdown` ‏←‏ `end` ‏←‏ הקו הראשי חוזר
   (‎`[1/0] via 200.1.1.1`).

<div dir="rtl">

> מגבלה: ה-PAT קשור ל-Gi0/1, ולכן ה**משתמשים** לא גולשים דרך ה-DSL — ראו תרגיל ב.

</div>

💾 ‏`copy running-config startup-config` בכל הנתבים, ‏`write memory` ב-ASA ‏←‏ **File → Save**.

---

## משימה 14 — תצוגה פיזית: עיר "Internet" לספקים
🧠 **למה:** הספקים **לא** נמצאים בחיפה — הם חברות אחרות, במקום אחר. בתצוגה הפיזית הם מקבלים עיר
משלהם. (רקע: [sites-and-views.md](../../docs/sites-and-views.md).)

<div dir="rtl">

| בניין (בעיר `Internet`) | מכשירים |
|---|---|
| ‎`ISP-A` | ‎R-ISPA-BR, R-ISPA-PE, SW-ISPA-NET, SRV-ISP-DNS, SRV-ISP-WEB1, SRV-ISP-WEB2 |
| ‎`ISP-B` | ‎R-ISPB-BR, R-ISPB-PE, CLOUD-DSL |
| ‎`ISP-C` | ‎R-ISPC-BR, R-ISPC-PE |
| ‎`Home` | ‎SW-ISPC-HOME, PC-HOME-01 |

</div>

‏**DSL-HFA נשאר בחיפה** ‏(HFA Data Center) — המודם עומד אצל הלקוח, לא אצל הספק.

### 14א — העיר והבניינים שלה (איך? ‏←‏ M25)
1. הלשונית **Physical** ‏←‏ בסרגל לוחצים **Intercity**.
2. לוחצים **New City** ‏←‏ היא מופיעה למעלה משמאל ‏←‏ גוררים אותה לצד הימני של המפה ‏←‏ לוחצים על
   השם שלה ‏←‏ מקלידים `Internet` ‏←‏ **Enter**.
3. לוחצים על העיר **Internet** ‏←‏ **New Building** ‏4 פעמים ‏←‏ גוררים כל אחד למקום פנוי ‏←‏ משנים
   את השמות ל-`ISP-A`, ‏`ISP-B`, ‏`ISP-C`, ‏`Home`.

(בלי ארונות תקשורת כאן — האינטרנט לא שלנו, רק מראים איזו חברה מחזיקה מה.)

### 14ב — מעבירים את המכשירים (איך? ‏←‏ M26)
1. בסרגל לוחצים **Navigation**.
2. המכשירים החדשים נמצאים ב-**Haifa ‏←‏ HFA Data Center** (נתבים ומתגים ב-**Main Wiring Closet**
   שלו, שרתים והמחשב בבניין עצמו). גוררים כל אחד אל הבניין שלו תחת **Internet** (הטבלה למעלה).
3. סוגרים את החלון.

✅ ב-**Intercity** רואים עכשיו שתי ערים, Haifa ו-Internet, מחוברות בקו (קישורי ה-WAN).
סמנו:
- [ ] ‏ISP-A
- [ ] ‏ISP-B
- [ ] ‏ISP-C
- [ ] ‏Home

### 14ג — בודקים ששום דבר לא נשבר
הלשונית **Logical** ‏←‏ ‏PC-HOME-01 ‏←‏ Web Browser ‏←‏ `http://www.intel.lab` ‏←‏ ✅.

❌ **הקישורים בין Haifa ל-Internet נפלו:** אפקט אורך הכבל דלוק — **Options ‏←‏ Preferences ‏←‏
Interface** ‏←‏ מורידים את הסימון מ-*Enable Cable Length Effects* ‏(M26).

💾 ‏**File → Save**.

---

## נקודת ביקורת
- [ ] ‏6 שותפויות BGP פעילות (2 לכל BR)
- [ ] המחשבים בחיפה גולשים לשני שרתי ה-web של הספק
- [ ] המחשב הביתי פותח את www.intel.lab
- [ ] תרגומי NAT נראים ב-R-HFA-EDGE
- [ ] נתיב הגיבוי של ה-DSL מופיע כשהראשי למטה
- [ ] תצוגה פיזית: עיר Internet עם ISP-A, ‏ISP-B, ‏ISP-C ו-Home

## אם משהו לא עובד

<div dir="rtl">

| בעיה | פתרון |
|---|---|
| שכן BGP תקוע ב-**Active/Idle** | ‏IP או מספר AS שגוי של השכן, או שהקישור למטה (‏`show ip interface brief`). קודם עשו ping לשכן |
| בלוק חסר ב-`show ip bgp` | ה-`network ... mask` לא תואם **בדיוק** לנתיב — בדקו את נתיב ה-null0 ואת המסיכה |
| חיפה לא גולשת אבל נתב הקצה כן | חסר `ip nat inside` על Gi0/0, או שה-ACL של ה-NAT לא תופסת את 10.10.x |
| המחשב הביתי לא פותח את www.intel.lab | רשומת ה-DNS של הספק (חייבת להיות 200.1.10.3); ‏`ip route 200.1.10.0 ...`‎ + ‏`redistribute static subnets` ב-R-ISPA-PE; שורת ה-ACL ל-www ב-ASA |
| קישור ה-DSL אדום | חסר המיפוי של ה-DSL בענן (משימה 12ב), או שכבל הטלפון בפורט הלא נכון של המודם |
| קישור של נתב אדום אחרי ההגדרה | חסר `no shutdown`, או שהשתמשתם ב-Straight-Through בין שני נתבים (חייב להיות Cross-Over) |

</div>

---

## 🏋 תרגילים

### תרגיל א — מספר AS שגוי ⭐⭐
- 🎯 **המשימה:** לראות איך נראית שגיאת כתיב ב-BGP ולמצוא אותה רק עם פקודות `show`.
- 📁 **מתחילים מ:** ‏`step12.pkt` ‏←‏ **Save As** ‏`step12-exA.pkt`.
- 👣 **צעדים:**
  1. ב-R-ISPB-BR: ‏`configure terminal` ‏←‏ `router bgp 200` ‏←‏ `no neighbor 200.0.23.2 remote-as 300`
     ‏←‏ `neighbor 200.0.23.2 remote-as 333` ‏←‏ `end`.
  2. ‏Fast Forward Time. ב-R-ISPB-BR: ‏`show ip bgp summary`. ב-R-ISPC-BR: אותו דבר.
  3. תקנו בחזרה.
- ✅ **גמרתם כש**אתם יודעים לומר איזו עמודה הראתה את הבעיה ואיזו הודעה הופיעה.

<details dir="rtl"><summary>💡 רמז</summary>

הסתכלו על העמודה האחרונה של `show ip bgp summary` ועל ההודעות ב-console ‏(‎`%BGP-3-NOTIFICATION`).
</details>
<details dir="rtl"><summary>✔ תשובה</summary>

השכן נשאר ב-`Active`/`Idle` במקום מספר. ‏R-ISPC-BR אומר שהוא AS 300, ‏R-ISPB-BR מצפה ל-333 ‏←‏ השיחה
נדחית ("bad remote AS"). שני הצדדים חייבים להסכים על **ה-IP וה-AS**. המשולש עדיין עובד דרך ISP-A,
ולכן האינטרנט לא נשבר — זו יתירות.
</details>

### תרגיל ב — גם המשתמשים גולשים דרך ה-DSL ⭐⭐⭐
- 🎯 **המשימה:** לגרום גם ל**משתמשים** לשרוד נפילה של הקישור הראשי, על ידי הוספת כלל PAT שני
  ל-Gi0/2.
- 📁 **מתחילים מ:** ‏`step12.pkt` ‏←‏ **Save As** ‏`step12-exB.pkt`.
- 👣 **צעדים:** כבו את Gi0/1, נסו לגלוש ממחשב (נכשל). מצאו דרך שיהיו שני כללי PAT.
- ✅ **גמרתם כש**כש-Gi0/1 כבוי, מחשב ENG פותח את `http://www.isp-web1.com` — או שכתבתם בספר למה PT סירב.

<details dir="rtl"><summary>💡 רמז</summary>

שני כללי `ip nat inside source list` עם אותה ACL מתנגשים — השתמשו ב-**route-maps** שתופסות את
ה-ACL **וגם** את ממשק היציאה.
</details>
<details dir="rtl"><summary>✔ תשובה</summary>

<div dir="ltr">

```
route-map NAT-PRIMARY permit 10
 match ip address NAT-HFA
 match interface gi0/1
route-map NAT-BACKUP permit 10
 match ip address NAT-HFA
 match interface gi0/2
no ip nat inside source list NAT-HFA interface gi0/1 overload
ip nat inside source route-map NAT-PRIMARY interface gi0/1 overload
ip nat inside source route-map NAT-BACKUP interface gi0/2 overload
```

</div>

התמיכה של Packet Tracer ב-`ip nat ... route-map` תלויה בגרסה. אם הפקודה נדחית, כתבו בספר הפרויקט
שגיבוי ה-DSL משרת את הנתב עצמו, ושבעולם האמיתי הפתרון הוא NAT עם route-map.
</details>

---

## 🛠 הפרויקט שלכם

עשיתם את השלב הזה על הדוגמה של אינטל. עכשיו עשו אותו שוב בפרויקט **שלכם**, עם הערכים
מהתוכנית **שלכם** (`my-project/plan.md`). הפקודות זהות — רק הערכים משתנים.

- [ ] פותחים את `my-project/step11.pkt` ‏←‏ **Save As** ‏`my-project/step12.pkt`
- [ ] קודם כותבים את טבלת כתובות ה-WAN שלכם (כמו 1.7) עם מספרי ה-AS והבלוקים שלכם
- [ ] מציבים ומחברים את 6 נתבי הספקים, השרתים והמחשב הביתי
- [ ] מגדירים את 3 הספקים; כל שותפויות ה-BGP מראות מספר
- [ ] שרתי אינטרנט + DNS (עם הכתובת ה**ציבורית** של האתר שלכם)
- [ ] נתב הקצה: קישור WAN, נתיב ברירת מחדל, ‏PAT, ‏static NAT; חורים ב-ASA
- [ ] גיבוי DSL + floating static; שתי בדיקות היתירות
- [ ] תצוגה פיזית: עיר Internet עם בניין לכל ספק + Home (משימה 14)

<div dir="rtl">

| בדוגמה | בפרויקט שלכם — לוקחים מ |
|---|---|
| מספרי ה-AS של הספקים 100 / 200 / 300 | מספרי AS משלכם |
| בלוקים ציבוריים ‎`200.1/2/3.0.0/16`, בין הספקים ‎`200.0.0.0/16` | תוכנית, חלק ג (בלוקי הספקים שלכם) |
| ‏Static NAT לשרתי ה-web וה-NTP, ‏PAT לגלישה | תוכנית, חלק ה (שורת ה-NAT — static באתר אחד, dynamic באתר אחר, overload בשלישי — דרישה 10) |
| גיבוי DSL עם floating static route | תוכנית, חלק ה (שורת גיבוי ה-WAN) |
| ניתוב סטטי מהאתר ל-WAN | להשאיר — משרד החינוך דורש (דרישה 22.17) |

</div>

**בדיקה:** ‏`show ip bgp summary` מראה שכל שכן במצב established; מחשב פנימי פותח דף אינטרנט;
‏`show ip nat translations` מציג את הכתובות שלכם.

💾 שמרו בשם `my-project/step12.pkt`.

---

## 🎓 מסבירים לבוחן

בבחינה, הבוחן מצביע על הפרויקט **שלכם** ומבקש **להסביר** ו**להראות**. תרגלו כל שאלה
**בקול**, ואז הראו את התשובה בפרויקט שלכם — לא בדוגמה. כסו את התשובה, ענו בעצמכם, ורק אז
פתחו והשוו.

★1–★3 = שאלה ממאגר השאלות של משרד החינוך (רמת קושי 1–3).
◆ = לא במאגר, אבל בוחנים שואלים אותה לעיתים קרובות.

**1. ★1 מה תפקידו של NAT? מהם 3 הסוגים ובמה הם שונים?**

<details dir="rtl"><summary>תשובה</summary>

‏NAT מתרגם כתובות פרטיות לציבוריות (ובחזרה), כדי שרשתות פרטיות יוכלו להגיע לאינטרנט וכדי לחסוך
כתובות ציבוריות. **‏Static**: פרטית אחת ↔ ציבורית אחת, קבוע — לשרת שהאינטרנט חייב להגיע אליו.
**‏Dynamic**: כתובות פרטיות לוקחות כתובת פנויה ממאגר של כתובות ציבוריות. **‏Overload ‏(PAT)**: הרבה
כתובות פרטיות חולקות כתובת ציבורית אחת, ומופרדות לפי מספרי פורט.

**איפה מראים:** `show running-config | include nat`, `show ip nat translations`
</details>

**2. ★1 מהו PAT?**

<details dir="rtl"><summary>תשובה</summary>

‏Port Address Translation ‏(NAT overload): הרבה מחשבים פנימיים חולקים IP ציבורי אחד; הנתב מבדיל בין
השיחות שלהם לפי מספר פורט המקור.

**איפה מראים:** `show ip nat translations` ‏←‏ אותו IP ציבורי עם פורטים שונים
</details>

**3. ★1 הצג את הגדרות ה-NAT בפרויקט שלך.**

<details dir="rtl"><summary>תשובה</summary>

‏`ip nat inside` / `ip nat outside` על הממשקים; ‏`ip nat inside source static …`‎ לכל שרת שמפורסם;
ה-ACL של הכתובות הפנימיות + ‏`ip nat inside source list … interface … overload` לגלישה.

**איפה מראים:** `show running-config`, `show ip nat translations`
</details>

**4. ★2 איזו פקודה מציגה את טבלת הניתוב של BGP?**

<details dir="rtl"><summary>תשובה</summary>

‏`show ip bgp` (טבלת BGP); ‏`show ip bgp summary` (השכנים והמצב שלהם).

**איפה מראים:** בנתב של ספק
</details>

**5. ★2 מה ההבדל בין IGP ל-EGP? מהי מערכת אוטונומית (AS)?**

<details dir="rtl"><summary>תשובה</summary>

‏AS הוא רשת תחת ניהול אחד עם מדיניות ניתוב אחת, שמזוהה במספר AS. ‏IGP ‏(OSPF, ‏EIGRP) מנתב **בתוך**
AS; ‏EGP ‏(BGP) מנתב **בין** ASים.

**איפה מראים:** `show ip bgp summary` ‏←‏ מספרי AS
</details>

**6. ★2 מה ההבדל בין iBGP ל-eBGP?**

<details dir="rtl"><summary>תשובה</summary>

‏eBGP: בין נתבים ב-ASים **שונים** (administrative distance ‏20). ‏iBGP: בין נתבים **באותו** AS
‏(administrative distance ‏200).

**איפה מראים:** `show ip bgp summary`
</details>

**7. ★2 איזו תכונה (attribute) של BGP מונעת לולאות?**

<details dir="rtl"><summary>תשובה</summary>

‏AS_PATH: רשימת ה-ASים שהנתיב עבר דרכם. נתב שרואה את מספר ה-AS שלו בנתיב דוחה את הנתיב.

**איפה מראים:** `show ip bgp` ‏←‏ העמודה Path
</details>

**8. ★3 איזו תכונה קובעת את נקודת היציאה מה-AS? מהם MED ו-Weight?**

<details dir="rtl"><summary>תשובה</summary>

‏LOCAL_PREF קובע איזה נתב הוא ה**יציאה** מה-AS שלכם (הגבוה מנצח, משותף בתוך ה-AS). ‏MED אומר ל-**AS
שכן** איזו כניסה ל-AS שלכם אתם מעדיפים (הנמוך מנצח). ‏Weight קיים רק אצל Cisco, מקומי לנתב אחד,
ונבדק ראשון (הגבוה מנצח).

**איפה מראים:** —
</details>

**9. ◆ למה הניתוב מהאתר ל-WAN סטטי ולא דרך ה-IGP? מהו floating static route?**

<details dir="rtl"><summary>תשובה</summary>

כדי שמידע הניתוב הפנימי לא ייחשף לספק, ושהספק לא יוכל להכניס נתיבים לחברה (דרישה 22.17). ‏Floating
static route הוא נתיב גיבוי עם administrative distance גבוה יותר (למשל ‎`… 10`): משתמשים בו רק כשהנתיב
הראשי נעלם — כאן, קו הגיבוי של ה-DSL.

**איפה מראים:** `show ip route static`; כבו את הקישור הראשי והסתכלו שוב
</details>

---

## 🔁 עושים שוב — בלי המדריך

הבוחן יכול לבקש מכם להגדיר משהו שוב, מולו. תצליחו רק אם עשיתם את זה **בלי המדריך** לפני כן.
עשו את התרגיל הזה בפרויקט שלכם:

בעותק של הקובץ שלכם, מחקו את שורות ה-NAT מנתב הקצה. בלי העמוד הזה, כתבו אותן שוב מתוך התוכנית
שלכם (inside/outside, ‏static NAT לשרת שלכם, ‏PAT לגלישה). יעד: **‏10 דקות**. אחר כך גלשו ממחשב, פתחו
את השרת שלכם מצד האינטרנט, והראו `show ip nat translations`. הסבירו שכן BGP אחד עם
`show ip bgp summary`.

---

## 👩‍🏫 הערות למורה
- **שיעור 1:** האינטרנט כרשת של ASים; ‏BGP מול OSPF (כבישים בינלאומיים מול כבישי עיר); בנייה
  וחיווט (14 כבלים!) ‏←‏ הגדרת ISP-A.
- **שיעור 2:** ‏ISP-B ו-ISP-C ‏←‏ בדיקות BGP (‏`show ip bgp`, קריאת ה-AS path) ‏←‏ בדיקת משולש ה-BGP.
- **שיעור 3:** סוגי NAT עם ההשוואה למרכזיה ‏←‏ NAT בנתב הקצה ‏←‏ החורים ב-ASA ‏←‏ בדיקות משימות 10–11.
- **שיעור 4:** מודם DSL + ענן + ‏floating static ‏←‏ בדיקת הגיבוי ‏←‏ אתגר.
- **מראים NAT במצב Simulation:** ‏ping ממחשב ל-200.1.100.11, לוחצים על החבילה לפני ואחרי R-HFA-EDGE —
  כתובת המקור משתנה מ-10.10.16.x ל-200.1.1.2.
- **שאלות נפוצות של תלמידים**
  - *"למה BGP לוקח כל כך הרבה זמן?"* — הוא מתוכנן ליציבות, לא למהירות. לחצו Fast Forward.
  - *"למה לא להריץ OSPF מול הספק?"* — היינו מספרים לאינטרנט את המפה הפנימית שלנו — בעיה של אבטחה
    ושל יציבות. נתיב ברירת מחדל סטטי אחד מספיק.
- **טעויות אופייניות:** ‏cross-over מול straight בין נתבים; מספרי AS עם שגיאת כתיב; שכחת `ip nat inside`
  על הממשק הפנימי.
