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

## 🗺 המשימות שלכם בשלב הזה
- [ ] **משימה 1** — פותחים את שלב 05 ושומרים בשם שלב 06 (2 דקות)
- [ ] **משימה 2** — ‏ACC1: ‏DHCP snooping ‏(10 דקות)
- [ ] **משימה 3** — ‏ACC1: ‏port-security בפורטים של המשתמשים, המדפסת והמנהל (10 דקות)
- [ ] **משימה 4** — ‏ACC2: אותו דבר + הפורטים של נקודות הגישה (15 דקות)
- [ ] **משימה 5** — נותנים למתגים ללמוד את כתובות ה-MAC, ובודקים (15 דקות)
- [ ] **משימה 6** — התקפה 1: שרת DHCP מזויף (20 דקות)
- [ ] **משימה 7** — התקפה 2: לפטופ לא מוכר בפורט של המדפסת (15 דקות)
- [ ] **משימה 8** — שומרים הכול (2 דקות)
- [ ] **תרגיל** — ‏Dynamic ARP Inspection (בונוס)
- [ ] **🛠 הפרויקט שלכם**

## מה יהיה לכם בסוף השלב
מתגי ה-access מתגוננים מפני ההתקפות הקלאסיות שאדם יכול לבצע רק על ידי **חיבור משהו לשקע
בקיר**: הצפת המתג בכתובות MAC מזויפות, הפעלת שרת DHCP מזויף, חיבור מכשיר לא מוכר. **תנסו את
ההתקפות בעצמכם** ותראו איך ההגנות עוצרות אותן.

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

## משימה 1 — פותחים את שלב 05 ושומרים בשם שלב 06 (איך? ‏←‏ M1)
‏**File → Open** ‏←‏ `my-work/step05.pkt` ‏←‏ **File → Save As** ‏←‏ `my-work/step06.pkt`.

אין מה לבנות עכשיו (מעבדת ההתקפות במשימות 6–7 מוסיפה מכשירים לזמן קצר).

---

## משימה 2 — ‏ACC1: ‏DHCP snooping
👉 **איפה:** ‏**SW-HFA-A-ACC1** ‏←‏ CLI ‏←‏ נכנסים ‏←‏ `SW-HFA-A-ACC1#`‎.

⌨️ מקלידים:
```
configure terminal
ip dhcp snooping
ip dhcp snooping vlan 10,20,30,99,110,120
! the option-82 trap (section 1.5)
no ip dhcp snooping information option

! uplinks lead to the real DHCP servers (DIST1/DIST2) -> trusted
interface range gi0/1 - 2
 ip dhcp snooping trust
 exit
```
🔍 **בודקים עכשיו:** ‏`do show ip dhcp snooping` ‏←‏ `Switch DHCP snooping is enabled`, ושתי שורות
ה-`GigabitEthernet0/x` אומרות `yes` תחת **Trusted**.\
❌ ‏`Insertion of option 82 is enabled` ‏←‏ דילגתם על `no ip dhcp snooping information option`.
הקלידו אותה עכשיו.

---

## משימה 3 — ‏ACC1: ‏port-security בפורטים של המשתמשים, המדפסת והמנהל
👉 **איפה:** ‏ACC1, שורת הפקודה `SW-HFA-A-ACC1(config)#`‎.

### 3א — פורטי המשתמשים: Engineering + Finance (עד 2 מכשירים, רושמים הפרות)
⌨️ מקלידים:
```
interface range fa0/1 - 20
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
 ip dhcp snooping limit rate 10
 no cdp enable
 exit
```

### 3ב — הפורט של המדפסת והפורט של מחשב המנהל: מכשיר אחד בדיוק, נכבה בהפרה
⌨️ מקלידים:
```
interface fa0/21
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
 no cdp enable
 exit
interface fa0/22
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
 no cdp enable
 end
copy running-config startup-config
```
✅ ‏‎`[OK]`‎.\
❌ ‏‎`% Command rejected: Fa0/x is a dynamic port` ‏←‏ בפורט הזה חסר `switchport mode access`
(שלב 02). הוסיפו אותו בפורט, ואז הקלידו שוב את שורות ה-port-security.

---

## משימה 4 — ‏ACC2: אותו דבר + הפורטים של נקודות הגישה
👉 **איפה:** ‏**SW-HFA-A-ACC2** ‏←‏ CLI ‏←‏ נכנסים ‏←‏ `SW-HFA-A-ACC2#`‎.

### 4א — ‏Snooping, משתמשים ומדפסת (כמו ב-ACC1)
⌨️ מקלידים:
```
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
```

### 4ב — שני הפורטים של נקודות הגישה (חדש ב-ACC2)
ה-MAC של כל לפטופ אלחוטי מופיע בפורט של נקודת הגישה ‏←‏ מרשים הרבה.

⌨️ מקלידים:
```
interface range fa0/22 - 23
 switchport port-security
 switchport port-security maximum 30
 switchport port-security violation restrict
 ip dhcp snooping limit rate 20
 no cdp enable
 end
copy running-config startup-config
```
✅ ‏‎`[OK]`‎.

### מה הפקודות החדשות אומרות

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

## משימה 5 — נותנים למתגים ללמוד את כתובות ה-MAC, ובודקים
🧠 **למה:** למידת sticky צריכה תעבורה. פורט לומד MAC רק אחרי שהמכשיר שולח משהו.

### 5א — גורמים לכל מכשיר לדבר
1. ב**כל מחשב משתמש** (6 מחשבים): ‏Desktop ‏←‏ Command Prompt ‏←‏ `ipconfig /renew`, ואז
   ‏`ping` לשער שלו (‎`10.10.16.1` ל-ENG, ‏‎`10.10.17.1` ל-FIN).
2. ב-**PC-HFA-ADMIN-01**: ‏`ping 10.10.19.1`.
3. המדפסת לא יודעת להקליד — **עשו לה פינג** ממחשב: `ping 10.10.18.10`.

✅ כל מחשב קיבל שוב כתובת (`ipconfig /renew` הצליח) וכל פינג ענה.\
❌ מחשב מקבל ‎`169.254.x.x` ‏←‏ ראו סעיף 1.5 ואת טבלת התקלות.

### 5ב — בודקים DHCP snooping
👉 ב-**ACC1**: ‏`show ip dhcp snooping`

✅ אמורים לראות:
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
👉 ‏`show ip dhcp snooping binding` ‏←‏ ✅ שורה לכל מחשב ב-ACC1 שקיבל כתובת (MAC, ‏IP, ‏VLAN, פורט).

### 5ג — בודקים port-security
👉 ב-**ACC1**: ‏`show port-security`

✅ אמורים לראות:
```
Secure Port  MaxSecureAddr  CurrentAddr  SecurityViolation  Security Action
     Fa0/1         2             1               0               Restrict
     Fa0/21        1             1               0               Shutdown
...
```
👉 ‏`show port-security interface fa0/1` ‏←‏ ✅ ‏`Port Status : Secure-up`.\
👉 ‏`show running-config | include sticky` ‏←‏ ✅ כתובות ה-MAC שנלמדו כתובות עכשיו בהגדרות.

### 5ד — שומרים את כתובות ה-MAC שנלמדו
ב-ACC1 **וגם** ב-ACC2: ‏`copy running-config startup-config` (ה-MACים ה-sticky הם שורות חדשות
בהגדרות).

---

## משימה 6 — התקפה 1: שרת DHCP מזויף
🧠 **למה:** להיות התוקף, ולראות איך DHCP snooping עוצר אתכם.

### 6א — בונים את השרת של התוקף
1. ‏**End Devices** ‏←‏ גררו **Server** ליד ACC1. שנו את שמו ל-`SRV-ROGUE` ‏(M4).
2. חברו אותו ב-**Copper Straight-Through**: ‏SRV-ROGUE ‏**FastEthernet0** ‏←‏ ACC1 ‏**Fa0/9**
   (פורט פנוי של Engineering — ‏VLAN 10) ‏(M5).
3. ‏SRV-ROGUE ‏←‏ **Desktop → IP Configuration** ‏←‏ **Static**: ‏IP ‏‎`10.10.16.250`, מסיכה
   ‏‎`255.255.255.0`. סגרו.

### 6ב — מדליקים את שירות ה-DHCP המזויף שלו (איך? ‏←‏ M20)
1. ‏SRV-ROGUE ‏←‏ לשונית **Services** ‏←‏ **DHCP** (ברשימה משמאל).
2. ‏**Service**: לחצו **On**.
3. ‏**Default Gateway**: ‏‎`10.10.16.250` (התוקף שולח את עצמו בתור השער!)
4. ‏**Start IP Address**: ‏‎`10.10.16.200`, ‏**Subnet Mask**: ‏‎`255.255.255.0`.
5. לחצו **Save**. סגרו את החלון.

### 6ג — מנסים
1. ב**מחשב Engineering**: ‏Desktop ‏←‏ IP Configuration ‏←‏ לחצו **Static**, ואז שוב **DHCP**.
2. הסתכלו על הכתובת והשער שהוא קיבל.

✅ המחשב מקבל כתובת בין **‎.11 ל-‎.254** עם שער **10.10.16.1** — מ-DIST1/DIST2. ההצעות של
השרת המזויף **נזרקו** ב-Fa0/9 (פורט לא מהימן).\
❌ המחשב קיבל ‎`.200` עם שער ‎`.250` ‏←‏ ‏Fa0/9 מוגדר מהימן בטעות, או שה-snooping לא פועל
ב-VLAN 10. בדקו `show ip dhcp snooping`.

### 6ד — בונוס: רואים את ההתקפה מצליחה
1. ב-ACC1: ‏`configure terminal` ‏←‏ `interface fa0/9` ‏←‏ `ip dhcp snooping trust` ‏←‏ `end`.
2. חדשו שוב את המחשב (Static ‏←‏ DHCP). עכשיו הוא עלול לקבל ‎`.200` עם שער ‎`.250`: ההתקפה עובדת.
3. **הסירו את ה-trust מייד:** ‏`configure terminal` ‏←‏ `interface fa0/9` ‏←‏
   ‏`no ip dhcp snooping trust` ‏←‏ `end`.
4. חדשו את המחשב עוד פעם ‏←‏ חזרה לכתובת אמיתית עם שער ‎`.1`.

### 6ה — מנקים
מחקו את SRV-ROGUE עם כלי ה-Delete ‏(M7).

---

## משימה 7 — התקפה 2: לפטופ לא מוכר בפורט של המדפסת
1. מחקו את הכבל בין **PRN-HFA-A-01** ל-ACC1 ‏(M7).
2. גררו **Laptop** וחברו אותו (Straight-Through) ל-ACC1 ‏**Fa0/21**.
3. גרמו ללפטופ לשלוח מסגרת: ‏Desktop ‏←‏ IP Configuration ‏←‏ Static IP ‏‎`10.10.18.50`, מסיכה
   ‏‎`255.255.255.0` ‏←‏ Command Prompt ‏←‏ `ping 10.10.18.1`.
4. הסתכלו על ה-CLI של ACC1.

✅ מופיע ‎`%PORT_SECURITY-2-PSECURE_VIOLATION` ו-Fa0/21 יורד (**down** — נקודה אדומה).\
👉 ‏`show port-security interface fa0/21` ‏←‏ ✅ ‏`Port Status : Secure-shutdown`.

5. משחזרים: מחקו את הלפטופ, חברו שוב את המדפסת ל-**Fa0/21** ‏(Straight-Through), ואז ב-ACC1:
```
configure terminal
interface fa0/21
 shutdown
 no shutdown
 end
```
6. עשו פינג למדפסת ממחשב (`ping 10.10.18.10`).

✅ שוב יש תשובות.

---

## משימה 8 — שומרים הכול
‏`copy running-config startup-config` ב-ACC1 וב-ACC2 ‏←‏ **File → Save**.

---

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
| פורט של מחשב אמיתי נכנס להפרה (violation) | יותר מדי כתובות MAC (למשל הזזתם מחשבים). מחקו את כתובות ה-MAC שנלמדו: בפורט `no switchport port-security`, ואז הקלידו שוב את שורות ה-port-security שלו ממשימה 3, ואז `shutdown` / `no shutdown` |
| פורט המדפסת למטה אחרי שרק הזזתם את הכבל שלה | ה-sticky זכר את ה-MAC של הפורט הקודם; שחזרו כמו במשימה 7 צעד 5 |

</div>

---

## 🏋 תרגיל — ‏Dynamic ARP Inspection (בונוס — בזהירות!) ⭐⭐⭐
- 🎯 **המשימה:** ‏**Dynamic ARP Inspection ‏(DAI)** משתמש בטבלת ה-binding של ה-snooping כדי
  לזרוק תשובות ARP מזויפות (ARP poisoning — עוד תרגיל של man-in-the-middle). הפעילו אותו עבור
  **‏VLAN 10 בלבד** ב-ACC1, בלי לשבור שום דבר.
- 📁 **מתחילים מ:** ה-`step06.pkt` שלכם — קודם **Save As** ‏`step06-dai.pkt`.
- 👣 **צעדים:**
  1. החליטו אילו פורטים של ACC1 חייבים להיות **מהימנים** עבור DAI.
  2. הפעילו DAI עבור VLAN 10.
  3. חדשו כתובת במחשב ENG ועשו פינג לשער שלו ולמחשב ENG אחר.
- ✅ **גמרתם כש**הפינגים עדיין עובדים, ואתם יודעים להסביר (א) על אילו פורטים סמכתם ולמה,
  (ב) למה רק VLAN 10 ולא VLAN 30 או 99.

<details dir="rtl"><summary>💡 רמז 1</summary>

‏DAI משווה כל תשובת ARP לטבלת ה-binding. אילו מכשירים **לא** נמצאים בטבלה? (הסתכלו ב-`show ip dhcp snooping binding`.)
</details>
<details dir="rtl"><summary>💡 רמז 2</summary>

הפקודות הן `ip arp inspection vlan …`‎ (גלובלית) ו-`ip arp inspection trust` (בממשק).
</details>
<details dir="rtl"><summary>✔ תשובה</summary>

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

לשלב 07 חזרו ל-`step06.pkt`.

---

## 🛠 הפרויקט שלכם

עשיתם את השלב הזה על הדוגמה של אינטל. עכשיו עשו אותו שוב בפרויקט **שלכם**, עם הערכים
מהתוכנית **שלכם** (`my-project/plan.md`). הפקודות זהות — רק הערכים משתנים.

- [ ] פותחים את `my-project/step05.pkt` ‏←‏ **Save As** ‏`my-project/step06.pkt`
- [ ] ‏DHCP snooping בכל מתג access: ה-VLANים **שלכם** של המשתמשים, קישורים כלפי מעלה מהימנים, option 82 כבוי
- [ ] ‏Port-security: משתמשים `restrict`, מדפסות / מחשב מנהל `shutdown`, פורטי AP עם maximum גבוה
- [ ] גורמים לכל מכשיר לדבר, בודקים את טבלת ה-binding ואת `show port-security`, שומרים
- [ ] חוזרים על שתי ההתקפות (משימות 6–7) מול הרשת **שלכם** — הן חייבות להיחסם

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
