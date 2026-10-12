# שלב 03 — Trunks ו-VTP

<div dir="rtl">

> ⏱ ‏2 שיעורים · 🎯 דרישות משרד החינוך 22.6, ‏22.7, ‏22.8, ‏6\
> 📁 מתחילים מ: `my-work/step02.pkt`\
> 💾 שומרים בשם: `my-work/step03.pkt`

</div>

<div dir="rtl">

> ✅ **לפני שמתחילים:** כל הסעיפים בנקודת הביקורת של שלב 02 מסומנים, ועשיתם את
> תרגיל ה-🔁 שלו בפרויקט שלכם. אל תדלגו על שלבים — כל שלב בנוי על הקובץ של השלב הקודם.

</div>

## מה יהיה לכם בסוף השלב
בניין A מקבל את שני מתגי ה-**distribution** שלו ומתג access שני. לכל מתג access יש **שני
קישורי trunk כלפי מעלה** (אחד לכל מתג distribution). ה-VLANים נוצרים **פעם אחת** ב-DIST1
ומועתקים אוטומטית לשאר המתגים בעזרת **VTP**.

```
        SWL3-HFA-A-DIST1 (3650)            SWL3-HFA-A-DIST2 (3650)
          Gi1/0/1   Gi1/0/2                  Gi1/0/1   Gi1/0/2
             │         ╲                      ╱         │
             │           ╲──────────╲  ╱────╱           │
             │                       ╳                   │
             │           ╱──────────╱  ╲────╲           │
          Gi0/1     Gi0/2                      Gi0/1     Gi0/2
        SW-HFA-A-ACC1 (2960)                SW-HFA-A-ACC2 (2960)
     ACC1 Gi0/1→DIST1 Gi1/0/1   ACC1 Gi0/2→DIST2 Gi1/0/1
     ACC2 Gi0/1→DIST1 Gi1/0/2   ACC2 Gi0/2→DIST2 Gi1/0/2
```
(הכבל בין DIST1 ל-DIST2 יגיע בשלב 04.)

---

## חלק 1 — קודם מבינים (בשפה פשוטה)

### 1.1 הבעיה: VLANים על יותר ממתג אחד
מחשבי ההנדסה יושבים גם על **ACC1 וגם על ACC2**, ושני המתגים מחוברים למתגי ה-distribution.
איך מעבירים 8 VLANים בין מתגים? כבל לכל VLAN היה דורש 8 כבלים לכל קישור — בלתי אפשרי.

### 1.2 הפתרון: trunk
**‏trunk** הוא כבל אחד שמעביר **הרבה VLANים** בבת אחת.

חשבו על כביש מהיר בין שני בנייני משרדים. כל מכונית (frame — מסגרת) מקבלת **מדבקה צבעונית**
עם מספר החדר שלה (VLAN) כשהיא עולה על הכביש. בצד השני, המתג קורא את המדבקה, שולח את המכונית
לחדר הנכון, ומוריד את המדבקה.

- המדבקה נקראת **תג (tag)** ‏(4 בתים, לפי התקן **802.1Q**).
- **פורט access** = דלת לחדר אחד ‏←‏ בלי מדבקה (המחשב אף פעם לא רואה תגים).
- **פורט trunk** = הכביש המהיר ‏←‏ עם מדבקות.

<div dir="rtl">

| | פורט access | פורט trunk |
|---|---|---|
| מעביר | ‏VLAN אחד | הרבה VLANים |
| מתחבר אל | מחשב, מדפסת, נקודת גישה | מתג אחר / נתב |
| תגים | לא | כן (חוץ מה-native VLAN) |

</div>

### 1.3 ‏Native VLAN — המכוניות בלי מדבקה
ב-trunk, ‏VLAN אחד עובר **בלי** תג: ה-**native VLAN** ‏(VLAN 1 כברירת מחדל). תוקפים יכולים
לנצל את זה ("double tagging" — להחביא מדבקה שנייה מתחת לראשונה כדי לקפוץ ל-VLAN אחר). הפתרון
שלנו: native VLAN **998**, ‏VLAN שאף אחד לא משתמש בו. בשני הקצוות של trunk **חייב** להיות
אותו native VLAN.

### 1.4 רשימת ה-VLANים המותרים (allowed VLAN list)
כברירת מחדל trunk מעביר **את כל** ה-VLANים. אנחנו מפרטים רק את אלה שצריך
(‎`10,20,30,99,110,120,998`): פחות תעבורה מיותרת, ופחות דרכים לתוקף להיכנס.

### 1.5 ‏DTP — ולמה מכבים אותו
**‏DTP** מאפשר לשני פורטים *לנהל משא ומתן* ולהפוך ל-trunk לבד. נוח — אבל לפטופ יכול להתחזות
למתג, לנהל משא ומתן על trunk ולראות את כל ה-VLANים.
‏`switchport nonegotiate` מכבה את DTP: פורט הוא trunk רק כי **אנחנו** קבענו.

### 1.6 ‏VTP — רשימת VLANים אחת לכל הבניין
ליצור את אותם 8 VLANים ידנית בכל מתג זה איטי ומועד לטעויות. **‏VTP** ‏(VLAN Trunking Protocol)
הוא כמו משרד ראשי שמפרסם את הרשימה הרשמית של החדרים; כל משרד סניף מעתיק אותה אוטומטית
(ההודעות עוברות על קווי ה-trunk).

<div dir="rtl">

| מצב VTP | תפקיד | השוואה |
|---|---|---|
| ‎**‏Server** | כאן יוצרים / מוחקים / משנים שם ל-VLANים; שולח את הרשימה | המשרד הראשי |
| ‎**‏Client** | מקבל את הרשימה, לא יכול לשנות אותה | משרד סניף |
| ‎**‏Transparent** | מתעלם מהרשימה, שומר VLANים משלו (מעביר את ההודעות הלאה) | חנות עצמאית |

</div>

מתגים חולקים רשימה רק אם יש להם אותו **שם דומיין** ואותה **סיסמה**. כל בניין בחיפה הוא דומיין
נפרד (`HFA-A`, ‏`HFA-B`, ‏`HFA-C`), כי הבניינים יחוברו בקישורים **מנותבים**, שלא מעבירים VLANים.

⚠️ **הסכנה של מספר הגרסה (revision).** כל שינוי ברשימה מוסיף 1 ל-**configuration revision**
שלה. מתג תמיד מקבל את הרשימה עם המספר **הגבוה** ביותר — גם אם היא ריקה או שגויה. אסון
קלאסי: מישהו מחבר מתג ממעבדה (revision 50) לרשת של החברה ‏←‏ הרשימה שלו דורסת את של כולם ‏←‏
ה-VLANים נעלמים ‏←‏ החברה מושבתת. **כלל בטוח:** לפני שמצרפים מתג לדומיין, מעבירים אותו
ל-`vtp mode transparent` (מאפס את ה-revision ל-0), ורק אחר כך ל-`client`.

ל-ACC1 כבר יש revision גדול מ-0 (יצרתם עליו 8 VLANים בשלב 02) — ולכן משתמשים עליו בכלל הבטוח.

### 1.7 למה לכל מתג access יש שני קישורים כלפי מעלה
אם למתג access היה רק כבל אחד למתג distribution אחד, איבוד הכבל היה מנתק את כל מי שמחובר
למתג. עם **שני קישורים לשני מתגי distribution שונים**, כל אחד מהם יכול ליפול והמשתמשים
ממשיכים לעבוד (דרישה 6).

שני קישורים יוצרים **לולאה** ‏(ACC1 ‏←‏ DIST1 ‏←‏ ACC2 ‏←‏ DIST2 ‏←‏ ACC1). הודעת broadcast הייתה
מסתובבת לנצח ומשביתה את הרשת. **‏Spanning Tree Protocol** חוסם קישור אחד אוטומטית — ולכן
נורית של אחד הקישורים תישאר **כתומה**. בשלב 04 תשלטו בזה בעצמכם.

### 1.8 מתג שכבה 3 (ה-3650)
מתגי ה-distribution הם **Catalyst 3650** — מתגי שכבה 3. היום משתמשים בהם רק כמתגים; בשלב 05
הם יהפכו גם לנתבים. ב-Packet Tracer ה-3650 מגיע **בלי ספק כוח** — חייבים להוסיף אחד, אחרת
הוא נשאר כבוי.

---

## חלק 2 — הכנה
1. ‏**File → Open** ‏←‏ `my-work/step02.pkt` ‏←‏ **File → Save As** ‏←‏ `my-work/step03.pkt`.

---

## חלק 3 — בונים (לחיצה אחרי לחיצה)

### 3.1 מוסיפים את שני מתגי ה-3650
1. ‏**Network Devices → Switches** ‏←‏ גררו **3650-24PS** לתוך בניין A, מעל ACC1.
2. גררו **3650-24PS** שני לידו.
3. שנו את השמות (**Config → Display Name**): `SWL3-HFA-A-DIST1` ו-`SWL3-HFA-A-DIST2`.

### 3.2 נותנים לכל 3650 ספק כוח (⚠️ אל תדלגו)
לכל אחד משני ה-3650:
1. לחצו על המתג ‏←‏ לשונית **Physical**.
2. הגדילו את תמונת המכשיר (כפתור **Zoom In** באותו חלון). הסתכלו על הגב שלו: יש **חריץ
   ריק לספק כוח**.
3. ברשימת **MODULES** בצד שמאל, מצאו את **AC-POWER-SUPPLY**.
4. **גררו** אותו אל החריץ הריק. תמונת המתג משתנה והנוריות שלו נדלקות.
5. סגרו את החלון.
(אם המודול לא נכנס, ודאו שגררתם אותו בדיוק על החריץ הריק.)

### 3.3 מוסיפים את מתג ה-access השני ו-2 מחשבים
1. גררו **2960** ליד ACC1 ‏←‏ שנו את שמו ל-`SW-HFA-A-ACC2`.
2. גררו 2 מחשבים מתחתיו ‏←‏ שנו את שמותיהם ל-`PC-HFA-ENG-03` ו-`PC-HFA-FIN-03`.

### 3.4 כבלים — קישורים כלפי מעלה (מתג ↔ מתג = **Copper Cross-Over**)

<div dir="rtl">

| לחצו קודם על | פורט | לחצו אחר כך על | פורט |
|---|---|---|---|
| ‎SW-HFA-A-ACC1 | ‎**GigabitEthernet0/1** | ‎SWL3-HFA-A-DIST1 | ‎**GigabitEthernet1/0/1** |
| ‎SW-HFA-A-ACC1 | ‎**GigabitEthernet0/2** | ‎SWL3-HFA-A-DIST2 | ‎**GigabitEthernet1/0/1** |
| ‎SW-HFA-A-ACC2 | ‎**GigabitEthernet0/1** | ‎SWL3-HFA-A-DIST1 | ‎**GigabitEthernet1/0/2** |
| ‎SW-HFA-A-ACC2 | ‎**GigabitEthernet0/2** | ‎SWL3-HFA-A-DIST2 | ‎**GigabitEthernet1/0/2** |

</div>

### 3.5 כבלים — מחשבים (Copper **Straight-Through**)

<div dir="rtl">

| מכשיר | פורט | פורט במתג |
|---|---|---|
| ‎PC-HFA-ENG-03 | ‎FastEthernet0 | ‎SW-HFA-A-ACC2 **Fa0/1** |
| ‎PC-HFA-FIN-03 | ‎FastEthernet0 | ‎SW-HFA-A-ACC2 **Fa0/11** |

</div>

לחצו **Fast Forward Time** כמה פעמים. רוב הנוריות הופכות לירוקות; **קישור אחד או יותר נשאר
כתום** — זה Spanning Tree שחוסם את הלולאה (סעיף 1.7). נכון!

### 3.6 כתובות המחשבים (Desktop ‏←‏ IP Configuration ‏←‏ Static)

<div dir="rtl">

| מחשב | ‎IP | מסיכה |
|---|---|---|
| ‎PC-HFA-ENG-03 | ‎10.10.16.103 | ‎255.255.255.0 |
| ‎PC-HFA-FIN-03 | ‎10.10.17.103 | ‎255.255.255.0 |

</div>

---

## חלק 4 — מגדירים (הקלידו כל שורה; שורות שמתחילות ב-‎`!`‎ הן הערות)

### 4.1 ‏SWL3-HFA-A-DIST1 — בסיס + VTP **server** + trunks
לחצו עליו ‏←‏ **CLI** ‏←‏ לחצו Enter.
```
enable
configure terminal
! ---------- hardening (same as step 02) ----------
hostname SWL3-HFA-A-DIST1
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
line console 0
 password Intel#Con
 login
 logging synchronous
 exec-timeout 10 0
 exit

! ---------- VTP: this switch is the head office of building A ----------
vtp domain HFA-A
vtp version 2
vtp password Intel#Vtp
vtp mode server

! ---------- the VLAN list (created only here) ----------
vlan 10
 name ENGINEERING
vlan 20
 name FINANCE
vlan 30
 name PRINTERS-A
vlan 99
 name MGMT-A
vlan 110
 name WIFI-EMP
vlan 120
 name WIFI-GUEST
vlan 998
 name NATIVE
vlan 999
 name PARKING
 exit

! ---------- downlinks to ACC1 and ACC2 = trunks ----------
interface range gi1/0/1 - 2
 description TRUNK to access switch
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 10,20,30,99,110,120,998
 switchport nonegotiate
 no shutdown

! ---------- unused ports -> parking + off ----------
interface range gi1/0/3 - 22
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 end
copy running-config startup-config
```
ההערות בבלוק אומרות: הקשחה (כמו בשלב 02); ‏VTP — המתג הזה הוא המשרד הראשי של בניין A;
רשימת ה-VLANים (נוצרת רק כאן); הקישורים למטה ל-ACC1 ול-ACC2 = trunks; פורטים שלא בשימוש ‏←‏
חניה + כיבוי.

(הפורטים Gi1/0/23-24 נשארים כמו שהם — משתמשים בהם בשלב 04.)

<div dir="rtl">

> **הערה על ה-3650:** ה-3650 מדבר רק 802.1Q, ולכן הוא לא צריך (ולא מקבל) את הפקודה
> `switchport trunk encapsulation dot1q`. אם ה-Packet Tracer שלכם דורש אותה, הקלידו אותה לפני
> `switchport mode trunk`.

</div>

### 4.2 ‏SWL3-HFA-A-DIST2 — בסיס + VTP **client** + trunks
```
enable
configure terminal
hostname SWL3-HFA-A-DIST2
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
line console 0
 password Intel#Con
 login
 logging synchronous
 exec-timeout 10 0
 exit

! ---------- safe join: transparent first (revision -> 0), then client ----------
vtp mode transparent
vtp domain HFA-A
vtp version 2
vtp password Intel#Vtp
vtp mode client

interface range gi1/0/1 - 2
 description TRUNK to access switch
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 10,20,30,99,110,120,998
 switchport nonegotiate
 no shutdown
interface range gi1/0/3 - 22
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 end
copy running-config startup-config
```
ההערה אומרת: הצטרפות בטוחה — קודם transparent ‏(revision ‏←‏ 0), ואז client.
אין כאן פקודות `vlan` — ‏DIST2 מקבל את הרשימה מ-DIST1.

<div dir="rtl">

> ייתכן שתראו אזהרה כמו ‎`% Access VLAN does not exist` על `switchport access vlan 999`.
> זה תקין: DIST2 עוד לא קיבל את רשימת ה-VLANים (היא מגיעה ברגע שקווי ה-trunk של מתגי ה-access
> עולים, בסעיפים 4.3–4.4). ההגדרה נשמרת ומתחילה לעבוד כש-VLAN 999 מגיע.

</div>

### 4.3 ‏SW-HFA-A-ACC1 — מצטרף ל-VTP + קישורי trunk כלפי מעלה
‏ACC1 הוגדר בשלב 02. התחברו (סיסמת console ‏`Intel#Con`, ‏enable ‏`Intel#En4ble`):
```
enable
configure terminal
! ACC1 has revision > 0 from step 02 -> safe join
vtp mode transparent
vtp domain HFA-A
vtp version 2
vtp password Intel#Vtp
vtp mode client

interface range gi0/1 - 2
 description TRUNK uplink to DIST1 / DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 10,20,30,99,110,120,998
 switchport nonegotiate
 no shutdown
 end
copy running-config startup-config
```
ההערה אומרת: ל-ACC1 יש revision גדול מ-0 משלב 02 ‏←‏ הצטרפות בטוחה.

### 4.4 ‏SW-HFA-A-ACC2 — הכול (הוא חדש)
```
enable
configure terminal
hostname SW-HFA-A-ACC2
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
line console 0
 password Intel#Con
 login
 logging synchronous
 exec-timeout 10 0
 exit

vtp mode transparent
vtp domain HFA-A
vtp version 2
vtp password Intel#Vtp
vtp mode client

interface range gi0/1 - 2
 description TRUNK uplink to DIST1 / DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 10,20,30,99,110,120,998
 switchport nonegotiate
 no shutdown

interface range fa0/1 - 10
 description ENGINEERING users
 switchport mode access
 switchport access vlan 10
interface range fa0/11 - 20
 description FINANCE users
 switchport mode access
 switchport access vlan 20
interface fa0/21
 description printer
 switchport mode access
 switchport access vlan 30
interface fa0/22
 description AP-HFA-A-EMP (step 10)
 switchport mode access
 switchport access vlan 110
interface fa0/23
 description AP-HFA-A-GUEST (step 10)
 switchport mode access
 switchport access vlan 120
interface fa0/24
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 end
copy running-config startup-config
```
תוכנית הפורטים של ACC2: כמו ב-ACC1, חוץ מ-Fa0/22-23 ששמורים לשתי נקודות הגישה האלחוטיות.

### 4.5 מה הפקודות החדשות אומרות

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`vtp domain HFA-A` | "אני שייך למועדון ה-VLANים של בניין A" |
| ‎`vtp password Intel#Vtp` | סיסמת המועדון — רק חברים שיודעים אותה חולקים רשימות |
| ‎`vtp mode server` / `client` / `transparent` | משרד ראשי / משרד סניף / עצמאי |
| ‎`vtp version 2` | להשתמש ב-VTP גרסה 2 (כל החברים חייבים להתאים) |
| ‎`switchport mode trunk` | "הפורט הזה הוא כביש מהיר — העבר VLANים מתויגים" |
| ‎`switchport trunk native vlan 998` | "מכוניות בלי מדבקה שייכות ל-VLAN 998 שלא בשימוש" |
| ‎`switchport trunk allowed vlan ...`‎ | "רק ה-VLANים האלה רשאים לנסוע בכביש הזה" |
| ‎`switchport nonegotiate` | "אל תנהל משא ומתן עם מי שבצד השני (DTP כבוי)" |

</div>

---

## חלק 5 — בודקים את העבודה

### 5.1 ‏VTP
ב-**SW-HFA-A-ACC2**:
```
show vtp status
```
חפשו:
```
VTP Version capable             : 1 to 2
VTP version running             : 2
VTP Domain Name                 : HFA-A
VTP Operating Mode              : Client
Configuration Revision          : 16         <- your number may differ - it must be the SAME as on DIST1
```
(המספר של ה-Configuration Revision אצלכם יכול להיות שונה — אבל הוא חייב להיות **זהה** לזה של DIST1.)
הריצו `show vtp status` גם ב-DIST1: ה-**Configuration Revision** חייב להיות זהה.

```
show vlan brief
```
ב-ACC2 ‏←‏ כל 8 ה-VLANים נמצאים שם, למרות שאף פעם לא יצרתם אותם ב-ACC2. ✅ ‏VTP עובד.

### 5.2 ‏Trunks
ב-**SWL3-HFA-A-DIST1**:
```
show interfaces trunk
```
```
Port        Mode         Encapsulation  Status        Native vlan
Gig1/0/1    on           802.1q         trunking      998
Gig1/0/2    on           802.1q         trunking      998

Port        Vlans allowed on trunk
Gig1/0/1    10,20,30,99,110,120,998
...
```
✅ שני הפורטים במצב `trunking`, ‏native 998, ורשימת ה-VLANים המותרים שלנו.

### 5.3 ‏Ping דרך ה-trunk

<div dir="rtl">

| מאיפה | מקלידים | צפוי | למה |
|---|---|---|---|
| ‏PC-HFA-ENG-01 (על ACC1) | ‏`ping 10.10.16.103` (ENG-03 על ACC2) | ‎✅ | ‏VLAN 10 עובר על ה-trunks דרך מתג distribution |
| ‎PC-HFA-FIN-01 (ACC1) | ‏`ping 10.10.17.103` (FIN-03 על ACC2) | ‎✅ | גם VLAN 20 |
| ‎PC-HFA-ENG-01 | ‎`ping 10.10.17.103` | ‎❌ | עדיין אין נתב |

</div>

### 5.4 צופים ב-VTP בזמן אמת
1. ב-**DIST1**: `configure terminal` ‏←‏ `vlan 50` ‏←‏ `name TEST` ‏←‏ `end`.
2. ב-**ACC2**: `show vlan brief` ‏←‏ ‏VLAN 50 TEST מופיע תוך שניות.
3. ב-DIST1: `configure terminal` ‏←‏ `no vlan 50` ‏←‏ `end`. בדקו שוב ב-ACC2 ‏←‏ נעלם.
4. נסו ב-ACC2: `configure terminal` ‏←‏ `vlan 60` ‏←‏ תקבלו
   `VTP VLAN configuration not allowed when device is in CLIENT mode.` ✅

### 5.5 רואים את התג (מצב Simulation)
1. לחצו **Simulation** (ימין למטה). בחלונית לחצו **Show All/None** כדי לבטל את כל הסינונים,
   ואז **Edit Filters** ‏←‏ בלשונית **IPv4** סמנו רק **ICMP**. סגרו את חלון הסינון.
2. ‏**Add Simple PDU** (מעטפה) ‏←‏ לחצו על PC-HFA-ENG-01 ‏←‏ לחצו על PC-HFA-ENG-03.
3. לחצו **Capture / Forward** עד שהמעטפה נמצאת על כבל של קישור כלפי מעלה. לחצו על המעטפה.
4. ב-**Outbound PDU Details** רואים כותרת **802.1Q** עם `VLAN: 10`. על הכבל של המחשב עצמו
   אין כותרת כזו. זו המדבקה!
5. חזרו ל-**Realtime**.

---

## חלק 6 — שומרים
‏`copy running-config startup-config` בכל 4 המתגים (עשיתם את זה למעלה), ואז **File → Save**.

## נקודת ביקורת
- [ ] ל-DIST1 ול-DIST2 יש ספקי כוח והם דולקים
- [ ] ‏`show vtp status` — אותו דומיין ואותו revision בכל 4 המתגים; DIST1 הוא server, השאר client
- [ ] ‏`show interfaces trunk` — כל הקישורים כלפי מעלה במצב trunking, ‏native 998
- [ ] פינג ב-VLAN 10 וב-VLAN 20 עובד בין ACC1 ל-ACC2

## אם משהו לא עובד

<div dir="rtl">

| בעיה | פתרון |
|---|---|
| ה-3650 חשוך, אין פורטים | חסר ספק כוח (3.2) |
| נורית קישור כלפי מעלה אדומה | מתג ↔ מתג צריך **Cross-Over**. מחקו את הכבל וחברו מחדש |
| ‏ACC2 לא לומד VLANים | ‏`show vtp status` בשני הצדדים: הדומיין, הסיסמה (`show vtp password`) והגרסה חייבים להתאים **בדיוק** (רגיש לאותיות גדולות/קטנות) |
| הודעות ‎`%CDP-4-NATIVE_VLAN_MISMATCH` | בצד אחד של ה-trunk יש native 998 ובצד השני אין. תקנו את הצד החסר |
| ‏`show interfaces trunk` לא מציג כלום | הפורט לא מוגדר trunk באחד הצדדים, או שהוא כבוי |
| פינג ENG-01 ‏←‏ ENG-03 נכשל | האם VLAN 10 ברשימת המותרים **בשני** הקצוות? האם המחשבים ב-VLAN 10 (`show vlan brief`)? |

</div>

## אתגר
הריצו `show spanning-tree vlan 10` ב-ACC1. אחד משני הקישורים שלו כלפי מעלה הוא **BLK**
(blocking — חסום). למה המתג חוסם כבל תקין לגמרי? איזה מתג הוא ה-**root bridge** כרגע, ולמה
דווקא הוא?

<details dir="rtl"><summary>תשובה</summary>

‏ACC1 ‏←‏ DIST1 ‏←‏ ACC2 ‏←‏ DIST2 ‏←‏ ACC1 הוא **לולאה**. בלי Spanning Tree, הודעת broadcast הייתה
מסתובבת לנצח ("סערת broadcast") ומשביתה את הרשת תוך שניות. ‏STP חוסם פורט אחד כדי לשבור את
הלולאה; אם הדרך הפעילה נופלת, הפורט החסום נכנס במקומה (יתירות).

ה-root הוא המתג עם ה-**bridge ID הנמוך ביותר** = עדיפות (priority — ברירת מחדל 32768 + מספר
ה-VLAN), ואחר כך **כתובת ה-MAC הנמוכה ביותר**. כל העדיפויות שוות, ולכן ה-MAC הנמוך ביותר מנצח
— אולי מתג access, שהוא root גרוע (התעבורה תעבור בדרכים מוזרות). נתקן את זה בשלב 04 כשנבחר את
ה-root בעצמנו.
</details>

---

## 🛠 הפרויקט שלכם

עשיתם את השלב הזה על הדוגמה של אינטל. עכשיו עשו אותו שוב בפרויקט **שלכם**, עם הערכים
מהתוכנית **שלכם** (`my-project/plan.md`). הפקודות זהות — רק הערכים משתנים.

<div dir="rtl">

| בדוגמה | בפרויקט שלכם — לוקחים מ |
|---|---|
| ‎‏Native VLAN ‏‎`998` | תוכנית, חלק ד (ה-VLAN ה-NATIVE שלכם) |
| רשימת ה-VLANים המותרים ב-trunks | תוכנית, חלק ד (רק ה-VLANים **שלכם** של אותו בניין) |
| דומיין VTP ‏`HFA-A` | שם דומיין משלכם לכל בניין, למשל ‎`<SITE>-A` |
| סיסמת VTP ‏`Intel#Vtp` | תוכנית, חלק ו |
| שמות המכשירים ופורטי הקישורים כלפי מעלה | תוכנית, חלקים ב ו-ד |

</div>

**בדיקה:** ‏`show interfaces trunk` מציג את ה-native VLAN שלכם ורק את ה-VLANים שלכם;
‏`show vtp status` מציג את הדומיין שלכם בכל מתג בבניין.

💾 שמרו בשם `my-project/step03.pkt`.

---

## 🎓 מסבירים לבוחן

בבחינה, הבוחן מצביע על הפרויקט **שלכם** ומבקש **להסביר** ו**להראות**. תרגלו כל שאלה
**בקול**, ואז הראו את התשובה בפרויקט שלכם — לא בדוגמה. כסו את התשובה, ענו בעצמכם, ורק אז
פתחו והשוו.

‏★1–★3 = שאלה ממאגר השאלות של משרד החינוך (רמת קושי 1–3).
‏◆ = לא במאגר, אבל בוחנים שואלים אותה לעיתים קרובות.

**1. ★2 מהו פרוטוקול 802.1Q ומדוע משתמשים בו?**

<details dir="rtl"><summary>תשובה</summary>

תקן ה-trunk: הוא מכניס לכל מסגרת Ethernet תג של 4 בתים עם מספר VLAN של 12 ביטים, כך שקישור
אחד יכול להעביר הרבה VLANים והצד השני יודע לאיזה VLAN שייכת כל מסגרת. משתמשים בו בין מתגים,
ובין מתג לנתב (router-on-a-stick).

**איפה מראים:** `show interfaces trunk`
</details>

**2. ◆ מה זה native VLAN, ולמה אצלכם הוא VLAN שלא בשימוש?**

<details dir="rtl"><summary>תשובה</summary>

מסגרות של ה-native VLAN עוברות ב-trunk **בלי תג**. אם ה-native VLAN הוא VLAN של משתמשים, תוקף
יכול לתייג מסגרות פעמיים (double tagging) ולקפוץ ל-VLAN אחר. ‏native VLAN שלא בשימוש, בלי
פורטים ובלי IP, חוסם את זה.

**איפה מראים:** `show interfaces trunk` ‏←‏ העמודה Native vlan
</details>

**3. ◆ למה מגבילים את ה-VLANים המותרים ב-trunk?**

<details dir="rtl"><summary>תשובה</summary>

רק ה-VLANים שצריך עוברים בקישור: פחות תעבורת broadcast מיותרת, ו-VLAN שלא אמור להיות בבניין
לא יכול "לדלוף" אליו.

**איפה מראים:** `show interfaces trunk` ‏←‏ "Vlans allowed on trunk"
</details>

**4. ◆ מה זה VTP? מה ההבדל בין server, ‏client ו-transparent?**

<details dir="rtl"><summary>תשובה</summary>

‏VTP משתף את רשימת ה-VLANים בין המתגים בדומיין אחד. ‏Server: יוצר/מוחק VLANים ומפרסם אותם.
‏Client: לומד את ה-VLANים מה-server ולא יכול לשנות אותם. ‏Transparent: שומר VLANים משלו ורק
מעביר את ההודעות הלאה.

**איפה מראים:** `show vtp status`
</details>

**5. ◆ מה הסכנה ב-VTP ואיך מתגוננים ממנה?**

<details dir="rtl"><summary>תשובה</summary>

מתג עם configuration revision גבוה יותר שמצטרף לדומיין יכול לדרוס (ואפילו למחוק) את ה-VLANים
של כל המתגים. הגנה: סיסמת VTP, אותו שם דומיין רק איפה שמתכוונים, ואיפוס ה-revision של מתג חדש
(מעבר ל-transparent) לפני שמחברים אותו.

**איפה מראים:** `show vtp status` ‏←‏ Configuration Revision
</details>

---

## 🔁 עושים שוב — בלי המדריך

הבוחן יכול לבקש מכם להגדיר משהו שוב, מולו. תצליחו רק אם עשיתם את זה **בלי המדריך** לפני כן.
עשו את התרגיל הזה בפרויקט שלכם:

בעותק של קובץ שלב 02 שלכם: הוסיפו את מתג ה-access השני ואת שני מתגי ה-distribution, חברו את
הקישורים כלפי מעלה, והקלידו את הגדרות ה-trunk וה-VTP מתוך התוכנית שלכם, בלי העמוד הזה. יעד:
**‏20 דקות**. אחר כך `show interfaces trunk` ו-`show vtp status` בכל מתג, והסבירו את ה-native
VLAN ואת רשימת ה-VLANים המותרים שבחרתם.

---

## 👩‍🏫 הערות למורה
- **שיעור 1 (90 דקות):** ‏trunks (ציירו את הכביש המהיר עם המדבקות הצבעוניות), ‏native VLAN,
  רשימת VLANים מותרים, DTP ‏←‏ בנייה: מתגי 3650 + ספקי כוח, חיווט עם סוגי הכבלים הנכונים ‏←‏
  הגדרת DIST1.
- **שיעור 2 (90 דקות):** ‏VTP עם ההשוואה למשרד הראשי + הסיפור על מספר ה-revision ‏←‏ הגדרת
  DIST2, ‏ACC1, ‏ACC2 ‏←‏ בדיקות 5.1–5.3 ‏←‏ הדגמת VTP בזמן אמת (5.4) ‏←‏ תיוג במצב Simulation
  (5.5) על המקרן.
- **שאלות נפוצות של תלמידים**
  - *"למה המחשבים לא צריכים להבין תגים?"* — פורט ה-access מוסיף/מוריד את התג; המחשב רואה רק
    מסגרות רגילות.
  - *"אם VTP מסוכן, למה משתמשים בו?"* — הוא חוסך הרבה עבודה. את הסכנה מנהלים עם סיסמאות ועם
    הכלל transparent‏←‏client. בקריית גת (שלב 14) משתמשים בכוונה במצב transparent — החלטת
    תכנון שכדאי לדון בה בספר הפרויקט.
  - *"למה נורית אחת כתומה?"* — ‏Spanning Tree חוסם את הלולאה. זו הגנה, לא תקלה.
- **טעויות אופייניות:** שכחת ספק הכוח של ה-3650; כבל straight-through במקום cross-over בין
  מתגים; שגיאת כתיב בדומיין ה-VTP (`HFA-A` ≠ `hfa-a`); ‏native VLAN מוגדר רק בצד אחד.
