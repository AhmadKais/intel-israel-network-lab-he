# שלב 04 — EtherChannel ו-Spanning Tree

<div dir="rtl">

> ⏱ ‏2 שיעורים · 🎯 דרישות משרד החינוך 14, ‏15, ‏22.14, ‏6, ‏13 · 📁 מתחילים מ: `my-work/step03.pkt` · 💾 שומרים בשם: `my-work/step04.pkt`

</div>

<div dir="rtl">

> ✅ **לפני שמתחילים:** כל הסעיפים בנקודת הביקורת של שלב 03 מסומנים, ועשיתם את
> תרגיל ה-🔁 שלו בפרויקט שלכם. אל תדלגו על שלבים — כל שלב בנוי על הקובץ של השלב הקודם.

</div>

## מה יהיה לכם בסוף השלב
- ‏DIST1 ו-DIST2 מחוברים ב-**שני כבלים שמאוחדים לקישור לוגי אחד** (‏**EtherChannel** בשם
  `Port-channel1`).
- **‏Rapid Spanning Tree** בכל מתג, ו**אתם** מחליטים איזה מתג הוא ה"בוס" (root) של כל VLAN.
- פורטים של מחשבים שעולים מיד (**PortFast**) ומכבים את עצמם אם מישהו מחבר אליהם מתג
  (**BPDU Guard**).
- פורטים במתגי ה-distribution שמסרבים ל"בוס" מזויף (**Root Guard**).

```
        SWL3-HFA-A-DIST1 ══ Gi1/0/23 + Gi1/0/24 (Po1, LACP) ══ SWL3-HFA-A-DIST2
        root: VLAN 10,30,99,110                                 root: VLAN 20,120
             │   ╲                                          ╱   │
             │     ╲──────────────╲          ╱────────────╱     │
           ACC1                     ╲      ╱                 ACC2
                                      ╲  ╱
```

---

## חלק 1 — קודם מבינים (בשפה פשוטה)

### 1.1 בעיית הלולאה (שוב)
מאז שלב 03 המתגים שלנו מחוברים במעגל. יתירות זה טוב — אבל מתגים שולחים broadcast לכל
הפורטים, ולכן בלולאה **הודעת broadcast אחת מסתובבת לנצח**, מתרבה, ותוך כמה שניות תופסת 100%
מכל קישור: **סערת broadcast** ‏(broadcast storm). הרשת קופאת.

### 1.2 ‏Spanning Tree ‏(STP) — שוטר התנועה של המתגים
**‏STP** מוצא לולאות ו**חוסם** בדיוק מספיק פורטים כדי לשבור אותן. אם קישור פעיל נופל, הוא
**משחרר** פורט גיבוי. מקבלים יתירות *וגם* אין לולאות.

איך הוא מחליט, בצעדים פשוטים:
1. **בוחרים בוס — ה-root bridge.** לכל מתג יש *bridge ID* = **מספר עדיפות (priority)** + כתובת
   ה-MAC שלו. **הנמוך מנצח.** כמו בחירת קפטן לקבוצה: המספר הנמוך הוא הקפטן.
2. **כל מתג אחר מוצא את הדרך הטובה ביותר שלו אל הבוס** (ה-*root port* שלו).
3. **בכל קישור אחר, צד אחד נחסם.** זו הנורית הכתומה שראיתם בשלב 03.

**למה לבחור את הבוס בעצמנו?** כברירת מחדל כל העדיפויות שוות (32768), ולכן המתג עם ה-MAC הנמוך
ביותר — לעיתים קרובות מתג access ישן בקצה — הופך ל-root. התעבורה עוברת אז בדרכים מטופשות.
ה-root חייב להיות מתג **distribution** חזק.

**‏PVST+** = ‏**P**er-**V**LAN Spanning Tree: עץ נפרד לכל VLAN. כך DIST1 יכול להיות הבוס של
VLAN 10 בזמן ש-DIST2 הוא הבוס של VLAN 20 ← שני מתגי ה-distribution מעבירים תעבורה
(**חלוקת עומס** — load sharing).

**‏Rapid-PVST+** = הגרסה המודרנית והמהירה: מתאוששת מתקלה תוך כ-**שנייה אחת** במקום 30–50
שניות. אנחנו תמיד משתמשים בה.

התוכנית שלנו:

<div dir="rtl">

| ‏VLANים | בוס (root primary) | סגן (root secondary) |
|---|---|---|
| ‎10, 30, 99, 110 | ‎DIST1 | ‎DIST2 |
| ‎20, 120 | ‎DIST2 | ‎DIST1 |

</div>

(בשלב 05 הבוס של כל VLAN יהיה גם השער הראשי שלו — כך התעבורה עוברת בדרך הקצרה ביותר.)

### 1.3 ‏EtherChannel — שני כבלים, דרך אחת
שני כבלים בין DIST1 ל-DIST2 היו בדרך כלל לולאה, ו-STP היה חוסם אחד מהם — ומבזבז אותו.
**‏EtherChannel** מאחד 2–8 כבלים ל**קישור לוגי אחד**. ‏STP רואה קישור *אחד*, ולכן שום דבר
לא נחסם:
- **רוחב פס כפול**,
- אם כבל אחד נקרע, השני ממשיך לעבוד — אף אחד לא מרגיש.

השוואה: שני נתיבים שצבועים ככביש רחב אחד.

שני המתגים מסכימים על האיחוד בעזרת פרוטוקול:

<div dir="rtl">

| פרוטוקול | מי יצר אותו | מצבים שיוצרים איחוד |
|---|---|---|
| **‏LACP** (בו משתמשים בחיפה) | תקן IEEE — עובד עם כל יצרן | ‏`active` ↔ `active`, או `active` ↔ `passive` |
| **‏PAgP** (בו משתמשים בירושלים, שלב 13) | ‏Cisco בלבד | ‏`desirable` ↔ `desirable`, או `desirable` ↔ `auto` |

</div>

לכל הכבלים באיחוד חייבות להיות **הגדרות זהות** (מהירות, trunk, ‏native VLAN, ‏VLANים מותרים).

### 1.4 ‏PortFast — מדלגים על חדר ההמתנה למחשבים
פורט רגיל במתג מחכה כ-30 שניות לפני שהוא מעביר תעבורה, כדי לוודא שהוא לא יוצר לולאה. מחשב אף
פעם לא יוצר לולאה, וההמתנה גורמת למחשבים להיכשל בקבלת כתובת מ-DHCP. **‏PortFast** מאפשר
ל**פורטים של מכשירי קצה** להעביר תעבורה מיד.
⚠️ רק בפורטים למכשירי קצה — אף פעם לא בקישורים בין מתגים.

### 1.5 ‏BPDU Guard — "פורט של מחשב אף פעם לא אמור לשמוע מתג"
מתגים מדברים STP בהודעות שנקראות **BPDU**. מחשבים אף פעם לא שולחים אותן. לכן אם BPDU מגיעה
לפורט עם PortFast, מישהו חיבר שם **מתג** (טעות או התקפה). **‏BPDU Guard** **מכבה את הפורט**
מיד (מצב: *err-disabled*). מנהל צריך להפעיל אותו מחדש.

### 1.6 ‏Root Guard — "אף אחד מתחתיי לא יהיה הבוס"
תוקף יכול לחבר מתג עם priority 0 ולהפוך ל-root ← כל התעבורה עוברת דרכו. **‏Root Guard**
בפורטים של מתגי ה-distribution שפונים למתגי ה-access אומר: "אם בוס טוב יותר מופיע דרך הפורט
*הזה*, חסום את הפורט". זה מגן על בחירת ה-root.

---

## חלק 2 — הכנה
‏**File → Open** ← `my-work/step03.pkt` ← **File → Save As** ← `my-work/step04.pkt`.

---

## חלק 3 — בונים (לחיצה אחרי לחיצה)
שני כבלים חדשים, שניהם **Copper Cross-Over** (מתג ↔ מתג):

<div dir="rtl">

| לחצו קודם על | פורט | לחצו אחר כך על | פורט |
|---|---|---|---|
| ‎SWL3-HFA-A-DIST1 | ‎**GigabitEthernet1/0/23** | ‎SWL3-HFA-A-DIST2 | ‎**GigabitEthernet1/0/23** |
| ‎SWL3-HFA-A-DIST1 | ‎**GigabitEthernet1/0/24** | ‎SWL3-HFA-A-DIST2 | ‎**GigabitEthernet1/0/24** |

</div>

אל תדאגו אם הם נשארים כתומים — מגדירים אותם עכשיו.

---

## חלק 4 — מגדירים (הקלידו כל שורה)

### 4.1 ‏SWL3-HFA-A-DIST1
התחברו (console ‏`Intel#Con`, ‏enable ‏`Intel#En4ble`):
```
enable
configure terminal

! ---------- Spanning Tree: rapid mode + choose the boss ----------
spanning-tree mode rapid-pvst
spanning-tree vlan 10,30,99,110 root primary
spanning-tree vlan 20,120 root secondary

! ---------- EtherChannel members: identical trunk settings + bundle 1 ----------
interface range gi1/0/23 - 24
 description Po1 member to SWL3-HFA-A-DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 10,20,30,99,110,120,998
 switchport nonegotiate
 channel-group 1 mode active
 no shutdown
 exit

! ---------- the logical link that the bundle creates ----------
interface port-channel 1
 description EtherChannel to SWL3-HFA-A-DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 10,20,30,99,110,120,998
 switchport nonegotiate
 exit

! ---------- Root Guard on the ports facing the access switches ----------
interface range gi1/0/1 - 2
 spanning-tree guard root
 end
copy running-config startup-config
```
ההערות בבלוק אומרות: ‏Spanning Tree — מצב מהיר + בחירת הבוס; חברי ה-EtherChannel — הגדרות
trunk זהות + איחוד מספר 1; הקישור הלוגי שהאיחוד יוצר; ‏Root Guard בפורטים שפונים למתגי ה-access.

אחרי `channel-group 1 mode active` תראו `Creating a port-channel interface Port-channel 1` — מצוין.

### 4.2 ‏SWL3-HFA-A-DIST2
אותו מבנה, אבל DIST2 הוא הבוס של VLAN 20 ו-120:
```
enable
configure terminal

spanning-tree mode rapid-pvst
spanning-tree vlan 20,120 root primary
spanning-tree vlan 10,30,99,110 root secondary

interface range gi1/0/23 - 24
 description Po1 member to SWL3-HFA-A-DIST1
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 10,20,30,99,110,120,998
 switchport nonegotiate
 channel-group 1 mode active
 no shutdown
 exit

interface port-channel 1
 description EtherChannel to SWL3-HFA-A-DIST1
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 10,20,30,99,110,120,998
 switchport nonegotiate
 exit

interface range gi1/0/1 - 2
 spanning-tree guard root
 end
copy running-config startup-config
```

### 4.3 ‏SW-HFA-A-ACC1
```
enable
configure terminal
spanning-tree mode rapid-pvst

! ports to end devices (PCs, printer, admin PC): PortFast + BPDU Guard
interface range fa0/1 - 22
 spanning-tree portfast
 spanning-tree bpduguard enable
 end
copy running-config startup-config
```
ההערה אומרת: פורטים למכשירי קצה (מחשבים, מדפסת, מחשב המנהל): PortFast + BPDU Guard.

‏PT מדפיס אזהרה ארוכה `%Warning: portfast should only be enabled on ports connected to a single
host...` — זו תזכורת, לא שגיאה. כאן זה נכון.

### 4.4 ‏SW-HFA-A-ACC2
```
enable
configure terminal
spanning-tree mode rapid-pvst

! PCs, printer and the two access-point ports (an AP is an end device for STP)
interface range fa0/1 - 23
 spanning-tree portfast
 spanning-tree bpduguard enable
 end
copy running-config startup-config
```
ההערה אומרת: מחשבים, מדפסת ושני הפורטים של נקודות הגישה (מבחינת STP נקודת גישה היא מכשיר קצה).

לחצו **Fast Forward Time** כמה פעמים.

### 4.5 מה הפקודות החדשות אומרות

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`spanning-tree mode rapid-pvst` | "השתמש בגרסה המהירה של STP, עם עץ אחד לכל VLAN" |
| ‎`spanning-tree vlan 10 root primary` | "תעשה אותי הבוס של VLAN 10" (קובע priority נמוך: 24576) |
| ‎`spanning-tree vlan 20 root secondary` | "תעשה אותי הסגן של VLAN 20" ‏(28672) — נכנס לתפקיד אם הבוס מת |
| ‎`channel-group 1 mode active` | "הכנס את הכבל הזה לאיחוד מספר 1, ובקש באופן פעיל מהצד השני בעזרת LACP" |
| ‎`interface port-channel 1` | הקישור הלוגי שמייצג את כל האיחוד |
| ‎`spanning-tree portfast` | "הפורט הזה הולך למכשיר קצה — דלג על ההמתנה" |
| ‎`spanning-tree bpduguard enable` | "אם מתג מדבר בפורט הזה, כבה אותו" |
| ‎`spanning-tree guard root` | "אף פעם אל תקבל בוס חדש דרך הפורט הזה" |

</div>

---

## חלק 5 — בודקים את העבודה

### 5.1 ה-EtherChannel
ב-**DIST1**:
```
show etherchannel summary
```
```
Flags:  D - down        P - bundled in port-channel
        S - Layer2      U - in use
...
Group  Port-channel  Protocol    Ports
------+-------------+-----------+--------------------------------
1      Po1(SU)           LACP   Gig1/0/23(P) Gig1/0/24(P)
```
✅ ‏`Po1(SU)`‎ = שכבה 2, **בשימוש**. שני הפורטים ‎`(P)`‎ = באיחוד.
אם אתם רואים ‎`(SD)`‎, או ‎`(I)`‎/‎`(s)`‎ ליד הפורטים, ראו את טבלת "אם משהו לא עובד".

### 5.2 מי הבוס?
ב-**DIST1**: `show spanning-tree vlan 10`
```
VLAN0010
  Spanning tree enabled protocol rstp
  Root ID    Priority    24586
             Address     000A.F3C4.1101
             This bridge is the root            <- ✅ DIST1 is boss of VLAN 10
```
(ה-‏✅ אומר: DIST1 הוא הבוס של VLAN 10. כתובת ה-MAC אצלכם תהיה שונה.)
ב-**DIST2**: `show spanning-tree vlan 20` ← `This bridge is the root` ✅

ב-**ACC1**: `show spanning-tree vlan 10`
```
Interface        Role Sts Cost      Prio.Nbr Type
---------------- ---- --- --------- -------- -----------
Gi0/1            Root FWD 4         128.25   P2p        <- road to the boss (DIST1)
Gi0/2            Altn BLK 4         128.26   P2p        <- backup road, blocked
Fa0/1            Desg FWD 19        128.1    P2p Edge   <- "Edge" = PortFast
```
‏Gi0/1 = הדרך אל הבוס (DIST1); ‏Gi0/2 = דרך הגיבוי, חסומה; ‏`Edge` = ‏PortFast.

עכשיו `show spanning-tree vlan 20` ב-ACC1 ← הפעם **Gi0/2** (לכיוון DIST2) הוא ה-Root port.
זו חלוקת העומס: VLAN 10 עולה דרך DIST1, ו-VLAN 20 דרך DIST2.

‏`show spanning-tree summary` ← `Switch is in rapid-pvst mode` ✅

### 5.3 שוברים דברים בכוונה (הדרך הכי טובה ללמוד)
**בדיקה 1 — יתירות**
1. ‏PC-HFA-ENG-01 ← Command Prompt ← `ping -t 10.10.16.103` (ping רציף).
2. לחצו על הכלי **Delete** ‏(X) ← לחצו על הכבל **ACC1 Gi0/1 ↔ DIST1**.
3. הסתכלו על ה-ping: 1–2 שורות timeout, ואז שוב תשובות — התעבורה עברה לדרך של Gi0/2.
4. לחצו **Ctrl+C** ב-Command Prompt כדי לעצור. החזירו את הכבל (Cross-Over,
   ‏ACC1 Gi0/1 ← DIST1 Gi1/0/1).

**בדיקה 2 — ה-EtherChannel שורד כבל קרוע**
1. מחקו את אחד משני הכבלים DIST1 ↔ DIST2.
2. ‏`show etherchannel summary` ← ‏Po1 עדיין ‎`(SU)`‎ עם חבר אחד.
3. החזירו את הכבל (אותם פורטים) ← אחרי רגע שני החברים שוב ‎`(P)`‎.

**בדיקה 3 — BPDU Guard תופס מתג מתחזה**
1. גררו **2960** חדש ליד ACC1 (השאירו לו את השם `Switch…`‎).
2. חברו אותו ב-**Copper Cross-Over**: המתג החדש **Fa0/1** ← ‏ACC1 **Fa0/9**.
3. הסתכלו ב-CLI של ACC1: ‎`%SPANTREE-2-BLOCK_BPDUGUARD: Received BPDU on port Fa0/9 with BPDU Guard enabled. Disabling port.`‎
4. ‏`show interfaces status` ← ליד Fa0/9 כתוב `err-disabled`. נורית הקישור אדומה.
5. מחקו את המתג המתחזה. החזירו את הפורט לפעולה:
```
configure terminal
interface fa0/9
 shutdown
 no shutdown
 end
```

---

## חלק 6 — שומרים
`copy running-config startup-config` בכל 4 המתגים ← **File → Save**.

## נקודת ביקורת
- [ ] ‏`show etherchannel summary` ← `Po1(SU)`‎, שני הפורטים ‎`(P)`‎ — ב-DIST1 וב-DIST2
- [ ] ‏DIST1 הוא root של 10/30/99/110, ‏DIST2 של 20/120
- [ ] פורטי ה-access מציגים `Edge` ‏(PortFast) ב-`show spanning-tree`
- [ ] עשיתם את 3 בדיקות השבירה

## אם משהו לא עובד

<div dir="rtl">

| בעיה | פתרון |
|---|---|
| ‏`Po1(SD)`‎ או פורטים ‎`(s)`‎ / ‎`(I)`‎ | שני הכבלים מוגדרים אחרת, או שהמתג השני עוד לא הוגדר. ב**שני** המתגים: `interface range gi1/0/23 - 24` ← `no channel-group 1` ← `exit` ← `no interface port-channel 1`, ואז הקלידו שוב את חלק ה-EtherChannel של 4.1/4.2 |
| מתג אחד משתמש ב-`active` והשני ב-`desirable` | ערבוב של LACP ו-PAgP — השתמשו ב-`active` בשניהם |
| המתג הלא נכון הוא ה-root | בדקו `show run \| include spanning-tree vlan` — אולי הקלדתם `primary` בשני המתגים עבור אותו VLAN |
| המחשבים ב-ACC1 מאבדים קישוריות אחרי Root Guard | ‏`show spanning-tree vlan 10` ב-DIST1 — הפורט למתג ה-access חסום על ידי Root Guard כי למתג access יש priority נמוך יותר מ-DIST1/2. הסירו כל `spanning-tree vlan ... priority` ממתגי ה-access |
| ‏Fa0/9 נשאר אדום אחרי שהסרתם את המתג המתחזה | צריך `shutdown` ואז `no shutdown` עליו |

</div>

## אתגר
‏`spanning-tree vlan 10 root primary` הוא קיצור דרך. הריצו `show run | include priority`
ב-DIST1: איזה priority הוא קבע בפועל? למה המספר הזה הוא כפולה של 4096?

<details dir="rtl"><summary>תשובה</summary>

‏`spanning-tree vlan 10 priority 24576` ‏(secondary = 28672). לשדה ה-priority יש 16 ביטים,
אבל 12 הביטים האחרונים משמשים להעברת מספר ה-VLAN ("extended system ID"), ולכן ה-priority עצמו
יכול להשתנות רק בקפיצות של 2 בחזקת 12 = **‏4096**. בגלל זה `show spanning-tree` מציג 24586
עבור VLAN 10: ‏24576 + 10.
</details>

---

## 🛠 הפרויקט שלכם

עשיתם את השלב הזה על הדוגמה של אינטל. עכשיו עשו אותו שוב בפרויקט **שלכם**, עם הערכים
מהתוכנית **שלכם** (`my-project/plan.md`). הפקודות זהות — רק הערכים משתנים.

<div dir="rtl">

| בדוגמה | בפרויקט שלכם — לוקחים מ |
|---|---|
| ‏Port-channel בין שני מתגי ה-distribution, ‏LACP | תוכנית, חלק ה (שורת ה-EtherChannel: איזה אתר משתמש ב-LACP) |
| ‏root לכל VLAN: ‏DIST1 עבור 10,30,99,110 — ‏DIST2 עבור 20,120 | תוכנית, חלק ד (עמודת ה"ראשי" — ה-root של STP חייב להיות אותו מתג כמו ה-primary של HSRP) |
| ‏PortFast / BPDU guard בפורטים של המשתמשים | פורטי ה-access שלכם מתוכנית הפורטים |

</div>

**בדיקה:** ‏`show etherchannel summary` מציג ‎`(SU)`‎ ו-‎`(P)`‎; ‏`show spanning-tree vlan <שלכם>`‎
מציג את המתג הנכון כ-root עבור כל אחד מה-VLANים שלכם.

💾 שמרו בשם `my-project/step04.pkt`.

---

## 🎓 מסבירים לבוחן

בבחינה, הבוחן מצביע על הפרויקט **שלכם** ומבקש **להסביר** ו**להראות**. תרגלו כל שאלה
**בקול**, ואז הראו את התשובה בפרויקט שלכם — לא בדוגמה. כסו את התשובה, ענו בעצמכם, ורק אז
פתחו והשוו.

‏★1–★3 = שאלה ממאגר השאלות של משרד החינוך (רמת קושי 1–3).
‏◆ = לא במאגר, אבל בוחנים שואלים אותה לעיתים קרובות.

**1. ★2 מה היתרון בהגדרת EtherChannel בין שני מתגים?**

<details dir="rtl"><summary>תשובה</summary>

כמה קישורים פיזיים פועלים כקישור לוגי אחד: יותר רוחב פס, ואם כבל אחד נופל התעבורה ממשיכה
בשאר הכבלים בלי ש-STP צריך לחשב מחדש.

**איפה מראים:** `show etherchannel summary`
</details>

**2. ★2 שני מתגים מחוברים ב-4 כבלי רשת של 100 Mbps כל אחד, אבל בפועל המהירות ביניהם היא 100 ולא 400. מדוע? מה הפתרון?**

<details dir="rtl"><summary>תשובה</summary>

‏STP רואה 4 קישורים מקבילים כלולאה וחוסם 3 מהם; רק אחד מעביר תעבורה. הפתרון: לאחד אותם
ל-EtherChannel — אז STP רואה קישור לוגי אחד, וכל ה-4 מעבירים תעבורה.

**איפה מראים:** `show spanning-tree` לפני ואחרי ה-port-channel.
</details>

**3. ★2 אילו שני פרוטוקולים יכולים לייצר bundle של EtherChannel?**

<details dir="rtl"><summary>תשובה</summary>

‏LACP ‏(IEEE 802.3ad, תקן פתוח — מצבים `active`/`passive`) ו-PAgP ‏(Cisco — מצבים
`desirable`/`auto`). אפשר גם לכפות איחוד במצב `on` (בלי פרוטוקול).

**איפה מראים:** `show etherchannel summary` ← העמודה Protocol
</details>

**4. ★1 מה תפקידו של פרוטוקול STP ברשת מקומית?**

<details dir="rtl"><summary>תשובה</summary>

למנוע לולאות בשכבה 2 ברשת עם יתירות: הוא חוסם חלק מהפורטים כך שיש בדיוק דרך פעילה אחת בין
כל שני מתגים, ומשחרר דרך גיבוי אם הדרך הפעילה נופלת.

**איפה מראים:** `show spanning-tree vlan <שלכם>`‎
</details>

**5. ★2 איפה בפרויקט מיושם STP, ואיזה סוג STP אתה מיישם?**

<details dir="rtl"><summary>תשובה</summary>

בכל המתגים, במצב Rapid-PVST+ ‏(`spanning-tree mode rapid-pvst`): עץ Spanning Tree מהיר אחד
לכל VLAN.

**איפה מראים:** `show spanning-tree summary`
</details>

**6. ★2 הראה לי איזה מתג מוגדר כמתג השורש. איך תגדיר מתג שאינו השורש להיות מתג השורש?**

<details dir="rtl"><summary>תשובה</summary>

ה-root הוא המתג עם ה-bridge ID הנמוך ביותר (priority + MAC). ‏`show spanning-tree vlan 10` ←
"This bridge is the root". כדי להפוך מתג אחר ל-root: `spanning-tree vlan 10 root primary` (או
`spanning-tree vlan 10 priority 4096`).

**איפה מראים:** `show spanning-tree vlan <שלכם>`‎ בשני מתגי ה-distribution
</details>

**7. ★2 הראה לי את מצב הפורטים. מה המשמעות של פורט במצב Block / Forwarding?**

<details dir="rtl"><summary>תשובה</summary>

‏Forwarding ‏(FWD): הפורט שולח ומקבל מסגרות. ‏Blocking ‏(BLK, ב-RSTP נקרא "discarding"): הוא
רק מקשיב ל-BPDU וזורק מסגרות נתונים, כדי לשבור לולאה. תפקידי פורטים: Root, ‏Designated,
‏Alternate/Backup.

**איפה מראים:** `show spanning-tree vlan <שלכם>`‎
</details>

**8. ★2 מה זה BPDU?**

<details dir="rtl"><summary>תשובה</summary>

‏Bridge Protocol Data Unit — ההודעה שהמתגים מחליפים ביניהם (כל 2 שניות) כדי לבחור את ה-root
bridge ולהחליט אילו פורטים מעבירים ואילו חוסמים.

**איפה מראים:** מצב Simulation עם הסינון STP.
</details>

**9. ★2 אילו שתי פקודות מומלץ להגדיר על ממשקי access שקשורות ל-STP, ומה תפקידן?**

<details dir="rtl"><summary>תשובה</summary>

‏`spanning-tree portfast` — הפורט עובר ישר ל-forwarding (מחשב לא מחכה כ-30 שניות).
‏`spanning-tree bpduguard enable` — אם מגיעה BPDU (מישהו חיבר מתג), הפורט נכבה (err-disabled).

**איפה מראים:** `show running-config interface fa0/1`
</details>

**10. ★2 אילו גרסאות של STP קיימות? מה ההבדל בין STP ל-PVST?**

<details dir="rtl"><summary>תשובה</summary>

‏802.1D STP (עץ אחד לכל ה-VLANים), ‏PVST+ ‏(Cisco — עץ לכל VLAN), ‏RSTP 802.1w (התכנסות
מהירה), ‏Rapid-PVST+ ‏(RSTP לכל VLAN — בו אנחנו משתמשים), ‏MSTP 802.1s (מקבץ VLANים לקבוצות).
‏PVST מאפשר לכל VLAN root אחר, כך ש-VLANים שונים יכולים להשתמש בקישורים שונים (חלוקת עומס).

**איפה מראים:** `show spanning-tree summary` ← mode
</details>

**11. ★3 כמה זמן לוקח לפורט להתחיל להעביר נתונים ב-STP הקלאסי? באילו מצבים הוא עובר?**

<details dir="rtl"><summary>תשובה</summary>

‏Blocking ← Listening ‏(15 שניות) ← Learning ‏(15 שניות) ← Forwarding: ‏30 שניות לפורט חדש,
ועד 50 שניות אם הוא מחכה קודם max-age ‏(20 שניות) אחרי שינוי בטופולוגיה. ‏Rapid-PVST+ ו-PortFast
הופכים את זה כמעט למיידי.

**איפה מראים:** —
</details>

**12. ★3 איך אפשר לתקוף רשת LAN בעזרת STP, ואיך מתגוננים?**

<details dir="rtl"><summary>תשובה</summary>

תוקף מחבר מתג ששולח BPDU עם priority טוב יותר (נמוך יותר), הופך ל-root, והתעבורה עוברת דרכו
(man-in-the-middle), או שהטופולוגיה משתנה כל הזמן. הגנה: ‏BPDU Guard בפורטי ה-access, ו-Root
Guard בפורטים שפונים למטה לשכבת ה-access.

**איפה מראים:** `show running-config | include guard`
</details>

**13. ★3 מה ההבדל בין BPDU Guard ל-Root Guard?**

<details dir="rtl"><summary>תשובה</summary>

‏BPDU Guard מכבה את הפורט אם מגיעה **איזושהי** BPDU — לפורטים עם מכשירי קצה. ‏Root Guard
מאפשר BPDU, אבל חוסם את הפורט (root-inconsistent) אם מגיעה BPDU **עדיפה** — לפורטים בין
מתגים, שדרכם אסור ש-root חדש יופיע.

**איפה מראים:** `show running-config` בפורט שפונה למטה ← `spanning-tree guard root`; ‏`show spanning-tree vlan <שלכם>`‎
</details>

---

## 🔁 עושים שוב — בלי המדריך

הבוחן יכול לבקש מכם להגדיר משהו שוב, מולו. תצליחו רק אם עשיתם את זה **בלי המדריך** לפני כן.
עשו את התרגיל הזה בפרויקט שלכם:

בעותק של קובץ שלב 04 הגמור שלכם, מחקו את ה-port-channel ואת פקודות ה-root/priority. בלי העמוד הזה:
בנו מחדש את ה-EtherChannel בין מתגי ה-distribution שלכם, קבעו את ה-root לכל VLAN לפי התוכנית
שלכם, והוסיפו PortFast + BPDU Guard בפורטי ה-access ו-Root Guard בפורטים שפונים למטה. יעד:
**‏15 דקות**. אחר כך הראו `show etherchannel summary` ו-`show spanning-tree vlan <שלכם>`‎,
והסבירו איזה פורט חסום ולמה.

---

## 👩‍🏫 הערות למורה
- **שיעור 1 (90 דקות):** ציירו לולאה על הלוח ו"העבירו broadcast" סביבה עד שהכיתה רואה את
  הסערה; בחירת STP כמו בחירת קפטן; פורטים root/designated/blocked; חלוקת עומס ב-PVST ←
  התלמידים מגדירים STP בכל 4 המתגים ← בדיקה 5.2.
- **שיעור 2 (90 דקות):** ‏EtherChannel (שני נתיבים = כביש אחד), ‏LACP מול PAgP ← כבלים +
  הגדרות ← PortFast/BPDU Guard/Root Guard ← 3 בדיקות השבירה (תלמידים אוהבים את בדיקה 3).
- **שאלות נפוצות של תלמידים**
  - *"למה לא פשוט כבל אחד ובלי STP?"* — כבל אחד = נקודת כשל אחת. חברות משלמות על יתירות;
    ‏STP הופך אותה לבטוחה.
  - *"למה הפורט החסום מבוזבז?"* — הוא גלגל רזרבי. ועם חלוקת העומס של PVST הוא *לא* מבוזבז:
    הוא חוסם רק חלק מה-VLANים ומעביר את האחרים.
  - *"למה `active` בשני הצדדים?"* — `passive` + `passive` אף פעם לא יוצרים איחוד (שניהם מחכים).
    ‏`active` + `active` היא הבחירה הבטוחה.
- **טעויות אופייניות:** הגדרת ה-Port-channel ושכחת החברים (או ההפך); ‏`root primary` בשני
  המתגים עבור אותו VLAN; ‏PortFast בקישורים כלפי מעלה.
