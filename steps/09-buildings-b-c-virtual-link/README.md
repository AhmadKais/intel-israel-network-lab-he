# שלב 09 — בניינים B ו-C + ‏virtual link של OSPF

<div dir="rtl">

> ⏱ ‏4 שיעורים · 🎯 דרישות משרד החינוך 8, ‏22.16, ‏22.15, ‏20.1, ‏20.2\
> 📁 מתחילים מ: `my-work/step08.pkt`\
> 💾 שומרים בשם: `my-work/step09.pkt`

</div>

<div dir="rtl">

> ✅ **לפני שמתחילים:** כל הסעיפים בנקודת הביקורת של שלב 08 מסומנים, ועשיתם את
> תרגיל ה-🔁 שלו בפרויקט שלכם. אל תדלגו על שלבים — כל שלב בנוי על הקובץ של השלב הקודם.

</div>

## 🗺 המשימות שלכם בשלב הזה
**שיעור 1 — בונים ומחברים**
- [ ] **משימה 1** — פותחים את שלב 08 ושומרים בשם שלב 09 (2 דקות)
- [ ] **משימה 2** — מציבים את בניין B ואת בניין C (עם 4 ספקי כוח!) (20 דקות)
- [ ] **משימה 3** — מחברים את בניין B ‏(20 דקות)
- [ ] **משימה 4** — מחברים את בניין C ‏(20 דקות)

**שיעור 2 — בניין B**
- [ ] **משימה 5** — ‏B-DIST1, חלק 1: הקשחה, ‏VTP, ‏VLANים, ‏STP, ‏trunks, ‏EtherChannel ‏(15 דקות)
- [ ] **משימה 6** — ‏B-DIST1, חלק 2: שערים, ‏DHCP, קישורים כלפי מעלה, ‏OSPF, ניהול (20 דקות)
- [ ] **משימה 7** — ‏B-DIST2: תמונת המראה של B-DIST1 ‏(25 דקות)
- [ ] **משימה 8** — ‏B-ACC1 ו-B-ACC2 ‏(25 דקות)
- [ ] **משימה 9** — פותחים את פורטי ה-core לכיוון בניין B ‏(10 דקות)
- [ ] **משימה 10** — מכשירי הקצה של בניין B + בדיקת בניין B ‏(10 דקות)

**שיעור 3 — בניין C**
- [ ] **משימה 11** — ‏C-DIST1 ‏(30 דקות)
- [ ] **משימה 12** — ‏C-DIST2 ‏(25 דקות)
- [ ] **משימה 13** — ‏C-ACC1 ו-C-ACC2 ‏(25 דקות)
- [ ] **משימה 14** — מכשירי הקצה של בניין C + **רואים את הבעיה** 🔍 (10 דקות)

**שיעור 4 — התיקון והסיום**
- [ ] **משימה 15** — ה-virtual links ‏(10 דקות)
- [ ] **משימה 16** — מעדכנים את רשימת האורחים של 7 המכשירים הישנים (15 דקות)
- [ ] **משימה 17** — רושמים את 8 המכשירים החדשים בשרת ה-AAA ‏(10 דקות)
- [ ] **משימה 18** — בדיקות סופיות (15 דקות)
- [ ] **תרגילים** א ו-ב
- [ ] **🛠 הפרויקט שלכם**

## מה יהיה לכם בסוף השלב
הרשת המקומית של המטה בחיפה **שלמה**: ‏3 בניינים, ‏6 מחלקות, תכנון תלת-שכבתי, ‏OSPF areas
‏0/1/2/3. בניין C מחובר רק לבניין B, ולכן תפגשו בעיית OSPF אמיתית ותפתרו אותה עם
**virtual link** (קישור וירטואלי).

```
                       CORE1 ═══════ CORE2                        AREA 0
                    ╱    │    ╲    ╱   │    ╲
       A-DIST1/2 (area 1)      B-DIST1 ═ B-DIST2 (ABRs 0/2)       AREA 2 links
                                 │   ╲  ╱   │
                                 │    ╳     │         10.10.36.x/30
                                 │   ╱  ╲   │
                              C-DIST1 ═ C-DIST2 (ABRs 2/3)        AREA 3
                    ······ virtual links B-DIST ⇄ C-DIST through area 2 ······
```
(למעלה: ‏CORE1 ו-CORE2 ב-area 0. ‏A-DIST ב-area 1. ‏B-DIST1/2 הם ABR בין area 0 ל-area 2. ‏C-DIST1/2 הם
ABR בין area 2 ל-area 3, מחוברים ל-B בקישורי ‎10.10.36.x/30. הקו המנוקד = ה-virtual links דרך area 2.)

<div dir="rtl">

> **איך משתמשים בשלב הזה בכיתה:** בניינים B ו-C חוזרים על כל מה שעשינו בשלבים 02–08.
> תלמידים חזקים יכולים לנסות להגדיר כל מכשיר **לפני** שהם מסתכלים על ההגדרות שלו למטה — זו
> החזרה הכי טובה על הקורס. כל השאר מקלידים מתוך המדריך.

</div>

## חלק 1 — קודם מבינים (בשפה פשוטה)

### 1.1 אותו מתכון, בניינים חדשים
בניינים B ו-C בנויים בדיוק לפי המתכון של בניין A:

<div dir="rtl">

| שכבה | בניין A | בניין B | בניין C |
|---|---|---|---|
| דומיין VTP | ‎HFA-A | ‎**HFA-B** | ‎**HFA-C** |
| מחלקות | הנדסה (10), כספים (20) | **משאבי אנוש (40), שיווק (50)** | **מו"פ (70), IT ‏(80)** |
| ‏VLAN מדפסות | ‎30 | ‎**60** | ‎**90** |
| ‏VLAN ניהול 99 | ‎10.10.19.0/24 | ‎**10.10.35.0/24** | ‎**10.10.51.0/24** |
| ‎‏OSPF area | ‎1 (10.10.16.0/20) | ‎**2 (10.10.32.0/20)** | ‎**3 (10.10.48.0/20)** |
| הקישורים כלפי מעלה הולכים אל | ה-core | ה-core | **בניין B** ⚠️ |

</div>

ל-VLAN 99 יש אותו **מספר** בכל בניין אבל **רשת משנה אחרת** — זה בסדר, כי הבניינים מחוברים
בקישורים מנותבים: ‏VLANים לא עוברים מבניין לבניין.

### 1.2 הבעיה: בניין C לא נוגע ב-area 0
ל-OSPF יש כלל נוקשה: **כל area חייב להתחבר ל-area 0** (עמוד השדרה, backbone). נתיבים בין
areas עוברים רק *דרך* area 0 — כמו ערים שמותר להן לסחור זו עם זו רק דרך הכביש הארצי.

בניין C ‏(area 3) מחובר רק ל-area 2 של בניין B. לכן:
- ל-C-DIST1/2 אין רגל ב-area 0 ‏←‏ הם לא יכולים להעביר את הנתיבים של area 3 לעמוד השדרה;
- בניין C הופך ל**אי**: אף אחד מחוץ ל-area 2 לא מגיע אליו, והוא לא מגיע לשרתים.

קודם **תראו** את זה קורה, ואחר כך תתקנו.

### 1.3 הפתרון: virtual link
**‏Virtual link** הוא חתיכה לוגית של area 0 ש"עוברת במנהרה" דרך area אחר (area ה-**transit**,
המעבר — כאן area 2), בין שני ABRs:
- קצה אחד בנתב שיושב ב-**area 0 + area 2** ‏←‏ B-DIST1/2 (‏router-IDs ‏10.10.5.21 / ‏.22)
- הקצה השני בנתב שיושב ב-**area 2 + area 3** ‏←‏ C-DIST1/2 (‏router-IDs ‏10.10.63.1 / ‏.2)

השוואה: לעיירה של בניין C אין יציאה לכביש הארצי, אז חותמים על הסכם עם העיירה השכנה שאחד
הכבישים שלה ייחשב **כאילו** הוא כביש ארצי.

הפקודה משתמשת ב-**router-ID** של הקצה השני — לא בכתובת של ממשק:
`area 2 virtual-link 10.10.63.1`. בונים את כל 4 הצירופים (B1↔C1, ‏B1↔C2, ‏B2↔C1, ‏B2↔C2),
כך שגם אם מתג אחד נופל, ‏area 3 נשאר מחובר.

<div dir="rtl">

> דרישה 22.16 מבקשת בדיוק את זה: "OSPF מרובה areas בסניף אחד, כולל מבנה שמחייב virtual link".

</div>

### 1.4 למה הקישורים בין B ל-C ממוספרים 10.10.36.x
הם שייכים ל-area 2, ולכן הם מקבלים כתובות **בתוך הבלוק של area 2** ‏(10.10.32.0/20). כך הסיכום
של B ‏‎`10.10.32.0/20` מכסה גם אותם, והם לא "דולפים" ל-core כנתיבים נוספים. ה-loopbacks של בניין
C ‏(10.10.63.x) נמצאים בתוך הבלוק של **area 3** מאותה סיבה.

### 1.5 תוכנית הכתובות של השלב הזה
השאירו את זה פתוח — כל משימה לוקחת מכאן את המספרים.

<div dir="rtl">

| קישור | רשת משנה | צד 1 | צד 2 | ‎‏Area |
|---|---|---|---|---|
| ‎B-DIST1 Gi1/1/1 ↔ CORE1 Gi1/0/3 | ‎10.10.4.16/30 | ‎B-DIST1 .17 | ‎CORE1 .18 | ‎0 |
| ‎B-DIST1 Gi1/1/2 ↔ CORE2 Gi1/0/3 | ‎10.10.4.20/30 | ‎B-DIST1 .21 | ‎CORE2 .22 | ‎0 |
| ‎B-DIST2 Gi1/1/1 ↔ CORE1 Gi1/0/4 | ‎10.10.4.24/30 | ‎B-DIST2 .25 | ‎CORE1 .26 | ‎0 |
| ‎B-DIST2 Gi1/1/2 ↔ CORE2 Gi1/0/4 | ‎10.10.4.28/30 | ‎B-DIST2 .29 | ‎CORE2 .30 | ‎0 |
| ‎B-DIST1 Gi1/1/3 ↔ C-DIST1 Gi1/1/1 | ‎10.10.36.0/30 | ‎B-DIST1 .1 | ‎C-DIST1 .2 | ‎2 |
| ‎B-DIST2 Gi1/1/3 ↔ C-DIST1 Gi1/1/2 | ‎10.10.36.4/30 | ‎B-DIST2 .5 | ‎C-DIST1 .6 | ‎2 |
| ‎B-DIST1 Gi1/1/4 ↔ C-DIST2 Gi1/1/1 | ‎10.10.36.8/30 | ‎B-DIST1 .9 | ‎C-DIST2 .10 | ‎2 |
| ‎B-DIST2 Gi1/1/4 ↔ C-DIST2 Gi1/1/2 | ‎10.10.36.12/30 | ‎B-DIST2 .13 | ‎C-DIST2 .14 | ‎2 |

</div>

<div dir="rtl">

| מכשיר | ‎‏Loopback0 / ‏router-ID | ניהול (VLAN 99) |
|---|---|---|
| ‎SWL3-HFA-B-DIST1 / DIST2 | ‎10.10.5.21 / 10.10.5.22 | ‎10.10.35.2 / .3 (VIP .1) |
| ‎SW-HFA-B-ACC1 / ACC2 | ‎— | ‎10.10.35.11 / .12 |
| ‎SWL3-HFA-C-DIST1 / DIST2 | ‎10.10.63.1 / 10.10.63.2 | ‎10.10.51.2 / .3 (VIP .1) |
| ‎SW-HFA-C-ACC1 / ACC2 | ‎— | ‎10.10.51.11 / .12 |

</div>

<div dir="rtl">

| ‎‏VLAN | שם | רשת משנה | ראשי (STP root + ‏HSRP active) |
|---|---|---|---|
| ‎40 | ‎HR | ‎10.10.32.0/24 | ‎B-DIST1 |
| ‎50 | ‎MARKETING | ‎10.10.33.0/24 | ‎B-DIST2 |
| ‎60 | ‎PRINTERS-B | ‎10.10.34.0/24 | ‎B-DIST1 |
| ‎99 | ‎MGMT-B | ‎10.10.35.0/24 | ‎B-DIST1 |
| ‎70 | ‎RND | ‎10.10.48.0/24 | ‎C-DIST1 |
| ‎80 | ‎IT | ‎10.10.49.0/24 | ‎C-DIST2 |
| ‎90 | ‎PRINTERS-C | ‎10.10.50.0/24 | ‎C-DIST1 |
| ‎99 | ‎MGMT-C | ‎10.10.51.0/24 | ‎C-DIST1 |

</div>

### 1.6 שני בלוקים שתקלידו הרבה פעמים
**בלוק הניהול** זהה בכל מתג חדש — ‏SSH (שלב 07) + רשימת האורחים הסופית + Syslog + AAA (שלב 08).
מעכשיו מותר לנהל את ציוד הרשת מ**כל שלושת ה-VLANים של הניהול** ומ**מחלקת IT**.

**🅼 בלוק ניהול — ל-4 מתגי שכבה 3** ‏(B-DIST1/2, ‏C-DIST1/2):
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
 permit 10.10.19.0 0.0.0.255
 permit 10.10.35.0 0.0.0.255
 permit 10.10.51.0 0.0.0.255
 permit 10.10.49.0 0.0.0.255
 deny any log
 exit
service timestamps log datetime msec
logging trap informational
logging host 10.10.1.10
aaa new-model
tacacs-server host 10.10.1.11 key Intel#Tac
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

**🅰 בלוק ניהול — ל-4 מתגי ה-access** ‏(B-ACC1/2, ‏C-ACC1/2): בדיוק אותו דבר, **בלי** השורה
‏`ip tacacs source-interface loopback 0` (למתגי access אין loopback).

<div dir="rtl">

> כמו תמיד: אם `login block-for ...`‎ או `ip tacacs source-interface` נדחים, דלגו על השורה הזו
> (ראו את ההערות בשלבים 07–08).

</div>

---

## משימה 1 — פותחים את שלב 08 ושומרים בשם שלב 09 (איך? ‏←‏ M1)
‏**File → Open** ‏←‏ `my-work/step08.pkt` ‏←‏ **File → Save As** ‏←‏ `my-work/step09.pkt`.

---

## משימה 2 — מציבים את בניין B ואת בניין C

### 2א — בניין B (בתוך המלבן "BUILDING B" — איך? ‏←‏ M2, ‏M3, ‏M4)

<div dir="rtl">

| דגם | ‎Display Name |
|---|---|
| ‎3650-24PS | ‎`SWL3-HFA-B-DIST1`, `SWL3-HFA-B-DIST2` |
| ‎2960 | ‎`SW-HFA-B-ACC1`, `SW-HFA-B-ACC2` |
| ‎PC ×4 | ‎`PC-HFA-HR-01`, `PC-HFA-HR-02`, `PC-HFA-MKT-01`, `PC-HFA-MKT-02` |
| ‎Printer | ‎`PRN-HFA-B-01` |

</div>

### 2ב — בניין C (בתוך המלבן "BUILDING C")

<div dir="rtl">

| דגם | ‎Display Name |
|---|---|
| ‎3650-24PS | ‎`SWL3-HFA-C-DIST1`, `SWL3-HFA-C-DIST2` |
| ‎2960 | ‎`SW-HFA-C-ACC1`, `SW-HFA-C-ACC2` |
| ‎PC ×4 | ‎`PC-HFA-RND-01`, `PC-HFA-RND-02`, `PC-HFA-IT-01`, `PC-HFA-IT-02` |
| ‎Printer | ‎`PRN-HFA-C-01` |

</div>

### 2ג — ספקי כוח בכל **4** מתגי ה-3650 החדשים (⚠️ איך? ‏←‏ M8)
כל 3650 ‏←‏ **Physical** ‏←‏ גוררים **AC-POWER-SUPPLY** לחריץ הריק ‏←‏ סוגרים. סמנו:
- [ ] ‏SWL3-HFA-B-DIST1
- [ ] ‏SWL3-HFA-B-DIST2
- [ ] ‏SWL3-HFA-C-DIST1
- [ ] ‏SWL3-HFA-C-DIST2

✅ ‏18 מכשירים חדשים, לכולם שמות, ו-4 מתגי 3650 עם נורות ירוקות.

---

## משימה 3 — מחברים את בניין B (איך? ‏←‏ M5)
מתג ↔ מתג = **Cross-Over**; מכשיר קצה ↔ מתג = **Straight-Through**.

<div dir="rtl">

| ‎# | כבל | לוחצים קודם על | פורט | לוחצים אחר כך על | פורט |
|---|---|---|---|---|---|
| ‎1 | ‎Cross-Over | ‎SW-HFA-B-ACC1 | ‎Gi0/1 | ‎SWL3-HFA-B-DIST1 | ‎Gi1/0/1 |
| ‎2 | ‎Cross-Over | ‎SW-HFA-B-ACC1 | ‎Gi0/2 | ‎SWL3-HFA-B-DIST2 | ‎Gi1/0/1 |
| ‎3 | ‎Cross-Over | ‎SW-HFA-B-ACC2 | ‎Gi0/1 | ‎SWL3-HFA-B-DIST1 | ‎Gi1/0/2 |
| ‎4 | ‎Cross-Over | ‎SW-HFA-B-ACC2 | ‎Gi0/2 | ‎SWL3-HFA-B-DIST2 | ‎Gi1/0/2 |
| ‎5 | ‎Cross-Over | ‎SWL3-HFA-B-DIST1 | ‎Gi1/0/23 | ‎SWL3-HFA-B-DIST2 | ‎Gi1/0/23 |
| ‎6 | ‎Cross-Over | ‎SWL3-HFA-B-DIST1 | ‎Gi1/0/24 | ‎SWL3-HFA-B-DIST2 | ‎Gi1/0/24 |
| ‎7 | ‎Cross-Over | ‎SWL3-HFA-B-DIST1 | ‎**Gi1/1/1** | ‎SWL3-HFA-CORE1 | ‎**Gi1/0/3** |
| ‎8 | ‎Cross-Over | ‎SWL3-HFA-B-DIST1 | ‎**Gi1/1/2** | ‎SWL3-HFA-CORE2 | ‎**Gi1/0/3** |
| ‎9 | ‎Cross-Over | ‎SWL3-HFA-B-DIST2 | ‎**Gi1/1/1** | ‎SWL3-HFA-CORE1 | ‎**Gi1/0/4** |
| ‎10 | ‎Cross-Over | ‎SWL3-HFA-B-DIST2 | ‎**Gi1/1/2** | ‎SWL3-HFA-CORE2 | ‎**Gi1/0/4** |
| ‎11 | ‎Straight | ‎PC-HFA-HR-01 | ‎Fa0 | ‎SW-HFA-B-ACC1 | ‎Fa0/1 |
| ‎12 | ‎Straight | ‎PC-HFA-HR-02 | ‎Fa0 | ‎SW-HFA-B-ACC2 | ‎Fa0/1 |
| ‎13 | ‎Straight | ‎PC-HFA-MKT-01 | ‎Fa0 | ‎SW-HFA-B-ACC1 | ‎Fa0/11 |
| ‎14 | ‎Straight | ‎PC-HFA-MKT-02 | ‎Fa0 | ‎SW-HFA-B-ACC2 | ‎Fa0/11 |
| ‎15 | ‎Straight | ‎PRN-HFA-B-01 | ‎Fa0 | ‎SW-HFA-B-ACC1 | ‎Fa0/21 |

</div>

<div dir="rtl">

> אם PT לא מקבל נחושת בפורטי ה-`Gi1/1/x` של ה-3650, השתמשו בכבל ה-**Fiber** הכתום (כמו בשלב 08).

</div>

✅ ‏15 כבלים. בדקו כל תווית (M6). סמנו כל שורה תוך כדי עבודה — קל לדלג על אחת.

---

## משימה 4 — מחברים את בניין C (הקישורים כלפי מעלה שלו הולכים ל**בניין B**)

<div dir="rtl">

| ‎# | כבל | לוחצים קודם על | פורט | לוחצים אחר כך על | פורט |
|---|---|---|---|---|---|
| ‎1 | ‎Cross-Over | ‎SW-HFA-C-ACC1 | ‎Gi0/1 | ‎SWL3-HFA-C-DIST1 | ‎Gi1/0/1 |
| ‎2 | ‎Cross-Over | ‎SW-HFA-C-ACC1 | ‎Gi0/2 | ‎SWL3-HFA-C-DIST2 | ‎Gi1/0/1 |
| ‎3 | ‎Cross-Over | ‎SW-HFA-C-ACC2 | ‎Gi0/1 | ‎SWL3-HFA-C-DIST1 | ‎Gi1/0/2 |
| ‎4 | ‎Cross-Over | ‎SW-HFA-C-ACC2 | ‎Gi0/2 | ‎SWL3-HFA-C-DIST2 | ‎Gi1/0/2 |
| ‎5 | ‎Cross-Over | ‎SWL3-HFA-C-DIST1 | ‎Gi1/0/23 | ‎SWL3-HFA-C-DIST2 | ‎Gi1/0/23 |
| ‎6 | ‎Cross-Over | ‎SWL3-HFA-C-DIST1 | ‎Gi1/0/24 | ‎SWL3-HFA-C-DIST2 | ‎Gi1/0/24 |
| ‎7 | ‎Cross-Over | ‎SWL3-HFA-C-DIST1 | ‎**Gi1/1/1** | ‎SWL3-HFA-B-DIST1 | ‎**Gi1/1/3** |
| ‎8 | ‎Cross-Over | ‎SWL3-HFA-C-DIST1 | ‎**Gi1/1/2** | ‎SWL3-HFA-B-DIST2 | ‎**Gi1/1/3** |
| ‎9 | ‎Cross-Over | ‎SWL3-HFA-C-DIST2 | ‎**Gi1/1/1** | ‎SWL3-HFA-B-DIST1 | ‎**Gi1/1/4** |
| ‎10 | ‎Cross-Over | ‎SWL3-HFA-C-DIST2 | ‎**Gi1/1/2** | ‎SWL3-HFA-B-DIST2 | ‎**Gi1/1/4** |
| ‎11 | ‎Straight | ‎PC-HFA-RND-01 | ‎Fa0 | ‎SW-HFA-C-ACC1 | ‎Fa0/1 |
| ‎12 | ‎Straight | ‎PC-HFA-RND-02 | ‎Fa0 | ‎SW-HFA-C-ACC2 | ‎Fa0/1 |
| ‎13 | ‎Straight | ‎PC-HFA-IT-01 | ‎Fa0 | ‎SW-HFA-C-ACC1 | ‎Fa0/11 |
| ‎14 | ‎Straight | ‎PC-HFA-IT-02 | ‎Fa0 | ‎SW-HFA-C-ACC2 | ‎Fa0/11 |
| ‎15 | ‎Straight | ‎PRN-HFA-C-01 | ‎Fa0 | ‎SW-HFA-C-ACC1 | ‎Fa0/21 |

</div>

✅ ‏15 כבלים, התוויות נבדקו. ‏**File → Save**.

---

## משימה 5 — ‏B-DIST1, חלק 1: הקשחה, ‏VTP, ‏VLANים, ‏STP, ‏trunks, ‏EtherChannel
👉 **איפה:** ‏**SWL3-HFA-B-DIST1** ‏←‏ CLI ‏←‏ **Enter** ‏←‏ `Switch>`‎ (מתג חדש, עוד אין סיסמאות).

### 5א — הקשחה (שלב 02)
⌨️ מקלידים:
```
enable
configure terminal
hostname SWL3-HFA-B-DIST1
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
```

### 5ב — שרת ה-VTP של בניין B + ‏VLANים (שלב 03)
⌨️ מקלידים:
```
vtp domain HFA-B
vtp version 2
vtp password Intel#Vtp
vtp mode server
vlan 40
 name HR
vlan 50
 name MARKETING
vlan 60
 name PRINTERS-B
vlan 99
 name MGMT-B
vlan 998
 name NATIVE
vlan 999
 name PARKING
 exit
```

### 5ג — ‏Spanning Tree, ‏trunks, ‏EtherChannel, פורטים שלא בשימוש (שלבים 03–04)
‏B-DIST1 הוא הבוס של 40, ‏60, ‏99; סגן של 50.

⌨️ מקלידים:
```
spanning-tree mode rapid-pvst
spanning-tree vlan 40,60,99 root primary
spanning-tree vlan 50 root secondary
interface range gi1/0/1 - 2
 description TRUNK to access switch
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 40,50,60,99,998
 switchport nonegotiate
 spanning-tree guard root
 no shutdown
interface range gi1/0/23 - 24
 description Po1 member to SWL3-HFA-B-DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 40,50,60,99,998
 switchport nonegotiate
 channel-group 1 mode active
 no shutdown
interface port-channel 1
 description EtherChannel to SWL3-HFA-B-DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 40,50,60,99,998
 switchport nonegotiate
interface range gi1/0/3 - 22
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 exit
```
🔍 **בודקים עכשיו:** ‏`do show vlan brief` ‏←‏ ‏VLANים 40, ‏50, ‏60, ‏99, ‏998, ‏999 עם השמות שלהם.

---

## משימה 6 — ‏B-DIST1, חלק 2: שערים, ‏DHCP, קישורים כלפי מעלה, ‏OSPF, ניהול
👉 **איפה:** ‏B-DIST1, שורת הפקודה `SWL3-HFA-B-DIST1(config)#`‎.

### 6א — שערים: ‏SVIs + HSRP (שלב 05)
‏priority **‏110** ב-40, ‏60, ‏99 (‏B-DIST1 הוא Active); **‏90** ב-50.

⌨️ מקלידים:
```
ip routing
interface vlan 40
 description GW HR
 ip address 10.10.32.2 255.255.255.0
 standby version 2
 standby 40 ip 10.10.32.1
 standby 40 priority 110
 standby 40 preempt
 no shutdown
interface vlan 50
 description GW MARKETING
 ip address 10.10.33.2 255.255.255.0
 standby version 2
 standby 50 ip 10.10.33.1
 standby 50 priority 90
 standby 50 preempt
 no shutdown
interface vlan 60
 description GW PRINTERS-B
 ip address 10.10.34.2 255.255.255.0
 standby version 2
 standby 60 ip 10.10.34.1
 standby 60 priority 110
 standby 60 preempt
 no shutdown
interface vlan 99
 description GW MGMT-B
 ip address 10.10.35.2 255.255.255.0
 standby version 2
 standby 99 ip 10.10.35.1
 standby 99 priority 110
 standby 99 preempt
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
 exit
```

### 6ב — חלוקת טווח DHCP: המתג הזה מחלק ‎.11–.130 (שלב 05)
⌨️ מקלידים:
```
ip dhcp excluded-address 10.10.32.1 10.10.32.10
ip dhcp excluded-address 10.10.32.131 10.10.32.254
ip dhcp excluded-address 10.10.33.1 10.10.33.10
ip dhcp excluded-address 10.10.33.131 10.10.33.254
ip dhcp pool HFA-HR
 network 10.10.32.0 255.255.255.0
 default-router 10.10.32.1
 dns-server 10.10.200.11
 domain-name intel.lab
ip dhcp pool HFA-MARKETING
 network 10.10.33.0 255.255.255.0
 default-router 10.10.33.1
 dns-server 10.10.200.11
 domain-name intel.lab
 exit
```

### 6ג — קישורים מנותבים כלפי מעלה: ל-core ‏(area 0) ולבניין C ‏(area 2) (שלב 08)
⌨️ מקלידים:
```
interface loopback 0
 ip address 10.10.5.21 255.255.255.255
interface gi1/1/1
 description to SWL3-HFA-CORE1 Gi1/0/3
 no switchport
 ip address 10.10.4.17 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/1/2
 description to SWL3-HFA-CORE2 Gi1/0/3
 no switchport
 ip address 10.10.4.21 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/1/3
 description to SWL3-HFA-C-DIST1 Gi1/1/1
 no switchport
 ip address 10.10.36.1 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/1/4
 description to SWL3-HFA-C-DIST2 Gi1/1/1
 no switchport
 ip address 10.10.36.9 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
 exit
```

### 6ד — ‏OSPF: ‏ABR בין area 0 ל-area 2 (שלב 08)
⌨️ מקלידים:
```
router ospf 1
 router-id 10.10.5.21
 passive-interface default
 no passive-interface gi1/1/1
 no passive-interface gi1/1/2
 no passive-interface gi1/1/3
 no passive-interface gi1/1/4
 no passive-interface vlan 99
 network 10.10.0.0 0.0.15.255 area 0
 network 10.10.32.0 0.0.15.255 area 2
 area 2 range 10.10.32.0 255.255.240.0
 exit
```

### 6ה — ניהול
⌨️ הקלידו את **🅼 בלוק הניהול למתגי שכבה 3** מסעיף 1.6 (ענו ‎`1024` לשאלה על המפתח).

✅ ‏‎`[OK]`‎ בסוף. 🔍 ‏`show ip interface brief` ‏←‏ ‏Loopback0 ‏‎`10.10.5.21`, ‏Gi1/1/1–4
ו-Vlan40/50/60/99 עם הכתובות מסעיף 1.5.

---

## משימה 7 — ‏B-DIST2: תמונת המראה של B-DIST1
👉 **איפה:** ‏**SWL3-HFA-B-DIST2** ‏←‏ CLI ‏←‏ **Enter** ‏←‏ `Switch>`‎.

מה משתנה לעומת B-DIST1:

<div dir="rtl">

| | ‎B-DIST1 | ‎**B-DIST2** |
|---|---|---|
| ‎hostname | ‎SWL3-HFA-B-DIST1 | ‎**SWL3-HFA-B-DIST2** |
| ‎VTP | ‏server + יוצר את ה-VLANים | **‏transparent ‏←‏ client, בלי פקודות `vlan`** |
| ‎STP root primary / secondary | ‎40,60,99 / 50 | ‎**50 / 40,60,99** |
| כתובות ה-SVI | ‎.2 | **‎.3** |
| ‏HSRP priority 110 ב- | ‎40, 60, 99 | ‎**50** |
| ‏DHCP מחלק | ‎.11–.130 | **‎.131–.254** |
| ‎Loopback0 / router-id | ‎10.10.5.21 | ‎**10.10.5.22** |
| ‎Gi1/1/1, Gi1/1/2 | ‎10.10.4.17, .21 | ‎**10.10.4.25, .29** |
| ‎Gi1/1/3, Gi1/1/4 | ‎10.10.36.1, .9 | ‎**10.10.36.5, .13** |

</div>

### 7א — הקשחה, ‏VTP client, ‏STP, ‏trunks, ‏EtherChannel
⌨️ מקלידים:
```
enable
configure terminal
hostname SWL3-HFA-B-DIST2
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vtp domain HFA-B
vtp version 2
vtp password Intel#Vtp
vtp mode client
spanning-tree mode rapid-pvst
spanning-tree vlan 50 root primary
spanning-tree vlan 40,60,99 root secondary
interface range gi1/0/1 - 2
 description TRUNK to access switch
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 40,50,60,99,998
 switchport nonegotiate
 spanning-tree guard root
 no shutdown
interface range gi1/0/23 - 24
 description Po1 member to SWL3-HFA-B-DIST1
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 40,50,60,99,998
 switchport nonegotiate
 channel-group 1 mode active
 no shutdown
interface port-channel 1
 description EtherChannel to SWL3-HFA-B-DIST1
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 40,50,60,99,998
 switchport nonegotiate
interface range gi1/0/3 - 22
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 exit
```
לחצו **Fast Forward Time**. 🔍 **בודקים עכשיו:** ‏`do show etherchannel summary` ‏←‏ `Po1(SU)`‎, שני
החברים ‎`(P)`‎; ‏`do show vlan brief` ‏←‏ ה-VLANים של בניין B הגיעו ב-VTP.

### 7ב — שערים ו-DHCP
⌨️ מקלידים:
```
ip routing
interface vlan 40
 description GW HR
 ip address 10.10.32.3 255.255.255.0
 standby version 2
 standby 40 ip 10.10.32.1
 standby 40 priority 90
 standby 40 preempt
 no shutdown
interface vlan 50
 description GW MARKETING
 ip address 10.10.33.3 255.255.255.0
 standby version 2
 standby 50 ip 10.10.33.1
 standby 50 priority 110
 standby 50 preempt
 no shutdown
interface vlan 60
 description GW PRINTERS-B
 ip address 10.10.34.3 255.255.255.0
 standby version 2
 standby 60 ip 10.10.34.1
 standby 60 priority 90
 standby 60 preempt
 no shutdown
interface vlan 99
 description GW MGMT-B
 ip address 10.10.35.3 255.255.255.0
 standby version 2
 standby 99 ip 10.10.35.1
 standby 99 priority 90
 standby 99 preempt
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
 exit
! DHCP: this switch gives .131-.254
ip dhcp excluded-address 10.10.32.1 10.10.32.130
ip dhcp excluded-address 10.10.33.1 10.10.33.130
ip dhcp pool HFA-HR
 network 10.10.32.0 255.255.255.0
 default-router 10.10.32.1
 dns-server 10.10.200.11
 domain-name intel.lab
ip dhcp pool HFA-MARKETING
 network 10.10.33.0 255.255.255.0
 default-router 10.10.33.1
 dns-server 10.10.200.11
 domain-name intel.lab
 exit
```

### 7ג — קישורים כלפי מעלה ו-OSPF
⌨️ מקלידים:
```
interface loopback 0
 ip address 10.10.5.22 255.255.255.255
interface gi1/1/1
 description to SWL3-HFA-CORE1 Gi1/0/4
 no switchport
 ip address 10.10.4.25 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/1/2
 description to SWL3-HFA-CORE2 Gi1/0/4
 no switchport
 ip address 10.10.4.29 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/1/3
 description to SWL3-HFA-C-DIST1 Gi1/1/2
 no switchport
 ip address 10.10.36.5 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/1/4
 description to SWL3-HFA-C-DIST2 Gi1/1/2
 no switchport
 ip address 10.10.36.13 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
 exit
router ospf 1
 router-id 10.10.5.22
 passive-interface default
 no passive-interface gi1/1/1
 no passive-interface gi1/1/2
 no passive-interface gi1/1/3
 no passive-interface gi1/1/4
 no passive-interface vlan 99
 network 10.10.0.0 0.0.15.255 area 0
 network 10.10.32.0 0.0.15.255 area 2
 area 2 range 10.10.32.0 255.255.240.0
 exit
```

### 7ד — ניהול
⌨️ הקלידו את **🅼 בלוק הניהול למתגי שכבה 3** (סעיף 1.6).

✅ ‏‎`[OK]`‎. לחצו Fast Forward Time. 🔍 ‏`show standby brief` ‏←‏ ‏Active ל-50, ‏Standby ל-40/60/99.

---

## משימה 8 — ‏B-ACC1 ו-B-ACC2

### 8א — ‏SW-HFA-B-ACC1
👉 **איפה:** ‏**SW-HFA-B-ACC1** ‏←‏ CLI ‏←‏ **Enter** ‏←‏ `Switch>`‎.

⌨️ **הקשחה + VTP client** (שלבים 02–03):
```
enable
configure terminal
hostname SW-HFA-B-ACC1
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vtp domain HFA-B
vtp version 2
vtp password Intel#Vtp
vtp mode client
spanning-tree mode rapid-pvst
```
⌨️ **קישורים כלפי מעלה, פורטי משתמשים, מדפסת, פורטים שלא בשימוש** (שלבים 02–04, ‏06):
```
interface range gi0/1 - 2
 description TRUNK uplink to B-DIST1 / B-DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 40,50,60,99,998
 switchport nonegotiate
 ip dhcp snooping trust
 no shutdown
interface range fa0/1 - 10
 description HR users
 switchport mode access
 switchport access vlan 40
interface range fa0/11 - 20
 description MARKETING users
 switchport mode access
 switchport access vlan 50
interface range fa0/1 - 20
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
 ip dhcp snooping limit rate 10
 no cdp enable
interface fa0/21
 description PRN-HFA-B-01
 switchport mode access
 switchport access vlan 60
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
```
⌨️ **‏DHCP snooping + כתובת ניהול** (שלבים 05–06):
```
ip dhcp snooping
ip dhcp snooping vlan 40,50,60,99
no ip dhcp snooping information option
interface vlan 99
 description MANAGEMENT
 ip address 10.10.35.11 255.255.255.0
 no shutdown
 exit
ip default-gateway 10.10.35.1
```
⌨️ ואחר כך את **🅰 בלוק הניהול למתגי access** (סעיף 1.6).

✅ ‏‎`[OK]`‎.

### 8ב — ‏SW-HFA-B-ACC2
👉 **איפה:** ‏**SW-HFA-B-ACC2** ‏←‏ CLI ‏←‏ **Enter** ‏←‏ `Switch>`‎.

בדיוק כמו 8א, עם **שני שינויים**: ‏`hostname SW-HFA-B-ACC2` וכתובת הניהול ‎`10.10.35.12`. הנה
הבלוק המלא, כדי שלא תצטרכו לגלול:

⌨️ מקלידים:
```
enable
configure terminal
hostname SW-HFA-B-ACC2
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vtp domain HFA-B
vtp version 2
vtp password Intel#Vtp
vtp mode client
spanning-tree mode rapid-pvst
interface range gi0/1 - 2
 description TRUNK uplink to B-DIST1 / B-DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 40,50,60,99,998
 switchport nonegotiate
 ip dhcp snooping trust
 no shutdown
interface range fa0/1 - 10
 description HR users
 switchport mode access
 switchport access vlan 40
interface range fa0/11 - 20
 description MARKETING users
 switchport mode access
 switchport access vlan 50
interface range fa0/1 - 20
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
 ip dhcp snooping limit rate 10
 no cdp enable
interface fa0/21
 description printer
 switchport mode access
 switchport access vlan 60
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
ip dhcp snooping vlan 40,50,60,99
no ip dhcp snooping information option
interface vlan 99
 description MANAGEMENT
 ip address 10.10.35.12 255.255.255.0
 no shutdown
 exit
ip default-gateway 10.10.35.1
```
⌨️ ואחר כך את **🅰 בלוק הניהול למתגי access**.

✅ ‏‎`[OK]`‎. 🔍 ב-B-ACC2: ‏`show vtp status` ‏←‏ דומיין `HFA-B`, מצב Client;
‏`show interfaces trunk` ‏←‏ ‏Gi0/1, ‏Gi0/2 במצב trunking, ‏native 998.

---

## משימה 9 — פותחים את פורטי ה-core לכיוון בניין B
הפורטים האלה היו ב"חניה" וכבויים מאז שלב 08. עכשיו הם הופכים לקישורים מנותבים.

### 9א — ‏SWL3-HFA-CORE1
👉 ‏CORE1 ‏←‏ CLI ‏←‏ נכנסים (`admin` / `Intel#Adm1n`) ‏←‏ `SWL3-HFA-CORE1#`‎.

⌨️ מקלידים:
```
configure terminal
interface gi1/0/3
 description to SWL3-HFA-B-DIST1 Gi1/1/1
 no switchport
 ip address 10.10.4.18 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/0/4
 description to SWL3-HFA-B-DIST2 Gi1/1/1
 no switchport
 ip address 10.10.4.26 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
 exit
router ospf 1
 no passive-interface gi1/0/3
 no passive-interface gi1/0/4
 end
copy running-config startup-config
```

### 9ב — ‏SWL3-HFA-CORE2
👉 ‏CORE2 ‏←‏ CLI ‏←‏ נכנסים ‏←‏ `SWL3-HFA-CORE2#`‎. הכתובות ‎`.22` ו-‎`.30`:

⌨️ מקלידים:
```
configure terminal
interface gi1/0/3
 description to SWL3-HFA-B-DIST1 Gi1/1/2
 no switchport
 ip address 10.10.4.22 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/0/4
 description to SWL3-HFA-B-DIST2 Gi1/1/2
 no switchport
 ip address 10.10.4.30 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
 exit
router ospf 1
 no passive-interface gi1/0/3
 no passive-interface gi1/0/4
 end
copy running-config startup-config
```
לחצו **Fast Forward Time** כמה פעמים.

✅ ‏‎`%OSPF-5-ADJCHG ... Nbr 10.10.5.21 ... to FULL` ו-‎`... 10.10.5.22 ... to FULL` בשני מתגי ה-core.

---

## משימה 10 — מכשירי הקצה של בניין B + בדיקת בניין B

### 10א — מכשירי קצה
- ‏**מחשבים** HR-01, ‏HR-02, ‏MKT-01, ‏MKT-02: ‏Desktop ‏←‏ IP Configuration ‏←‏ **DHCP** ‏(M16).
- ‏**PRN-HFA-B-01** ‏(M15): ‏Config ‏←‏ FastEthernet0 ‏←‏ **Static**, ‏IP ‏‎`10.10.34.10`, מסיכה
  ‏‎`255.255.255.0`; ‏Config ‏←‏ Settings ‏←‏ Gateway ‏‎`10.10.34.1`.

### 10ב — בודקים את בניין B לפני שממשיכים

<div dir="rtl">

| ‎# | איפה | מקלידים | ✅ צפוי |
|---|---|---|---|
| ‎1 | ‎CORE1 | ‎`show ip route ospf` | ‏`O IA 10.10.32.0/20` דרך B-DIST1 **וגם** B-DIST2 |
| ‎2 | ‎B-DIST1 | ‎`show ip ospf neighbor` | ‏CORE1, ‏CORE2 ו-B-DIST2 — כולם FULL |
| ‎3 | ‎B-DIST1 | ‎`show standby brief` | ‏Active ל-40/60/99, ‏Standby ל-50 |
| ‎4 | ‎B-DIST1 | ‎`show etherchannel summary` | ‏`Po1(SU)`‎, שניהם ‎`(P)`‎ |
| ‎5 | ‎PC-HFA-HR-01 | ‎`ipconfig` | כתובת ‎`10.10.32.x`, שער ‎`10.10.32.1` |
| ‎6 | ‎PC-HFA-HR-01 | ‏`ping` למחשב Engineering בבניין A | יש תשובות |

</div>

❌ אל תתחילו את בניין C לפני שכל השש עוברות. **File → Save**.

---

## משימה 11 — ‏C-DIST1
👉 **איפה:** ‏**SWL3-HFA-C-DIST1** ‏←‏ CLI ‏←‏ **Enter** ‏←‏ `Switch>`‎.

בניין C הוא כמו בניין B עם מספרים משלו: ‏VTP ‏`HFA-C`, ‏VLANים 70/80/90/99, ‏C-DIST1 הוא הבוס
של 70, ‏90, ‏99. **ההבדל הגדול הוא ה-OSPF ‏(11ד): אין כאן area 0.**

### 11א — הקשחה, שרת VTP, ‏VLANים
⌨️ מקלידים:
```
enable
configure terminal
hostname SWL3-HFA-C-DIST1
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp domain HFA-C
vtp version 2
vtp password Intel#Vtp
vtp mode server
vlan 70
 name RND
vlan 80
 name IT
vlan 90
 name PRINTERS-C
vlan 99
 name MGMT-C
vlan 998
 name NATIVE
vlan 999
 name PARKING
 exit
```

### 11ב — ‏STP, ‏trunks, ‏EtherChannel, פורטים שלא בשימוש
⌨️ מקלידים:
```
spanning-tree mode rapid-pvst
spanning-tree vlan 70,90,99 root primary
spanning-tree vlan 80 root secondary
interface range gi1/0/1 - 2
 description TRUNK to access switch
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 70,80,90,99,998
 switchport nonegotiate
 spanning-tree guard root
 no shutdown
interface range gi1/0/23 - 24
 description Po1 member to SWL3-HFA-C-DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 70,80,90,99,998
 switchport nonegotiate
 channel-group 1 mode active
 no shutdown
interface port-channel 1
 description EtherChannel to SWL3-HFA-C-DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 70,80,90,99,998
 switchport nonegotiate
interface range gi1/0/3 - 22
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 exit
```

### 11ג — שערים ו-DHCP ‏(‎.11–.130)
⌨️ מקלידים:
```
ip routing
interface vlan 70
 description GW RND
 ip address 10.10.48.2 255.255.255.0
 standby version 2
 standby 70 ip 10.10.48.1
 standby 70 priority 110
 standby 70 preempt
 no shutdown
interface vlan 80
 description GW IT
 ip address 10.10.49.2 255.255.255.0
 standby version 2
 standby 80 ip 10.10.49.1
 standby 80 priority 90
 standby 80 preempt
 no shutdown
interface vlan 90
 description GW PRINTERS-C
 ip address 10.10.50.2 255.255.255.0
 standby version 2
 standby 90 ip 10.10.50.1
 standby 90 priority 110
 standby 90 preempt
 no shutdown
interface vlan 99
 description GW MGMT-C
 ip address 10.10.51.2 255.255.255.0
 standby version 2
 standby 99 ip 10.10.51.1
 standby 99 priority 110
 standby 99 preempt
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
 exit
ip dhcp excluded-address 10.10.48.1 10.10.48.10
ip dhcp excluded-address 10.10.48.131 10.10.48.254
ip dhcp excluded-address 10.10.49.1 10.10.49.10
ip dhcp excluded-address 10.10.49.131 10.10.49.254
ip dhcp pool HFA-RND
 network 10.10.48.0 255.255.255.0
 default-router 10.10.48.1
 dns-server 10.10.200.11
 domain-name intel.lab
ip dhcp pool HFA-IT
 network 10.10.49.0 255.255.255.0
 default-router 10.10.49.1
 dns-server 10.10.200.11
 domain-name intel.lab
 exit
```

### 11ד — ‏Loopback, קישורים כלפי מעלה לבניין B, ‏OSPF areas 2 ו-3 (אין כאן area 0!)
⌨️ מקלידים:
```
! loopback inside AREA 3's block
interface loopback 0
 ip address 10.10.63.1 255.255.255.255
! uplinks to building B (area 2)
interface gi1/1/1
 description to SWL3-HFA-B-DIST1 Gi1/1/3
 no switchport
 ip address 10.10.36.2 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/1/2
 description to SWL3-HFA-B-DIST2 Gi1/1/3
 no switchport
 ip address 10.10.36.6 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
 exit
router ospf 1
 router-id 10.10.63.1
 passive-interface default
 no passive-interface gi1/1/1
 no passive-interface gi1/1/2
 no passive-interface vlan 99
 network 10.10.36.0 0.0.0.15 area 2
 network 10.10.48.0 0.0.15.255 area 3
 area 3 range 10.10.48.0 255.255.240.0
 exit
```

<div dir="rtl">

> ‏`network 10.10.36.0 0.0.0.15` = ‏16 הכתובות 10.10.36.0–15: בדיוק ארבעת הקישורים בין B ל-C.

</div>

### 11ה — ניהול
⌨️ הקלידו את **🅼 בלוק הניהול למתגי שכבה 3** (סעיף 1.6).

✅ ‏‎`[OK]`‎.

---

## משימה 12 — ‏C-DIST2
👉 **איפה:** ‏**SWL3-HFA-C-DIST2** ‏←‏ CLI ‏←‏ **Enter** ‏←‏ `Switch>`‎.

<div dir="rtl">

| | ‎C-DIST1 | ‎**C-DIST2** |
|---|---|---|
| ‎VTP | ‏server + ‏VLANים | ‎**‏transparent ‏←‏ client** |
| ‎STP root primary / secondary | ‎70,90,99 / 80 | ‎**80 / 70,90,99** |
| ‏SVIs / ‏HSRP 110 ב- | ‎.2 / 70, 90, 99 | **‎.3 / 80** |
| ‏DHCP מחלק | ‎.11–.130 | **‎.131–.254** |
| ‎Loopback0 / router-id | ‎10.10.63.1 | ‎**10.10.63.2** |
| ‎Gi1/1/1, Gi1/1/2 | ‎10.10.36.2, .6 | ‎**10.10.36.10, .14** |

</div>

### 12א — הקשחה, ‏VTP, ‏STP, ‏trunks, ‏EtherChannel
⌨️ מקלידים:
```
enable
configure terminal
hostname SWL3-HFA-C-DIST2
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vtp domain HFA-C
vtp version 2
vtp password Intel#Vtp
vtp mode client
spanning-tree mode rapid-pvst
spanning-tree vlan 80 root primary
spanning-tree vlan 70,90,99 root secondary
interface range gi1/0/1 - 2
 description TRUNK to access switch
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 70,80,90,99,998
 switchport nonegotiate
 spanning-tree guard root
 no shutdown
interface range gi1/0/23 - 24
 description Po1 member to SWL3-HFA-C-DIST1
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 70,80,90,99,998
 switchport nonegotiate
 channel-group 1 mode active
 no shutdown
interface port-channel 1
 description EtherChannel to SWL3-HFA-C-DIST1
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 70,80,90,99,998
 switchport nonegotiate
interface range gi1/0/3 - 22
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 exit
```

### 12ב — שערים ו-DHCP ‏(‎.131–.254)
⌨️ מקלידים:
```
ip routing
interface vlan 70
 description GW RND
 ip address 10.10.48.3 255.255.255.0
 standby version 2
 standby 70 ip 10.10.48.1
 standby 70 priority 90
 standby 70 preempt
 no shutdown
interface vlan 80
 description GW IT
 ip address 10.10.49.3 255.255.255.0
 standby version 2
 standby 80 ip 10.10.49.1
 standby 80 priority 110
 standby 80 preempt
 no shutdown
interface vlan 90
 description GW PRINTERS-C
 ip address 10.10.50.3 255.255.255.0
 standby version 2
 standby 90 ip 10.10.50.1
 standby 90 priority 90
 standby 90 preempt
 no shutdown
interface vlan 99
 description GW MGMT-C
 ip address 10.10.51.3 255.255.255.0
 standby version 2
 standby 99 ip 10.10.51.1
 standby 99 priority 90
 standby 99 preempt
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
 exit
ip dhcp excluded-address 10.10.48.1 10.10.48.130
ip dhcp excluded-address 10.10.49.1 10.10.49.130
ip dhcp pool HFA-RND
 network 10.10.48.0 255.255.255.0
 default-router 10.10.48.1
 dns-server 10.10.200.11
 domain-name intel.lab
ip dhcp pool HFA-IT
 network 10.10.49.0 255.255.255.0
 default-router 10.10.49.1
 dns-server 10.10.200.11
 domain-name intel.lab
 exit
```

### 12ג — ‏Loopback, קישורים כלפי מעלה, ‏OSPF
⌨️ מקלידים:
```
interface loopback 0
 ip address 10.10.63.2 255.255.255.255
interface gi1/1/1
 description to SWL3-HFA-B-DIST1 Gi1/1/4
 no switchport
 ip address 10.10.36.10 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/1/2
 description to SWL3-HFA-B-DIST2 Gi1/1/4
 no switchport
 ip address 10.10.36.14 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
 exit
router ospf 1
 router-id 10.10.63.2
 passive-interface default
 no passive-interface gi1/1/1
 no passive-interface gi1/1/2
 no passive-interface vlan 99
 network 10.10.36.0 0.0.0.15 area 2
 network 10.10.48.0 0.0.15.255 area 3
 area 3 range 10.10.48.0 255.255.240.0
 exit
```

### 12ד — ניהול
⌨️ הקלידו את **🅼 בלוק הניהול למתגי שכבה 3** (סעיף 1.6).

✅ ‏‎`[OK]`‎.

---

## משימה 13 — ‏C-ACC1 ו-C-ACC2
אותו דבר כמו B-ACC1/2 (משימה 8) עם הערכים של בניין C: ‏VTP ‏`HFA-C`, ‏VLANים **‏70** ‏(R&D,
‏Fa0/1–10), **‏80** ‏(IT, ‏Fa0/11–20), **‏90** (מדפסת, ‏Fa0/21), ניהול ‎`10.10.51.11` / ‎`.12`,
שער ‎`10.10.51.1`.

### 13א — ‏SW-HFA-C-ACC1
👉 **איפה:** ‏**SW-HFA-C-ACC1** ‏←‏ CLI ‏←‏ **Enter** ‏←‏ `Switch>`‎.

⌨️ מקלידים:
```
enable
configure terminal
hostname SW-HFA-C-ACC1
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vtp domain HFA-C
vtp version 2
vtp password Intel#Vtp
vtp mode client
spanning-tree mode rapid-pvst
interface range gi0/1 - 2
 description TRUNK uplink to C-DIST1 / C-DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 70,80,90,99,998
 switchport nonegotiate
 ip dhcp snooping trust
 no shutdown
interface range fa0/1 - 10
 description RND users
 switchport mode access
 switchport access vlan 70
interface range fa0/11 - 20
 description IT users
 switchport mode access
 switchport access vlan 80
interface range fa0/1 - 20
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
 ip dhcp snooping limit rate 10
 no cdp enable
interface fa0/21
 description PRN-HFA-C-01
 switchport mode access
 switchport access vlan 90
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
ip dhcp snooping vlan 70,80,90,99
no ip dhcp snooping information option
interface vlan 99
 description MANAGEMENT
 ip address 10.10.51.11 255.255.255.0
 no shutdown
 exit
ip default-gateway 10.10.51.1
```
⌨️ ואחר כך את **🅰 בלוק הניהול למתגי access**. ✅ ‏‎`[OK]`‎.

### 13ב — ‏SW-HFA-C-ACC2
👉 **איפה:** ‏**SW-HFA-C-ACC2** ‏←‏ CLI ‏←‏ **Enter** ‏←‏ `Switch>`‎.

הקלידו **שוב את כל הבלוק של 13א**, כששתי שורות **משתנות**:
- ‏`hostname SW-HFA-C-ACC2`
- תחת `interface vlan 99`: ‏`ip address 10.10.51.12 255.255.255.0`

(ואם תרצו, `description printer` ב-Fa0/21 — זו רק תווית.)
אחר כך את **🅰 בלוק הניהול**. ✅ ‏‎`[OK]`‎.

🔍 ב-C-ACC2: ‏`show vlan brief` ‏←‏ ‏VLANים 70/80/90/99 הגיעו; ‏Fa0/1 ב-70, ‏Fa0/11 ב-80.

---

## משימה 14 — מכשירי הקצה של בניין C + רואים את הבעיה 🔍

### 14א — מכשירי קצה
- המחשבים RND-01, ‏RND-02, ‏IT-01, ‏IT-02 ‏←‏ **DHCP**.
- ‏PRN-HFA-C-01 ‏←‏ IP ‏‎`10.10.50.10` / ‏‎`255.255.255.0`, שער ‎`10.10.50.1`.

✅ המחשבים מקבלים ‎`10.10.48.x` ‏(R&D) ו-‎`10.10.49.x` ‏(IT) — ה-DHCP עובד **בתוך** הבניין.

### 14ב — רואים את הבעיה
לחצו **Fast Forward Time** כמה פעמים, ואז:

<div dir="rtl">

| ‎# | איפה | מקלידים | מה רואים | המשמעות |
|---|---|---|---|---|
| ‎1 | ‎B-DIST1 | ‎`show ip ospf neighbor` | ‏C-DIST1 ו-C-DIST2 במצב FULL | ‏area 2 עובד |
| ‎2 | ‎CORE1 | ‎`show ip route ospf` | ‏‎`10.10.16.0/20`, ‏‎`10.10.32.0/20` — אבל **אין** ‎`10.10.48.0/20` | ‏area 3 לא נראה ל-core |
| ‎3 | ‎PC-HFA-RND-01 | `ping 10.10.1.10` (שרת ה-Syslog) | ‎❌ ‏Request timed out | בניין C לא יכול לצאת |
| ‎4 | ‎C-DIST1 | ‎`show ip route` | אין נתיבי `O IA` מ-areas 0 ו-1 | האי מושלם |

</div>

✅ כל הארבע כמו שתואר. **זו התוצאה הצפויה** — הכלל מסעיף 1.2 בפעולה. כתבו במחברת, במשפט
אחד, **למה** זה קורה. אחר כך תקנו את זה במשימה 15.

---

## משימה 15 — ה-virtual links
🧠 **למה:** לתת לבניין C "חתיכה של area 0" דרך area 2.

### 15א — ב-B-DIST1 **וגם** ב-B-DIST2 ‏(ABRs של 0/2): מצביעים על ה-router-IDs של C
⌨️ מקלידים ב**כל אחד** מהשניים:
```
configure terminal
router ospf 1
 area 2 virtual-link 10.10.63.1
 area 2 virtual-link 10.10.63.2
 end
copy running-config startup-config
```

### 15ב — ב-C-DIST1 **וגם** ב-C-DIST2 ‏(ABRs של 2/3): מצביעים על ה-router-IDs של B
⌨️ מקלידים ב**כל אחד** מהשניים:
```
configure terminal
router ospf 1
 area 2 virtual-link 10.10.5.21
 area 2 virtual-link 10.10.5.22
 end
copy running-config startup-config
```
לחצו **Fast Forward Time**.

✅ מופיע ‎`%OSPF-5-ADJCHG: Process 1, Nbr 10.10.63.1 on OSPF_VL0 from LOADING to FULL`.

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎‏`area 2 virtual-link 10.10.63.1` | "בנה חתיכה של area 0 **דרך area 2**, אל הנתב שה-router-ID שלו הוא 10.10.63.1" |

</div>

🔍 **בודקים עכשיו:** ב-B-DIST1 ‏`show ip ospf virtual-links`:
```
Virtual Link OSPF_VL0 to router 10.10.63.1 is up
  Transit area 2, via interface GigabitEthernet1/1/3, Cost of using 1
  ...
Virtual Link OSPF_VL1 to router 10.10.63.2 is up
```
❌ ‏`is down` ‏←‏ הקלדתם **IP של ממשק** במקום ה-**router-ID**, או שאזור המעבר הוא לא ‎`2`.

---

## משימה 16 — מעדכנים את רשימת האורחים של 7 המכשירים הישנים
🧠 **למה:** גם ל-IT ול-VLANים החדשים של הניהול צריך להיות מותר לנהל את בניין A, את מתגי
ה-core ואת מתג השרתים.

ב-**SW-HFA-A-ACC1, ‏SW-HFA-A-ACC2, ‏SWL3-HFA-A-DIST1, ‏SWL3-HFA-A-DIST2, ‏SWL3-HFA-CORE1,
‏SWL3-HFA-CORE2, ‏SW-HFA-SRV** (נכנסים עם `admin` / `Intel#Adm1n`):

⌨️ מקלידים:
```
configure terminal
ip access-list standard MGMT-ONLY
 no deny any log
 permit 10.10.35.0 0.0.0.255
 permit 10.10.51.0 0.0.0.255
 permit 10.10.49.0 0.0.0.255
 deny any log
 end
copy running-config startup-config
```

<div dir="rtl">

> למה מוחקים קודם את ה-`deny`? שורות חדשות נוספות ל**תחתית** של ACL עם שם. אילו ה-`deny any`
> היה נשאר מעליהן, אף פעם לא היו מגיעים ל-permit החדשים.

</div>

🔍 בכל אחד: ‏`show access-lists MGMT-ONLY` ‏←‏ ‏4 שורות permit, ואחריהן ה-deny. סמנו:
- [ ] ‏A-ACC1
- [ ] ‏A-ACC2
- [ ] ‏A-DIST1
- [ ] ‏A-DIST2
- [ ] ‏CORE1
- [ ] ‏CORE2
- [ ] ‏SW-HFA-SRV

---

## משימה 17 — רושמים את 8 המכשירים החדשים בשרת ה-AAA
👉 **איפה:** ‏SRV-HFA-AAA ‏←‏ **Services → AAA → Network Configuration** (כמו בשלב 08, משימה 13).
לכל שורה: ‏Client Name, ‏Client IP, ‏Secret ‏`Intel#Tac`, ‏ServerType **Tacacs** ‏←‏ **Add**.

<div dir="rtl">

| ‎Client Name | ‎Client IP |
|---|---|
| ‎SWL3-HFA-B-DIST1 | ‎10.10.5.21 |
| ‎SWL3-HFA-B-DIST2 | ‎10.10.5.22 |
| ‎SW-HFA-B-ACC1 | ‎10.10.35.11 |
| ‎SW-HFA-B-ACC2 | ‎10.10.35.12 |
| ‎SWL3-HFA-C-DIST1 | ‎10.10.63.1 |
| ‎SWL3-HFA-C-DIST2 | ‎10.10.63.2 |
| ‎SW-HFA-C-ACC1 | ‎10.10.51.11 |
| ‎SW-HFA-C-ACC2 | ‎10.10.51.12 |

</div>

✅ ברשימת ה-clients יש עכשיו 15 שורות.

---

## משימה 18 — בדיקות סופיות

### 18א — ה-core רואה עכשיו כל בניין כנתיב אחד
👉 ב-**CORE1**: ‏`show ip route ospf`

✅ אמורים לראות:
```
O IA  10.10.16.0/20 ...   <- building A (area 1)
O IA  10.10.32.0/20 ...   <- building B (area 2)
O IA  10.10.48.0/20 ...   <- building C (area 3) — arrived through the virtual link!
```

### 18ב — פינגים ו-SSH

<div dir="rtl">

| ‎# | מאיפה | מקלידים | צפוי |
|---|---|---|---|
| ‎1 | ‎PC-HFA-RND-01 | ‎`ping 10.10.1.10` | ✅ (נכשל לפני ה-virtual link) |
| ‎2 | ‎PC-HFA-IT-01 | ‏`ping` למחשב Engineering בבניין A | ‎✅ |
| ‎3 | ‎PC-HFA-HR-01 | ‏`ping` למחשב R&D | ‎✅ |
| ‎4 | ‎PC-HFA-IT-01 | `ssh -l admin 10.10.19.11` (‏ACC1 בבניין A) | ✅ ל-IT מותר לנהל מכשירים |
| ‎5 | ‎PC-HFA-RND-01 | ‎`ssh -l admin 10.10.51.11` | ❌ נדחה (לא ברשימת האורחים) |

</div>

### 18ג — שומרים
‏`copy running-config startup-config` בכל מתג ששיניתם ‏←‏ **File → Save**.

---

## נקודת ביקורת
- [ ] המחשבים בבניינים B ו-C מקבלים כתובות DHCP ממתגי ה-DIST של הבניין שלהם
- [ ] כל 4 ה-virtual links ‏up
- [ ] ל-CORE1 יש בדיוק שלושה נתיבי `O IA` של ‎/20
- [ ] כל מחשב בכל בניין מגיע לשרתים
- [ ] ‏IT יכול להתחבר ב-SSH לכל מתג; ‏R&D לא

## אם משהו לא עובד

<div dir="rtl">

| בעיה | פתרון |
|---|---|
| ה-virtual link נשאר down | השתמשתם ב-**IP של ממשק** במקום ב-**router-ID**; או שאזור המעבר הוא לא ‎`2`; או של-C-DIST עדיין אין שכן במצב FULL ב-area 2 |
| ל-C-DIST אין שכנים ב-area 2 | שגיאת כתיב במפתח ה-MD5 על קישור ‎10.10.36.x, או שחסר `network 10.10.36.0 0.0.0.15 area 2` |
| ה-core רואה הרבה נתיבים קטנים מ-area 2 | חסר `area 2 range 10.10.32.0 255.255.240.0` ב-B-DIST1/2 |
| המחשבים בבניין C לא מקבלים כתובת | שגיאת כתיב בדומיין ה-VTP ‏`HFA-C` במתג access, או snooping בלי `trust` על הקישורים כלפי מעלה |
| אזהרות ‎`% Access VLAN does not exist` | נורמלי בזמן ש-VTP לומד — ראו שלב 03 |
| לכל הקישורים של 3650 חדש יש נקודות אדומות | חסר לו ספק כוח (משימה 2ג) |

</div>

---

## 🏋 תרגילים

### תרגיל א — מוחקים את הסיכום ⭐⭐
- 🎯 **המשימה:** לראות מה הסיכום של area 2 מסתיר מה-core.
- 📁 **מתחילים מ:** ה-`step09.pkt` שלכם (‏Save As ‏`step09-exA.pkt`).
- 👣 **צעדים:**
  1. ב-B-DIST1 **וגם** ב-B-DIST2: ‏`configure terminal` ‏←‏ `router ospf 1` ‏←‏
     ‏`no area 2 range 10.10.32.0 255.255.240.0` ‏←‏ `end`.
  2. ‏Fast Forward Time. ב-CORE1: ‏`show ip route ospf`. ספרו את השורות שמתחילות ב-‎`10.10.3`.
  3. החזירו את הסיכום בשניהם.
- ✅ **גמרתם כש**אתם יודעים לומר כמה שורות נוספו, ולמה קישורי ה-‎`10.10.36.x` ביניהן.

<details dir="rtl"><summary>💡 רמז</summary>

אילו רשתות נמצאות ב-area 2? ה-VLANים של בניין B… ומה עוד?
</details>
<details dir="rtl"><summary>✔ תשובה</summary>

בלי הסיכום, כל רשת של area 2 מפורסמת בנפרד כ-`O IA`: ‏4 ה-VLANים (40, ‏50, ‏60, ‏99) **וגם**
ארבעת קישורי ה-‎/30 לבניין C — בערך 8 שורות במקום אחת. גם קישורי ה-‎/30 הם רשתות של area 2. עם
הסיכום הם מוסתרים בתוך 10.10.32.0/20 — ובגלל זה מספרנו אותם 10.10.36.x ולא 10.10.4.x.
</details>

### תרגיל ב — שוברים virtual link אחד ⭐⭐
- 🎯 **המשימה:** להוכיח שבניין C שורד אובדן של אחד משני מתגי ה-B-DIST.
- 📁 **מתחילים מ:** ה-`step09.pkt` שלכם — קודם **File → Save**.
- 👣 **צעדים:**
  1. מ-PC-HFA-RND-01 הפעילו `ping -t 10.10.1.10`.
  2. מחקו את **SWL3-HFA-B-DIST1** (כלי ה-Delete).
  3. הסתכלו על הפינג. ב-C-DIST1: ‏`show ip ospf virtual-links`.
  4. ‏**File → Open** לקובץ `step09.pkt` ששמרתם (ענו **No** לשמירה).
- ✅ **גמרתם כש**אתם יודעים להסביר למה הפינג חזר, ואילו virtual links עדיין למעלה.

<details dir="rtl"><summary>✔ תשובה</summary>

כמה פינגים הולכים לאיבוד, ואז הם ממשיכים: ה-virtual links אל ‎`10.10.5.22` ‏(B-DIST2) עדיין
למעלה, ולכן ל-area 3 עדיין יש דרך ל-area 0. בגלל זה בנינו את כל 4 הצירופים (B1↔C1, ‏B1↔C2,
‏B2↔C1, ‏B2↔C2) ולא רק אחד.
</details>

---

## 🛠 הפרויקט שלכם

עשיתם את השלב הזה על הדוגמה של אינטל. עכשיו עשו אותו שוב בפרויקט **שלכם**, עם הערכים
מהתוכנית **שלכם** (`my-project/plan.md`). הפקודות זהות — רק הערכים משתנים.

- [ ] פותחים את `my-project/step08.pkt` ‏←‏ **Save As** ‏`my-project/step09.pkt`
- [ ] קודם כותבים טבלאות משלכם, כמו 1.5: קישורים, ‏loopbacks, ‏VLANים, מי ה"ראשי"
- [ ] כותבים שני בלוקי ניהול משלכם, כמו 1.6, עם רשימת האורחים שלכם
- [ ] בונים, נותנים חשמל ומחברים את שאר הבניינים של המטה שלכם
- [ ] מגדירים את הבניין שנוגע ב-core; בודקים אותו (כמו משימה 10ב)
- [ ] מגדירים את הבניין שנוגע רק בבניין השני; **רואים את הבעיה**
- [ ] מוסיפים את ה-virtual links; מעדכנים את ה-ACL של המכשירים הישנים; רושמים את החדשים ב-AAA
- [ ] הבדיקות של משימה 18 עוברות בפרויקט שלכם

<div dir="rtl">

| בדוגמה | בפרויקט שלכם — לוקחים מ |
|---|---|
| בניינים B ו-C וה-VLANים שלהם 40–90 | תוכנית, חלק ד (הבניינים / המחלקות האחרים של המטה שלכם) |
| דומייני VTP ‏`HFA-B`, ‏`HFA-C` | דומיין אחד לכל בניין, בשמות שלכם |
| ‏Area 3 לא נוגע ב-area 0 ‏←‏ ‏virtual link דרך area 2 | משרד החינוך דורש OSPF virtual link (דרישה 8): בתכנון שלכם חייב להיות area אחד שמגיע ל-area 0 רק דרך area אחר |
| סיכום לכל area | ה-‎/20 שלכם לכל area |

</div>

**בדיקה:** ‏`show ip ospf virtual-links` מראה שהקישור **up**; כל מחלקה במטה מצליחה ping לכל
מחלקה אחרת.

💾 שמרו בשם `my-project/step09.pkt`.

---

## 🎓 מסבירים לבוחן

בבחינה, הבוחן מצביע על הפרויקט **שלכם** ומבקש **להסביר** ו**להראות**. תרגלו כל שאלה
**בקול**, ואז הראו את התשובה בפרויקט שלכם — לא בדוגמה. כסו את התשובה, ענו בעצמכם, ורק אז
פתחו והשוו.

★1–★3 = שאלה ממאגר השאלות של משרד החינוך (רמת קושי 1–3).
◆ = לא במאגר, אבל בוחנים שואלים אותה לעיתים קרובות.

**1. ★3 היכן הגדרת virtual link? מדוע?**

<details dir="rtl"><summary>תשובה</summary>

כל OSPF area חייב לגעת ב-area 0. הבניין שה-area שלו לא מחובר ישירות ל-area 0 מצורף לעמוד השדרה
**דרך** area מעבר (transit): ‏`area <transit> virtual-link <router-ID של ה-ABR השני>`‎ בשני ה-ABRs.
משרד החינוך דורש את המבנה הזה (דרישות 8, ‏22.16).

**איפה מראים:** `show ip ospf virtual-links` ‏←‏ "is up"
</details>

**2. ◆ למה area המעבר של virtual link לא יכול להיות stub?**

<details dir="rtl"><summary>תשובה</summary>

‏Virtual link צריך מידע ניתוב מלא ב-area המעבר; ‏stub areas חוסמים אותו, ולכן virtual link יכול
לעבור רק דרך area רגיל.

**איפה מראים:** —
</details>

**3. ★3 מהו STUB area? אילו LSAs הוא חוסם ואילו הוא מקבל?**

<details dir="rtl"><summary>תשובה</summary>

‏Area שלא מקבל נתיבים חיצוניים: ‏LSAs מסוג 4 ו-5 חסומים; הוא מקבל סוגים 1, ‏2, ‏3 ונתיב ברירת
מחדל מה-ABR. מגדירים עם `area X stub` ב**כל** הנתבים של ה-area.

**איפה מראים:** —
</details>

**4. ★3 מהו TOTALLY STUBBY area, ואיך הופכים stub area ל-totally stubby?**

<details dir="rtl"><summary>תשובה</summary>

הוא חוסם גם LSAs מסוג 3 (בין areas); ה-area מקבל רק סוגים 1, ‏2 ונתיב ברירת מחדל. רק ב-ABR:
‏`area X stub no-summary`.

**איפה מראים:** —
</details>

**5. ★3 מהו NSSA, ואיך הופכים אותו ל-totally NSSA?**

<details dir="rtl"><summary>תשובה</summary>

‏Not-So-Stubby Area: כמו stub, אבל נתב בתוכו רשאי להכניס נתיבים חיצוניים. הם עוברים כ-LSAs מסוג 7,
וה-ABR ממיר אותם לסוג 5. ‏Totally NSSA: ‏`area X nssa no-summary` ב-ABR.

**איפה מראים:** —
</details>

**6. ◆ איך מסכמים area ב-OSPF?**

<details dir="rtl"><summary>תשובה</summary>

ב-ABR: ‏`area <N> range <network> <mask>`‎ — נתיב אחד לכל ה-‎/20 של הבניין נשלח לעמוד השדרה.

**איפה מראים:** `show ip route` במתג core ‏←‏ ‏`O IA` אחד לכל בניין
</details>

---

## 🔁 עושים שוב — בלי המדריך

הבוחן יכול לבקש מכם להגדיר משהו שוב, מולו. תצליחו רק אם עשיתם את זה **בלי המדריך** לפני כן.
עשו את התרגיל הזה בפרויקט שלכם:

בעותק של קובץ שלב 09 שלכם, מחקו את ה-virtual link בשני ה-ABRs. הראו שה-area המרוחק כבר לא
נגיש (`show ip route`), ואז הוסיפו שוב את ה-virtual link בלי העמוד הזה. יעד: **‏5 דקות**. הסבירו
לבוחן למה ה-area צריך אותו.

---

## 👩‍🏫 הערות למורה
- **שיעור 1:** משחק חזרה — התלמידים אומרים מאיזה שלב מגיע כל בלוק בהגדרות של B-DIST1 (הקשחה = 02,
  ‏VTP = 03, ‏STP/EtherChannel = 04, ‏SVIs/HSRP/DHCP = 05, …). אחר כך בונים ומחווטים את שני הבניינים.
- **שיעור 2:** מגדירים את בניין B; בודקים לפי משימה 10ב.
- **שיעור 3:** מגדירים את בניין C; **עוצרים במשימה 14ב** ונותנים לכיתה לגלות את הבעיה. שואלים: "שכני
  ה-OSPF במצב FULL — אז למה ה-core לא רואה את area 3?" מובילים אותם לכלל "כל area חייב לגעת
  ב-area 0".
- **שיעור 4:** ‏virtual links ‏←‏ בדיקות ‏←‏ ה-ACL הסופית ‏←‏ אתגר.
- **שאלות נפוצות של תלמידים**
  - *"למה לא פשוט לחבר את בניין C ל-core?"* — בקמפוס אמיתי זה התכנון הטוב יותר! בונים כך כי משרד
    החינוך דורש virtual link ‏(22.16). כתבו את זה בספר הפרויקט.
  - *"למה router-ID ולא כתובת IP?"* — ה-virtual link הוא בין שני *נתבים*, לא בין שני ממשקים.
    ‏OSPF מזהה נתבים לפי router-ID.
- **טעויות אופייניות:** ספקי כוח חסרים (4 מתגי 3650 חדשים!); הצד הלא נכון של ה-‎/30 בקישורים בין B
  ל-C; שכחה לעדכן את ה-ACL במכשירים הישנים.
