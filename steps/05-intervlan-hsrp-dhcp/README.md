# שלב 05 — ניתוב בין VLANים, HSRP ו-DHCP

<div dir="rtl">

> ⏱ ‏2–3 שיעורים · 🎯 דרישות משרד החינוך 22.10, ‏17, ‏20.7, ‏22.11, ‏6\
> 📁 מתחילים מ: `my-work/step04.pkt`\
> 💾 שומרים בשם: `my-work/step05.pkt`

</div>

<div dir="rtl">

> ✅ **לפני שמתחילים:** כל הסעיפים בנקודת הביקורת של שלב 04 מסומנים, ועשיתם את
> תרגיל ה-🔁 שלו בפרויקט שלכם. אל תדלגו על שלבים — כל שלב בנוי על הקובץ של השלב הקודם.

</div>

## מה יהיה לכם בסוף השלב
- שני מתגי ה-distribution עובדים גם כ**נתבים**: המחלקות סוף סוף יכולות לדבר זו עם זו.
- לכל VLAN יש כתובת שער (‎`.1`) ש**ממשיכה לעבוד גם אם אחד ממתגי ה-distribution מת** ‏(HSRP).
- המחשבים מקבלים את הגדרות ה-IP שלהם **אוטומטית** ‏(DHCP), משני מתגי ה-distribution.

```
                    VLAN 10 gateway = 10.10.16.1  (virtual — shared by both)
                            ╱                         ╲
   SWL3-HFA-A-DIST1  10.10.16.2  ACTIVE         SWL3-HFA-A-DIST2  10.10.16.3  STANDBY
   DHCP: hands out .11 – .130                   DHCP: hands out .131 – .254
```
(השער של VLAN 10 הוא ‎`10.10.16.1` — כתובת וירטואלית ששני המתגים חולקים. ‏DIST1 ‏(‎`.2`) הוא
ה-Active ומחלק בכתובות ‎`.11–.130`; ‏DIST2 ‏(‎`.3`) הוא ה-Standby ומחלק ‎`.131–.254`.)

---

## חלק 1 — קודם מבינים (בשפה פשוטה)

### 1.1 למה המחלקות עדיין לא יכולות לדבר
הנדסה (‎`10.10.16.0/24`, ‏VLAN 10) וכספים (‎`10.10.17.0/24`, ‏VLAN 20) הם חדרים שונים **וגם**
רחובות שונים. כדי לעבור בין רחובות צריך **נתב**. מתגי ה-distribution שלנו הם מתגי שכבה 3 —
*יש* בתוכם נתב; פשוט עוד לא הפעלנו אותו.

### 1.2 ‏SVI — הדלת מכל חדר אל הנתב
**‏SVI** ‏(Switched Virtual Interface, מקלידים `interface vlan 10`) הוא פורט נתב וירטואלי
**בתוך** המתג, אחד לכל VLAN. דמיינו שלכל חדר (VLAN) יש דלת למסדרון מרכזי (הנתב). כתובת ה-IP
של ה-SVI היא הכתובת של הדלת הזו.

- ‏`ip routing` — מדליק את "המוח" של הנתב (בלעדיו הדלתות קיימות, אבל אף אחד לא עובר בהן).
- אחרי שהוא דולק, המתג מנתב אוטומטית בין כל ה-SVIים שלו = **ניתוב בין VLANים** ‏(inter-VLAN routing).

### 1.3 ‏HSRP — שתי פקידות קבלה, מספר טלפון אחד
לכל מחשב יש כתובת שער ברירת מחדל **אחת**. אם השער הזה הוא DIST1 ו-DIST1 מת, כל ה-VLAN מנותק
— למרות ש-DIST2 תקין.

**‏HSRP** ‏(Hot Standby Router Protocol) פותר את זה. כמו שתי פקידות קבלה שחולקות **מספר טלפון
אחד**: אחת עונה (**Active**), והשנייה מקשיבה ונכנסת במקומה אם הראשונה הולכת (**Standby**).

<div dir="rtl">

| | ‎DIST1 | ‎DIST2 | ה"וירטואלי" המשותף |
|---|---|---|---|
| ‏IP ב-VLAN 10 | ‎10.10.16.2 | ‎10.10.16.3 | **10.10.16.1** ‏←‏ המחשבים משתמשים בזה |

</div>

- **‏Priority** קובע מי ה-Active (הגבוה מנצח; ברירת מחדל 100). אנחנו נותנים 110 למתג המועדף
  ו-90 לשני.
- **‏Preempt** — כשהמתג המועדף חוזר אחרי תקלה, הוא לוקח בחזרה את התפקיד. בלי preempt הוא היה
  נשאר Standby לתמיד.
- **‏`standby version 2`** — הגרסה החדשה (יותר קבוצות, תמיכה ב-IPv6). שני הצדדים חייבים להתאים.
- אנחנו ממספרים כל **קבוצת** HSRP ‏(group) כמו ה-VLAN שלה (VLAN 10 ‏←‏ קבוצה 10): קל לקריאה.

**מתאימים את HSRP ל-Spanning Tree.** בשלב 04 ‏DIST1 נהיה הבוס (STP root) של VLAN 10. עכשיו
DIST1 הוא גם ה-HSRP Active של VLAN 10. כך מסגרת ממחשב עולה ישר למתג שמנתב אותה — הדרך הקצרה
ביותר. (‏DIST2 עושה אותו דבר עבור VLAN 20 ו-120.)

### 1.4 ‏DHCP — כתובות אוטומטיות
להקליד IP ב-50 מחשבים זה איטי ומלא טעויות. **שרת DHCP** מחלק הגדרות IP אוטומטית — כמו קבלה
במלון שנותנת לכל אורח מספר חדר פנוי, ואיתו את הסיסמה ל-WiFi (השער) ואת ספר הטלפונים (DNS).

השיחה כוללת 4 הודעות — זכרו **DORA**:

<div dir="rtl">

| | הודעה | משמעות |
|---|---|---|
| ‎D | **‏Discover** (מחשב ‏←‏ כולם) | "יש פה שרת DHCP?" |
| ‎O | **‏Offer** (שרת ‏←‏ מחשב) | "אתה יכול לקבל את 10.10.16.11" |
| ‎R | **‏Request** (מחשב ‏←‏ שרת) | "כן בבקשה, אני לוקח את 10.10.16.11" |
| ‎A | **‏Acknowledge** (שרת ‏←‏ מחשב) | "היא שלך. שער .1, ‏DNS ‏10.10.200.11" |

</div>

ההגדרות ב-**pool** ‏(מאגר) של DHCP:
- ‏`network` — לאיזו רשת המאגר נותן שירות
- ‏`default-router` — השער (אנחנו נותנים את ה-‎`.1` ה**וירטואלי** של HSRP, כדי שישרוד תקלות)
- ‏`dns-server` — שרת השמות (הוא יגיע בשלב 11)
- ‏`ip dhcp excluded-address` — כתובות שהשרת **אף פעם** לא מחלק

**‏Split scope (יתירות ב-DHCP).** שני מתגי ה-distribution מריצים DHCP לאותן רשתות, אבל מחלקים
**חצאים שונים**, כך שהם אף פעם לא נותנים את אותה כתובת פעמיים, ואם אחד מת השני עדיין נותן שירות:

<div dir="rtl">

| טווח | משמש עבור |
|---|---|
| ‎.1 – .10 | שמורות: שער (.1), ‏DIST1 ‏(.2), ‏DIST2 ‏(.3), מדפסות, ציוד |
| ‎.11 – .130 | ‏DIST1 מחלק אותן |
| ‎.131 – .254 | ‏DIST2 מחלק אותן |

</div>

<div dir="rtl">

> בחיפה DHCP רץ על **ציוד הניתוב** (מתגי שכבה 3). משרד החינוך דורש DHCP על נתבים בסניף אחד
> ועל שרת בסניף אחר (דרישה 22.11) — ירושלים משתמשת בשרת (שלב 13).

</div>

---

## חלק 2 — הכנה
‏**File → Open** ‏←‏ `my-work/step04.pkt` ‏←‏ **File → Save As** ‏←‏ `my-work/step05.pkt`.

---

## חלק 3 — בונים
אין מה לבנות — בשלב הזה אין מכשירים או כבלים חדשים. הכול קורה ב-CLI.

---

## חלק 4 — מגדירים (הקלידו כל שורה)

### 4.1 ‏SWL3-HFA-A-DIST1 — ניתוב + שערים (Active עבור 10, ‏30, ‏99, ‏110)
```
enable
configure terminal
! switch the router brain on
ip routing

interface vlan 10
 description GW ENGINEERING
 ip address 10.10.16.2 255.255.255.0
 standby version 2
 standby 10 ip 10.10.16.1
 standby 10 priority 110
 standby 10 preempt
 no shutdown
interface vlan 20
 description GW FINANCE
 ip address 10.10.17.2 255.255.255.0
 standby version 2
 standby 20 ip 10.10.17.1
 standby 20 priority 90
 standby 20 preempt
 no shutdown
interface vlan 30
 description GW PRINTERS-A
 ip address 10.10.18.2 255.255.255.0
 standby version 2
 standby 30 ip 10.10.18.1
 standby 30 priority 110
 standby 30 preempt
 no shutdown
interface vlan 99
 description GW MGMT-A
 ip address 10.10.19.2 255.255.255.0
 standby version 2
 standby 99 ip 10.10.19.1
 standby 99 priority 110
 standby 99 preempt
 no shutdown
interface vlan 110
 description GW WIFI-EMP
 ip address 10.10.20.2 255.255.255.0
 standby version 2
 standby 110 ip 10.10.20.1
 standby 110 priority 110
 standby 110 preempt
 no shutdown
interface vlan 120
 description GW WIFI-GUEST
 ip address 10.10.21.2 255.255.255.0
 standby version 2
 standby 120 ip 10.10.21.1
 standby 120 priority 90
 standby 120 preempt
 no shutdown
 exit
```
ההערה אומרת: מדליקים את "המוח" של הנתב.
תראו הודעות כמו ‎`%HSRP-6-STATECHANGE: Vlan10 Grp 10 state Standby -> Active`.

‏DHCP ב-DIST1 — הוא מחלק ‎`.11 – .130`, ולכן מחריג את ‎`.1 – .10` ואת ‎`.131 – .254`:
```
ip dhcp excluded-address 10.10.16.1 10.10.16.10
ip dhcp excluded-address 10.10.16.131 10.10.16.254
ip dhcp excluded-address 10.10.17.1 10.10.17.10
ip dhcp excluded-address 10.10.17.131 10.10.17.254
ip dhcp excluded-address 10.10.20.1 10.10.20.10
ip dhcp excluded-address 10.10.20.131 10.10.20.254
ip dhcp excluded-address 10.10.21.1 10.10.21.10
ip dhcp excluded-address 10.10.21.131 10.10.21.254

ip dhcp pool HFA-ENGINEERING
 network 10.10.16.0 255.255.255.0
 default-router 10.10.16.1
 dns-server 10.10.200.11
 domain-name intel.lab
ip dhcp pool HFA-FINANCE
 network 10.10.17.0 255.255.255.0
 default-router 10.10.17.1
 dns-server 10.10.200.11
 domain-name intel.lab
ip dhcp pool HFA-WIFI-EMP
 network 10.10.20.0 255.255.255.0
 default-router 10.10.20.1
 dns-server 10.10.200.11
 domain-name intel.lab
ip dhcp pool HFA-WIFI-GUEST
 network 10.10.21.0 255.255.255.0
 default-router 10.10.21.1
 dns-server 200.1.100.10
 end
copy running-config startup-config
```

<div dir="rtl">

> האורחים מקבלים את ה-DNS של **ספק האינטרנט** ‏(200.1.100.10), אף פעם לא את ה-DNS הפנימי שלנו.
> שני שרתי ה-DNS נבנים מאוחר יותר (שלבים 11–12) — עד אז שמות לא יתורגמו לכתובות; כתובות IP עובדות.

</div>

<div dir="rtl">

> אין מאגר ל-VLAN 30 (מדפסות) ול-VLAN 99 (ניהול): למכשירים האלה יש כתובות **קבועות**.

</div>

### 4.2 ‏SWL3-HFA-A-DIST2 — ניתוב + שערים (Active עבור 20, ‏120)
```
enable
configure terminal
ip routing

interface vlan 10
 description GW ENGINEERING
 ip address 10.10.16.3 255.255.255.0
 standby version 2
 standby 10 ip 10.10.16.1
 standby 10 priority 90
 standby 10 preempt
 no shutdown
interface vlan 20
 description GW FINANCE
 ip address 10.10.17.3 255.255.255.0
 standby version 2
 standby 20 ip 10.10.17.1
 standby 20 priority 110
 standby 20 preempt
 no shutdown
interface vlan 30
 description GW PRINTERS-A
 ip address 10.10.18.3 255.255.255.0
 standby version 2
 standby 30 ip 10.10.18.1
 standby 30 priority 90
 standby 30 preempt
 no shutdown
interface vlan 99
 description GW MGMT-A
 ip address 10.10.19.3 255.255.255.0
 standby version 2
 standby 99 ip 10.10.19.1
 standby 99 priority 90
 standby 99 preempt
 no shutdown
interface vlan 110
 description GW WIFI-EMP
 ip address 10.10.20.3 255.255.255.0
 standby version 2
 standby 110 ip 10.10.20.1
 standby 110 priority 90
 standby 110 preempt
 no shutdown
interface vlan 120
 description GW WIFI-GUEST
 ip address 10.10.21.3 255.255.255.0
 standby version 2
 standby 120 ip 10.10.21.1
 standby 120 priority 110
 standby 120 preempt
 no shutdown
 exit
```
‏DHCP ב-DIST2 — הוא מחלק ‎`.131 – .254`, ולכן מחריג את ‎`.1 – .130`:
```
ip dhcp excluded-address 10.10.16.1 10.10.16.130
ip dhcp excluded-address 10.10.17.1 10.10.17.130
ip dhcp excluded-address 10.10.20.1 10.10.20.130
ip dhcp excluded-address 10.10.21.1 10.10.21.130

ip dhcp pool HFA-ENGINEERING
 network 10.10.16.0 255.255.255.0
 default-router 10.10.16.1
 dns-server 10.10.200.11
 domain-name intel.lab
ip dhcp pool HFA-FINANCE
 network 10.10.17.0 255.255.255.0
 default-router 10.10.17.1
 dns-server 10.10.200.11
 domain-name intel.lab
ip dhcp pool HFA-WIFI-EMP
 network 10.10.20.0 255.255.255.0
 default-router 10.10.20.1
 dns-server 10.10.200.11
 domain-name intel.lab
ip dhcp pool HFA-WIFI-GUEST
 network 10.10.21.0 255.255.255.0
 default-router 10.10.21.1
 dns-server 200.1.100.10
 end
copy running-config startup-config
```

### 4.3 מתגי ה-access — כתובת ניהול
מתגי ה-access הם מתגי שכבה 2: הם לא מנתבים. אבל אנחנו רוצים להגיע אליהם דרך הרשת (SSH
בשלב 07), ולכן כל אחד מקבל כתובת IP **אחת** ב-VLAN הניהול 99, ושער (כמו מחשב).

**‏SW-HFA-A-ACC1:**
```
enable
configure terminal
interface vlan 99
 description MANAGEMENT
 ip address 10.10.19.11 255.255.255.0
 no shutdown
 exit
ip default-gateway 10.10.19.1
end
copy running-config startup-config
```
**‏SW-HFA-A-ACC2:** אותו דבר, עם `ip address 10.10.19.12 255.255.255.0`.

### 4.4 המחשבים ‏←‏ DHCP
בכל **מחשב משתמש** ‏(ENG-01/02/03, ‏FIN-01/02/03): לחיצה ‏←‏ **Desktop** ‏←‏ **IP Configuration**
‏←‏ בחרו **DHCP**. אחרי כמה שניות תראו `DHCP request successful` והשדות מתמלאים לבד. (אם אתם
רואים `DHCP failed. APIPA is being used`, לחצו **Fast Forward Time** ולחצו שוב על **DHCP**.)

נשארים **סטטיים**: המדפסת (10.10.18.10, שער 10.10.18.1) ומחשב המנהל (10.10.19.100, שער
10.10.19.1).

### 4.5 מה הפקודות החדשות אומרות

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`ip routing` | "הדלק את הנתב שבתוך המתג הזה" |
| ‎`interface vlan 10` | "הדלת של הנתב לחדר 10" ‏(SVI) |
| ‎`ip address 10.10.16.2 255.255.255.0` | הכתובת של הדלת הזו עצמה |
| ‎`standby version 2` | להשתמש ב-HSRP גרסה 2 |
| ‎`standby 10 ip 10.10.16.1` | "בקבוצת HSRP מספר 10, אנחנו חולקים את מספר הטלפון ‎.1" |
| ‎`standby 10 priority 110` | "אני מעדיף להיות זה שעונה" (הגבוה מנצח) |
| ‎`standby 10 preempt` | "כשאני חוזר, אני לוקח בחזרה את התפקיד שלי" |
| ‎`ip dhcp excluded-address A B` | "אף פעם אל תחלק את הכתובות מ-A עד B" |
| ‎`ip dhcp pool NAME` | מתחיל רשימת הגדרות לחלוקה |
| ‎`network` / `default-router` / `dns-server` | איזו רשת / איזה שער / איזה DNS המחשבים מקבלים |
| ‎`ip default-gateway 10.10.19.1` | במתג שכבה 2: לאן לשלוח את תעבורת הניהול של המתג עצמו |

</div>

---

## חלק 5 — בודקים את העבודה

### 5.1 ‏HSRP
ב-**DIST1**: `show standby brief`
```
                     P indicates configured to preempt.
Interface   Grp  Pri P State    Active          Standby         Virtual IP
Vl10        10   110 P Active   local           10.10.16.3      10.10.16.1
Vl20        20   90  P Standby  10.10.17.3      local           10.10.17.1
Vl30        30   110 P Active   local           10.10.18.3      10.10.18.1
Vl99        99   110 P Active   local           10.10.19.3      10.10.19.1
Vl110       110  110 P Active   local           10.10.20.3      10.10.20.1
Vl120       120  90  P Standby  10.10.21.3      local           10.10.21.1
```
✅ ‏Active עבור 10/30/99/110, ‏Standby עבור 20/120. ‏DIST2 מציג את ההפך.

### 5.2 טבלת הניתוב
ב-**DIST1**: `show ip route`
```
C    10.10.16.0/24 is directly connected, Vlan10
C    10.10.17.0/24 is directly connected, Vlan20
...
```
‏`C` = ‏**C**onnected (מחובר ישירות): המתג מכיר כל VLAN כי יש לו דלת (SVI) בכל אחד.

### 5.3 ‏DHCP
ב-**DIST1**: `show ip dhcp binding` ‏←‏ כתובות בין ‎.11 ל-‎.130 עם כתובות ה-MAC של המחשבים.
ב-**DIST2**: `show ip dhcp binding` ‏←‏ אולי כמה כתובות ‎.131 ומעלה (מי שענה ראשון).

במחשב ‏←‏ Command Prompt ‏←‏ `ipconfig /all`:
```
   IPv4 Address......: 10.10.16.11
   Subnet Mask.......: 255.255.255.0
   Default Gateway...: 10.10.16.1
   DHCP Servers......: 10.10.16.2
   DNS Servers.......: 10.10.200.11
```

### 5.4 בדיקות ping

<div dir="rtl">

| מאיפה | מקלידים | צפוי |
|---|---|---|
| מחשב ENG | ‎`ping 10.10.16.1` | ✅ השער שלו |
| מחשב ENG | ‏`ping` לכתובת של מחשב FIN | ✅ **הניתוב בין VLANים עובד!** |
| מחשב ENG | ‏`ping 10.10.18.10` (מדפסת) | ‎✅ |
| מחשב ENG | ‏`tracert` למחשב FIN | הקפיצה הראשונה ‎`10.10.16.2` ‏(DIST1 — ה-Active של VLAN 10) |
| ‎PC-HFA-ADMIN-01 | ‏`ping 10.10.19.11` ו-‎`10.10.19.12` | ✅ כתובות הניהול של מתגי ה-access |

</div>

### 5.5 בדיקת כשל — HSRP בפעולה
נגרום לשער של DIST1 ב-VLAN 10 ליפול, ונראה איך DIST2 נכנס במקומו.
1. ב-**מחשב ENG**: `ping -t` ל-**מחשב FIN** (ping רציף).
2. ב-**DIST1**, כבו את הדלת שלו ל-VLAN 10:
```
configure terminal
interface vlan 10
 shutdown
 end
```
3. הסתכלו על ה-ping: כמה שורות timeout (עד 10 שניות — זמן ה-hold של HSRP), ואז התשובות
   ממשיכות — ‏DIST2 לקח את ה-‎`.1`.
4. ב-**DIST2**: `show standby brief` ‏←‏ עכשיו הוא **Active** גם עבור קבוצה 10.
5. ב**מחשב ENG** אחר ‏←‏ Command Prompt: `ipconfig /release`, ואז `ipconfig /renew` ‏←‏ תקבלו
   כתובת **‎.131 ומעלה** — מ-DIST2, כי DIST1 לא שומע עכשיו את VLAN 10. ה-split scope עובד!
6. ב-**DIST1**, פתחו שוב את הדלת:
```
configure terminal
interface vlan 10
 no shutdown
 end
```
   אחרי כמה שניות `show standby brief` ב-DIST1 ‏←‏ שוב **Active** עבור קבוצה 10 — זה ה-**preempt**.
7. עצרו את ה-ping עם **Ctrl+C**.

---

## חלק 6 — שומרים
‏`copy running-config startup-config` בכל 4 המתגים ‏←‏ **File → Save**.

## נקודת ביקורת
- [ ] ‏`show standby brief` נכון בשני מתגי ה-DIST
- [ ] מחשבי המשתמשים מקבלים כתובות DHCP עם השער ‎`.1`
- [ ] פינג הנדסה ↔ כספים עובד
- [ ] בדיקת הכשל עברה (ה-ping שורד את נפילת השער של DIST1 ב-VLAN 10; ה-preempt מחזיר אותו)

## אם משהו לא עובד

<div dir="rtl">

| בעיה | פתרון |
|---|---|
| ה-SVI במצב `down/down` ‏(`show ip interface brief`) | ה-VLAN לא קיים במתג הזה, או שאף פורט/trunk לא מעביר אותו. ‏`show vlan brief`, ‏`show interfaces trunk` |
| פינג בין VLANים נכשל, אבל כל VLAN מגיע לשער שלו | שכחתם `ip routing` |
| שני המתגים אומרים **Active** עבור אותה קבוצה | ה-`standby version` שונה, או שה-VLAN לא עובר ביניהם (בדקו את רשימת ה-VLANים המותרים ב-trunk של Po1) |
| המחשבים מקבלים ‎`169.254.x.x` ‏(APIPA) | אין תשובת DHCP: שגיאת כתיב ב-`network` של המאגר, כל הכתובות מוחרגות, או שהפורט של המחשב ב-VLAN הלא נכון. לחצו Fast Forward Time ונסו שוב |
| המחשב מקבל כתובת אבל בלי שער | חסר `default-router` במאגר |

</div>

## אתגר
שאלה על חלוקת עומס: התעבורה של VLAN 10 עוברת דרך DIST1, ושל VLAN 20 דרך DIST2. דמיינו שהפכתם
את DIST1 ל-HSRP Active עבור VLAN 20, **אבל** DIST2 נשאר ה-STP root של VLAN 20. שרטטו את הדרך
שמחשב FIN שמחובר ל-ACC1 עובר כדי להגיע לשער שלו. למה היא גרועה יותר?

<details dir="rtl"><summary>תשובה</summary>

מחשב ‏←‏ ACC1 ‏←‏ (STP מעביר לכיוון ה-root, ‏DIST2) ‏←‏ DIST2 ‏←‏ Po1 ‏←‏ DIST1 ‏(HSRP Active) ‏←‏ מנותב.
המסגרת חוצה את ה-EtherChannel סתם: קפיצה מיותרת, והקישור בין מתגי ה-DIST נושא תעבורה שלא
אמור לשאת. הכלל: **HSRP Active = STP root**, לכל VLAN.
</details>

---

## 🛠 הפרויקט שלכם

עשיתם את השלב הזה על הדוגמה של אינטל. עכשיו עשו אותו שוב בפרויקט **שלכם**, עם הערכים
מהתוכנית **שלכם** (`my-project/plan.md`). הפקודות זהות — רק הערכים משתנים.

<div dir="rtl">

| בדוגמה | בפרויקט שלכם — לוקחים מ |
|---|---|
| ‏SVIים ‎`.2` / ‎`.3`, שער וירטואלי ‎`.1` | תוכנית, חלק ד (רשתות המשנה שלכם, אותו כלל ‎`.1/.2/.3`) |
| מספר קבוצת HSRP = מספר ה-VLAN | שומרים על הכלל, עם מספרי ה-VLAN **שלכם** |
| ה-primary של HSRP ‏(priority + preempt) לכל VLAN | תוכנית, חלק ד (עמודת ה"ראשי" — אותו מתג כמו ה-STP root משלב 04) |
| מאגרי DHCP ‏`HFA-ENGINEERING`… והכתובות המוחרגות | שמות מאגרים משלכם ‎`<SITE>-<DEPT>`‎, רשתות המשנה שלכם, הטווח השמור שלכם |
| ‏DHCP על מתגי שכבה 3 | תוכנית, חלק ה (שורת ה-DHCP) — משרד החינוך דורש DHCP על נתבים/שכבה 3 באתר אחד ועל שרת באתר אחר (דרישה 22.11) |

</div>

**בדיקה:** מחשבים במצב DHCP מקבלים כתובת מרשת המשנה **שלכם** עם השער ‎`.1`; פינג בין שתיים
מהמחלקות שלכם עובד; כבו את ה-SVI של המתג ה-primary ‏(`shutdown`) — ה-ping ממשיך לעבוד.

💾 שמרו בשם `my-project/step05.pkt`.

---

## 🎓 מסבירים לבוחן

בבחינה, הבוחן מצביע על הפרויקט **שלכם** ומבקש **להסביר** ו**להראות**. תרגלו כל שאלה
**בקול**, ואז הראו את התשובה בפרויקט שלכם — לא בדוגמה. כסו את התשובה, ענו בעצמכם, ורק אז
פתחו והשוו.

‏★1–★3 = שאלה ממאגר השאלות של משרד החינוך (רמת קושי 1–3).
‏◆ = לא במאגר, אבל בוחנים שואלים אותה לעיתים קרובות.

**1. ★2 מהו SVI ומדוע משתמשים בו? הראה לי היכן הגדרת SVI.**

<details dir="rtl"><summary>תשובה</summary>

‏Switch Virtual Interface — ממשק שכבה 3 וירטואלי עבור VLAN ‏(`interface vlan 10`) במתג שכבה 3.
הוא השער של אותו VLAN ומנתב בין VLANים בתוך המתג, מהר, בלי נתב חיצוני.

**איפה מראים:** `show ip interface brief`, `show running-config interface vlan 10`
</details>

**2. ★1 מהו נתב על מקל (router-on-a-stick)? איזו בעיה הוא פותר? הצג את הפקודות שלו.**

<details dir="rtl"><summary>תשובה</summary>

ממשק נתב אחד שמחובר ל-trunk ומחולק לתתי-ממשקים, אחד לכל VLAN (`interface g0/0.10` ‏←‏
`encapsulation dot1Q 10` ‏←‏ `ip address …`‎). הוא נותן ניתוב בין VLANים עם פורט נתב אחד בלבד.
**בפרויקט הזה הניתוב בין ה-VLANים נעשה עם SVIים במתגי שכבה 3** (מהיר יותר, בלי צוואר בקבוק של
קישור אחד) — אמרו את זה, והסבירו את הנתב על מקל כחלופה. אם בפרויקט שלכם משתמשים בו איפשהו,
הראו אותו שם.

**איפה מראים:** ה-SVIים שלכם: `show ip interface brief`
</details>

**3. ★1 מהו פרוטוקול HSRP? מהם היתרונות של השימוש בו?**

<details dir="rtl"><summary>תשובה</summary>

‏Hot Standby Router Protocol ‏(Cisco): שני נתבים או יותר חולקים **כתובת IP וכתובת MAC
וירטואליות** אחת, שבה המחשבים משתמשים כשער. אם הנתב ה-Active נופל, ה-Standby לוקח את הכתובת
הווירטואלית — המחשבים לא מרגישים. היתרון: יתירות לשער בלי לשנות שום דבר במחשבים.

**איפה מראים:** `show standby brief`
</details>

**4. ★2 איך עובד HSRP? מה התפקיד של ה-Active Router ושל ה-Standby Router?**

<details dir="rtl"><summary>תשובה</summary>

הנתבים באותה קבוצה שולחים הודעות hello. ה-**Active** עונה בשם ה-IP/MAC הווירטואליים ומעביר את
התעבורה. ה-**Standby** מקשיב ל-hello של ה-Active ונכנס במקומו אם הן נפסקות. השאר נשארים
במצב Listen.

**איפה מראים:** `show standby brief` ‏←‏ העמודה State
</details>

**5. ★2 מהם זמני ה-hello וה-hold של HSRP? מה קורה כשה-Active נופל?**

<details dir="rtl"><summary>תשובה</summary>

‏Hello כל 3 שניות, ‏hold ‏10 שניות. אם ה-Standby לא שומע hello במשך 10 שניות, הוא הופך ל-Active,
לוקח את ה-IP וה-MAC הווירטואליים, ונבחר Standby חדש. המחשבים ממשיכים עם אותו שער.

**איפה מראים:** כבו את ה-SVI של ה-Active (`shutdown`) והריצו ping רציף ממחשב (בדיקה 5.5).
</details>

**6. ★2 כיצד נבחר ה-Active? איך קובעים איזה נתב יהיה ה-Active?**

<details dir="rtl"><summary>תשובה</summary>

ה-priority הגבוה ביותר מנצח (ברירת מחדל 100); בשוויון — כתובת ה-IP הגבוהה ביותר. מגדירים
`standby 10 priority 110` ו-`standby 10 preempt` בנתב שצריך להיות Active.

**איפה מראים:** `show standby` ‏←‏ Priority, ‏Preemption
</details>

**7. ★2 הסבר את המשמעות של הפקודה preempt.**

<details dir="rtl"><summary>תשובה</summary>

נתב עם priority גבוה יותר לוקח בחזרה את תפקיד ה-Active ברגע שהוא חוזר לפעול. בלי preempt,
הנתב שהוא Active נשאר Active גם אם נתב טוב יותר חוזר.

**איפה מראים:** `show standby` ‏←‏ "Preemption enabled"
</details>

**8. ★2 מהם מצבי ה-HSRP?**

<details dir="rtl"><summary>תשובה</summary>

‏Initial ‏←‏ Learn ‏←‏ Listen ‏←‏ Speak ‏←‏ Standby ‏←‏ Active.

**איפה מראים:** `show standby`
</details>

**9. ★2 לאיזו קבוצת (GROUP) HSRP שייכים הנתבים בסניף? מה המשמעות של קבוצה?**

<details dir="rtl"><summary>תשובה</summary>

קבוצה = הנתבים שחולקים כתובת IP וירטואלית אחת. בפרויקט הזה מספר הקבוצה שווה למספר ה-VLAN
(‏VLAN 10 ‏←‏ קבוצה 10), קבוצה אחת לכל VLAN.

**איפה מראים:** `show standby brief` ‏←‏ העמודה Grp
</details>

**10. ★2 מה תפקידה של הפקודה track והיכן מגדירים אותה?**

<details dir="rtl"><summary>תשובה</summary>

היא עוקבת אחרי ממשק (בדרך כלל הקישור כלפי מעלה) ומורידה את ה-priority של HSRP אם הוא נופל,
כך שהנתב השני (עם preempt) הופך ל-Active. מגדירים אותה בנתב ה-Active, תחת ה-SVI:
`standby 10 track <uplink> 20`. **הדוגמה לא משתמשת ב-track** — הסבירו אותה, והוסיפו אותה
לפרויקט שלכם אם אתם רוצים שהשער יעבור למתג שהקישור שלו כלפי מעלה עובד.

**איפה מראים:** —
</details>

**11. ★2 אם הנתב הזה קורס, מה קורה מבחינת ניתוב אל מחוץ לסניף? איזה פרוטוקול אחראי על היתירות?**

<details dir="rtl"><summary>תשובה</summary>

‏HSRP מעביר את השער למתג השני תוך זמן ה-hold ‏(10 שניות לכל היותר), כך שהמחשבים ממשיכים לשלוח.
פרוטוקול הניתוב (OSPF/EIGRP) מוריד את הקישורים של הנתב שנפל ומחשב מחדש את הנתיבים אל מחוץ
לסניף.

**איפה מראים:** `show standby brief`, ו-`show ip route` אחרי כיבוי המתג.
</details>

**12. ★2 מה גורם ל-HSRP לעבור ממצב Active למצב Standby?**

<details dir="rtl"><summary>תשובה</summary>

הנתב נופל או שהממשק שלו נופל; ממשק שנמצא במעקב (track) מוריד את ה-priority שלו מתחת לזה של
הנתב השני (שיש לו preempt); נתב עם priority גבוה יותר ו-preempt עולה; או שמשנים את ה-priority
ידנית.

**איפה מראים:** —
</details>

**13. ★3 איך HSRP יכול לספק יתירות לרשת ה-LAN ולרשת ה-WAN?**

<details dir="rtl"><summary>תשובה</summary>

‏LAN: שני שערים לכל VLAN — אם מתג אחד מת, השני עונה. ‏WAN: עוקבים (track) אחרי ממשק ה-WAN/הקישור
כלפי מעלה, כך שתפקיד ה-Active עובר לנתב שקישור ה-WAN שלו עדיין עובד.

**איפה מראים:** —
</details>

**14. ★3 איך אפשר לבצע load balancing בין הנתבים בהגדרת HSRP?**

<details dir="rtl"><summary>תשובה</summary>

משתמשים בכמה קבוצות עם Active שונה. בפרויקט הזה DIST1 הוא Active עבור חלק מה-VLANים ו-DIST2
עבור האחרים, כך ששני המתגים מעבירים תעבורה.

**איפה מראים:** `show standby brief` בשני מתגי ה-distribution
</details>

**15. ★1 כיצד מקבלים המחשבים ברשת שלך את כתובות ה-IP שלהם?**

<details dir="rtl"><summary>תשובה</summary>

מ-DHCP: המחשב שולח Discover לכולם ‏←‏ השרת שולח Offer ‏←‏ המחשב שולח Request ‏←‏ השרת שולח Ack
‏(DORA). המחשב מקבל IP, מסיכה, שער ו-DNS.

**איפה מראים:** מחשב ‏←‏ IP Configuration ‏←‏ DHCP; ‏`ipconfig /all`
</details>

**16. ★1 הצג את הטבלה שמראה את הקשר בין הכתובת הפיזית (MAC) של ההתקן לכתובת ה-IP שהוא קיבל מהשרת.**

<details dir="rtl"><summary>תשובה</summary>

במכשיר שהוא שרת ה-DHCP (כאן מתג שכבה 3): טבלת ה-binding.

**איפה מראים:** `show ip dhcp binding`
</details>

**17. ★2 הראה את ההגדרות ב-running-config שקשורות לשירותי ה-DHCP שהגדרת, והסבר אותן.**

<details dir="rtl"><summary>תשובה</summary>

‏`ip dhcp excluded-address` (כתובות ש-DHCP לא מחלק — שערים, שרתים), ‏`ip dhcp pool NAME` ‏←‏
‏`network` (הרשת), ‏`default-router` (השער ‎`.1`), ‏`dns-server`.

**איפה מראים:** `show running-config` ‏←‏ גללו (רווח) עד שורות ה-`ip dhcp`
</details>

---

## 🔁 עושים שוב — בלי המדריך

הבוחן יכול לבקש מכם להגדיר משהו שוב, מולו. תצליחו רק אם עשיתם את זה **בלי המדריך** לפני כן.
עשו את התרגיל הזה בפרויקט שלכם:

בעותק של קובץ שלב 05 הגמור שלכם, מחקו את ה-SVIים, שורות ה-HSRP ומאגרי ה-DHCP של VLAN **אחד**.
בלי העמוד הזה, בנו אותם מחדש מתוך התוכנית שלכם בשני מתגי ה-distribution. יעד: **‏10 דקות לכל
VLAN**. אחר כך הראו לבוחן: מחשב שמקבל כתובת ב-DHCP, ‏`show standby brief`, ו-ping רציף ששורד
כיבוי של השער ה-Active ‏(`interface vlan <x>`‎ ‏←‏ `shutdown` במתג ה-Active).

---

## 👩‍🏫 הערות למורה
- **שיעור 1 (90 דקות):** למה VLANים לא יכולים לדבר ‏←‏ SVIים כ"דלתות לנתב" ‏←‏ `ip routing` ‏←‏
  אם הכיתה איטית, הגדירו קודם SVIים ב-DIST1 בלי HSRP ובדקו ping בין VLANים.
- **שיעור 2 (90 דקות):** ‏HSRP (שתי פקידות קבלה, מספר טלפון אחד) ‏←‏ הוספת HSRP בשני המתגים ‏←‏
  ‏`show standby brief` ‏←‏ בדיקת הכשל על המקרן.
- **שיעור 3 (60–90 דקות):** ‏DHCP ו-DORA (הראו במצב Simulation עם הסינון **DHCP**) ‏←‏ split
  scope ‏←‏ מאגרים בשני המתגים ‏←‏ העברת המחשבים ל-DHCP ‏←‏ בדיקת release/renew כשה-SVI של VLAN 10
  ב-DIST1 כבוי.
- **שאלות נפוצות של תלמידים**
  - *"למה DHCP נותן ‎`.1` ולא ‎`.2` כשער?"* — ‏‎`.2` הוא DIST1 עצמו; אם DIST1 מת, ‏‎`.2` מת איתו.
    ‏‎`.1` עובר למתג שחי.
  - *"למה שני שרתי DHCP? הם לא יתנגשו?"* — לא עם split scope: הם אף פעם לא נותנים את אותה כתובת.
  - *"למה מתגי access צריכים IP?"* — רק כדי לנהל אותם מרחוק. הם לא מנתבים.
- **טעויות אופייניות:** שגיאת כתיב ב-IP הווירטואלי של HSRP באחד המתגים (שני "מספרי טלפון"
  שונים); שכחת `no shutdown` ב-SVIים; אותו priority בשני המתגים (ואז ה-IP הגבוה מנצח — לא
  צפוי מבחינת התלמידים).
