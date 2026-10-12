# שלב 06 — אבטחת שכבה 2

<div dir="rtl">

> ⏱ ‏1–2 שיעורים · 🎯 דרישות משרד החינוך 13, ‏16, ‏22.9\
> 📁 מתחילים מ: `my-work/step05.pkt`\
> 💾 שומרים בשם: `my-work/step06.pkt`

</div>

<div dir="rtl">

> ✅ **לפני שמתחילים:** כל הסעיפים בנקודת הביקורת של שלב 05 מסומנים, ועשיתם את
> תרגיל ה-🔁 שלו בפרויקט שלכם. אל תדלגו על שלבים — כל שלב בנוי על הקובץ של השלב הקודם.

</div>

## מה יהיה לכם בסוף השלב
מתגי ה-access מתגוננים מפני ההתקפות הקלאסיות שאדם יכול לבצע רק על ידי **חיבור משהו לשקע
בקיר**: הצפת המתג בכתובות MAC מזויפות, הפעלת שרת DHCP מזויף, חיבור מכשיר לא מוכר. **תנסו את
ההתקפות בעצמכם** ותראו איך ההגנות עוצרות אותן.

---

## חלק 1 — קודם מבינים (בשפה פשוטה)

### 1.1 למה שכבת ה-access צריכה אבטחה
חומות אש מגינות על החברה מפני ה**אינטרנט**. אבל הרבה התקפות מתחילות **מבפנים**: מבקר, עובד
ממורמר, לפטופ נגוע שמחובר לשקע פנוי. מתג ה-access הוא המכשיר הראשון שהם נוגעים בו — ולכן הוא
חייב להגן על עצמו.

### 1.2 ההתקפות וההגנות שלנו

<div dir="rtl">

| התקפה | מה התוקף עושה (בפשטות) | ההגנה שלנו |
|---|---|---|
| ‎**‏MAC flooding** | שולח אלפי מסגרות עם כתובות MAC מזויפות. טבלת ה-MAC של המתג מתמלאת, ומתג מלא שולח כל מסגרת ל**כל** הפורטים, כמו hub ‏←‏ התוקף יכול לקרוא תעבורה של אחרים | **‏Port-security**: רק N כתובות MAC מותרות בכל פורט |
| **שרת DHCP מזויף** (rogue) | מפעיל שרת DHCP משלו שנותן למחשבים את הכתובת **שלו** כשער ‏←‏ כל התעבורה שלהם עוברת דרכו ("man in the middle") | **‏DHCP snooping**: תשובות DHCP מתקבלות רק מפורטים מהימנים (הקישורים כלפי מעלה לשרתים האמיתיים) |
| ‎**‏DHCP starvation** | מבקש כל כתובת פנויה כך שלמחשבים האמיתיים לא נשאר כלום | **הגבלת קצב** ב-DHCP snooping ‏+ port-security |
| **מכשיר לא מוכר** | מנתק את המדפסת ומחבר את הלפטופ שלו | ‏Port-security עם כתובת MAC מותרת **אחת** ‏(sticky) |
| **מתג מתחזה** | מחבר מתג כדי להפוך ל-root של STP | ‏BPDU Guard + Root Guard (נעשה בשלב 04) |
| ‎**‏VLAN hopping** | מנהל משא ומתן על trunk, או מנצל את ה-native VLAN | `mode access`, `nonegotiate`, ‏native VLAN 998 (נעשה בשלבים 02–03) |
| **שקע פנוי** | מתחבר לפורט שלא בשימוש | ‏VLAN חניה + כיבוי (נעשה בשלב 02) |
| **איסוף מידע** | משתמש בהודעות CDP כדי ללמוד את הדגם, התוכנה וה-IP של המתג | `no cdp enable` בפורטים של המשתמשים |

</div>

### 1.3 ‏Port-security — הסלקטור בדלת
‏Port-security הוא סלקטור בכל פורט, עם רשימת אורחים מותרים (כתובות MAC).

<div dir="rtl">

| הגדרה | משמעות |
|---|---|
| ‎`maximum 2` | לכל היותר 2 כתובות MAC שונות בפורט הזה (מחשב + טלפון IP / תחנת עגינה) |
| ‎`mac-address sticky` | לזכור את כתובות ה-MAC הראשונות שמופיעות ולכתוב אותן בהגדרות — בלי להקליד MAC ידנית |
| ‎`violation protect` | ‏MAC לא מוכר ‏←‏ המסגרות שלו נזרקות בשקט |
| ‎`violation restrict` | נזרקות **+ נרשמות ביומן + נספרות** ‏←‏ בזה משתמשים למשתמשים (טעות אחת לא הורגת את הפורט) |
| ‎`violation shutdown` | הפורט נכבה לגמרי (err-disabled) ‏←‏ בזה משתמשים למדפסות ולמחשב המנהל (רק מכשיר אחד אמור להיות שם) |

</div>

### 1.4 ‏DHCP snooping — רק פורטים מהימנים רשאים לחלק כתובות
המתג צופה בכל הודעות ה-DHCP:
- פורטים **לא מהימנים** ‏(untrusted — מחשבים): רשאים *לבקש* כתובת, **אסור** להם *להציע* כתובת. הצעות מזויפות נזרקות.
- פורטים **מהימנים** ‏(trusted — הקישורים כלפי מעלה לכיוון DIST1/DIST2, שרתי ה-DHCP האמיתיים שלנו): מותר להציע.

בזמן הצפייה המתג גם בונה **טבלת binding**: איזה MAC קיבל איזה IP, באיזה פורט. (הגנות אחרות
משתמשות בה, ראו את האתגר.)

### 1.5 המלכודת של "option 82" (למה המחשבים פתאום מקבלים 169.254.x.x)
כש-snooping פועל, המתג מוסיף לבקשות ה-DHCP מידע נוסף שנקרא **option 82**. שרתי ה-DHCP שלנו
(מתגי שכבה 3 עם IOS) רואים option 82 שמגיע ממקום לא צפוי ו**זורקים את הבקשה** ‏←‏ המחשבים לא
מקבלים כתובת. הפתרון במתגי ה-access: `no ip dhcp snooping information option`. זו הטעות מספר 1
בשלב הזה.

---

## חלק 2 — הכנה
‏**File → Open** ‏←‏ `my-work/step05.pkt` ‏←‏ **File → Save As** ‏←‏ `my-work/step06.pkt`.

## חלק 3 — בונים
אין מה לבנות עכשיו (מעבדת ההתקפות בחלק 6 מוסיפה מכשירים באופן זמני).

---

## חלק 4 — מגדירים (הקלידו כל שורה)

### 4.1 ‏SW-HFA-A-ACC1
```
enable
configure terminal

! ---------- DHCP snooping ----------
ip dhcp snooping
ip dhcp snooping vlan 10,20,30,99,110,120
! the option-82 trap (section 1.5)
no ip dhcp snooping information option

! uplinks lead to the real DHCP servers (DIST1/DIST2) -> trusted
interface range gi0/1 - 2
 ip dhcp snooping trust
 exit

! ---------- user ports: Engineering + Finance ----------
interface range fa0/1 - 20
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
 ip dhcp snooping limit rate 10
 no cdp enable
 exit

! ---------- printer port: exactly one device ----------
interface fa0/21
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
 no cdp enable
 exit

! ---------- admin PC port: exactly one device ----------
interface fa0/22
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
 no cdp enable
 end
copy running-config startup-config
```
ההערות בבלוק אומרות: ‏DHCP snooping; המלכודת של option 82 (סעיף 1.5); הקישורים כלפי מעלה
מובילים לשרתי ה-DHCP האמיתיים (DIST1/DIST2) ‏←‏ מהימנים; פורטי משתמשים: הנדסה + כספים; פורט
המדפסת: בדיוק מכשיר אחד; פורט מחשב המנהל: בדיוק מכשיר אחד.

### 4.2 ‏SW-HFA-A-ACC2
```
enable
configure terminal

ip dhcp snooping
ip dhcp snooping vlan 10,20,30,99,110,120
no ip dhcp snooping information option

interface range gi0/1 - 2
 ip dhcp snooping trust
 exit

interface range fa0/1 - 20
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
 ip dhcp snooping limit rate 10
 no cdp enable
 exit

interface fa0/21
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
 no cdp enable
 exit

! ---------- the two access-point ports ----------
! every wireless laptop's MAC appears on the AP's port -> allow many
interface range fa0/22 - 23
 switchport port-security
 switchport port-security maximum 30
 switchport port-security violation restrict
 ip dhcp snooping limit rate 20
 no cdp enable
 end
copy running-config startup-config
```
ההערות אומרות: שני הפורטים של נקודות הגישה — כתובת ה-MAC של כל לפטופ אלחוטי מופיעה בפורט של
נקודת הגישה ‏←‏ מאפשרים הרבה.

### 4.3 נותנים למתגים ללמוד את כתובות ה-MAC
למידת sticky צריכה תעבורה. ב**כל מחשב**: ‏Desktop ‏←‏ Command Prompt ‏←‏ `ipconfig /renew` (ועשו
ping לשער שלו). המדפסת: עשו לה ping ממחשב (`ping 10.10.18.10`).

### 4.4 מה הפקודות החדשות אומרות

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`ip dhcp snooping` | "התחל לצפות ב-DHCP" |
| ‎`ip dhcp snooping vlan ...`‎ | "…ב-VLANים האלה" |
| ‎`no ip dhcp snooping information option` | "אל תוסיף option 82" (נמנעים מהמלכודת) |
| ‎`ip dhcp snooping trust` | "שרתי DHCP אמיתיים נמצאים מאחורי הפורט הזה" |
| ‎`ip dhcp snooping limit rate 10` | "לכל היותר 10 הודעות DHCP בשנייה מהפורט הזה" (עוצר starvation) |
| ‎`switchport port-security` | "הפעל את הסלקטור" |
| ‎`... maximum 2` / `mac-address sticky` / `violation restrict` | ראו את הטבלה בסעיף 1.3 |
| ‎`no cdp enable` | "אל תספר לפורט הזה מי אני" |

</div>

---

## חלק 5 — בודקים את העבודה

### 5.1 ‏DHCP snooping
ב-**ACC1**: `show ip dhcp snooping`
```
Switch DHCP snooping is enabled
DHCP snooping is configured on following VLANs:
10,20,30,99,110,120
Insertion of option 82 is disabled
Interface                  Trusted    Rate limit (pps)
-----------------------    -------    ----------------
GigabitEthernet0/1         yes        unlimited
GigabitEthernet0/2         yes        unlimited
FastEthernet0/1            no         10
...
```
‏`show ip dhcp snooping binding` ‏←‏ שורה אחת לכל מחשב שקיבל כתובת (MAC, ‏IP, ‏VLAN, פורט).

### 5.2 ‏Port-security
```
show port-security
```
```
Secure Port  MaxSecureAddr  CurrentAddr  SecurityViolation  Security Action
     Fa0/1         2             1               0               Restrict
     Fa0/21        1             1               0               Shutdown
...
```
‏`show port-security interface fa0/1` ‏←‏ `Port Status : Secure-up`.
‏`show running-config | include sticky` ‏←‏ כתובות ה-MAC שנלמדו כתובות עכשיו בהגדרות.

### 5.3 המחשבים עדיין עובדים
בכל מחשב: `ipconfig /release`, ואז `ipconfig /renew` ‏←‏ עדיין מקבל כתובת ✅.
אם לא ‏←‏ סעיף 1.5 / טבלת "אם משהו לא עובד".

---

## חלק 6 — מעבדת התקפות (נסו את ההתקפות!)

### התקפה 1 — שרת DHCP מזויף
1. ‏**End Devices** ‏←‏ גררו **Server** ליד ACC1. שנו את שמו ל-`SRV-ROGUE`.
2. חברו אותו ב-**Copper Straight-Through**: ‏SRV-ROGUE **FastEthernet0** ‏←‏ ‏ACC1 **Fa0/9**
   (פורט פנוי של הנדסה — VLAN 10).
3. ‏SRV-ROGUE ‏←‏ **Desktop → IP Configuration**: ‏IP ‏‎`10.10.16.250`, מסיכה ‎`255.255.255.0`.
4. ‏SRV-ROGUE ‏←‏ לשונית **Services** ‏←‏ **DHCP** (ברשימה משמאל):
   - ‏Service: **On**
   - ‏Default Gateway: ‎`10.10.16.250` (התוקף שולח את עצמו כשער!)
   - ‏Start IP Address: ‎`10.10.16.200`, ‏Subnet Mask ‏‎`255.255.255.0`
   - לחצו **Save**.
5. במחשב של הנדסה: ‏Desktop ‏←‏ IP Configuration ‏←‏ לחצו **Static**, ואז שוב **DHCP**.
6. התוצאה: המחשב מקבל כתובת בין **‎.11 ל-‎.254** עם השער **10.10.16.1** — מ-DIST1/DIST2.
   ההצעות של השרת המזויף **נזרקו** ב-Fa0/9 (פורט לא מהימן). ✅
7. *בונוס:* הפכו זמנית את Fa0/9 למהימן (`interface fa0/9` ‏←‏ `ip dhcp snooping trust`), ובקשו
   שוב כתובת במחשב — עכשיו הוא עלול לקבל ‎`.200` עם השער ‎`.250`: ההתקפה עובדת.
   **הסירו את ה-trust** (`no ip dhcp snooping trust`) מיד.
8. מחקו את SRV-ROGUE (הכלי Delete).

### התקפה 2 — מכשיר לא מוכר בפורט של המדפסת
1. מחקו את הכבל בין **PRN-HFA-A-01** ל-ACC1.
2. גררו **Laptop**, וחברו אותו (Straight-Through) ל-ACC1 **Fa0/21**.
3. הלפטופ שולח מסגרת (תנו לו IP כלשהו, למשל ‎`10.10.18.50`, ועשו ping ל-‎`10.10.18.1`).
4. ‏ACC1 מציג ‎`%PORT_SECURITY-2-PSECURE_VIOLATION` ו-Fa0/21 **נופל** (נורית אדומה).
   ‏`show port-security interface fa0/21` ‏←‏ `Port Status : Secure-shutdown`.
5. שחזור: מחקו את הלפטופ, חברו מחדש את המדפסת ל-Fa0/21, ואז ב-ACC1:
```
configure terminal
interface fa0/21
 shutdown
 no shutdown
 end
```
6. עשו ping למדפסת ממחשב ‏←‏ עובד שוב ✅.

---

## חלק 7 — שומרים
‏`copy running-config startup-config` ב-ACC1 וב-ACC2 (שוב, כי נלמדו כתובות MAC במצב sticky) ‏←‏
**File → Save**.

## נקודת ביקורת
- [ ] ‏Snooping פועל, הקישורים כלפי מעלה מהימנים, option 82 כבוי — בשני מתגי ה-access
- [ ] כל המחשבים עדיין מקבלים כתובות DHCP
- [ ] השרת המזויף לא הצליח לחלק כתובות
- [ ] פורט המדפסת נכבה כשלפטופ תפס את מקומה, ושחזרתם אותו

## אם משהו לא עובד

<div dir="rtl">

| בעיה | פתרון |
|---|---|
| המחשבים מקבלים ‎`169.254.x.x` אחרי השלב הזה | חסר `no ip dhcp snooping information option`, או שהקישורים כלפי מעלה לא מוגדרים `trust` |
| ‎`% Command rejected: Fa0/x is a dynamic port` | הפורט לא מוגדר `switchport mode access` — הגדירו את זה קודם |
| פורט של מחשב אמיתי נכנס להפרה (violation) | יותר מדי כתובות MAC (למשל הזזתם מחשבים). מחקו את כתובות ה-MAC שנלמדו: בפורט `no switchport port-security`, ואז הקלידו שוב את שורות ה-port-security שלו מסעיף 4.1, ואז `shutdown` / `no shutdown` |
| פורט המדפסת למטה אחרי שרק הזזתם את הכבל שלה | ה-sticky זכר את ה-MAC של הפורט הקודם; שחזרו כמו בהתקפה 2 צעד 5 |

</div>

## אתגר (בונוס — בזהירות!)
‏**Dynamic ARP Inspection ‏(DAI)** משתמש בטבלת ה-binding של ה-snooping כדי לזרוק תשובות ARP
מזויפות (ARP poisoning — עוד תרגיל של man-in-the-middle). הפעילו אותו עבור VLAN 10 בלבד
ב-ACC1, בלי לשבור שום דבר. אילו פורטים חייבים להיות מהימנים, ולמה רק VLAN 10?

<details dir="rtl"><summary>תשובה</summary>

<div dir="ltr">

```
configure terminal
ip arp inspection vlan 10
interface range gi0/1 - 2
 ip arp inspection trust
 end
```

</div>

רק VLAN 10, כי כל המכשירים בו משתמשים ב-DHCP — ולכן הם נמצאים בטבלת ה-binding. ‏VLAN 30
(מדפסת עם כתובת קבועה) ו-VLAN 99 (מחשב המנהל עם כתובת קבועה) **לא** נמצאים בטבלה, ולכן DAI היה
זורק את ה-ARP שלהם והם היו מתנתקים (אלא אם כותבים בשבילם ARP ACL). הקישורים כלפי מעלה חייבים
להיות מהימנים, אחרת תשובות ה-ARP של השער (שמגיעות מהקישור כלפי מעלה ולא נמצאות בטבלה) היו
נזרקות.
</details>

---

## 🛠 הפרויקט שלכם

עשיתם את השלב הזה על הדוגמה של אינטל. עכשיו עשו אותו שוב בפרויקט **שלכם**, עם הערכים
מהתוכנית **שלכם** (`my-project/plan.md`). הפקודות זהות — רק הערכים משתנים.

<div dir="rtl">

| בדוגמה | בפרויקט שלכם — לוקחים מ |
|---|---|
| ‏Port-security בפורטים של המשתמשים | פורטי המשתמשים שלכם מתוכנית הפורטים |
| רשימת ה-VLANים של DHCP snooping | תוכנית, חלק ד (ה-VLANים של המשתמשים שלכם) |
| פורטים מהימנים = הקישורים כלפי מעלה ל-DIST1/DIST2 | הקישורים כלפי מעלה שלכם |

</div>

**בדיקה:** חזרו על מעבדת ההתקפות של השלב הזה מול הרשת **שלכם** — ההתקפות חייבות להיחסם.

💾 שמרו בשם `my-project/step06.pkt`.

---

## 🎓 מסבירים לבוחן

בבחינה, הבוחן מצביע על הפרויקט **שלכם** ומבקש **להסביר** ו**להראות**. תרגלו כל שאלה
**בקול**, ואז הראו את התשובה בפרויקט שלכם — לא בדוגמה. כסו את התשובה, ענו בעצמכם, ורק אז
פתחו והשוו.

‏★1–★3 = שאלה ממאגר השאלות של משרד החינוך (רמת קושי 1–3).
‏◆ = לא במאגר, אבל בוחנים שואלים אותה לעיתים קרובות.

**1. ★3 איזו התקפה הקשורה ל-DHCP אתה מכיר, ומה הפתרון? היכן יישמת אותו?**

<details dir="rtl"><summary>תשובה</summary>

**שרת DHCP מזויף (rogue DHCP):** מכשיר של תוקף עונה לבקשות DHCP ונותן את עצמו כשער
(man-in-the-middle). הפתרון: **‏DHCP snooping** — רק פורטים שמסומנים `trust` (הקישורים כלפי מעלה
לכיוון השרת האמיתי) רשאים לשלוח הצעות DHCP; הצעות מכל פורט אחר נזרקות.

**איפה מראים:** `show ip dhcp snooping`, `show running-config interface <uplink>`‎ ‏←‏ `ip dhcp snooping trust`
</details>

**2. ★3 קיימת התקפה שנקראת DHCP starvation. הסבר מהי וכיצד ניתן למנוע אותה. היכן הגדרת את זה בפרויקט?**

<details dir="rtl"><summary>תשובה</summary>

התוקף שולח אלפי בקשות DHCP עם כתובות MAC מזויפות עד שהמאגר מתרוקן; משתמשים אמיתיים לא מקבלים
כתובת (מניעת שירות), ואז שרת מזויף יכול לתת להם שירות. מניעה: **‏port-security** (הגבלת מספר
כתובות ה-MAC בכל פורט) והגבלת קצב ב-DHCP snooping.

**איפה מראים:** `show port-security`, `show port-security interface fa0/1`
</details>

**3. ◆ מה זה port-security? מהם מצבי ה-violation? מה זה `sticky`?**

<details dir="rtl"><summary>תשובה</summary>

הוא מגביל אילו כתובות MAC, וכמה, רשאיות להשתמש בפורט. מצבי violation: ‏`shutdown` (הפורט עובר
ל-err-disabled — ברירת המחדל), ‏`restrict` (זורק ורושם ביומן), ‏`protect` (זורק בשקט). ‏`sticky`
לומד אוטומטית את ה-MAC (או ה-MACים) הראשונים וכותב אותם ב-running-config.

**איפה מראים:** `show port-security interface fa0/1`
</details>

**4. ◆ איך מחזירים לפעולה פורט ש-port-security כיבה?**

<details dir="rtl"><summary>תשובה</summary>

מסירים את הגורם (מנתקים את המכשיר הזר), ואז בממשק: `shutdown` ואחר כך `no shutdown`.

**איפה מראים:** `show interfaces status` ‏←‏ err-disabled
</details>

**5. ◆ מה זה Dynamic ARP Inspection?**

<details dir="rtl"><summary>תשובה</summary>

הוא בודק תשובות ARP מול טבלת ה-binding של DHCP snooping וזורק תשובות מזויפות, וכך עוצר ARP
spoofing (תוקף שטוען שהוא השער).

**איפה מראים:** `show running-config | include arp inspection`
</details>

---

## 🔁 עושים שוב — בלי המדריך

הבוחן יכול לבקש מכם להגדיר משהו שוב, מולו. תצליחו רק אם עשיתם את זה **בלי המדריך** לפני כן.
עשו את התרגיל הזה בפרויקט שלכם:

בעותק של קובץ שלב 06 הגמור שלכם, הסירו את ה-port-security ואת ה-DHCP snooping ממתג access אחד.
בלי העמוד הזה, הגדירו אותם שוב מתוך התוכנית שלכם. יעד: **‏10 דקות**. אחר כך חזרו על מעבדת
ההתקפות של השלב הזה מול הבוחן, והראו שההתקפות נחסמות.

---

## 👩‍🏫 הערות למורה
- **מערך שיעור (כ-90–120 דקות):** ‏25 דק' טבלת ההתקפות — ספרו אותה כסיפורים ("מבקר בחדר
  הישיבות…") ‏←‏ 10 דק' הסבר על הסלקטור ועל פורט מהימן ‏←‏ 30 דק' הגדרות ‏←‏ 10 דק' בדיקות ‏←‏ 30 דק'
  מעבדת התקפות (תלמידים נהנים להיות התוקף).
- **הראו DHCP במצב Simulation** עם הסינון **DHCP**: רואים את ה-OFFER של השרת המזויף מגיע
  ל-ACC1 ונעלם.
- **שאלות נפוצות של תלמידים**
  - *"למה restrict למשתמשים אבל shutdown למדפסת?"* — משתמש עלול לחבר בטעות מכשיר שני באופן
    לגיטימי; אנחנו רושמים את זה בלי להרוס לו את העבודה. פורט של מדפסת אמור לראות רק את המדפסת
    הזו — כל דבר אחר חשוד.
  - *"למה סומכים על הקישורים כלפי מעלה?"* — שרתי ה-DHCP האמיתיים (DIST1/2) נמצאים מאחוריהם.
  - *"התוקף לא יכול פשוט להעתיק את ה-MAC של המדפסת?"* — כן (MAC spoofing). ‏Port-security הוא
    שכבה אחת; רשתות אמיתיות מוסיפות אימות 802.1X. נקודה טובה לדיון בספר הפרויקט.
- **טעויות אופייניות:** המלכודת של option 82; שכחה לשמור אחרי למידת ה-sticky.
