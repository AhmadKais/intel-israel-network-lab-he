# שלב 13 — ירושלים: ‏collapsed core, ‏EIGRP, שרת DHCP, ‏dynamic NAT, ‏CBAC

<div dir="rtl">

> ⏱ ‏4 שיעורים · 🎯 דרישות משרד החינוך 5, ‏10 (dynamic), ‏17, ‏20.x, ‏22.11, ‏22.13, ‏22.14, ‏22.15, ‏22.18\
> 📁 מתחילים מ: `my-work/step12.pkt`\
> 💾 שומרים בשם: `my-work/step13.pkt`

</div>

<div dir="rtl">

> ✅ **לפני שמתחילים:** כל הסעיפים בנקודת הביקורת של שלב 12 מסומנים, ועשיתם את
> תרגיל ה-🔁 שלו בפרויקט שלכם. אל תדלגו על שלבים — כל שלב בנוי על הקובץ של השלב הקודם.

</div>

## 🗺 המשימות שלכם בשלב הזה
**שיעור 1 — בונים**
- [ ] **משימה 1** — פותחים את שלב 12, שומרים בשם שלב 13, מציירים את הסניף (3 דקות)
- [ ] **משימה 2** — מציבים את המכשירים (עם 2 ספקי כוח!) (15 דקות)
- [ ] **משימה 3** — מחברים את ציוד הרשת בכבלים (15 דקות)
- [ ] **משימה 4** — מחברים את מכשירי הקצה בכבלים (15 דקות)

**שיעור 2 — ה-collapsed core**
- [ ] **משימה 5** — ‏CC1, חלק 1: הקשחה, ‏VTP, ‏VLANים, ‏STP, ‏PAgP, ‏trunks ‏(15 דקות)
- [ ] **משימה 6** — ‏CC1, חלק 2: שערים + ‏DHCP relay ‏(15 דקות)
- [ ] **משימה 7** — ‏CC1, חלק 3: ‏EIGRP וניהול (15 דקות)
- [ ] **משימה 8** — ‏CC2: תמונת המראה של CC1 ‏(30 דקות)

**שיעור 3 — ‏access, שרתים, ‏DHCP**
- [ ] **משימה 9** — שלושת מתגי הקומות (30 דקות)
- [ ] **משימה 10** — ‏SW-JLM-SRV ‏(10 דקות)
- [ ] **משימה 11** — שלושת השרתים (שרת ה-DHCP לחיצה אחרי לחיצה) (20 דקות)
- [ ] **משימה 12** — מכשירי קצה + בודקים DHCP דרך ה-relay ‏(10 דקות)

**שיעור 4 — נתב הקצה**
- [ ] **משימה 13** — ‏R-JLM-EDGE, חלק 1: ממשקים ו-EIGRP ‏(15 דקות)
- [ ] **משימה 14** — ‏R-JLM-EDGE, חלק 2: ‏dynamic NAT ‏(10 דקות)
- [ ] **משימה 15** — ‏R-JLM-EDGE, חלק 3: חומת אש CBAC וניהול (15 דקות)
- [ ] **משימה 16** — בדיקות סופיות + המגבלה של dynamic NAT ‏(15 דקות)
- [ ] **תרגילים** א ו-ב
- [ ] **🛠 הפרויקט שלכם**

## מה יהיה לכם בסוף השלב
הסניף השני, בנוי **אחרת** מחיפה (משרד החינוך אוסר להעתיק סניף אחד לסניף אחר):

<div dir="rtl">

| | חיפה | **ירושלים** |
|---|---|---|
| תכנון | ‏3 שכבות (access / distribution / core) | **‏Collapsed core** — שתי שכבות |
| ניתוב | ‎‏OSPF | ‎**‏EIGRP** |
| ‎‏EtherChannel | ‎‏LACP | ‎**‏PAgP** |
| ‎‏DHCP | במתגי שכבה 3 | **שרת DHCP ייעודי** |
| ‎‏NAT | ‎‏static + ‏PAT | ‎**‏dynamic NAT** |
| חומת אש | ‎‏ASA | **‏CBAC** בנתב הקצה |

</div>

```
                        R-ISPB-PE (ISP-B)
                              │ 200.2.1.0/30
                         R-JLM-EDGE   (EIGRP + static default + dynamic NAT + CBAC)
                   Gi0/0 ╱          ╲ Gi0/2          10.20.4.0/30 and 10.20.4.4/30
           SWL3-JLM-CC1 ════ Po1 (PAgP) ════ SWL3-JLM-CC2        collapsed core
          ╱    │     │    ╲               ╱    │     │    ╲
     F1-ACC1  F2-ACC1  F3-ACC1  SW-JLM-SRV  (every access switch has a cable to BOTH CCs)
     Floor 1  Floor 2  Floor 3  DHCP/Syslog/AAA servers
```
(‏R-JLM-EDGE מחובר ל-ISP-B ומריץ EIGRP, נתיב ברירת מחדל סטטי, ‏dynamic NAT ו-CBAC. מתחתיו שני מתגי
ה-collapsed core ‏CC1 ו-CC2, מחוברים ב-Po1 ‏(PAgP). לכל מתג access — שלוש הקומות ומתג השרתים — יש
כבל לשני ה-CCs.)

## חלק 1 — קודם מבינים (בשפה פשוטה)

### 1.1 ‏Collapsed core
בחיפה, ה-distribution וה-core הם שכבות נפרדות — נכון לקמפוס גדול. ירושלים קטנה יותר: ‏core נפרד היה
יקר ולא מוסיף כלום. לכן **ה-core וה-distribution "מכווצים" (collapsed) לזוג אחד של מתגי שכבה 3**
‏(CC1, ‏CC2). הם השערים של ה-VLANים **וגם** עמוד השדרה. עדיין יש יתירות מלאה: לכל מתג access יש שני
קישורים כלפי מעלה, אחד לכל CC. משרד החינוך דורש collapsed core על מתגי שכבה 3 בסניף אחד לפחות
(דרישה 5).

### 1.2 ‏EIGRP — פרוטוקול ניתוב אחר
**‏EIGRP** הוא פרוטוקול הניתוב של Cisco. בהשוואה ל-OSPF:

<div dir="rtl">

| | ‏OSPF (חיפה) | ‏EIGRP (ירושלים) |
|---|---|---|
| איך הוא לומד | כל אחד בונה את ה**מפה** המלאה | שכנים מספרים זה לזה **מרחקים** ("אני מגיע ל-X בעלות 5") |
| מהירות כשיש תקלה | מהיר (מחשב את המפה מחדש) | מהיר מאוד — שומר **נתיב גיבוי מוכן** (feasible successor) |
| הגדרה | ‎‏areas, ‏router-IDs | פשוטה יותר: מספר AS אחד (‎`100`) |
| יצרנים | תקן פתוח | ‏Cisco (היום פתוח, אבל בעיקר Cisco) |

</div>

הגדרות EIGRP חשובות:
- ‏`no auto-summary` — אחרת EIGRP היה מקצר את הנתיבים שלנו ל-‎`10.0.0.0/8` (התנהגות ישנה).
- **סיכום ידני**: ‏6 רשתות המחלקות 10.20.10.0 – ‏10.20.15.0 נכנסות בתוך **10.20.8.0/21** (זוכרים את
  תרגיל 4 בשלב 01?). מפרסמים את הנתיב האחד הזה לכיוון נתב הקצה:
  ‏`ip summary-address eigrp 100 10.20.8.0 255.255.248.0` (דרישה 22.15).
- **אימות** עם **key chain** ‏(MD5) — כמו המפתח של OSPF בחיפה (דרישה 22.18).
- **ממשקים פסיביים** — אין הודעות EIGRP לכיוון המשתמשים.

### 1.3 ‏EtherChannel עם PAgP
אותו רעיון כמו צרור ה-LACP בחיפה, אבל עם הפרוטוקול של Cisco ‏**PAgP** — מצב `desirable` בשני הצדדים.
שימוש בשני הפרוטוקולים בפרויקט מראה שאתם מכירים את שניהם.

### 1.4 ‏DHCP משרת ייעודי + ‏DHCP relay
הכתובות של ירושלים מגיעות מ**שרת** (`SRV-JLM-DHCP`) ב-VLAN השרתים, לא מהמתגים (דרישה 22.11: נתבים
בסניף אחד, שרת בסניף אחר).

בעיה: ה-DHCP Discover של מחשב הוא **broadcast** — הוא אף פעם לא יוצא מה-VLAN שלו, והשרת יושב ב-VLAN
100. פתרון: **‏DHCP relay**. על השער של כל VLAN משתמשים כותבים `ip helper-address 10.20.1.10`: המתג
תופס את ה-broadcast ו**מעביר אותו כחבילה רגילה** לשרת. השרת רואה איזה שער שלח אותה ובוחר את המאגר
(pool) הנכון.

השוואה: פקידת קבלה בכל קומה שלוקחת את הבקשה שלכם ומתקשרת בשבילכם למשרד המרכזי.

### 1.5 ‏Dynamic NAT
ירושלים מקבלת **מאגר** של 6 כתובות ציבוריות: ‎`200.2.10.1 – 200.2.10.6`. כל מחשב שיוצא לאינטרנט שואל
כתובת אחת מהמאגר, מחשב אחד לכל כתובת. המחשב השביעי באותו זמן מקבל **כלום** — מגבלה אמיתית שתבדקו,
וזו הסיבה שרוב החברות משתמשות ב-PAT.

### 1.6 ‏CBAC — חומת אש בתוך הנתב
בירושלים אין ASA. נתב הקצה שלה מגן עליה עם **CBAC** ‏(`ip inspect`):
1. ‏ACL נכנסת בצד האינטרנט **חוסמת הכול**.
2. ‏CBAC עוקב אחרי חיבורים ש**יוצאים** מהסניף ופותח חור זמני **רק לתשובות שלהם**.

כך העובדים יכולים לגלוש, אבל אף אחד באינטרנט לא יכול להתחיל חיבור לתוך ירושלים. (ה-ACL כבר מכניסה
את ה-VPN מחיפה — בשימוש בשלב 15.)

### 1.7 הכתובות של הסניף הזה

<div dir="rtl">

| ‎‏VLAN | שם | רשת משנה | ‏VIP של השער | ‎‏CC1 | ‎‏CC2 | ראשי |
|---|---|---|---|---|---|---|
| ‎41 | ‎SALES | ‎10.20.10.0/24 | ‎.1 | ‎.2 | ‎.3 | ‎CC1 |
| ‎42 | ‎LOGISTICS | ‎10.20.11.0/24 | ‎.1 | ‎.2 | ‎.3 | ‎CC2 |
| ‎43 | ‎PRODUCTION | ‎10.20.12.0/24 | ‎.1 | ‎.2 | ‎.3 | ‎CC1 |
| ‎44 | ‎QA | ‎10.20.13.0/24 | ‎.1 | ‎.2 | ‎.3 | ‎CC2 |
| ‎45 | ‎SECURITY | ‎10.20.14.0/24 | ‎.1 | ‎.2 | ‎.3 | ‎CC1 |
| ‎46 | ‎ADMIN | ‎10.20.15.0/24 | ‎.1 | ‎.2 | ‎.3 | ‎CC2 |
| ‎99 | ‎MGMT | ‎10.20.0.0/24 | ‎.1 | ‎.2 | ‎.3 | ‎CC1 |
| ‎100 | ‎SERVERS | ‎10.20.1.0/24 | ‎.1 | ‎.2 | ‎.3 | ‎CC1 |
| ‎130 | ‎PRINTERS | ‎10.20.2.0/24 | ‎.1 | ‎.2 | ‎.3 | ‎CC1 |

</div>

<div dir="rtl">

| קישור / מכשיר | כתובת |
|---|---|
| ‎R-JLM-EDGE Gi0/0 ↔ CC1 Gi1/1/1 | ‎10.20.4.1 / 10.20.4.2 (/30) |
| ‎R-JLM-EDGE Gi0/2 ↔ CC2 Gi1/1/1 | ‎10.20.4.5 / 10.20.4.6 (/30) |
| ‎R-JLM-EDGE Gi0/1 ↔ R-ISPB-PE Gi0/1 | ‎200.2.1.2 / 200.2.1.1 (/30) |
| ‎‏Loopbacks | ‎CC1 10.20.5.1 · CC2 10.20.5.2 · EDGE 10.20.5.10 |
| ניהול (VLAN 99) | F1-ACC1 .11 · F2-ACC1 .12 · F3-ACC1 .13 · SW-JLM-SRV .14 · מחשב המנהל ‎.100 |
| שרתים | ‎DHCP 10.20.1.10 · SYSLOG .11 · AAA .12 |
| מאגר ה-dynamic NAT | ‎200.2.10.1 – 200.2.10.6 |

</div>

---

## משימה 1 — פותחים את שלב 12 ושומרים בשם שלב 13 (איך? ‏←‏ M1, ‏M19)
‏**File → Open** ‏←‏ `my-work/step12.pkt` ‏←‏ **File → Save As** ‏←‏ `my-work/step13.pkt`.
ציירו מלבן עם התווית `JERUSALEM BRANCH`, ובתוכו שלושה מלבנים קטנים: `FLOOR 1`, ‏`FLOOR 2`, ‏`FLOOR 3`.

---

## משימה 2 — מציבים את המכשירים (איך? ‏←‏ M2, ‏M3, ‏M4, ‏M8)

<div dir="rtl">

| דגם | ‎Display Name |
|---|---|
| ‎2911 | ‎`R-JLM-EDGE` |
| ‎3650-24PS | ‎`SWL3-JLM-CC1`, `SWL3-JLM-CC2` |
| ‎2960 | ‎`SW-JLM-F1-ACC1`, `SW-JLM-F2-ACC1`, `SW-JLM-F3-ACC1`, `SW-JLM-SRV` |
| ‎Server ×3 | ‎`SRV-JLM-DHCP`, `SRV-JLM-SYSLOG`, `SRV-JLM-AAA` |
| ‎PC ×13 | ‎`PC-JLM-SAL-01/02`, `PC-JLM-LOG-01/02`, `PC-JLM-PRD-01/02`, `PC-JLM-QA-01/02`, `PC-JLM-SEC-01/02`, `PC-JLM-ADM-01/02`, `PC-JLM-ADMIN-01` |
| ‎Printer ×3 | ‎`PRN-JLM-F1-01`, `PRN-JLM-F2-01`, `PRN-JLM-F3-01` |

</div>

⚠️ **ספקי כוח** בשני מתגי ה-3650 ‏(Physical ‏←‏ גוררים **AC-POWER-SUPPLY** לחריץ — M8):
- [ ] ‏CC1
- [ ] ‏CC2

<div dir="rtl">

> ‏`PC-JLM-ADM-01/02` = מחלקת **המנהלה** ‏(VLAN 46). ‏`PC-JLM-ADMIN-01` = המחשב של **מנהל
> הרשת** ‏(VLAN 99). תפקידים שונים — אל תבלבלו בין השמות.

</div>

---

## משימה 3 — מחברים את ציוד הרשת בכבלים (איך? ‏←‏ M5)

<div dir="rtl">

| ‎# | כבל | לוחצים קודם על | פורט | לוחצים אחר כך על | פורט |
|---|---|---|---|---|---|
| ‎1 | ‎Cross-Over | ‎SWL3-JLM-CC1 | ‎Gi1/0/1 | ‎SW-JLM-F1-ACC1 | ‎Gi0/1 |
| ‎2 | ‎Cross-Over | ‎SWL3-JLM-CC2 | ‎Gi1/0/1 | ‎SW-JLM-F1-ACC1 | ‎Gi0/2 |
| ‎3 | ‎Cross-Over | ‎SWL3-JLM-CC1 | ‎Gi1/0/2 | ‎SW-JLM-F2-ACC1 | ‎Gi0/1 |
| ‎4 | ‎Cross-Over | ‎SWL3-JLM-CC2 | ‎Gi1/0/2 | ‎SW-JLM-F2-ACC1 | ‎Gi0/2 |
| ‎5 | ‎Cross-Over | ‎SWL3-JLM-CC1 | ‎Gi1/0/3 | ‎SW-JLM-F3-ACC1 | ‎Gi0/1 |
| ‎6 | ‎Cross-Over | ‎SWL3-JLM-CC2 | ‎Gi1/0/3 | ‎SW-JLM-F3-ACC1 | ‎Gi0/2 |
| ‎7 | ‎Cross-Over | ‎SWL3-JLM-CC1 | ‎Gi1/0/4 | ‎SW-JLM-SRV | ‎Gi0/1 |
| ‎8 | ‎Cross-Over | ‎SWL3-JLM-CC2 | ‎Gi1/0/4 | ‎SW-JLM-SRV | ‎Gi0/2 |
| ‎9 | ‎Cross-Over | ‎SWL3-JLM-CC1 | ‎Gi1/0/23 | ‎SWL3-JLM-CC2 | ‎Gi1/0/23 |
| ‎10 | ‎Cross-Over | ‎SWL3-JLM-CC1 | ‎Gi1/0/24 | ‎SWL3-JLM-CC2 | ‎Gi1/0/24 |
| ‎11 | ‎Straight | ‎SWL3-JLM-CC1 | ‎**Gi1/1/1** | ‎R-JLM-EDGE | ‎**Gi0/0** |
| ‎12 | ‎Straight | ‎SWL3-JLM-CC2 | ‎**Gi1/1/1** | ‎R-JLM-EDGE | ‎**Gi0/2** |
| ‎13 | ‎Cross-Over | ‎R-JLM-EDGE | ‎Gi0/1 | ‎R-ISPB-PE | ‎Gi0/1 |

</div>

<div dir="rtl">

> מתג ↔ נתב = ‏Straight (סוגי מכשירים שונים). נתב ↔ נתב = ‏Cross-Over.

</div>

✅ ‏13 כבלים, התוויות נבדקו (M6).

---

## משימה 4 — מחברים את מכשירי הקצה (כולם Straight-Through)

<div dir="rtl">

| מכשיר | מתג | פורט |
|---|---|---|
| ‎PC-JLM-SAL-01 / -02 | ‎SW-JLM-F1-ACC1 | ‎Fa0/1 / Fa0/2 |
| ‎PC-JLM-LOG-01 / -02 | ‎SW-JLM-F1-ACC1 | ‎Fa0/11 / Fa0/12 |
| ‎PRN-JLM-F1-01 | ‎SW-JLM-F1-ACC1 | ‎Fa0/21 |
| ‎PC-JLM-ADMIN-01 | ‎SW-JLM-F1-ACC1 | ‎Fa0/22 |
| ‎PC-JLM-PRD-01 / -02 | ‎SW-JLM-F2-ACC1 | ‎Fa0/1 / Fa0/2 |
| ‎PC-JLM-QA-01 / -02 | ‎SW-JLM-F2-ACC1 | ‎Fa0/11 / Fa0/12 |
| ‎PRN-JLM-F2-01 | ‎SW-JLM-F2-ACC1 | ‎Fa0/21 |
| ‎PC-JLM-SEC-01 / -02 | ‎SW-JLM-F3-ACC1 | ‎Fa0/1 / Fa0/2 |
| ‎PC-JLM-ADM-01 / -02 | ‎SW-JLM-F3-ACC1 | ‎Fa0/11 / Fa0/12 |
| ‎PRN-JLM-F3-01 | ‎SW-JLM-F3-ACC1 | ‎Fa0/21 |
| ‎SRV-JLM-DHCP / SYSLOG / AAA | ‎SW-JLM-SRV | ‎Fa0/1 / Fa0/2 / Fa0/3 |

</div>

✅ ‏19 כבלים. ‏**File → Save**.

---

## משימה 5 — ‏CC1, חלק 1: הקשחה, ‏VTP, ‏VLANים, ‏STP, ‏PAgP, ‏trunks
👉 **איפה:** ‏**SWL3-JLM-CC1** ‏←‏ CLI ‏←‏ **Enter** ‏←‏ `Switch>`‎.

### 5א — הקשחה + שרת VTP + ‏VLANים
⌨️ מקלידים:
```
enable
configure terminal
hostname SWL3-JLM-CC1
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp domain JLM
vtp version 2
vtp password Intel#Vtp
vtp mode server
vlan 41
 name SALES
vlan 42
 name LOGISTICS
vlan 43
 name PRODUCTION
vlan 44
 name QA
vlan 45
 name SECURITY
vlan 46
 name ADMIN
vlan 99
 name MGMT
vlan 100
 name SERVERS
vlan 130
 name PRINTERS
vlan 998
 name NATIVE
vlan 999
 name PARKING
 exit
```
🔍 **בודקים עכשיו:** ‏`do show vlan brief` ‏←‏ ‏11 VLANים עם השמות שלהם.

### 5ב — ‏STP, ‏EtherChannel עם PAgP, ‏trunks, פורטים שלא בשימוש
‏CC1 הוא הבוס של 41, ‏43, ‏45, ‏99, ‏100, ‏130, והסגן של 42, ‏44, ‏46.

⌨️ מקלידים:
```
spanning-tree mode rapid-pvst
spanning-tree vlan 41,43,45,99,100,130 root primary
spanning-tree vlan 42,44,46 root secondary
interface range gi1/0/23 - 24
 description Po1 member to SWL3-JLM-CC2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 41-46,99,100,130,998
 switchport nonegotiate
 channel-group 1 mode desirable
 no shutdown
interface port-channel 1
 description EtherChannel (PAgP) to SWL3-JLM-CC2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 41-46,99,100,130,998
 switchport nonegotiate
interface range gi1/0/1 - 4
 description TRUNK to access switch
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 41-46,99,100,130,998
 switchport nonegotiate
 spanning-tree guard root
 no shutdown
interface range gi1/0/5 - 22
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 exit
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`channel-group 1 mode desirable` | הצטרף לצרור 1 עם **PAgP** (הפרוטוקול של Cisco) |

</div>

---

## משימה 6 — ‏CC1, חלק 2: שערים + ‏DHCP relay
👉 **איפה:** ‏CC1, שורת הפקודה `SWL3-JLM-CC1(config)#`‎.

🧠 **למה:** כל VLAN של משתמשים מקבל: כתובת ‎`.2`, שורת `ip helper-address` (ה-relay לשרת
ה-DHCP) ו-HSRP. עדיפות **110** איפה ש-CC1 ראשי (41, ‏43, ‏45, ‏99, ‏130), ‏**90** איפה שהוא סגן.

### 6א — שש ה-VLANים של המחלקות
⌨️ מקלידים:
```
ip routing
interface vlan 41
 description GW SALES
 ip address 10.20.10.2 255.255.255.0
 ip helper-address 10.20.1.10
 standby version 2
 standby 41 ip 10.20.10.1
 standby 41 priority 110
 standby 41 preempt
 no shutdown
interface vlan 42
 description GW LOGISTICS
 ip address 10.20.11.2 255.255.255.0
 ip helper-address 10.20.1.10
 standby version 2
 standby 42 ip 10.20.11.1
 standby 42 priority 90
 standby 42 preempt
 no shutdown
interface vlan 43
 description GW PRODUCTION
 ip address 10.20.12.2 255.255.255.0
 ip helper-address 10.20.1.10
 standby version 2
 standby 43 ip 10.20.12.1
 standby 43 priority 110
 standby 43 preempt
 no shutdown
interface vlan 44
 description GW QA
 ip address 10.20.13.2 255.255.255.0
 ip helper-address 10.20.1.10
 standby version 2
 standby 44 ip 10.20.13.1
 standby 44 priority 90
 standby 44 preempt
 no shutdown
interface vlan 45
 description GW SECURITY
 ip address 10.20.14.2 255.255.255.0
 ip helper-address 10.20.1.10
 standby version 2
 standby 45 ip 10.20.14.1
 standby 45 priority 110
 standby 45 preempt
 no shutdown
interface vlan 46
 description GW ADMIN
 ip address 10.20.15.2 255.255.255.0
 ip helper-address 10.20.1.10
 standby version 2
 standby 46 ip 10.20.15.1
 standby 46 priority 90
 standby 46 preempt
 no shutdown
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`ip helper-address 10.20.1.10` | "העבר broadcasts של DHCP מה-VLAN הזה לשרת ה-DHCP" (relay) |

</div>

### 6ב — ‏MGMT ו-PRINTERS (בלי relay: שם הכתובות סטטיות)
⌨️ מקלידים:
```
interface vlan 99
 description GW MGMT
 ip address 10.20.0.2 255.255.255.0
 standby version 2
 standby 99 ip 10.20.0.1
 standby 99 priority 110
 standby 99 preempt
 no shutdown
interface vlan 130
 description GW PRINTERS
 ip address 10.20.2.2 255.255.255.0
 standby version 2
 standby 130 ip 10.20.2.1
 standby 130 priority 110
 standby 130 preempt
 no shutdown
 exit
```
🔍 **בודקים עכשיו:** ‏`do show ip interface brief` ‏←‏ ‏Vlan41–46, ‏99, ‏130 עם כתובות ‎`.2`. (ייתכן
שהם מופיעים `down` עד שמגדירים את מתגי ה-access — זה בסדר.)

---

## משימה 7 — ‏CC1, חלק 3: ‏EIGRP וניהול

### 7א — מפתח ה-EIGRP, ‏VLAN 100 והקישור כלפי מעלה
⌨️ מקלידים:
```
key chain EIGRP-KEYS
 key 1
  key-string Intel#Eigrp
  exit
 exit
interface vlan 100
 description GW SERVERS (+ EIGRP peering CC1-CC2)
 ip address 10.20.1.2 255.255.255.0
 standby version 2
 standby 100 ip 10.20.1.1
 standby 100 priority 110
 standby 100 preempt
 ip authentication mode eigrp 100 md5
 ip authentication key-chain eigrp 100 EIGRP-KEYS
 no shutdown
interface loopback 0
 ip address 10.20.5.1 255.255.255.255
interface gi1/1/1
 description to R-JLM-EDGE Gi0/0
 no switchport
 ip address 10.20.4.2 255.255.255.252
 ip authentication mode eigrp 100 md5
 ip authentication key-chain eigrp 100 EIGRP-KEYS
 ip summary-address eigrp 100 10.20.8.0 255.255.248.0
 no shutdown
 exit
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`key chain EIGRP-KEYS` / `key 1` / `key-string ...`‎ | צרור מפתחות עם שם, שמחזיק את הסיסמה של EIGRP |
| ‎`ip authentication mode eigrp 100 md5` + `key-chain ...`‎ | "השתמש במפתח הזה על הקישור הזה" |
| ‎`ip summary-address eigrp 100 10.20.8.0 255.255.248.0` | "פרסם את 6 המחלקות כ-‎/21 אחד על הקישור הזה" |

</div>

<div dir="rtl">

> ‏VLAN 100 הוא המקום שבו CC1 ו-CC2 נפגשים כשכני EIGRP, ולכן גם הוא מקבל את המפתח.

</div>

### 7ב — ‏EIGRP
⌨️ מקלידים:
```
router eigrp 100
 eigrp router-id 10.20.5.1
 network 10.20.0.0 0.0.255.255
 passive-interface default
 no passive-interface gi1/1/1
 no passive-interface vlan 100
 no auto-summary
 exit
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`router eigrp 100` | הפעל EIGRP, מערכת אוטונומית 100 (חייב להתאים בכל הנתבים) |
| ‎`network 10.20.0.0 0.0.255.255` | "כל ממשק ב-10.20.x.x מצטרף ל-EIGRP" |
| ‎`no auto-summary` | "אל תקצר את הנתיבים שלי ל-10.0.0.0/8" |

</div>

### 7ג — ניהול
⌨️ מקלידים:
```
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
‏←‏ עונים **‎`1024`** ‏←‏ ואז:
```
ip ssh version 2
ip ssh time-out 60
ip ssh authentication-retries 3
login block-for 120 attempts 3 within 60
ip access-list standard MGMT-ONLY
 remark --- Jerusalem MGMT + Haifa IT (over the VPN) ---
 permit 10.20.0.0 0.0.0.255
 permit 10.10.49.0 0.0.0.255
 deny any log
 exit
service timestamps log datetime msec
logging trap informational
logging host 10.20.1.11
ntp server 10.10.200.14
aaa new-model
tacacs-server host 10.20.1.12 key Intel#Tac
aaa authentication login default group tacacs+ local
ip tacacs source-interface loopback 0
line vty 0 15
 transport input ssh
 login authentication default
 access-class MGMT-ONLY in
 exec-timeout 5 0
line console 0
 login authentication default
 logging synchronous
 end
copy running-config startup-config
```

<div dir="rtl">

> ‏`ntp server 10.10.200.14` — ‏CC1 הוא שרת ה-NTP של ה**סניף**: הוא מסתנכרן לשרת ה-NTP הראשי של
> חיפה (עובד אחרי ה-VPN, שלב 15), וכל שאר המכשירים בירושלים מסתנכרנים ל-CC1 ‏(10.20.5.1).

</div>

✅ ‏‎`[OK]`‎.

---

## משימה 8 — ‏CC2: תמונת המראה של CC1
👉 **איפה:** ‏**SWL3-JLM-CC2** ‏←‏ CLI ‏←‏ **Enter** ‏←‏ `Switch>`‎.

<div dir="rtl">

| | ‎CC1 | ‎**CC2** |
|---|---|---|
| ‎hostname | ‎SWL3-JLM-CC1 | ‎**SWL3-JLM-CC2** |
| ‎VTP | server + יוצר VLANים | **transparent ‏←‏ client, בלי פקודות `vlan`** |
| ‎STP root primary / secondary | ‎41,43,45,99,100,130 / 42,44,46 | ‎**42,44,46 / 41,43,45,99,100,130** |
| כתובות SVI | ‎.2 | **‎.3** |
| עדיפות HSRP ‏110 ב- | ‎41, 43, 45, 99, 100, 130 | ‎**42, 44, 46** |
| ‎Loopback / router-id | ‎10.20.5.1 | ‎**10.20.5.2** |
| ‎Gi1/1/1 | 10.20.4.2 (אל Gi0/0 של EDGE) | **10.20.4.6 (אל Gi0/2 של EDGE)** |
| שרת NTP | 10.10.200.14 (חיפה) | ‎**10.20.5.1 (CC1)** |

</div>

### 8א — הקשחה, ‏VTP client, ‏STP, ‏PAgP, ‏trunks
⌨️ מקלידים:
```
enable
configure terminal
hostname SWL3-JLM-CC2
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vtp domain JLM
vtp version 2
vtp password Intel#Vtp
vtp mode client
spanning-tree mode rapid-pvst
spanning-tree vlan 42,44,46 root primary
spanning-tree vlan 41,43,45,99,100,130 root secondary
interface range gi1/0/23 - 24
 description Po1 member to SWL3-JLM-CC1
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 41-46,99,100,130,998
 switchport nonegotiate
 channel-group 1 mode desirable
 no shutdown
interface port-channel 1
 description EtherChannel (PAgP) to SWL3-JLM-CC1
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 41-46,99,100,130,998
 switchport nonegotiate
interface range gi1/0/1 - 4
 description TRUNK to access switch
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 41-46,99,100,130,998
 switchport nonegotiate
 spanning-tree guard root
 no shutdown
interface range gi1/0/5 - 22
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 exit
```
לחצו **Fast Forward Time**. 🔍 **בודקים עכשיו:** ‏`do show etherchannel summary` ‏←‏
‏`Po1(SU)  PAgP  Gi1/0/23(P) Gi1/0/24(P)`‎; ‏`do show vlan brief` ‏←‏ ‏11 ה-VLANים הגיעו ב-VTP.

### 8ב — שערים
⌨️ מקלידים:
```
ip routing
interface vlan 41
 description GW SALES
 ip address 10.20.10.3 255.255.255.0
 ip helper-address 10.20.1.10
 standby version 2
 standby 41 ip 10.20.10.1
 standby 41 priority 90
 standby 41 preempt
 no shutdown
interface vlan 42
 description GW LOGISTICS
 ip address 10.20.11.3 255.255.255.0
 ip helper-address 10.20.1.10
 standby version 2
 standby 42 ip 10.20.11.1
 standby 42 priority 110
 standby 42 preempt
 no shutdown
interface vlan 43
 description GW PRODUCTION
 ip address 10.20.12.3 255.255.255.0
 ip helper-address 10.20.1.10
 standby version 2
 standby 43 ip 10.20.12.1
 standby 43 priority 90
 standby 43 preempt
 no shutdown
interface vlan 44
 description GW QA
 ip address 10.20.13.3 255.255.255.0
 ip helper-address 10.20.1.10
 standby version 2
 standby 44 ip 10.20.13.1
 standby 44 priority 110
 standby 44 preempt
 no shutdown
interface vlan 45
 description GW SECURITY
 ip address 10.20.14.3 255.255.255.0
 ip helper-address 10.20.1.10
 standby version 2
 standby 45 ip 10.20.14.1
 standby 45 priority 90
 standby 45 preempt
 no shutdown
interface vlan 46
 description GW ADMIN
 ip address 10.20.15.3 255.255.255.0
 ip helper-address 10.20.1.10
 standby version 2
 standby 46 ip 10.20.15.1
 standby 46 priority 110
 standby 46 preempt
 no shutdown
interface vlan 99
 description GW MGMT
 ip address 10.20.0.3 255.255.255.0
 standby version 2
 standby 99 ip 10.20.0.1
 standby 99 priority 90
 standby 99 preempt
 no shutdown
interface vlan 130
 description GW PRINTERS
 ip address 10.20.2.3 255.255.255.0
 standby version 2
 standby 130 ip 10.20.2.1
 standby 130 priority 90
 standby 130 preempt
 no shutdown
 exit
```

### 8ג — ‏EIGRP
⌨️ מקלידים:
```
key chain EIGRP-KEYS
 key 1
  key-string Intel#Eigrp
  exit
 exit
interface vlan 100
 description GW SERVERS (+ EIGRP peering CC1-CC2)
 ip address 10.20.1.3 255.255.255.0
 standby version 2
 standby 100 ip 10.20.1.1
 standby 100 priority 90
 standby 100 preempt
 ip authentication mode eigrp 100 md5
 ip authentication key-chain eigrp 100 EIGRP-KEYS
 no shutdown
interface loopback 0
 ip address 10.20.5.2 255.255.255.255
interface gi1/1/1
 description to R-JLM-EDGE Gi0/2
 no switchport
 ip address 10.20.4.6 255.255.255.252
 ip authentication mode eigrp 100 md5
 ip authentication key-chain eigrp 100 EIGRP-KEYS
 ip summary-address eigrp 100 10.20.8.0 255.255.248.0
 no shutdown
 exit
router eigrp 100
 eigrp router-id 10.20.5.2
 network 10.20.0.0 0.0.255.255
 passive-interface default
 no passive-interface gi1/1/1
 no passive-interface vlan 100
 no auto-summary
 exit
```
✅ ‏‎`%DUAL-5-NBRCHANGE: EIGRP-IPv4 100: Neighbor 10.20.1.2 (Vlan100) is up` — ‏CC1 ו-CC2 הם
שכני EIGRP.

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
ip ssh time-out 60
ip ssh authentication-retries 3
login block-for 120 attempts 3 within 60
ip access-list standard MGMT-ONLY
 permit 10.20.0.0 0.0.0.255
 permit 10.10.49.0 0.0.0.255
 deny any log
 exit
service timestamps log datetime msec
logging trap informational
logging host 10.20.1.11
ntp server 10.20.5.1
aaa new-model
tacacs-server host 10.20.1.12 key Intel#Tac
aaa authentication login default group tacacs+ local
ip tacacs source-interface loopback 0
line vty 0 15
 transport input ssh
 login authentication default
 access-class MGMT-ONLY in
 exec-timeout 5 0
line console 0
 login authentication default
 logging synchronous
 end
copy running-config startup-config
```
🔍 **בודקים עכשיו:** ‏`show standby brief` ‏←‏ ‏Active ב-42/44/46, ‏Standby בכל השאר.

---

## משימה 9 — שלושת מתגי הקומות
שלושתם עובדים לפי אותו מתכון (שלבים 02–06): ‏VTP client, ‏trunks עם snooping trust, פורטי משתמשים
עם port-security, מדפסת, ניהול. רק ה-VLANים והכתובת משתנים:

<div dir="rtl">

| מתג | ‎Fa0/1–10 | ‎Fa0/11–20 | ‎Fa0/21 | ‎Fa0/22 | IP ניהול |
|---|---|---|---|---|---|
| ‎SW-JLM-F1-ACC1 | ‎41 SALES | ‎42 LOGISTICS | 130 מדפסת | **99 מחשב המנהל** | ‎10.20.0.11 |
| ‎SW-JLM-F2-ACC1 | ‎43 PRODUCTION | ‎44 QA | 130 מדפסת | לא בשימוש | ‎10.20.0.12 |
| ‎SW-JLM-F3-ACC1 | ‎45 SECURITY | ‎46 ADMIN | 130 מדפסת | לא בשימוש | ‎10.20.0.13 |

</div>

### 9א — ‏SW-JLM-F1-ACC1 (מכירות + לוגיסטיקה + מחשב המנהל)
👉 **איפה:** ‏**SW-JLM-F1-ACC1** ‏←‏ CLI ‏←‏ **Enter** ‏←‏ `Switch>`‎.

⌨️ **הקשחה, ‏VTP, קישורים כלפי מעלה, פורטי משתמשים:**
```
enable
configure terminal
hostname SW-JLM-F1-ACC1
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vtp domain JLM
vtp version 2
vtp password Intel#Vtp
vtp mode client
spanning-tree mode rapid-pvst
interface range gi0/1 - 2
 description TRUNK uplink to CC1 / CC2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 41-46,99,100,130,998
 switchport nonegotiate
 ip dhcp snooping trust
 no shutdown
interface range fa0/1 - 10
 description SALES users
 switchport mode access
 switchport access vlan 41
interface range fa0/11 - 20
 description LOGISTICS users
 switchport mode access
 switchport access vlan 42
interface range fa0/1 - 20
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
 ip dhcp snooping limit rate 10
 no cdp enable
```
⌨️ **מדפסת, מחשב המנהל, פורטים שלא בשימוש, snooping, כתובת ניהול:**
```
interface fa0/21
 description PRN-JLM-F1-01
 switchport mode access
 switchport access vlan 130
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
 no cdp enable
interface fa0/22
 description PC-JLM-ADMIN-01 (management)
 switchport mode access
 switchport access vlan 99
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
 no cdp enable
interface range fa0/23 - 24
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 exit
ip dhcp snooping
ip dhcp snooping vlan 41-46,99,130
no ip dhcp snooping information option
interface vlan 99
 description MANAGEMENT
 ip address 10.20.0.11 255.255.255.0
 no shutdown
 exit
ip default-gateway 10.20.0.1
```

<div dir="rtl">

> ‏`no ip dhcp snooping information option` — **חייבת** להיות כאן, אחרת שרת ה-DHCP יתעלם
> מהבקשות (המלכודת של option-82 משלב 06).

</div>

⌨️ **ניהול:**
```
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
‏←‏ עונים **‎`1024`** ‏←‏ ואז:
```
ip ssh version 2
ip ssh time-out 60
ip ssh authentication-retries 3
login block-for 120 attempts 3 within 60
ip access-list standard MGMT-ONLY
 permit 10.20.0.0 0.0.0.255
 permit 10.10.49.0 0.0.0.255
 deny any log
 exit
service timestamps log datetime msec
logging trap informational
logging host 10.20.1.11
ntp server 10.20.5.1
aaa new-model
tacacs-server host 10.20.1.12 key Intel#Tac
aaa authentication login default group tacacs+ local
line vty 0 15
 transport input ssh
 login authentication default
 access-class MGMT-ONLY in
 exec-timeout 5 0
line console 0
 login authentication default
 logging synchronous
 end
copy running-config startup-config
```
✅ ‏‎`[OK]`‎. 🔍 ‏`show vlan brief` ‏←‏ ‏Fa0/1–10 ב-41, ‏Fa0/11–20 ב-42, ‏Fa0/21 ב-130, ‏Fa0/22 ב-99.

### 9ב — ‏SW-JLM-F2-ACC1 (ייצור + ‏QA)
👉 **איפה:** ‏**SW-JLM-F2-ACC1** ‏←‏ CLI ‏←‏ **Enter** ‏←‏ `Switch>`‎.

⌨️ **הקשחה, ‏VTP, קישורים כלפי מעלה, פורטי משתמשים:**
```
enable
configure terminal
hostname SW-JLM-F2-ACC1
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vtp domain JLM
vtp version 2
vtp password Intel#Vtp
vtp mode client
spanning-tree mode rapid-pvst
interface range gi0/1 - 2
 description TRUNK uplink to CC1 / CC2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 41-46,99,100,130,998
 switchport nonegotiate
 ip dhcp snooping trust
 no shutdown
interface range fa0/1 - 10
 description PRODUCTION users
 switchport mode access
 switchport access vlan 43
interface range fa0/11 - 20
 description QA users
 switchport mode access
 switchport access vlan 44
interface range fa0/1 - 20
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
 ip dhcp snooping limit rate 10
 no cdp enable
```
⌨️ **מדפסת, פורטים שלא בשימוש, snooping, כתובת ניהול:**
```
interface fa0/21
 description PRN-JLM-F2-01
 switchport mode access
 switchport access vlan 130
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
 no cdp enable
interface range fa0/22 - 24
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 exit
ip dhcp snooping
ip dhcp snooping vlan 41-46,99,130
no ip dhcp snooping information option
interface vlan 99
 description MANAGEMENT
 ip address 10.20.0.12 255.255.255.0
 no shutdown
 exit
ip default-gateway 10.20.0.1
```
⌨️ **ניהול:** אותו בלוק כמו ב-9א (מ-`ip domain-name intel.lab` ועד
`copy running-config startup-config`). ✅ ‏‎`[OK]`‎.

### 9ג — ‏SW-JLM-F3-ACC1 (ביטחון + מנהלה)
👉 **איפה:** ‏**SW-JLM-F3-ACC1** ‏←‏ CLI ‏←‏ **Enter** ‏←‏ `Switch>`‎.

⌨️ **הקשחה, ‏VTP, קישורים כלפי מעלה, פורטי משתמשים:**
```
enable
configure terminal
hostname SW-JLM-F3-ACC1
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vtp domain JLM
vtp version 2
vtp password Intel#Vtp
vtp mode client
spanning-tree mode rapid-pvst
interface range gi0/1 - 2
 description TRUNK uplink to CC1 / CC2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 41-46,99,100,130,998
 switchport nonegotiate
 ip dhcp snooping trust
 no shutdown
interface range fa0/1 - 10
 description SECURITY users
 switchport mode access
 switchport access vlan 45
interface range fa0/11 - 20
 description ADMIN users
 switchport mode access
 switchport access vlan 46
interface range fa0/1 - 20
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
 ip dhcp snooping limit rate 10
 no cdp enable
```
⌨️ **מדפסת, פורטים שלא בשימוש, snooping, כתובת ניהול:**
```
interface fa0/21
 description PRN-JLM-F3-01
 switchport mode access
 switchport access vlan 130
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
 no cdp enable
interface range fa0/22 - 24
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 exit
ip dhcp snooping
ip dhcp snooping vlan 41-46,99,130
no ip dhcp snooping information option
interface vlan 99
 description MANAGEMENT
 ip address 10.20.0.13 255.255.255.0
 no shutdown
 exit
ip default-gateway 10.20.0.1
```
⌨️ **ניהול:** אותו בלוק כמו ב-9א. ✅ ‏‎`[OK]`‎.

---

## משימה 10 — ‏SW-JLM-SRV
👉 **איפה:** ‏**SW-JLM-SRV** ‏←‏ CLI ‏←‏ **Enter** ‏←‏ `Switch>`‎.

⌨️ מקלידים:
```
enable
configure terminal
hostname SW-JLM-SRV
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vtp domain JLM
vtp version 2
vtp password Intel#Vtp
vtp mode client
spanning-tree mode rapid-pvst
interface range gi0/1 - 2
 description TRUNK uplink to CC1 / CC2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 41-46,99,100,130,998
 switchport nonegotiate
 no shutdown
interface range fa0/1 - 3
 description servers
 switchport mode access
 switchport access vlan 100
 spanning-tree portfast
 spanning-tree bpduguard enable
interface range fa0/4 - 24
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
interface vlan 99
 description MANAGEMENT
 ip address 10.20.0.14 255.255.255.0
 no shutdown
 exit
ip default-gateway 10.20.0.1
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
‏←‏ עונים **‎`1024`** ‏←‏ ואז:
```
ip ssh version 2
login block-for 120 attempts 3 within 60
ip access-list standard MGMT-ONLY
 permit 10.20.0.0 0.0.0.255
 permit 10.10.49.0 0.0.0.255
 deny any log
 exit
service timestamps log datetime msec
logging host 10.20.1.11
ntp server 10.20.5.1
aaa new-model
tacacs-server host 10.20.1.12 key Intel#Tac
aaa authentication login default group tacacs+ local
line vty 0 15
 transport input ssh
 login authentication default
 access-class MGMT-ONLY in
 exec-timeout 5 0
line console 0
 login authentication default
 end
copy running-config startup-config
```

<div dir="rtl">

> אין כאן DHCP snooping: שרת ה-DHCP ה**אמיתי** מחובר למתג הזה.

</div>

---

## משימה 11 — שלושת השרתים

### 11א — הגדרות IP (איך? ‏←‏ M14)
‏Desktop ‏←‏ IP Configuration ‏←‏ **Static**, לכולם mask ‏‎`255.255.255.0`, ‏gateway ‏‎`10.20.1.1`,
‏DNS ‏‎`10.10.200.11`:

<div dir="rtl">

| שרת | ‎IP |
|---|---|
| ‎SRV-JLM-DHCP | ‎10.20.1.10 |
| ‎SRV-JLM-SYSLOG | ‎10.20.1.11 |
| ‎SRV-JLM-AAA | ‎10.20.1.12 |

</div>

בכל אחד: לשונית **Services** ‏←‏ מעבירים ל-**Off** כל שירות שהוא לא צריך (M20).\
🔍 **בודקים עכשיו:** ‏SRV-JLM-DHCP ‏←‏ Command Prompt ‏←‏ `ping 10.20.1.1` ‏←‏ יש תשובות.

### 11ב — ‏SRV-JLM-SYSLOG
‏**Services ‏←‏ SYSLOG ‏←‏ On**.

### 11ג — ‏SRV-JLM-AAA
‏**Services ‏←‏ AAA ‏←‏ On**. ‏**Network Configuration** — לכל שורה: ‏Client Name, ‏Client IP,
‏Secret ‏`Intel#Tac`, ‏ServerType **Tacacs** ‏←‏ **Add**:

<div dir="rtl">

| ‎Client Name | ‎Client IP |
|---|---|
| ‎SWL3-JLM-CC1 | ‎10.20.5.1 |
| ‎SWL3-JLM-CC2 | ‎10.20.5.2 |
| ‎R-JLM-EDGE | ‎10.20.5.10 |
| ‎SW-JLM-F1-ACC1 | ‎10.20.0.11 |
| ‎SW-JLM-F2-ACC1 | ‎10.20.0.12 |
| ‎SW-JLM-F3-ACC1 | ‎10.20.0.13 |
| ‎SW-JLM-SRV | ‎10.20.0.14 |

</div>

‏**User Setup:** ‏Username ‏`admin`, ‏Password ‏`Intel#Adm1n` ‏←‏ **Add**.

### 11ד — ‏SRV-JLM-DHCP (לחיצה אחרי לחיצה)
👉 ‏SRV-JLM-DHCP ‏←‏ לשונית **Services** ‏←‏ **DHCP** (ברשימה משמאל).
1. לוחצים **On** (למעלה מימין).
2. המאגר המובנה **serverPool** מסומן. משנים את השדות שלו לרשת של השרת עצמו:
   ‏Default Gateway ‏‎`10.20.1.1`, ‏DNS Server ‏‎`10.10.200.11`, ‏Start IP Address ‏‎`10.20.1.100`,
   ‏Subnet Mask ‏‎`255.255.255.0`, ‏Maximum Number of Users ‏‎`50` ‏←‏ לוחצים **Save**.
3. עכשיו מוסיפים מאגר לכל מחלקה. ל**כל** שורה: מקלידים את ה-Pool Name ואת שאר השדות ‏←‏
   לוחצים **Add** (לא Save!):

<div dir="rtl">

| ‎Pool Name | ‎Default Gateway | ‎DNS Server | ‎Start IP Address | ‎Subnet Mask | ‎Max Users |
|---|---|---|---|---|---|
| ‎JLM-SALES | ‎10.20.10.1 | ‎10.10.200.11 | ‎10.20.10.11 | ‎255.255.255.0 | ‎240 |
| ‎JLM-LOGISTICS | ‎10.20.11.1 | ‎10.10.200.11 | ‎10.20.11.11 | ‎255.255.255.0 | ‎240 |
| ‎JLM-PRODUCTION | ‎10.20.12.1 | ‎10.10.200.11 | ‎10.20.12.11 | ‎255.255.255.0 | ‎240 |
| ‎JLM-QA | ‎10.20.13.1 | ‎10.10.200.11 | ‎10.20.13.11 | ‎255.255.255.0 | ‎240 |
| ‎JLM-SECURITY | ‎10.20.14.1 | ‎10.10.200.11 | ‎10.20.14.11 | ‎255.255.255.0 | ‎240 |
| ‎JLM-ADMIN | ‎10.20.15.1 | ‎10.10.200.11 | ‎10.20.15.11 | ‎255.255.255.0 | ‎240 |

</div>

✅ הטבלה למטה מציגה **7** מאגרים (serverPool + 6).

❌ **לחצתם Save במקום Add?** דרסתם את המאגר המסומן. תקנו את השורה הזו ולחצו **Save**, ואז
הוסיפו את המאגר החסר עם **Add**.

<div dir="rtl">

> **ה-Default Gateway הוא השדה הכי חשוב.** השרת בוחר מאגר לפי כתובת ה-relay (למשל 10.20.10.2) —
> הוא משתמש במאגר שהשער שלו נמצא באותה רשת משנה.
> שרת ה-DNS הוא של חיפה (10.10.200.11) — מגיעים אליו אחרי ה-VPN בשלב 15. עד אז, בודקים עם
> כתובות IP.

</div>

---

## משימה 12 — מכשירי קצה + בודקים DHCP דרך ה-relay

### 12א — מכשירי קצה
- כל 12 המחשבים של המחלקות ‏←‏ **DHCP** ‏(M16).
- מדפסות (M15): ‏F1 ‏‎`10.20.2.11`, ‏F2 ‏‎`10.20.2.12`, ‏F3 ‏‎`10.20.2.13`, mask ‏‎`255.255.255.0`,
  ‏gateway ‏‎`10.20.2.1`.
- ‏PC-JLM-ADMIN-01 ‏←‏ **Static** ‏‎`10.20.0.100` / ‏‎`255.255.255.0` / gateway ‏‎`10.20.0.1`.

### 12ב — בודקים

<div dir="rtl">

| ‎# | איפה | מקלידים | ✅ אמורים לראות |
|---|---|---|---|
| ‎1 | ‎PC-JLM-SAL-01 | ‎`ipconfig /all` | ‎`10.20.10.11` (או יותר), gateway ‏‎`10.20.10.1`, ‏DHCP server ‏‎`10.20.1.10` |
| ‎2 | ‎PC-JLM-QA-01 | ‎`ipconfig` | ‎`10.20.13.x` |
| ‎3 | ‎CC1 | ‎`show etherchannel summary` | ‎`Po1(SU)  PAgP  Gi1/0/23(P) Gi1/0/24(P)`‎ |
| ‎4 | ‎CC1 | ‎`show standby brief` | ‏Active ב-41/43/45/99/100/130 |
| ‎5 | ‎CC1 | ‎`show spanning-tree vlan 41` | ‎‏"This bridge is the root" |
| ‎6 | ‎PC-JLM-SAL-01 | `ping 10.20.13.11` (מחשב QA) | יש תשובות — הניתוב בין VLANים עובד |

</div>

❌ **המחשבים מקבלים ‎`169.254.x.x`:** חסר `ip helper-address` על ה-SVI; קישורי ה-snooping כלפי
מעלה לא מוגדרים trust; חסרה השורה `no ip dhcp snooping information option`; שגיאת כתיב במאגר
בשרת.\
❌ **כתובת מהמאגר הלא נכון:** ה-Default Gateway של המאגר לא תואם לשער של ה-VLAN.

💾 ‏**File → Save**.

---

## משימה 13 — ‏R-JLM-EDGE, חלק 1: ממשקים ו-EIGRP
👉 **איפה:** ‏**R-JLM-EDGE** ‏←‏ CLI ‏←‏ `no` לשאלה ‏←‏ `Router>`‎.

### 13א — הקשחה, מפתח, ממשקים
⌨️ מקלידים:
```
enable
configure terminal
hostname R-JLM-EDGE
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
key chain EIGRP-KEYS
 key 1
  key-string Intel#Eigrp
  exit
 exit
interface loopback 0
 ip address 10.20.5.10 255.255.255.255
interface gi0/0
 description to SWL3-JLM-CC1
 ip address 10.20.4.1 255.255.255.252
 ip authentication mode eigrp 100 md5
 ip authentication key-chain eigrp 100 EIGRP-KEYS
 ip nat inside
 no shutdown
interface gi0/2
 description to SWL3-JLM-CC2
 ip address 10.20.4.5 255.255.255.252
 ip authentication mode eigrp 100 md5
 ip authentication key-chain eigrp 100 EIGRP-KEYS
 ip nat inside
 no shutdown
interface gi0/1
 description WAN to R-ISPB-PE
 ip address 200.2.1.2 255.255.255.252
 ip nat outside
 no shutdown
 exit
```

### 13ב — נתיב ברירת מחדל סטטי לספק, ששותף פנימה עם EIGRP
⌨️ מקלידים:
```
ip route 0.0.0.0 0.0.0.0 200.2.1.1
router eigrp 100
 eigrp router-id 10.20.5.10
 network 10.20.4.0 0.0.0.7
 network 10.20.5.10 0.0.0.0
 redistribute static
 no auto-summary
 exit
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`network 10.20.4.0 0.0.0.7` | שני קישורי ה-‎/30 אל ה-CCים ‏(10.20.4.0–7) מצטרפים ל-EIGRP |
| ‎`redistribute static` | "שתף עם EIGRP את הנתיבים הסטטיים שלי (ברירת המחדל לספק)" |

</div>

לחצו **Fast Forward Time**.

🔍 **בודקים עכשיו:**
```
R-JLM-EDGE(config)# do show ip eigrp neighbors
H   Address         Interface   Hold Uptime    SRTT   RTO   Q   Seq
0   10.20.4.2       Gi0/0       12   00:01:10  ...
1   10.20.4.6       Gi0/2       13   00:01:05  ...
R-JLM-EDGE(config)# do show ip route eigrp
D     10.20.8.0/21 [90/...] via 10.20.4.2, Gi0/0
                   [90/...] via 10.20.4.6, Gi0/2     <- the summary, two paths
D     10.20.0.0/24 ..., D 10.20.1.0/24 ..., D 10.20.2.0/24 ...
```
ובנוסף ב-**CC1**: ‏`show ip route | include 0.0.0.0` ‏←‏ `D*EX 0.0.0.0/0 [170/...] via 10.20.4.1`.
‏`D` = נתיב EIGRP, ‏`EX` = חיצוני (הגיע מ-`redistribute`).

❌ **אין שכנים:** שגיאת כתיב בשם ה-key-chain או ב-key-string; מספר ה-AS הוא לא ‎`100` באחד הצדדים.\
❌ **שש רשתות ‎/24 נפרדות במקום ה-‎/21:** חסר `ip summary-address` על Gi1/1/1 של ה-CC.

---

## משימה 14 — ‏R-JLM-EDGE, חלק 2: ‏dynamic NAT
⌨️ מקלידים:
```
ip nat pool JLM-POOL 200.2.10.1 200.2.10.6 netmask 255.255.255.248
access-list 10 permit 10.20.0.0 0.0.255.255
ip nat inside source list 10 pool JLM-POOL
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`ip nat pool JLM-POOL 200.2.10.1 200.2.10.6 ...`‎ | המאגר של 6 הכתובות הציבוריות |
| ‎`ip nat inside source list 10 pool JLM-POOL` | "תרגם את הכתובות של ירושלים בעזרת המאגר" = **dynamic NAT** |

</div>

<div dir="rtl">

> השוו לחיפה: שם השורה נגמרת ב-`interface gi0/1 overload` ‏(PAT). כאן היא נגמרת
> ב-`pool JLM-POOL` **בלי** `overload` — כתובת ציבורית אחת לכל מחשב.

</div>

🔍 **בודקים עכשיו:** ‏PC-JLM-SAL-01 ‏←‏ `ping 200.1.100.11` ‏←‏ יש תשובות. בנתב הקצה:
‏`do show ip nat translations` ‏←‏ ‎`--- 200.2.10.1  10.20.10.11 ---`‎ — כתובת מהמאגר לכל מחשב.

---

## משימה 15 — ‏R-JLM-EDGE, חלק 3: חומת אש CBAC וניהול

### 15א — ‏CBAC
⌨️ מקלידים:
```
ip inspect name JLM-FW tcp
ip inspect name JLM-FW udp
ip inspect name JLM-FW icmp
ip access-list extended WAN-IN
 remark --- VPN from Haifa (step 15) ---
 permit udp host 200.1.1.2 host 200.2.1.2 eq isakmp
 permit esp host 200.1.1.2 host 200.2.1.2
 permit gre host 200.1.1.2 host 200.2.1.2
 remark --- everything else only as CBAC return traffic ---
 deny ip any any
 exit
interface gi0/1
 ip inspect JLM-FW out
 ip access-group WAN-IN in
 exit
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`ip inspect name JLM-FW tcp` ‏(udp, ‏icmp) | "עקוב אחרי סוגי החיבורים היוצאים האלה" |
| ‎`ip inspect JLM-FW out` | "…בתעבורה שיוצאת דרך הממשק הזה" |
| ‎`ip access-group WAN-IN in` | "חסום כל מה שמגיע מהאינטרנט, חוץ מה-VPN ומתשובות של CBAC" |

</div>

🔍 **בודקים עכשיו:** ‏PC-JLM-SAL-01 ‏←‏ `ping 200.1.100.11` ‏←‏ **עדיין** יש תשובות (‏CBAC פתח את
הדרך חזרה). ‏PC-HOME-01 ‏←‏ `ping 200.2.1.2` ‏←‏ ❌ חסום.

### 15ב — ניהול
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
ip access-list standard MGMT-ONLY
 permit 10.20.0.0 0.0.0.255
 permit 10.10.49.0 0.0.0.255
 deny any log
 exit
service timestamps log datetime msec
logging host 10.20.1.11
ntp server 10.20.5.1
aaa new-model
tacacs-server host 10.20.1.12 key Intel#Tac
aaa authentication login default group tacacs+ local
ip tacacs source-interface loopback 0
line vty 0 15
 transport input ssh
 login authentication default
 access-class MGMT-ONLY in
 exec-timeout 5 0
line console 0
 login authentication default
 end
copy running-config startup-config
```

---

## משימה 16 — בדיקות סופיות + המגבלה של dynamic NAT

### 16א — בדיקות

<div dir="rtl">

| ‎# | מאיפה | עושים | צפוי |
|---|---|---|---|
| ‎1 | ‎PC-JLM-SAL-01 | ‎`ping 200.1.100.11` | ‎✅ |
| ‎2 | ‎PC-JLM-SAL-01 | ‎`tracert 200.1.100.11` | ‎10.20.10.2 → 10.20.4.1 → 200.2.1.1 → … |
| ‎3 | ‎R-JLM-EDGE | ‎`show ip nat translations` | כתובת מהמאגר לכל מחשב |
| ‎4 | ‎R-JLM-EDGE | `show ip inspect sessions` (בזמן שמחשב עושה ping) | מופיעים sessions |
| ‎5 | ‎PC-HOME-01 | ‎`ping 200.2.1.2` | ❌ ‏CBAC זורק תעבורה שלא ביקשנו |
| ‎6 | ‎PC-JLM-ADMIN-01 | ‎`ssh -l admin 10.20.0.12` | ‎✅ ‏`SW-JLM-F2-ACC1#`‎ |

</div>

### 16ב — המגבלה של dynamic NAT
1. ב-R-JLM-EDGE: ‏`clear ip nat translation *`‎.
2. פותחים **7 מחשבים שונים** של מחלקות. בכל אחד מפעילים `ping -t 200.1.100.11` (אחד אחרי השני,
   ומשאירים אותם רצים).
3. המחשב ה-**7**: ‏`Request timed out`.
4. ב-R-JLM-EDGE: ‏`show ip nat statistics` ‏←‏ כל 6 הכתובות של המאגר בשימוש.
5. עוצרים את הפינגים (Ctrl+C) ומריצים `clear ip nat translation *`‎.

📝 כתבו את התצפית הזו בספר — זו הסיבה שרוב החברות משתמשות ב-PAT.

💾 ‏`copy running-config startup-config` בכל מכשיר ‏←‏ **File → Save**.

---

## נקודת ביקורת
- [ ] ‏EIGRP: לנתב הקצה יש 2 שכנים, והסיכום ‎`/21` מגיע דרך שניהם
- [ ] ‏PAgP ‏`Po1(SU)`‎; ‏HSRP מחולק בין CC1 ל-CC2
- [ ] כל המחשבים מקבלים כתובות מ-SRV-JLM-DHCP
- [ ] האינטרנט עובד דרך dynamic NAT; תעבורה נכנסת חסומה על ידי CBAC

## אם משהו לא עובד

<div dir="rtl">

| בעיה | פתרון |
|---|---|
| שכני EIGRP לא נוצרים | מספר ה-AS ‏(100) שונה; שגיאת כתיב בשם ה-key-chain או ב-key-string; הקישור לא נמצא ב-`network` |
| הנתיבים נראים כמו ‎`10.0.0.0/8` | חסר `no auto-summary` |
| המחשבים מקבלים ‎`169.254.x.x` | חסר `ip helper-address` על ה-SVI; קישורי ה-snooping כלפי מעלה לא מוגדרים trust; חסרה שורת option-82; שגיאת כתיב במאגר בשרת |
| המחשבים מקבלים כתובת מהמאגר הלא נכון | ה-*Default Gateway* של המאגר לא תואם לשער של ה-VLAN — השרת מתאים מאגרים לפי כתובת ה-relay |
| ‏`ip summary-address` נדחה | הוא שייך לקישור המנותב Gi1/1/1, לא ל-SVI |
| אין אינטרנט מירושלים | הנתיב של ISP-B ל-200.2.10.0/29 (שלב 12, משימה 5ב); ‏NAT inside/outside; המאגר נגמר |
| ל-3650 כל הקישורים אדומים | חסר לו ספק כוח (משימה 2) |

</div>

---

## 🏋 תרגילים

### תרגיל א — ‏CC1 מת ⭐⭐
- 🎯 **המשימה:** לגלות מה שורד כשמתג collapsed-core אחד נופל.
- 📁 **מתחילים מ:** ‏`step13.pkt` שלכם — קודם **File → Save**.
- 👣 **צעדים:**
  1. מוחקים את **SWL3-JLM-CC1** (הכלי **Delete** ‏←‏ לוחצים על CC1).
  2. ‏Fast Forward Time כמה פעמים.
  3. בודקים: (א) במחשב מכירות `ipconfig /release` ואז `ipconfig /renew`; (ב) במחשב QA
     ‏`ping 200.1.100.11`; (ג) ב-PC-JLM-ADMIN-01 ‏`ssh -l admin 10.20.0.12`.
  4. ‏**File → Open** לקובץ ששמרתם (עונים **No** לשמירה) כדי להחזיר את CC1.
- ✅ **גמרתם כש**אתם יודעים איזה מ-(א), (ב), (ג) עובד ו**למה**, ומצאתם את השירות היחיד שנפגע.

<details dir="rtl"><summary>💡 רמז</summary>

אילו תפקידים עשה CC1 ש-CC2 עושה גם כן? הסתכלו על שורות ה-NTP של שאר המכשירים.
</details>
<details dir="rtl"><summary>✔ תשובה</summary>

שלושתם. ‏CC2 משתלט על HSRP בכל ה-VLANים (‏‎`.1` נשאר חי), ‏CC2 גם מעביר DHCP (ה-helper מוגדר בשניהם),
‏STP מעביר את התעבורה לקישורים של CC2, ונתב הקצה עדיין מגיע ל-10.20.8.0/21 דרך CC2. רק NTP נפגע (CC1
היה שרת ה-NTP של הסניף) — נקודת כשל יחידה שכדאי לדון בה בספר הפרויקט (פתרון: ‏`ntp server 10.20.5.2`
כשרת שני בכל מקום, כש-CC2 גם מסתנכרן לחיפה).
</details>

### תרגיל ב — שוכחים את ה-relay ⭐
- 🎯 **המשימה:** להוכיח ש-DHCP בין VLANים צריך `ip helper-address`.
- 📁 **מתחילים מ:** ‏`step13.pkt` ‏←‏ **Save As** ‏`step13-exB.pkt`.
- 👣 **צעדים:**
  1. ב-**CC1 וגם ב-CC2**: ‏`configure terminal` ‏←‏ `interface vlan 44` ‏←‏
     ‏`no ip helper-address 10.20.1.10` ‏←‏ `end`.
  2. ‏PC-JLM-QA-01 ‏←‏ `ipconfig /release` ‏←‏ `ipconfig /renew`.
  3. עוברים למצב **Simulation** ‏(M21), מסננים **DHCP**, מחדשים שוב ומסתכלים איפה החבילה נעצרת.
- ✅ **גמרתם כש**אתם יודעים לומר איפה ה-Discover נעצר ולמה.

<details dir="rtl"><summary>✔ תשובה</summary>

המחשב מקבל ‎`169.254.x.x`. ה-Discover הוא broadcast — הוא מגיע ל-SVI של VLAN 44 ונעצר שם, כי
נתבים (ומתגי שכבה 3) אף פעם לא מעבירים broadcasts. בלי ה-helper, אף אחד לא הופך אותו ל-unicast
אל 10.20.1.10.
</details>

---

## 🛠 הפרויקט שלכם

עשיתם את השלב הזה על הדוגמה של אינטל. עכשיו עשו אותו שוב בפרויקט **שלכם**, עם הערכים
מהתוכנית **שלכם** (`my-project/plan.md`). הפקודות זהות — רק הערכים משתנים.

זה **הסניף השני** של הדוגמה. בנו את האתר השני **שלכם** מתוך חלקים ג–ה בתוכנית:

- [ ] פותחים את `my-project/step12.pkt` ‏←‏ **Save As** ‏`my-project/step13.pkt`
- [ ] קודם כותבים את טבלת הכתובות (כמו 1.7)
- [ ] מציבים (ספקי כוח!) ומחברים את האתר
- [ ] שני מתגי ה-collapsed core; בודקים PAgP, ‏HSRP, שכני EIGRP
- [ ] מתגי ה-access, מתג השרתים, השרתים (מאגרי DHCP!)
- [ ] המחשבים מקבלים כתובות דרך ה-relay
- [ ] נתב הקצה: ‏EIGRP + סיכום, ‏dynamic NAT, ‏CBAC; טבלת הבדיקות של משימה 16

<div dir="rtl">

| בדוגמה | בפרויקט שלכם — לוקחים מ |
|---|---|
| ‏Collapsed core על 2 מתגי שכבה 3 | משרד החינוך דורש collapsed core באתר אחד לפחות (דרישה 5) — תוכנית, חלק ה |
| ‏‎`10.20.0.0/16`, ‏VLANים 41–46, ‏99, ‏100, ‏130 | תוכנית, חלקים ג ו-ד (אתר 2) |
| ‏EIGRP AS 100, סיכום ‎`10.20.8.0/21` | מספר ה-AS שלכם; הסיכום שמכסה את רשתות המחלקות **שלכם** |
| ‏port-channel עם PAgP | תוכנית, חלק ה (שורת ה-EtherChannel) |
| שרת DHCP + ‏`ip helper-address` | תוכנית, חלק ה (שורת ה-DHCP) |
| מאגר dynamic NAT ‏`JLM-POOL`, ‏CBAC ‏`JLM-FW` | המאגר שלכם (מהבלוק הציבורי שלכם), השמות שלכם |

</div>

האתר הזה **אסור** שיהיה העתק של המטה שלכם (כלל ג של משרד החינוך): מודל תכנון אחר, ‏IGP אחר, סוג NAT
אחר ושיטת חומת אש אחרת.

**בדיקה:** ‏`show ip eigrp neighbors`; ‏`show ip route` בנתב הקצה מציג את הסיכום שלכם; המחשבים מקבלים
DHCP מהשרת; הגלישה לאינטרנט משתמשת במאגר הדינמי.

💾 שמרו בשם `my-project/step13.pkt`.

---

## 🎓 מסבירים לבוחן

בבחינה, הבוחן מצביע על הפרויקט **שלכם** ומבקש **להסביר** ו**להראות**. תרגלו כל שאלה
**בקול**, ואז הראו את התשובה בפרויקט שלכם — לא בדוגמה. כסו את התשובה, ענו בעצמכם, ורק אז
פתחו והשוו.

★1–★3 = שאלה ממאגר השאלות של משרד החינוך (רמת קושי 1–3).
◆ = לא במאגר, אבל בוחנים שואלים אותה לעיתים קרובות.

**1. ★1 באילו פרמטרים של מטריקה EIGRP משתמש? איך נקרא האלגוריתם שלו?**

<details dir="rtl"><summary>תשובה</summary>

רוחב פס (bandwidth) ועיכוב (delay) כברירת מחדל (אפשר להוסיף עומס ואמינות עם ערכי ה-K). האלגוריתם
הוא **DUAL** ‏(Diffusing Update Algorithm).

**איפה מראים:** `show ip protocols` ‏←‏ ערכי ה-K
</details>

**2. ★1 מהם זמני ה-Hello וה-Hold של EIGRP? לאיזו כתובת נשלחים העדכונים?**

<details dir="rtl"><summary>תשובה</summary>

בקישורים מהירים Hello ‏5 שניות, ‏Hold ‏15 שניות. העדכונים נשלחים לכתובת ה-multicast **224.0.0.10**.

**איפה מראים:** `show ip eigrp neighbors` ‏←‏ העמודה Hold
</details>

**3. ★1 הסבר Feasible Distance ו-Reported Distance, ‏Successor ו-Feasible Successor, ואת תנאי ה-feasibility.**

<details dir="rtl"><summary>תשובה</summary>

‏Reported Distance = העלות של השכן עצמו עד היעד. ‏Feasible Distance = העלות הכוללת הטובה ביותר מהנתב
הזה. ‏Successor = השכן של הנתיב הטוב ביותר (בטבלת הניתוב). ‏Feasible Successor = שכן גיבוי שעומד
ב**תנאי ה-feasibility**: ה-RD שלו נמוך מה-FD הנוכחי. התנאי מבטיח שבנתיב הגיבוי אין לולאה, ולכן אפשר
להשתמש בו מיד.

**איפה מראים:** `show ip eigrp topology`
</details>

**4. ★2 אילו שלוש טבלאות EIGRP מחזיק, ואילו פקודות מציגות אותן?**

<details dir="rtl"><summary>תשובה</summary>

טבלת שכנים `show ip eigrp neighbors`, טבלת טופולוגיה `show ip eigrp topology`, טבלת ניתוב
‏`show ip route eigrp`.

**איפה מראים:** שלוש הפקודות האלה
</details>

**5. ★2 מהו `passive-interface` והיכן מגדירים אותו?**

<details dir="rtl"><summary>תשובה</summary>

תחת `router eigrp`: הרשת של הממשק עדיין מפורסמת, אבל לא נשלחות עליו הודעות hello, ולכן לא נוצר שם
שכן — משתמשים בזה על ממשקים / ‏SVIs שפונים למשתמשים. הפרויקט הזה משתמש ב-`passive-interface default`,
ואז `no passive-interface` רק על הקישורים לשכנים.

**איפה מראים:** `show ip protocols` ‏←‏ Passive Interface(s)
</details>

**6. ★2 מהם שלושת ה-administrative distances של EIGRP?**

<details dir="rtl"><summary>תשובה</summary>

פנימי 90, חיצוני (redistributed) ‏170, סיכום 5.

**איפה מראים:** `show ip route` ‏←‏ [90/…]
</details>

**7. ★2 איך עושים איזון עומסים בעלויות לא שוות (unequal-cost load balancing) ב-EIGRP?**

<details dir="rtl"><summary>תשובה</summary>

‏`variance N` תחת `router eigrp`: גם נתיבים דרך feasible successors שהמטריקה שלהם עד פי N מהטוב
ביותר נמצאים בשימוש, ביחס לעלות שלהם.

**איפה מראים:** —
</details>

**8. ★2 איך מחברים שני פרוטוקולי ניתוב שונים, למשל OSPF ו-EIGRP?**

<details dir="rtl"><summary>תשובה</summary>

‏Redistribution בנתב שמריץ את שניהם: תחת `router eigrp` ‏←‏ `redistribute ospf 1 metric …`‎, ותחת
‏`router ospf` ‏←‏ `redistribute eigrp 100 subnets`.

**איפה מראים:** —
</details>

**9. ◆ איך סיכמת ואבטחת את EIGRP?**

<details dir="rtl"><summary>תשובה</summary>

סיכום על הממשק לכיוון נתב הקצה: ‏`ip summary-address eigrp 100 <network> <mask>`‎ (דרישה 22.15). אבטחה:
‏key chain ו-`ip authentication mode eigrp 100 md5` (דרישה 22.18).

**איפה מראים:** `show ip route` בנתב הקצה ‏←‏ סיכום אחד
</details>

**10. ★2 מה המשמעות של `ip helper-address`? למה משתמשים בו, ועל איזה ממשק?**

<details dir="rtl"><summary>תשובה</summary>

‏DHCP Discover הוא broadcast ולא עובר נתב. ‏`ip helper-address <server IP>`‎ על ממשק השער **של ה-VLAN של
הלקוחות** (ה-SVI) מעביר את ה-broadcasts של ה-DHCP שלהם כ-unicast לשרת ה-DHCP ברשת משנה אחרת.

**איפה מראים:** `show running-config interface vlan <x>`‎
</details>

**11. ★1 הראה לי את הגדרות ה-DHCP בשרת הייעודי והסבר את השדות.**

<details dir="rtl"><summary>תשובה</summary>

‏Services ‏←‏ DHCP: מאגר אחד לכל VLAN — שם המאגר, ‏default gateway ‏(‎`.1`), שרת DNS, כתובת התחלה, מסיכת
רשת, מספר משתמשים מקסימלי. השרת עונה לבקשות שהועברו לפי כתובת השער שבבקשה.

**איפה מראים:** ‏Server ‏←‏ Services ‏←‏ DHCP
</details>

**12. ◆ מהו CBAC?**

<details dir="rtl"><summary>תשובה</summary>

‏Context-Based Access Control ‏(`ip inspect`): הנתב זוכר שיחות שהתחילו בפנים ופותח רק להן את התעבורה
החוזרת; כל השאר מבחוץ נחסם על ידי ה-ACL (דרישה 22.13).

**איפה מראים:** `show running-config` ‏←‏ שורות `ip inspect` בנתב הקצה
</details>

**13. ◆ ‏PAgP לעומת LACP?**

<details dir="rtl"><summary>תשובה</summary>

שניהם מנהלים משא ומתן על EtherChannel. ‏PAgP קיים רק אצל Cisco ‏(`desirable`/`auto`); ‏LACP הוא התקן
הפתוח (`active`/`passive`). הסניף הזה משתמש ב-PAgP כדי להיות שונה מהמטה.

**איפה מראים:** `show etherchannel summary` ‏←‏ Protocol
</details>

---

## 🔁 עושים שוב — בלי המדריך

הבוחן יכול לבקש מכם להגדיר משהו שוב, מולו. תצליחו רק אם עשיתם את זה **בלי המדריך** לפני כן.
עשו את התרגיל הזה בפרויקט שלכם:

בעותק של הקובץ שלכם, מחקו את EIGRP ממתג collapsed-core אחד ואת שורות ה-`ip helper-address`. בלי
העמוד הזה, הגדירו אותם שוב מתוך התוכנית שלכם (AS, רשתות, ממשקים פסיביים, סיכום, אימות, helper). יעד:
**‏15 דקות**. אחר כך הראו את שלוש הטבלאות של EIGRP ומחשב שמקבל כתובת משרת ה-DHCP.

---

## 👩‍🏫 הערות למורה
- **שיעור 1:** ‏collapsed core מול 3 שכבות (עלות מול גודל); טבלת EIGRP מול OSPF; בנייה וחיווט.
- **שיעור 2:** ‏CC1 ו-CC2 (ארוך — חלקו את הכיתה לזוגות: אחד מקליד את CC1, השני את CC2, ואז מתחלפים
  ומשווים).
- **שיעור 3:** מתגי ה-access, מתג השרתים, השרתים; הדגמת DHCP relay במצב Simulation (מסננים **DHCP**:
  ה-broadcast נעצר ב-SVI וממשיך כ-unicast אל 10.20.1.10).
- **שיעור 4:** נתב הקצה — ‏EIGRP, ‏dynamic NAT, ‏CBAC; בדיקות; בדיקת המגבלה של NAT עם 7 מחשבים.
- **שאלות נפוצות של תלמידים**
  - *"למה לא להעתיק את התכנון של חיפה?"* — משרד החינוך אוסר סניפים זהים, וחברות אמיתיות בוחרות את
    התכנון שמתאים לגודל של כל אתר.
  - *"איך שרת ה-DHCP יודע איזה מאגר?"* — ה-relay שם בבקשה את הכתובת של ה-SVI (למשל 10.20.10.2);
    השרת בוחר את המאגר שהשער שלו נמצא ברשת המשנה הזו.
- **טעויות אופייניות:** ‏PAgP בצד אחד ו-LACP בצד השני; שכחת `no auto-summary`; סיכום על ה-SVI; חסר
  helper ב-CC2.
