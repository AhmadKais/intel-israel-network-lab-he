# שלב 08 — שכבת ה-Core, ‏OSPF, חוות שרתים, AAA ו-Syslog

<div dir="rtl">

> ⏱ ‏3 שיעורים · 🎯 דרישות משרד החינוך 8 (התחלה), ‏20.1, ‏20.9, ‏20.10, ‏22.5, ‏22.15, ‏22.18, ‏6\
> 📁 מתחילים מ: `my-work/step07.pkt`\
> 💾 שומרים בשם: `my-work/step08.pkt`

</div>

<div dir="rtl">

> ✅ **לפני שמתחילים:** כל הסעיפים בנקודת הביקורת של שלב 07 מסומנים, ועשיתם את
> תרגיל ה-🔁 שלו בפרויקט שלכם. אל תדלגו על שלבים — כל שלב בנוי על הקובץ של השלב הקודם.

</div>

## 🗺 המשימות שלכם בשלב הזה
**שיעור 1 — ה-core**
- [ ] **משימה 1** — פותחים את שלב 07 ושומרים בשם שלב 08 (2 דקות)
- [ ] **משימה 2** — מציבים את 2 מתגי ה-core (עם חשמל), את מתג השרתים ו-2 שרתים (10 דקות)
- [ ] **משימה 3** — מחברים הכול בכבלים לפורטים המדויקים (15 דקות)
- [ ] **משימה 4** — ‏CORE1: הקשחה, ניתוב, ‏VLANים, ‏Loopback0 ‏(10 דקות)
- [ ] **משימה 5** — ‏CORE1: קישורים מנותבים, פורט השרתים, שער השרתים (15 דקות)
- [ ] **משימה 6** — ‏CORE1: ‏OSPF + SSH ‏(10 דקות)
- [ ] **משימה 7** — ‏CORE2: אותו דבר, עם הערכים שלו (25 דקות)

**שיעור 2 — אזורי OSPF**
- [ ] **משימה 8** — ‏DIST1: קישורים כלפי מעלה + OSPF areas 0 ו-1 ‏(15 דקות)
- [ ] **משימה 9** — ‏DIST2: אותו דבר, עם הערכים שלו (10 דקות)
- [ ] **משימה 10** — בודקים OSPF: שכנים, נתיב הסיכום, פינגים (15 דקות)

**שיעור 3 — שרתים, ‏AAA, ‏Syslog**
- [ ] **משימה 11** — ‏SW-HFA-SRV: מתג השרתים (15 דקות)
- [ ] **משימה 12** — שני השרתים: כתובות ושירותים (10 דקות)
- [ ] **משימה 13** — ממלאים את שרת ה-AAA ‏(15 דקות)
- [ ] **משימה 14** — ‏AAA + Syslog בכל 7 המתגים (25 דקות)
- [ ] **משימה 15** — בודקים את ה-AAA, את הגיבוי שלו, ואת ה-Syslog ‏(10 דקות)
- [ ] **תרגילים** א, ב ו-ג
- [ ] **🛠 הפרויקט שלכם**

## מה יהיה לכם בסוף השלב
- שני מתגי **core** — עמוד השדרה של המטה בחיפה.
- בניין A מחובר ל-core בקישורים **מנותבים** (לא trunks).
- ניתוב **OSPF**: ה-core = ‏**area 0**, בניין A = ‏**area 1**, ובניין A מסוכם לנתיב **אחד**.
- **חוות שרתים** קטנה עם שרת **Syslog** (אוסף הודעות יומן) ושרת **AAA** (בודק באופן מרכזי
  כל התחברות של מנהל).

```
              SRV-HFA-SYSLOG  SRV-HFA-AAA
                     └──── SW-HFA-SRV ────┘
                       Gi0/1 │      │ Gi0/2        VLAN 100 = 10.10.1.0/24
                             │      │
   SWL3-HFA-CORE1 ═══ Gi1/0/23 (10.10.4.48/30) ═══ SWL3-HFA-CORE2          OSPF AREA 0
     Gi1/0/1  Gi1/0/2                            Gi1/0/1  Gi1/0/2
        │        ╲──────────────╲    ╱─────────────╱        │
        │                         ╳                          │
        │        ╱──────────────╱    ╲─────────────╲        │
     Gi1/1/1  Gi1/1/2                            Gi1/1/1  Gi1/1/2
   SWL3-HFA-A-DIST1 ══════════ Po1 ══════════ SWL3-HFA-A-DIST2            ABRs 0/1
            (VLANs 10,20,30,99,110,120 below)                            OSPF AREA 1
```
(בחלק העליון: חוות השרתים — VLAN 100 = ‏10.10.1.0/24, ‏OSPF area 0 בין שני מתגי ה-core. בחלק
התחתון: ‏DIST1 ו-DIST2 של בניין A הם ABRים בין area 0 ל-area 1.)

## חלק 1 — קודם מבינים (בשפה פשוטה)

### 1.1 למה צריך שכבת core?
בניין A עובד לבד. בקרוב יהיו **שלושה** בניינים, חומת אש ואינטרנט. לחבר כל בניין לכל בניין אחר
היה בלגן. במקום זה, כל בניין מתחבר ל-**core** מרכזי ומהיר — כמו שכל כבישי העיר מובילים לכביש
טבעת אחד. זה **המודל התלת-שכבתי**: **access** (המשתמשים מתחברים) ‏←‏ **distribution** (הנתבים
של כל בניין) ‏←‏ **core** (עמוד השדרה). דרישה 20.1 מבקשת בדיוק את זה.

### 1.2 קישורים מנותבים במקום trunks
בין ה-distribution ל-core משתמשים ב**קישורים מנותבים** (routed links): הפורט מפסיק להיות פורט
של מתג (`no switchport`) ומקבל כתובת IP משלו, כמו פורט של נתב. כל קישור הוא רשת ‎/30 קטנטנה עם
2 כתובות — אחת לכל קצה.

למה לא trunks? עם קישורים מנותבים:
- **אין Spanning Tree** בין השכבות — ולכן **אין קישורים חסומים**: שני הקישורים כלפי מעלה של כל
  מתג distribution מעבירים תעבורה בו-זמנית;
- אם קישור נופל, הניתוב מעביר את התעבורה תוך פחות משנייה;
- ה-VLANים (וה-broadcast שלהם) נשארים בתוך הבניין שלהם.

### 1.3 ניתוב — איך נתב יודע לאן לשלוח חבילות
נתב מכיר רק את הרשתות ש**מחוברות אליו ישירות** (נתיבי `C`). כדי להגיע לרשתות רחוקות יותר הוא
צריך **נתיבים**. שתי דרכים:
- **נתיבים סטטיים** — מקלידים כל נתיב ידנית. בסדר ל-1–2 נתיבים (נשתמש בהם לכיוון האינטרנט
  בשלב 12).
- **פרוטוקול ניתוב דינמי** — הנתבים **מספרים זה לזה** אילו רשתות הם מכירים, ומתעדכנים אוטומטית
  כשמשהו נשבר. בחיפה משתמשים ב-**OSPF**.

### 1.4 ‏OSPF במילים פשוטות
**‏OSPF** ‏(Open Shortest Path First):
1. נתבים מוצאים **שכנים** (neighbours) על ידי שליחת הודעות "Hello" קטנות על הקישורים שלהם.
2. השכנים מחליפים מידע על הקישורים שלהם ‏←‏ כל נתב בונה **מפה** של הרשת.
3. כל נתב מחשב את **הדרך הקצרה ביותר** לכל רשת שעל המפה.
4. אם קישור נופל, החדשות מתפשטות וכולם מחשבים מחדש — תוך כשנייה.

**‏Router-ID** — לכל נתב OSPF צריך שם ייחודי, שנכתב כמו כתובת IP. אנחנו משתמשים בכתובת של
**Loopback0**: ממשק וירטואלי שאף פעם לא נופל, ולכן ה-ID לא משתנה.

### 1.5 אזורי OSPF ‏(areas) — למה לחלק את המפה?
ברשת גדולה, מפה ענקית אחת איטית לחישוב, וכל שינוי קטן מפריע לכולם. ‏OSPF מחלק את הרשת
ל-**areas**:
- בתוך area, הנתבים מכירים את המפה ה**מפורטת**.
- בין areas, הם מחליפים רק **סיכומים**.
- **‏Area 0** הוא **עמוד השדרה** ‏(backbone): כל area אחר חייב להתחבר אליו.
- נתב שיש לו "רגליים" בשני areas הוא **ABR** ‏(Area Border Router). ‏DIST1 ו-DIST2 הם ABRים:
  הקישורים שלהם כלפי מעלה ב-area 0, וה-VLANים שלהם ב-area 1.

השוואה: מדינה (area 0 = הכבישים הארציים) עם ערים (areas 1, ‏2, ‏3). בתוך עיר מכירים כל רחוב;
בין ערים צריך רק "חיפה בכיוון ההוא".

### 1.6 סיכום נתיבים (Route summarization)
בשלב 01 נתנו לבניין A את הבלוק ‎`10.10.16.0/20`. ה-ABR יכול עכשיו לפרסם נתיב **אחד** —
‏‎`10.10.16.0/20` — במקום שש רשתות ‎/24: ‏`area 1 range 10.10.16.0 255.255.240.0`.
הטבלה של ה-core נשארת קטנה, ו-VLAN שעולה ויורד בבניין A לא מפריע לשאר החברה. (דרישה 22.15.)

### 1.7 הופכים את OSPF לבטוח
- **‏Passive interface** — ‏OSPF עדיין מפרסם את הרשת, אבל **לא שולח שם Hello**. ב-VLANים של
  המשתמשים זה מונע מתוקף להריץ OSPF על לפטופ ולהזריק נתיבים מזויפים. אנחנו משתמשים
  ב-`passive-interface default` (הכול פסיבי) ואז פותחים רק את הקישורים לכיוון נתבים אחרים.
- **אימות MD5** — שכנים חייבים לחלוק מפתח סודי, אחרת אין שכנות. (דרישה 22.18.)

### 1.8 ‏Syslog — היומן של הרשת
כל מכשיר כותב הודעות (`interface down`, ‏`login failed`, …). כברירת מחדל הן נשארות במכשיר
ונמחקות כשהוא מאותחל. **שרת Syslog** אוסף את כל ההודעות מכל המכשירים במקום אחד. (דרישה 20.9.)

### 1.9 ‏AAA — שומר מרכזי אחד לכל ההתחברויות
עד עכשיו לכל מתג היה משתמש מקומי משלו, `admin`. עם 50 מכשירים, החלפת סיסמה היא 50 שינויים.
‏**AAA** = ‏**A**uthentication (מי אתה?), ‏**A**uthorization (מה מותר לך?), ‏**A**ccounting (מה
עשית?). עם `aaa new-model` + שרת **TACACS+**, כל מתג שואל את שרת ה-AAA "האם שם המשתמש/הסיסמה
האלה תקינים?". המשתמש המקומי נשאר כ**גיבוי** אם השרת לא זמין. (דרישה 20.10.)

### 1.10 תוכנית הכתובות של השלב הזה
השאירו את הטבלה הזו פתוחה — כל משימה לוקחת ממנה את המספרים.

<div dir="rtl">

| קישור | רשת משנה | מכשיר ראשון | מכשיר שני |
|---|---|---|---|
| ‎A-DIST1 Gi1/1/1 ↔ CORE1 Gi1/0/1 | ‎10.10.4.0/30 | ‎DIST1 **.1** | ‎CORE1 **.2** |
| ‎A-DIST1 Gi1/1/2 ↔ CORE2 Gi1/0/1 | ‎10.10.4.4/30 | ‎DIST1 **.5** | ‎CORE2 **.6** |
| ‎A-DIST2 Gi1/1/1 ↔ CORE1 Gi1/0/2 | ‎10.10.4.8/30 | ‎DIST2 **.9** | ‎CORE1 **.10** |
| ‎A-DIST2 Gi1/1/2 ↔ CORE2 Gi1/0/2 | ‎10.10.4.12/30 | ‎DIST2 **.13** | ‎CORE2 **.14** |
| ‎CORE1 Gi1/0/23 ↔ CORE2 Gi1/0/23 | ‎10.10.4.48/30 | ‎CORE1 **.49** | ‎CORE2 **.50** |

</div>

<div dir="rtl">

| מכשיר | Loopback0 (= ה-router-ID של OSPF) |
|---|---|
| ‎SWL3-HFA-CORE1 / CORE2 | ‎10.10.5.1 / 10.10.5.2 |
| ‎SWL3-HFA-A-DIST1 / DIST2 | ‎10.10.5.11 / 10.10.5.12 |

</div>

<div dir="rtl">

| ‎VLAN 100 SERVERS — 10.10.1.0/24 | כתובת |
|---|---|
| שער HSRP (וירטואלי) | ‎10.10.1.1 |
| ‎CORE1 / CORE2 | ‎10.10.1.2 / 10.10.1.3 |
| SW-HFA-SRV (ניהול) | ‎10.10.1.5 |
| ‎SRV-HFA-SYSLOG | ‎10.10.1.10 |
| ‎SRV-HFA-AAA | ‎10.10.1.11 |
| (חומת האש ASA — שלב 11) | ‎10.10.1.254 |

</div>

---

## משימה 1 — פותחים את שלב 07 ושומרים בשם שלב 08 (איך? ‏←‏ M1)
‏**File → Open** ‏←‏ `my-work/step07.pkt` ‏←‏ **File → Save As** ‏←‏ `my-work/step08.pkt`.

---

## משימה 2 — מציבים את 2 מתגי ה-core (עם חשמל), את מתג השרתים ו-2 שרתים

### 2א — מציבים ונותנים שמות (איך? ‏←‏ M2, ‏M4)

<div dir="rtl">

| איפה מוצאים | דגם | ‎Display Name | איפה שמים |
|---|---|---|---|
| ‎Network Devices → Switches | ‎**3650-24PS** | ‎`SWL3-HFA-CORE1` | באזור **"HAIFA HQ - CORE"** למעלה, מעל DIST1 |
| ‎Network Devices → Switches | ‎**3650-24PS** | ‎`SWL3-HFA-CORE2` | ליד CORE1, מעל DIST2 |
| ‎Network Devices → Switches | ‎**2960** | ‎`SW-HFA-SRV` | בין שני מתגי ה-core ומעליהם |
| ‎End Devices → End Devices | ‎**Server** | ‎`SRV-HFA-SYSLOG` | ליד SW-HFA-SRV |
| ‎End Devices → End Devices | ‎**Server** | ‎`SRV-HFA-AAA` | ליד SW-HFA-SRV |

</div>

### 2ב — ספקי כוח (⚠️ אל תדלגו — איך? ‏←‏ M8)
‏CORE1 ו-CORE2 ‏←‏ לשונית **Physical** ‏←‏ גוררים **AC-POWER-SUPPLY** לחריץ הריק ‏←‏ סוגרים.
(בדיוק כמו בשלב 03, משימה 2ב.)

✅ בשני מתגי ה-core דולקות נורות ירוקות בלשונית Physical.

---

## משימה 3 — מחברים הכול בכבלים לפורטים המדויקים (איך? ‏←‏ M5)
מתג ↔ מתג = **Copper Cross-Over**. שרת ↔ מתג = **Copper Straight-Through**.

<div dir="rtl">

| ‎# | כבל | לוחצים קודם על | פורט | לוחצים אחר כך על | פורט |
|---|---|---|---|---|---|
| ‎1 | ‎Cross-Over | ‎SWL3-HFA-A-DIST1 | ‎**GigabitEthernet1/1/1** | ‎SWL3-HFA-CORE1 | ‎**GigabitEthernet1/0/1** |
| ‎2 | ‎Cross-Over | ‎SWL3-HFA-A-DIST1 | ‎**GigabitEthernet1/1/2** | ‎SWL3-HFA-CORE2 | ‎**GigabitEthernet1/0/1** |
| ‎3 | ‎Cross-Over | ‎SWL3-HFA-A-DIST2 | ‎**GigabitEthernet1/1/1** | ‎SWL3-HFA-CORE1 | ‎**GigabitEthernet1/0/2** |
| ‎4 | ‎Cross-Over | ‎SWL3-HFA-A-DIST2 | ‎**GigabitEthernet1/1/2** | ‎SWL3-HFA-CORE2 | ‎**GigabitEthernet1/0/2** |
| ‎5 | ‎Cross-Over | ‎SWL3-HFA-CORE1 | ‎**GigabitEthernet1/0/23** | ‎SWL3-HFA-CORE2 | ‎**GigabitEthernet1/0/23** |
| ‎6 | ‎Cross-Over | ‎SWL3-HFA-CORE1 | ‎**GigabitEthernet1/0/24** | ‎SW-HFA-SRV | ‎**GigabitEthernet0/1** |
| ‎7 | ‎Cross-Over | ‎SWL3-HFA-CORE2 | ‎**GigabitEthernet1/0/24** | ‎SW-HFA-SRV | ‎**GigabitEthernet0/2** |
| ‎8 | ‎Straight-Through | ‎SRV-HFA-SYSLOG | ‎FastEthernet0 | ‎SW-HFA-SRV | ‎**FastEthernet0/1** |
| ‎9 | ‎Straight-Through | ‎SRV-HFA-AAA | ‎FastEthernet0 | ‎SW-HFA-SRV | ‎**FastEthernet0/2** |

</div>

<div dir="rtl">

> פורטי ה-`Gi1/1/x` של ה-3650 הם פורטי ה-**uplink** (קרוב ל**סוף** רשימת הפורטים). אם PT
> לא מקבל עליהם כבל נחושת, אצלכם הם פורטי סיב — השתמשו בכבל ה-**Fiber** הכתום. כל השאר נשאר
> אותו דבר.

</div>

✅ תשעה כבלים חדשים. בדקו כל תווית מול הטבלה (M6). חלק מהנקודות נשארות כתומות/אדומות עד
שהפורטים מוגדרים — זה תקין עכשיו.

---

## משימה 4 — ‏CORE1: הקשחה, ניתוב, ‏VLANים, ‏Loopback0
👉 **איפה:** ‏**SWL3-HFA-CORE1** ‏←‏ CLI ‏←‏ **Enter** ‏←‏ `Switch>`‎ ‏(M9).

### 4א — הקשחה
⌨️ מקלידים:
```
enable
configure terminal
hostname SWL3-HFA-CORE1
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
```

### 4ב — ניתוב פועל, רשימת VLANים משלו, ‏Loopback0
ה-core לא מצטרף לדומיין ה-VTP של בניין — הוא שומר על VLANים משלו (`transparent`).

⌨️ מקלידים:
```
ip routing
vtp mode transparent
spanning-tree mode rapid-pvst
vlan 100
 name SERVERS
vlan 999
 name PARKING
 exit

! Loopback0 = stable router-ID
interface loopback 0
 ip address 10.10.5.1 255.255.255.255
 exit
```
🔍 **בודקים עכשיו:** ‏`do show ip interface brief` ‏←‏ השורה האחרונה היא `Loopback0  10.10.5.1  YES manual up up`.

---

## משימה 5 — ‏CORE1: קישורים מנותבים, פורט השרתים, שער השרתים
👉 **איפה:** ‏CORE1, שורת הפקודה `SWL3-HFA-CORE1(config)#`‎.

### 5א — קישורים מנותבים לבניין A ול-CORE2 (area 0, ‏MD5)
לכל קישור מנותב יש אותן 5 שורות; רק ה-description והכתובת משתנים.
‏`no switchport` **חייב** לבוא לפני `ip address`.

⌨️ מקלידים:
```
interface gi1/0/1
 description to SWL3-HFA-A-DIST1 Gi1/1/1
 no switchport
 ip address 10.10.4.2 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/0/2
 description to SWL3-HFA-A-DIST2 Gi1/1/1
 no switchport
 ip address 10.10.4.10 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/0/23
 description to SWL3-HFA-CORE2 Gi1/0/23
 no switchport
 ip address 10.10.4.49 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
```
❌ ‏‎`% Invalid input` על `ip address` ‏←‏ דילגתם על `no switchport` בממשק הזה.

### 5ב — הפורט למתג השרתים, פורטים שלא בשימוש, שער השרתים
⌨️ מקלידים:
```
interface gi1/0/24
 description to SW-HFA-SRV Gi0/1
 switchport mode access
 switchport access vlan 100
 no shutdown

! unused ports (Gi1/0/3-4 are used in step 09)
interface range gi1/0/3 - 22
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown

! gateway for the servers (HSRP, CORE1 = active)
interface vlan 100
 description GW SERVERS
 ip address 10.10.1.2 255.255.255.0
 standby version 2
 standby 100 ip 10.10.1.1
 standby 100 priority 110
 standby 100 preempt
 no shutdown
 exit
```
🔍 **בודקים עכשיו:** ‏`do show ip interface brief` ‏←‏ ‏`GigabitEthernet1/0/1` ‏‎`10.10.4.2`,
‏`Gi1/0/2` ‏‎`10.10.4.10`, ‏`Gi1/0/23` ‏‎`10.10.4.49`, ‏`Vlan100` ‏‎`10.10.1.2`, ‏`Loopback0` ‏‎`10.10.5.1`.
(הסטטוס יכול להיות `down` בקישורים שהצד השני שלהם עוד לא מוגדר — בסדר בינתיים.)

---

## משימה 6 — ‏CORE1: ‏OSPF + SSH
👉 **איפה:** ‏CORE1, שורת הפקודה `SWL3-HFA-CORE1(config)#`‎.

### 6א — ‏OSPF
⌨️ מקלידים:
```
router ospf 1
 router-id 10.10.5.1
 passive-interface default
 no passive-interface gi1/0/1
 no passive-interface gi1/0/2
 no passive-interface gi1/0/23
 network 10.10.0.0 0.0.15.255 area 0
 exit
```
✅ בתוך `router ospf 1` שורת הפקודה הייתה ‎`(config-router)#`‎.

<div dir="rtl">

> **מה פירוש `network 10.10.0.0 0.0.15.255 area 0`?** "כל ממשק שהכתובת שלו בתוך
> ‎10.10.0.0/20 מצטרף ל-OSPF area 0." השורה **האחת** הזו תופסת את קישורי ה-‎/30 ‏(10.10.4.x),
> את Loopback0 ‏(10.10.5.x) ואת VLAN 100 ‏(10.10.1.x) — זה הרווח מכך שתכננו בלוק אחד לכל area
> בשלב 01. ה-‎`0.0.15.255` הוא wildcard (כמו ב-ACL, שלב 07) של ‎/20.

</div>

### 6ב — ניהול ב-SSH (אותו דבר כמו בשלב 07)
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
 permit 10.10.19.0 0.0.0.255
 deny any log
 exit
line vty 0 15
 transport input ssh
 login local
 access-class MGMT-ONLY in
 exec-timeout 5 0
line console 0
 login local
 end
copy running-config startup-config
```
✅ ‏‎`[OK]`‎.

<div dir="rtl">

> כמו בשלב 07: אם מתג דוחה את `login block-for ...`‎, דלגו על השורה הזו במתג הזה.

</div>

---

## משימה 7 — ‏CORE2: אותו דבר, עם הערכים שלו
👉 **איפה:** ‏**SWL3-HFA-CORE2** ‏←‏ CLI ‏←‏ **Enter** ‏←‏ `Switch>`‎.

ההבדלים **היחידים** מ-CORE1:

<div dir="rtl">

| | ‎CORE1 | ‎**CORE2** |
|---|---|---|
| ‎hostname | ‎SWL3-HFA-CORE1 | ‎**SWL3-HFA-CORE2** |
| ‎Loopback0 / router-id | ‎10.10.5.1 | ‎**10.10.5.2** |
| ‎Gi1/0/1 | ‏10.10.4.2 (ל-DIST1 Gi1/1/1) | **10.10.4.6** (ל-DIST1 Gi1/1/2) |
| ‎Gi1/0/2 | ‏10.10.4.10 (ל-DIST2 Gi1/1/1) | **10.10.4.14** (ל-DIST2 Gi1/1/2) |
| ‎Gi1/0/23 | ‎10.10.4.49 | ‎**10.10.4.50** |
| ‎Gi1/0/24 | ל-SW-HFA-SRV Gi0/1 | ל-SW-HFA-SRV **Gi0/2** |
| ‎Vlan100 | ‎‏10.10.1.2, ‏priority 110 | ‎**‏10.10.1.3, ‏priority 90** |

</div>

### 7א — הקשחה, ניתוב, ‏VLANים, ‏Loopback0
⌨️ מקלידים:
```
enable
configure terminal
hostname SWL3-HFA-CORE2
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
ip routing
vtp mode transparent
spanning-tree mode rapid-pvst
vlan 100
 name SERVERS
vlan 999
 name PARKING
 exit
interface loopback 0
 ip address 10.10.5.2 255.255.255.255
 exit
```

### 7ב — קישורים, פורט השרתים, שער השרתים
⌨️ מקלידים:
```
interface gi1/0/1
 description to SWL3-HFA-A-DIST1 Gi1/1/2
 no switchport
 ip address 10.10.4.6 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/0/2
 description to SWL3-HFA-A-DIST2 Gi1/1/2
 no switchport
 ip address 10.10.4.14 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/0/23
 description to SWL3-HFA-CORE1 Gi1/0/23
 no switchport
 ip address 10.10.4.50 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/0/24
 description to SW-HFA-SRV Gi0/2
 switchport mode access
 switchport access vlan 100
 no shutdown
interface range gi1/0/3 - 22
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
interface vlan 100
 description GW SERVERS
 ip address 10.10.1.3 255.255.255.0
 standby version 2
 standby 100 ip 10.10.1.1
 standby 100 priority 90
 standby 100 preempt
 no shutdown
 exit
```

### 7ג — ‏OSPF ו-SSH
⌨️ מקלידים:
```
router ospf 1
 router-id 10.10.5.2
 passive-interface default
 no passive-interface gi1/0/1
 no passive-interface gi1/0/2
 no passive-interface gi1/0/23
 network 10.10.0.0 0.0.15.255 area 0
 exit
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
‏←‏ **‎`1024`** ‏←‏ ואז:
```
ip ssh version 2
ip ssh time-out 60
ip ssh authentication-retries 3
login block-for 120 attempts 3 within 60
ip access-list standard MGMT-ONLY
 permit 10.10.19.0 0.0.0.255
 deny any log
 exit
line vty 0 15
 transport input ssh
 login local
 access-class MGMT-ONLY in
 exec-timeout 5 0
line console 0
 login local
 end
copy running-config startup-config
```
לחצו **Fast Forward Time** כמה פעמים (M18).

✅ ב-CORE2 מופיע ‎`%OSPF-5-ADJCHG: Process 1, Nbr 10.10.5.1 on GigabitEthernet1/0/23 from LOADING to FULL`
— **שני מתגי ה-core הם שכני OSPF**.\
🔍 **בודקים עכשיו:** ‏`show ip ospf neighbor` ‏←‏ שורה אחת, ‏‎`10.10.5.1`, מצב `FULL`.\
❌ אין שכן ‏←‏ השוו את מפתח ה-MD5 על Gi1/0/23 בשני מתגי ה-core ‏(`show running-config interface gi1/0/23`).

---

## משימה 8 — ‏DIST1: קישורים כלפי מעלה + OSPF areas 0 ו-1
👉 **איפה:** ‏**SWL3-HFA-A-DIST1** ‏←‏ CLI ‏←‏ נכנסים (`admin` / `Intel#Adm1n` מאז שלב 07) ‏←‏
‏`SWL3-HFA-A-DIST1#`‎.

ב-DIST1 כבר יש את כל מה שמשלבים 03–07. אנחנו **מוסיפים** לו.

### 8א — ‏Loopback0 ושני הקישורים כלפי מעלה
⌨️ מקלידים:
```
configure terminal
interface loopback 0
 ip address 10.10.5.11 255.255.255.255
interface gi1/1/1
 description to SWL3-HFA-CORE1 Gi1/0/1
 no switchport
 ip address 10.10.4.1 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/1/2
 description to SWL3-HFA-CORE2 Gi1/0/1
 no switchport
 ip address 10.10.4.5 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
```

### 8ב — ‏DIST1 ו-DIST2 הם גם שכנים בתוך area 1, דרך VLAN 99
⌨️ מקלידים:
```
interface vlan 99
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 exit
```

### 8ג — ‏OSPF עם שני areas והסיכום
⌨️ מקלידים:
```
router ospf 1
 router-id 10.10.5.11
 passive-interface default
 no passive-interface gi1/1/1
 no passive-interface gi1/1/2
 no passive-interface vlan 99
 ! uplinks + loopback -> area 0
 network 10.10.0.0 0.0.15.255 area 0
 ! building A VLANs -> area 1
 network 10.10.16.0 0.0.15.255 area 1
 ! announce building A as ONE route
 area 1 range 10.10.16.0 255.255.240.0
 end
copy running-config startup-config
```
לחצו **Fast Forward Time**.

✅ הודעות ‎`%OSPF-5-ADJCHG: ... Nbr 10.10.5.1 ... to FULL` ו-‎`... Nbr 10.10.5.2 ... to FULL`.\
🔍 **בודקים עכשיו:** ‏`show ip ospf neighbor` ‏←‏ ‏CORE1 ‏(‎`10.10.5.1`) ו-CORE2 ‏(‎`10.10.5.2`), שניהם `FULL`.

---

## משימה 9 — ‏DIST2: אותו דבר, עם הערכים שלו
👉 **איפה:** ‏**SWL3-HFA-A-DIST2** ‏←‏ CLI ‏←‏ נכנסים ‏←‏ `SWL3-HFA-A-DIST2#`‎.

<div dir="rtl">

| מה | ב-DIST1 | ב-DIST2 |
|---|---|---|
| ‎‏Loopback0 / router-id | ‎‏10.10.5.11 | ‎**‏10.10.5.12** |
| ‏Gi1/1/1 (ל-CORE1) | ‏10.10.4.1 (ל-Gi1/0/1) | **‏10.10.4.9** (ל-Gi1/0/2) |
| ‏Gi1/1/2 (ל-CORE2) | ‏10.10.4.5 (ל-Gi1/0/1) | **‏10.10.4.13** (ל-Gi1/0/2) |

</div>

⌨️ מקלידים:
```
configure terminal
interface loopback 0
 ip address 10.10.5.12 255.255.255.255
interface gi1/1/1
 description to SWL3-HFA-CORE1 Gi1/0/2
 no switchport
 ip address 10.10.4.9 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/1/2
 description to SWL3-HFA-CORE2 Gi1/0/2
 no switchport
 ip address 10.10.4.13 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface vlan 99
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 exit
router ospf 1
 router-id 10.10.5.12
 passive-interface default
 no passive-interface gi1/1/1
 no passive-interface gi1/1/2
 no passive-interface vlan 99
 network 10.10.0.0 0.0.15.255 area 0
 network 10.10.16.0 0.0.15.255 area 1
 area 1 range 10.10.16.0 255.255.240.0
 end
copy running-config startup-config
```
לחצו **Fast Forward Time** כמה פעמים.

✅ הודעות ‎`%OSPF-5-ADJCHG`: השכנים CORE1, ‏CORE2 ו-DIST1 מגיעים ל-`FULL`.

### מה הפקודות החדשות אומרות

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`no switchport` | "תפסיק להיות פורט של מתג, תהיה פורט של נתב" |
| ‎`interface loopback 0` | ממשק וירטואלי שתמיד פעיל — תעודת הזהות של המכשיר |
| ‎`router ospf 1` | מפעיל OSPF (תהליך מספר 1 — משנה רק מקומית) |
| ‎`router-id 10.10.5.1` | השם שלי ב-OSPF |
| ‎`passive-interface default` | "אל תשלח Hello לשום מקום…" |
| ‎`no passive-interface gi1/0/1` | "…חוץ מהקישור הזה לכיוון נתב אחר" |
| ‎`network 10.10.0.0 0.0.15.255 area 0` | "ממשקים בטווח הזה מצטרפים ל-area 0" |
| ‎`area 1 range 10.10.16.0 255.255.240.0` | "פרסם את area 1 כנתיב סיכום אחד" |
| ‎`ip ospf message-digest-key 1 md5 KEY` + `ip ospf authentication message-digest` | "דבר OSPF רק עם שכנים שמכירים את המפתח הזה" |
| ‎`logging host 10.10.1.10` | "שלח עותק של כל הודעה לשרת ה-Syslog" |
| ‎`service timestamps log datetime msec` | "שים תאריך ושעה על כל הודעה" |
| ‎`aaa new-model` | "הפעל AAA" |
| ‎`tacacs-server host ... key ...`‎ | "זה שרת ה-AAA, וזה הסוד המשותף שלנו" |
| ‎`aaa authentication login default group tacacs+ local` | "בדוק התחברויות מול TACACS+; אם הוא לא עונה, השתמש במשתמשים המקומיים שלי" |

</div>

---

## משימה 10 — בודקים OSPF: שכנים, נתיב הסיכום, פינגים

### 10א — שכנים
👉 ב-**CORE1**: ‏`show ip ospf neighbor`

✅ אמורים לראות:
```
Neighbor ID     Pri   State           Dead Time   Address         Interface
10.10.5.11        1   FULL/DR         00:00:35    10.10.4.1       GigabitEthernet1/0/1
10.10.5.12        1   FULL/DR         00:00:36    10.10.4.9       GigabitEthernet1/0/2
10.10.5.2         1   FULL/BDR        00:00:33    10.10.4.50      GigabitEthernet1/0/23
```
שלושה שכנים, כולם **FULL**. ‏(DR/BDR הם תפקידים בקישורים משותפים — התעלמו מהם בינתיים. מי
יהיה DR תלוי במי עלה ראשון, ולכן התוויות DR/BDR אצלכם יכולות להיות שונות.)

👉 ב-**DIST1**: ‏`show ip ospf neighbor` ‏←‏ ✅ ‏CORE1, ‏CORE2 **וגם** DIST2 (דרך Vlan99).

### 10ב — נתיב הסיכום
👉 ב-**CORE1**: ‏`show ip route ospf`

✅ אמורים לראות:
```
     10.0.0.0/8 is variably subnetted, ...
O IA    10.10.16.0/20 [110/2] via 10.10.4.1, GigabitEthernet1/0/1
                      [110/2] via 10.10.4.9, GigabitEthernet1/0/2
O       10.10.5.11/32 [110/2] via 10.10.4.1, ...
...
```
‏**O IA** = נתיב OSPF מ-**area אחר** ‏(Inter-Area). נתיב סיכום **אחד** לכל בניין A, שאפשר
להגיע אליו בשתי **דרכים** ‏(DIST1 ו-DIST2) — חלוקת עומס.

👉 ב-**DIST1**: ‏`show ip ospf interface` ‏←‏ בכל ממשק הסתכלו על שורת ה-`Area`.\
✅ ‏Gi1/1/1, ‏Gi1/1/2 ו-Loopback0 נמצאים ב-**area 0**; ה-VLANים ב-**area 1**.

### 10ג — פינגים (איך? ‏←‏ M17)

<div dir="rtl">

| ‎# | מאיפה | מקלידים | צפוי |
|---|---|---|---|
| ‎1 | מחשב ENG | ‎`ping 10.10.1.1` | ✅ השער של השרתים, דרך ה-core |
| ‎2 | מחשב ENG | ‎`tracert 10.10.1.1` | ‏‎`10.10.16.2` ‏←‏ ‎`10.10.4.2` (או ‎`.6`) ‏←‏ ‎`10.10.1.x` |
| ‎3 | ‎PC-HFA-ADMIN-01 | ‎`ssh -l admin 10.10.5.1` | ✅ התחברות ל-CORE1 (בינתיים משתמש מקומי) |

</div>

### 10ד — רואים את הממשקים הפסיביים (מצב Simulation — איך? ‏←‏ M21)
‏**Simulation** ‏←‏ **Show All/None** ‏←‏ **Edit Filters** ‏←‏ סמנו רק **OSPF** ‏←‏ סגרו.
לחצו **Capture / Forward** כמה פעמים.

✅ מעטפות ה-Hello עוברות רק בקישורים המנותבים וב-VLAN 99 — **אף פעם** לא לכיוון המחשבים.

חזרו ל-**Realtime**. ‏**File → Save**.

---

## משימה 11 — ‏SW-HFA-SRV: מתג השרתים
👉 **איפה:** ‏**SW-HFA-SRV** ‏←‏ CLI ‏←‏ **Enter** ‏←‏ `Switch>`‎.

### 11א — הקשחה ו-VLAN 100
⌨️ מקלידים:
```
enable
configure terminal
hostname SW-HFA-SRV
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
spanning-tree mode rapid-pvst
vlan 100
 name SERVERS
 exit
```

### 11ב — פורטים וכתובת ניהול
⌨️ מקלידים:
```
interface range gi0/1 - 2
 description uplinks to CORE1 / CORE2
 switchport mode access
 switchport access vlan 100
interface range fa0/1 - 23
 description servers
 switchport mode access
 switchport access vlan 100
 spanning-tree portfast
 spanning-tree bpduguard enable
interface fa0/24
 description to ASA-HFA-FW1 inside (step 11)
 switchport mode access
 switchport access vlan 100
interface vlan 100
 description MANAGEMENT
 ip address 10.10.1.5 255.255.255.0
 no shutdown
 exit
ip default-gateway 10.10.1.1
```

### 11ג — ‏SSH
⌨️ מקלידים:
```
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
‏←‏ **‎`1024`** ‏←‏ ואז:
```
ip ssh version 2
login block-for 120 attempts 3 within 60
ip access-list standard MGMT-ONLY
 permit 10.10.19.0 0.0.0.255
 deny any log
 exit
line vty 0 15
 transport input ssh
 login local
 access-class MGMT-ONLY in
 exec-timeout 5 0
line console 0
 login local
 end
copy running-config startup-config
```
🔍 **בודקים עכשיו:** ‏`ping 10.10.1.1` ‏←‏ ✅ יש תשובות (שער ה-HSRP במתגי ה-core).

---

## משימה 12 — שני השרתים: כתובות ושירותים

### 12א — כתובות (איך? ‏←‏ M14)
לכל שרת: לחיצה ‏←‏ **Desktop** ‏←‏ **IP Configuration** ‏←‏ **Static**:

<div dir="rtl">

| שרת | ‎IPv4 Address | ‎Subnet Mask | ‎Default Gateway | ‎DNS Server |
|---|---|---|---|---|
| ‎SRV-HFA-SYSLOG | ‎10.10.1.10 | ‎255.255.255.0 | ‎10.10.1.1 | ‎10.10.200.11 |
| ‎SRV-HFA-AAA | ‎10.10.1.11 | ‎255.255.255.0 | ‎10.10.1.1 | ‎10.10.200.11 |

</div>

### 12ב — תפקיד אחד לכל שרת (איך? ‏←‏ M20)
ב**כל** שרת ‏←‏ לשונית **Services** ‏←‏ עבור **HTTP**, ‏**DHCP**, ‏**DNS**, ‏**EMAIL**, ‏**FTP**, ‏**NTP**
‏←‏ העבירו כל אחד ל-**Off** ‏(ב-HTTP: כבו גם את HTTP וגם את HTTPS).

אחר כך:
- ‏**SRV-HFA-SYSLOG:** ‏**Services** ‏←‏ **SYSLOG** ‏←‏ **On**.

✅ ממחשב ENG: ‏`ping 10.10.1.10` ו-`ping 10.10.1.11` ‏←‏ שניהם עונים.

---

## משימה 13 — ממלאים את שרת ה-AAA
👉 **איפה:** לחצו על **SRV-HFA-AAA** ‏←‏ לשונית **Services** ‏←‏ **AAA** (ברשימה משמאל).

1. ‏**Service:** לחצו **On**.
2. ‏**Network Configuration** (החלק העליון) — מוסיפים שורה לכל מכשיר רשת. לכל שורה בטבלה
   שלמטה:
   1. לחצו ב-**Client Name**, הקלידו את השם.
   2. לחצו ב-**Client IP**, הקלידו את ה-IP.
   3. ‏**Secret**: ‏`Intel#Tac`
   4. ‏**ServerType**: בחרו **Tacacs**.
   5. לחצו **Add**. השורה מופיעה ברשימה שמתחת.

   | Client Name | Client IP |
   |---|---|
   | SW-HFA-A-ACC1 | 10.10.19.11 |
   | SW-HFA-A-ACC2 | 10.10.19.12 |
   | SWL3-HFA-A-DIST1 | 10.10.5.11 |
   | SWL3-HFA-A-DIST2 | 10.10.5.12 |
   | SWL3-HFA-CORE1 | 10.10.5.1 |
   | SWL3-HFA-CORE2 | 10.10.5.2 |
   | SW-HFA-SRV | 10.10.1.5 |

3. ‏**User Setup** (החלק התחתון) — ‏**Username** ‏`admin`, ‏**Password** ‏`Intel#Adm1n` ‏←‏ **Add**.

✅ ברשימת ה-clients יש 7 שורות; ברשימת המשתמשים יש `admin`.\
❌ בשורה יש שגיאת כתיב ‏←‏ לחצו עליה ברשימה ‏←‏ **Remove** ‏←‏ הוסיפו אותה שוב.

<div dir="rtl">

> למה דווקא כתובות ה-client האלה? שרת ה-AAA עונה רק למכשירים שהוא מכיר **לפי כתובת המקור של
> הבקשה שלהם**. מתגי ה-access שולחים מהכתובת שלהם ב-VLAN 99. מתגי שכבה 3 היו שולחים מאיזה
> קישור כלפי מעלה שהם משתמשים בו — ולכן אנחנו אומרים להם לשלוח תמיד מ-Loopback0 (משימה 14ב).

</div>

---

## משימה 14 — ‏AAA + Syslog בכל 7 המתגים

### 14א — הבלוק לכל מתג
הקלידו את הבלוק הזה ב**כל 7**. התחברו לכל אחד עם `admin` / `Intel#Adm1n`.

⌨️ מקלידים:
```
configure terminal
! ---------- Syslog ----------
service timestamps log datetime msec
logging trap informational
logging host 10.10.1.10

! ---------- AAA: ask the TACACS+ server, local user as backup ----------
aaa new-model
tacacs-server host 10.10.1.11 key Intel#Tac
aaa authentication login default group tacacs+ local
line vty 0 15
 login authentication default
line console 0
 login authentication default
 end
copy running-config startup-config
```

<div dir="rtl">

> תחביר ישן של PT: אם `logging host` נדחה, הקלידו `logging 10.10.1.10`.

</div>

סמנו כל מתג כשהוא מראה ‎`[OK]`‎:
- [ ] ‏SW-HFA-A-ACC1
- [ ] ‏SW-HFA-A-ACC2
- [ ] ‏SWL3-HFA-A-DIST1
- [ ] ‏SWL3-HFA-A-DIST2
- [ ] ‏SWL3-HFA-CORE1
- [ ] ‏SWL3-HFA-CORE2
- [ ] ‏SW-HFA-SRV

### 14ב — רק 4 מתגי שכבה 3: מדברים עם ה-AAA מ-Loopback0
ב-**DIST1, ‏DIST2, ‏CORE1, ‏CORE2**:

⌨️ מקלידים:
```
configure terminal
ip tacacs source-interface loopback 0
end
copy running-config startup-config
```
(‏`ip tacacs source-interface loopback 0` = "כשאתה פונה לשרת ה-AAA, שלח מ-Loopback0".)

<div dir="rtl">

> אם `ip tacacs source-interface` נדחה, רשמו את מתגי שכבה 3 בשרת ה-AAA לפי הכתובות שהם שולחים
> מהן במקום זה. ל-DIST1 ול-DIST2 יש שני קישורים כלפי מעלה שווים, אז הוסיפו **את שניהם** לכל אחד:
> ‏DIST1 ‏10.10.4.1 ו-10.10.4.5, ‏DIST2 ‏10.10.4.9 ו-10.10.4.13, ‏CORE1 ‏10.10.1.2, ‏CORE2 ‏10.10.1.3.

</div>

---

## משימה 15 — בודקים את ה-AAA, את הגיבוי שלו, ואת ה-Syslog

### 15א — התחברות דרך AAA
מ-**PC-HFA-ADMIN-01**: ‏`ssh -l admin 10.10.5.1` ‏←‏ `Intel#Adm1n`.\
✅ מגיעים ל-`SWL3-HFA-CORE1#`‎ — הפעם הסיסמה נבדקה על ידי שרת ה-AAA.

### 15ב — הגיבוי עובד
1. לחצו על **SRV-HFA-AAA** ‏←‏ לשונית **Physical** ‏←‏ לחצו על **כפתור ההפעלה** שלו (הנורה כבית).
2. התחברו שוב ב-SSH ממחשב המנהל ל-‎`10.10.5.1`.\
   ✅ עדיין עובד עם `admin` / `Intel#Adm1n` — המתג השתמש במשתמש המקומי שלו (גיבוי). (זה עשוי
   לקחת כמה שניות יותר, בזמן שהמתג מחכה לשרת המת.)
3. הדליקו שוב את שרת ה-AAA.

### 15ג — ‏Syslog
1. ב-**ACC1**: ‏`configure terminal` ‏←‏ `interface fa0/24` ‏←‏ `no shutdown` ‏←‏ `shutdown` ‏←‏ `end`.
2. לחצו על **SRV-HFA-SYSLOG** ‏←‏ **Services** ‏←‏ **SYSLOG**.\
   ✅ ההודעות מ-ACC1 מופיעות ברשימה, עם שעה וכתובת מקור.

📸 צלמו מסך של רשימת ה-Syslog לספר שלכם. אחר כך **File → Save**.

---

## נקודת ביקורת
- [ ] ל-CORE1 יש 3 שכני OSPF במצב FULL
- [ ] ‏CORE1 רואה `O IA 10.10.16.0/20` דרך שתי דרכים
- [ ] המחשבים מגיעים לשרתים
- [ ] ‏SSH עובד דרך AAA, וממשיך לעבוד כששרת ה-AAA כבוי
- [ ] שרת ה-Syslog מקבל הודעות

## אם משהו לא עובד

<div dir="rtl">

| בעיה | פתרון |
|---|---|
| ‎`% Invalid input` על `ip address` תחת Gi1/1/1 | הקלידו קודם `no switchport` |
| השכנים אף פעם לא מגיעים ל-FULL (תקועים ב-INIT/EXSTART) או שאין שכנים בכלל | שגיאת כתיב במפתח ה-MD5 בצד אחד; או שצד אחד עדיין פסיבי; או שה-IP בצד הלא נכון של ה-‎/30 ‏(`show ip interface brief`) |
| ‏`show ip ospf neighbor` ריק ב-DIST2 ‏←‏ DIST1 | ‏VLAN 99 לא נמצא ב-`no passive-interface`, או שאין MD5 על Vlan99 |
| ה-core לא רואה את ‎`10.10.16.0/20` | חסר `network 10.10.16.0 0.0.15.255 area 1` במתגי ה-DIST |
| ‏SSH תמיד משתמש במשתמש המקומי (ה-AAA לא בשימוש) | ה-Client IP בשרת ה-AAA לא תואם לכתובת המקור של הבקשה. ראו את ההערה במשימה 14ב |
| שרת ה-Syslog לא מציג כלום | שירות ה-SYSLOG בשרת כבוי, או כתובת `logging host` שגויה, או שהמכשיר לא מצליח ping ל-10.10.1.10 |

</div>

---

## 🏋 תרגילים

### תרגיל א — "הורגים" מתג core ⭐⭐
- 🎯 **המשימה:** להוכיח שהמטה בחיפה שורד אובדן מוחלט של CORE1.
- 📁 **מתחילים מ:** ה-`step08.pkt` שלכם — קודם **File → Save** (תצטרכו אותו בחזרה).
- 👣 **צעדים:**
  1. ממחשב ENG הפעילו `ping -t 10.10.1.10` (שרת ה-Syslog).
  2. מחקו את CORE1 (כלי ה-Delete ‏←‏ לחצו על CORE1).
  3. הסתכלו על הפינג. אחר כך ב-DIST1 הריצו `show ip route ospf` וב-CORE2 ‏`show standby brief`.
  4. ‏**File → Open** לקובץ `step08.pkt` ששמרתם כדי להחזיר את CORE1 (ענו **No** על "save changes").
- ✅ **גמרתם כש**אתם יודעים להסביר מה קרה (א) לפינג, (ב) לנתיבים של DIST1, (ג) לשער של
  השרתים 10.10.1.1.

<details dir="rtl"><summary>💡 רמז</summary>

לפני: כמה דרכים היו ל-DIST1 אל ‎`10.10.1.0/24`? איזה core היה HSRP Active עבור VLAN 100?
</details>
<details dir="rtl"><summary>✔ תשובה</summary>

שני הנתיבים השווים של DIST1 הופכים לאחד (דרך CORE2); כמה פינגים הולכים לאיבוד בזמן ש-OSPF מבחין
בשכן שמת. ‏CORE2 הופך ל-HSRP **Active** עבור VLAN 100, ולכן השער של השרתים 10.10.1.1 ממשיך
לעבוד. (אילו CORE1 רק היה מאותחל, ה-`preempt` היה מחזיר לו את VLAN 100 כשהוא חוזר.)
</details>

### תרגיל ב — המפתח הלא נכון ⭐⭐
- 🎯 **המשימה:** לראות מה מפתח MD5 שגוי עושה לשכן OSPF.
- 📁 **מתחילים מ:** ה-`step08.pkt` שלכם (‏Save As ‏`step08-exB.pkt`).
- 👣 **צעדים:**
  1. ב-CORE2: ‏`interface gi1/0/23` ‏←‏ `no ip ospf message-digest-key 1 md5 Intel#Ospf` ‏←‏
     ‏`ip ospf message-digest-key 1 md5 WRONG` ‏←‏ `end`.
  2. לחצו Fast Forward Time לזמן מה (ה-dead timer הוא 40 שניות).
  3. ב-CORE1: ‏`show ip ospf neighbor`. האם CORE2 עדיין שם?
  4. החזירו את המפתח הנכון.
- ✅ **גמרתם כש**ראיתם את השכן נעלם וחוזר, ואתם יודעים לומר למה זה מגן על הרשת.

<details dir="rtl"><summary>✔ תשובה</summary>

אחרי זמן ה-dead ‏CORE2 ‏(‎`10.10.5.2`) נעלם מרשימת השכנים של CORE1: המפתחות לא תואמים, ולכן
הודעות ה-Hello נדחות. אותו דבר קורה ללפטופ של תוקף שמנסה להזריק נתיבים מזויפים בלי המפתח
(דרישה 22.18). כשהמפתח הנכון חוזר, השכן חוזר ל-FULL.
</details>

### תרגיל ג — קוראים את טבלת הניתוב ⭐
- 🎯 **המשימה:** ב-DIST1, למצוא את הנתיב ל-VLAN השרתים ולהסביר כל חלק בשורה.
- 👣 **צעדים:** ב-DIST1 הריצו `show ip route 10.10.1.0`, ואז `show ip route ospf`.
- ✅ **גמרתם כש**אתם יודעים להסביר את `O`, את ‎`[110/2]`‎, את `via 10.10.4.2`, ולמה יש שתי
  שורות `via`.

<details dir="rtl"><summary>✔ תשובה</summary>

‏`O` = נלמד ב-OSPF בתוך אותו area ‏(area 0 — ‏DIST1 נמצא ב-area 0 בקישורים כלפי מעלה שלו).
‏‎`110` = ה-administrative distance של OSPF (כמה הנתב סומך על OSPF), ‏‎`2` = ה-cost (סכום עלויות
הקישורים). ‏`via 10.10.4.2` = הקפיצה הבאה (CORE1). שתי שורות `via` = שתי דרכים בעלות שווה
‏(CORE1 ו-CORE2) — התעבורה מתחלקת ביניהן.
</details>

---

## 🛠 הפרויקט שלכם

עשיתם את השלב הזה על הדוגמה של אינטל. עכשיו עשו אותו שוב בפרויקט **שלכם**, עם הערכים
מהתוכנית **שלכם** (`my-project/plan.md`). הפקודות זהות — רק הערכים משתנים.

- [ ] פותחים את `my-project/step07.pkt` ‏←‏ **Save As** ‏`my-project/step08.pkt`
- [ ] קודם כותבים טבלת קישורים + loopbacks משלכם (כמו 1.10) מתוך בלוק ה-area 0 שלכם
- [ ] שני מתגי core עם חשמל, מתג שרתים, שרתי Syslog + AAA, מחוברים בכבלים
- [ ] ‏Cores: הקשחה, ניתוב, קישורים מנותבים עם MD5, שער ל-VLAN השרתים, ‏OSPF area 0, ‏SSH
- [ ] ‏Distribution: קישורים כלפי מעלה, ‏OSPF area 0 + ה-area של הבניין שלכם, סיכום
- [ ] שרתים + שרת AAA ממולא; ‏AAA + Syslog בכל מתג
- [ ] הבדיקות של משימות 10 ו-15 עוברות

<div dir="rtl">

| בדוגמה | בפרויקט שלכם — לוקחים מ |
|---|---|
| בלוק area 0 ‏‎`10.10.0.0/20`, ‏area 1 ‏‎`10.10.16.0/20` | תוכנית, חלק ג (ה-areas של המטה שלכם) |
| קישורי ‎/30 ‏‎`10.10.4.x`, ‏loopbacks ‏‎`10.10.5.x` | תוכנית, חלק ג — בנו טבלת קישורים ו-loopbacks משלכם מתוך בלוק ה-area 0 שלכם |
| ‏VLAN השרתים 100 וכתובות השרתים (Syslog, ‏AAA) | תוכנית, חלק ד (ה-VLAN של השרתים שלכם והכתובות הקבועות) |
| מפתח ה-MD5 של OSPF ‏`Intel#Ospf`, מפתח TACACS+ ‏`Intel#Tac` | תוכנית, חלק ו |
| ‎`area 1 range 10.10.16.0 255.255.240.0` | ה-‎/20 של הבניין שלכם (סיכום נתיבים — דרישה 22.15) |

</div>

**בדיקה:** ‏`show ip ospf neighbor` מציג FULL בכל קישור; ‏`show ip route` מציג נתיב סיכום **אחד**
לכל בניין; התחברות דרך שרת ה-AAA שלכם עובדת; שרת ה-Syslog שלכם מקבל הודעות.

💾 שמרו בשם `my-project/step08.pkt`.

---

## 🎓 מסבירים לבוחן

בבחינה, הבוחן מצביע על הפרויקט **שלכם** ומבקש **להסביר** ו**להראות**. תרגלו כל שאלה
**בקול**, ואז הראו את התשובה בפרויקט שלכם — לא בדוגמה. כסו את התשובה, ענו בעצמכם, ורק אז
פתחו והשוו.

‏★1–★3 = שאלה ממאגר השאלות של משרד החינוך (רמת קושי 1–3).
‏◆ = לא במאגר, אבל בוחנים שואלים אותה לעיתים קרובות.

**1. ★1 מה היתרון בחלוקה של הרשת לאזורים? מה המקסימום המומלץ של נתבים בתוך אזור OSPF?**

<details dir="rtl"><summary>תשובה</summary>

כל נתב מחזיק מפה מפורטת (LSDB) רק של האזור שלו; בין אזורים מוחלפים רק סיכומים. מסדי נתונים קטנים
יותר, פחות עומס על המעבד, ושינוי בתוך אזור אחד לא גורם לכל הנתבים לחשב מחדש. קו מנחה מקובל
הוא בערך **50 נתבים** באזור.

**איפה מראים:** `show ip ospf database`
</details>

**2. ★1 הראה לי איפה אזור 0 של OSPF. מה התפקיד שלו? איך הוא נקרא?**

<details dir="rtl"><summary>תשובה</summary>

‏Area 0 הוא **עמוד השדרה** ‏(backbone): כל אזור אחר חייב לגעת בו, ותעבורה בין אזורים עוברת דרכו.
בפרויקט הזה נמצאים בו מתגי ה-core, חוות השרתים וקישורי ה-core.

**איפה מראים:** `show ip ospf interface` במתג core ‏←‏ Area 0
</details>

**3. ★1 מה הם התזמונים של Hello ו-Dead ב-OSPF?**

<details dir="rtl"><summary>תשובה</summary>

ב-Ethernet ‏(broadcast ו-point-to-point): ‏Hello כל 10 שניות, ‏Dead אחרי 40 שניות. לשכנים חייבים
להיות אותם תזמונים כדי שיתחברו.

**איפה מראים:** `show ip ospf interface <int>`‎
</details>

**4. ★1 כיצד ניתן לראות את ה-Topology Table של OSPF? ואת ה-Neighbor Table?**

<details dir="rtl"><summary>תשובה</summary>

טבלת הטופולוגיה (מסד הנתונים של מצב הקישורים): `show ip ospf database`. השכנים:
‏`show ip ospf neighbor`. טבלת הניתוב: `show ip route ospf`.

**איפה מראים:** שלוש הפקודות האלה
</details>

**5. ★2 כיצד נקבע ה-Router-ID בפרוטוקול OSPF?**

<details dir="rtl"><summary>תשובה</summary>

1) הפקודה `router-id`; 2) אם אין — כתובת ה-IP הגבוהה ביותר על loopback; 3) אם אין — כתובת
ה-IP הגבוהה ביותר על ממשק פעיל. בפרויקט הזה הוא נקבע עם הפקודה `router-id` (אותו ערך כמו
Loopback0).

**איפה מראים:** `show ip protocols`, `show ip ospf`
</details>

**6. ★2 מי מהנתבים הוא DR ומי BDR? כיצד נקבע מי ה-DR ומי ה-BDR? מה ההבדל ביניהם?**

<details dir="rtl"><summary>תשובה</summary>

בקטעי broadcast ‏(Ethernet) נבחרים DR אחד ו-BDR אחד: ה-priority הגבוה ביותר של OSPF, ואז
ה-Router-ID הגבוה ביותר. כולם מחליפים עדכונים רק עם ה-DR (וה-BDR), וזה חוסך תעבורה. ה-BDR הוא
הגיבוי, והופך ל-DR אם ה-DR נופל.

**איפה מראים:** `show ip ospf neighbor` ‏←‏ העמודה State ‏(FULL/DR, ‏FULL/BDR, …)
</details>

**7. ★2 במידה ונתב ה-DR "נופל", איזה נתב מקבל את התפקיד? מה קורה אם אחרי זמן מסוים הנתב שנפל חוזר לפעילות?**

<details dir="rtl"><summary>תשובה</summary>

ה-BDR הופך ל-DR ונבחר BDR חדש. הבחירה **לא** pre-emptive: כשה-DR הישן חוזר, הוא לא לוקח את
התפקיד בחזרה — הוא מחכה עד שה-DR/BDR הנוכחיים ייפלו.

**איפה מראים:** כבו את הממשק של ה-DR, ואז `show ip ospf neighbor`.
</details>

**8. ★2 מהי רשת מסוג Point to Point ומהי רשת מסוג Broadcast?**

<details dir="rtl"><summary>תשובה</summary>

‏Point-to-point: בדיוק שני נתבים בקישור — אין בחירת DR/BDR. ‏Broadcast ‏(Ethernet): הרבה נתבים
יכולים לחלוק את הקטע — נבחרים DR/BDR. קישור Ethernet ‎/30 הוא מסוג broadcast כברירת מחדל, אלא אם
מגדירים `ip ospf network point-to-point`.

**איפה מראים:** `show ip ospf interface <int>`‎ ‏←‏ Network Type
</details>

**9. ★2 מהו type 1 LSA וכיצד הוא מסומן בטבלת הניתוב? ומהו type 3 LSA?**

<details dir="rtl"><summary>תשובה</summary>

‏Type 1 ‏(Router LSA): כל נתב מתאר את הקישורים שלו בתוך האזור שלו ‏←‏ נתיבים מסומנים `O`. ‏Type 3
‏(Summary LSA): נשלח על ידי ABR כדי לתאר רשתות של אזור אחר ‏←‏ מסומן `O IA` ‏(inter-area).

**איפה מראים:** `show ip route` במתג distribution
</details>

**10. ★2 הראה לי איזה נתב הוא ה-ABR ‏(area border router).**

<details dir="rtl"><summary>תשובה</summary>

נתב שיש לו ממשקים ב-area 0 ובאזור נוסף. בפרויקט הזה מתגי ה-distribution של כל בניין הם ABRים
(‏area 0 לכיוון ה-core, ‏area N לכיוון הבניין).

**איפה מראים:** `show ip ospf` ("It is an area border router")
</details>

**11. ◆ איך OSPF מאובטח בפרויקט שלכם?**

<details dir="rtl"><summary>תשובה</summary>

אימות MD5 בקישורים המנותבים (`ip ospf authentication message-digest` +
`ip ospf message-digest-key 1 md5 <key>`‎) — נתב בלי המפתח לא יכול להפוך לשכן ולהזריק נתיבים
(דרישה 22.18).

**איפה מראים:** `show ip ospf interface <int>`‎ ‏←‏ "Message digest authentication enabled"
</details>

**12. ★1 מה תפקידו של שרת NTP? הצג את ההגדרות בפרויקט (גם בשרת וגם על גבי הנתב/המתג).**

<details dir="rtl"><summary>תשובה</summary>

הוא שומר שהשעון של כל המכשירים יהיה זהה (UDP 123), כדי שזמני היומנים יתאימו בין מכשירים
ושתעודות/מפתחות יעבדו. בשרת: ‏Services ‏←‏ NTP ‏←‏ On. במכשיר: `ntp server <IP>`‎. (בפרויקט הזה
‏NTP מוגדר בשלב 11.)

**איפה מראים:** `show ntp status`, `show clock`
</details>

**13. ★1 מה תפקידו של שרת Syslog? מול איזה שרת הוא עובד?**

<details dir="rtl"><summary>תשובה</summary>

הוא אוסף הודעות יומן מכל הנתבים והמתגים למקום אחד (UDP 514), כך שמנהל הרשת יכול לראות אירועים
של כל הרשת. המכשירים שולחים אליו עם `logging host <IP>`‎.

**איפה מראים:** שרת ‏←‏ Services ‏←‏ SYSLOG (רשימת ההודעות); `show logging`
</details>

**14. ★1 מהו שרת AAA? מהם היתרונות והחסרונות של השימוש בו?**

<details dir="rtl"><summary>תשובה</summary>

‏Authentication (מי אתה), ‏Authorization (מה מותר לך), ‏Accounting (מה עשית). יתרון: מאגר משתמשים
מרכזי אחד לכל המכשירים; שינויים במקום אחד; רישום פעולות. חיסרון: אם השרת לא זמין אף אחד לא יכול
להתחבר — ולכן נשמר משתמש מקומי כגיבוי (‎`… group tacacs+ local`).

**איפה מראים:** `show running-config | include aaa`
</details>

**15. ★1/★2 מהם סוגי שרתי AAA הקיימים? מה ההבדל בין שרת RADIUS לשרת TACACS+?**

<details dir="rtl"><summary>תשובה</summary>

‏RADIUS (תקן פתוח, ‏UDP 1812/1813, מצפין רק את הסיסמה, משלב authentication ו-authorization —
נפוץ לגישה לרשת/WiFi). ‏TACACS+ ‏(Cisco, ‏TCP 49, מצפין את כל החבילה, מפריד בין שלושת ה-A — נפוץ
לניהול ציוד). בפרויקט הזה משתמשים ב-TACACS+ להתחברות לציוד.

**איפה מראים:** שרת ‏←‏ Services ‏←‏ AAA
</details>

**16. ★2 מהם פרמטרי ההגדרה העיקריים של שרת AAA? כיצד ניתן לאבטח שרת AAA?**

<details dir="rtl"><summary>תשובה</summary>

במכשיר: `aaa new-model`, השרת (`tacacs-server host <IP> key <key>`‎), ורשימת השיטות
(`aaa authentication login default group tacacs+ local`). בשרת: ה-client (שם המכשיר + IP +
מפתח) והמשתמשים. מאבטחים אותו עם מפתח משותף חזק, במיקום ב-VLAN השרתים מאחורי ACL, ועם משתמש גיבוי
מקומי.

**איפה מראים:** `show running-config` (שורות aaa / tacacs) ועמוד שירות ה-AAA
</details>

**17. ★3 הסבר את השורות של הגדרת AAA על גבי הנתב, והסבר את הגדרת ה-AAA על גבי השרת.**

<details dir="rtl"><summary>תשובה</summary>

עברו על כל שורת `aaa` ו-`tacacs-server` במכשיר, ואז על עמוד ה-AAA בשרת: שם ה-client, ‏IP של
ה-client, המפתח (חייב להתאים), סוג השרת TACACS, ואז רשימת המשתמשים.

**איפה מראים:** שני המסכים זה לצד זה
</details>

---

## 🔁 עושים שוב — בלי המדריך

הבוחן יכול לבקש מכם להגדיר משהו שוב, מולו. תצליחו רק אם עשיתם את זה **בלי המדריך** לפני כן.
עשו את התרגיל הזה בפרויקט שלכם:

בעותק של קובץ שלב 08 הגמור שלכם, הסירו את OSPF ממתג distribution אחד ואת שורות ה-AAA ממכשיר
אחד. בלי העמוד הזה, הגדירו אותם שוב מתוך התוכנית שלכם (router-ID, רשתות/areas, ‏MD5, סיכום, ‏AAA
עם גיבוי מקומי). יעד: **‏20 דקות**. אחר כך הראו `show ip ospf neighbor` ‏(FULL), ‏`show ip route`
(סיכום אחד לכל בניין), התחברות SSH דרך שרת ה-AAA, והודעת יומן שמגיעה לשרת ה-Syslog.

---

## 👩‍🏫 הערות למורה
- **שיעור 1 (90 דקות):** המודל התלת-שכבתי וקישורים מנותבים ‏←‏ ניתוב סטטי מול דינמי ‏←‏ OSPF
  במילים פשוטות (שכנים, מפה, דרך קצרה) ‏←‏ בנייה וחיווט ‏←‏ הגדרת CORE1/CORE2.
- **שיעור 2 (90 דקות):** ‏areas ו-ABRים (ההשוואה למדינה/עיר) ‏←‏ סיכום נתיבים ‏←‏ קישורי ה-DIST
  כלפי מעלה + OSPF ‏←‏ משימה 10 ‏←‏ ממשקים פסיביים במצב Simulation.
- **שיעור 3 (90 דקות):** ‏Syslog ו-AAA (שומר אחד לכל הדלתות) ‏←‏ הגדרת השרתים ‏←‏ בלוק ה-AAA בכל 7
  המכשירים ‏←‏ משימה 15 ‏←‏ תרגילים.
- **שאלות נפוצות של תלמידים**
  - *"למה המחשבים לא מריצים OSPF?"* — רק נתבים צריכים את המפה. מחשבים פשוט משתמשים בשער שלהם.
  - *"מה זה `O IA`?"* — נתיב שנלמד מאזור אחר. ‏`O` לבד = אותו אזור.
  - *"למה ה-wildcard הוא 0.0.15.255?"* — ‏‎/20 מכיל 16 רשתות ‎/24 ‏←‏ המספר השלישי יכול להשתנות
    ב-15.
- **טעויות אופייניות:** שכחת `no switchport`; צד לא נכון של ‎/30 (בשני הקצוות ‎`.1`); העתקת
  מפתח ה-MD5 עם שגיאת כתיב; שכחת ספקי הכוח של ה-3650.
