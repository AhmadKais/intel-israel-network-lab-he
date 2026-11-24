# שיעור 05 — אבטחה וניהול: ACL, ‏VPN, ‏SSH, ‏AAA, ‏NTP, ‏Syslog ו-ASA

<div dir="rtl">

> ⏱ 90 דקות · 🧰 Packet Tracer 9.x · 📂 קובץ התחלה: [`lesson05-start.pkt`](lesson05-start.pkt) או הקובץ שלכם אחרי [חלק D](../from-zero/README.md#part-d) · 💾 שומרים בשם `lesson05.pkt`

</div>

## מה יהיה לכם בסוף השיעור
חברה מוגנת: מחלקות שלא מגיעות לאן שאסור, מנהרה מוצפנת סכנין ↔ אילת, ניהול מוצפן עם משתמשים מרכזיים, שעון נכון ויומנים, וחומת אש.

![ההתחלה: חומת האש האדומה ומחשבי PC-LAB נוספו משמאל](images/01-start.png)

## 📖 הסיפור — פרק 5: סוגרים את הדלתות שצריך לסגור
**איך הגענו לכאן.** מחלקה אחת (1), חמש מחלקות (2), סניף שלם (3), שלושה סניפים באינטרנט (4). בארבעה שיעורים רק **פתחנו** דברים, כי המטרה הייתה שהכול יעבוד.

**איפה אנחנו עכשיו.** הכול עובד, **לכולם**: הנהלת החשבונות עושה ping למנהל, אילת וסכנין מדברות בלי הצפנה, כמעט 30 מכשירים עם סיסמה אחת, כל אחד מראה שעה אחרת, ומעבדת בדיקות חדשה עומדת בלי הגנה (קובץ ההתחלה, או [חלק D](../from-zero/)).

**מה רוצים היום.** כל אחד מגיע רק למה שהוא צריך, אף אחד לא קורא את התעבורה שלנו, לכל כניסה יש שם ושעה, והמעבדה יוצאת החוצה בלי שאף אחד נכנס אליה.

**הדרך של היום:**

<div dir="rtl">

| משימה | על איזו שאלה היא עונה | למה דווקא עכשיו |
|---|---|---|
| 1 שרת | מי המשתמשים? | המכשירים ישאלו את השרת, ולכן הוא ראשון |
| ‎2 ‏ACL | מי מגיע למה? | קודם הכללים בתוך כל סניף |
| ‎3 ‏VPN | מי יכול לקרוא מה שעובר בחוץ? | בפנים יש סדר, עכשיו הדרך בין הסניפים |
| ‎4 ‏SSH, AAA, NTP, Syslog | מי נכנס, מאיפה, ומתי? | הדלת האחרונה היא המכשירים עצמם |
| ‎5 ‏ASA | איך מגינים על אזור שלם? | כל מה שלמעלה בודק חבילות; חומת אש זוכרת **שיחות** |

</div>

## מהלך השיעור (למורה)

<div dir="rtl">

| דקות | חלק |
|---|---|
| ‎0–15 | חלק 1 — תיאוריה על הלוח |
| ‎15–23 | משימה 1 — השרת (AAA, ‏NTP, ‏Syslog) |
| ‎23–35 | משימה 2 — ACL |
| ‎35–58 | משימה 3 — VPN, כולל הכישלון המתוכנן |
| ‎58–72 | משימה 4 — SSH, ‏AAA, ‏NTP, ‏Syslog (סכנין בכיתה, השאר בהדבקה) |
| ‎72–83 | משימה 5 — ASA |
| ‎83–90 | טבלת הבדיקות הסופית, "הפרויקט שלכם" |

</div>

זה השיעור הצפוף ביותר. אם אין מספיק זמן: SSH במתגים (4.4) וה-ASA הם שיעורי בית טובים.
שירותי AAA ו-NTP בשרתים של אשדוד ואילת כבר מוגדרים בקובץ ההתחלה.

---

## חלק 1 — תיאוריה: קודם מבינים

### ‏1.1 ACL
רשימת כללים שנקראת מ**למעלה למטה**. ההתאמה הראשונה קובעת, ובסוף יש שורה בלתי נראית: **deny הכול**.

<div dir="rtl">

| | סטנדרטי | מורחב |
|---|---|---|
| בודק | מקור בלבד | מקור, יעד, פרוטוקול, פורט |
| מספרים | ‎1–99 | ‎100–199 |
| שמים אותו | קרוב ל**יעד** | קרוב ל**מקור** |

</div>

💬 **במילים פשוטות:** שומר בכניסה עם רשימה. הוא קורא מלמעלה, פועל לפי השורה **הראשונה** שמתאימה, ומי שלא ברשימה לא נכנס.

**דוגמה — קוראים את הרשימה שלנו (משימה 2) כמו הנתב:**

<div dir="rtl">

| חבילה | השורה הראשונה שמתאימה | תוצאה |
|---|---|---|
| מ-0.0.0.0 ל-255.255.255.255, ‏UDP 67 ‏(DHCP) | ‎`permit udp any any eq bootps` | ✅ עוברת |
| מ-192.168.62.22 ל-192.168.60.21, ‏ping | ‎`deny ip ...62.0 ...60.0` | ❌ חסומה |
| מ-192.168.62.22 ל-192.168.63.1, ‏TCP 80 | ‎`permit tcp ... eq www` | ✅ עוברת |
| מ-192.168.62.22 ל-192.168.63.1, ‏ping | ‎`deny ip ...62.0 ...63.0` | ❌ חסומה |
| מ-192.168.62.22 ל-200.200.0.2, ‏ping | ‎`permit ip ...62.0 any` | ✅ עוברת |

</div>

❓ **שאלו את הכיתה:** מה קורה אם כותבים את השורה האחרונה ראשונה?

<details dir="rtl"><summary>תשובה</summary>

היא מתאימה לכל מה ש-VLAN 62 שולח, ולכן לעולם לא מגיעים לשורות ה-deny ושום דבר לא נחסם.

</details>

### ‏1.2 VPN IPsec

<div dir="rtl">

| שלב | מה קורה | פקודה |
|---|---|---|
| ‎‏1 (ISAKMP) | הנתבים מזדהים (מפתח) ומסכימים על הצפנה | ‎`crypto isakmp policy` |
| ‎‏2 (IPsec) | הנתונים עצמם מוצפנים (ESP) | ‎`transform-set` |

</div>

- **הצפנה** (AES) — אף אחד לא קורא. **Hash** ‏(SHA) — אף אחד לא שינה. **מפתח משותף** — זה באמת אתם. **קבוצת DH** — יצירת סוד משותף דרך קו פתוח.
- ‏**Interesting traffic**: ‏ACL שאומר מה נכנס למנהרה.

💬 **במילים פשוטות:** שני סניפים שולחים מכתבים בדואר רגיל, בתוך כספת נעולה. הדואר רואה רק את הכתובות של הסניפים, לא מה
בפנים ולא מי כתב למי.

**דוגמה — ping מ-PC-E-MEET-1 ‏(192.168.82.23) לשרת בסכנין:**

<div dir="rtl">

| איפה | ממי למי | אפשר לקרוא? |
|---|---|---|
| ב-LAN של אילת | מ-192.168.82.23 ל-192.168.50.1 | כן |
| באינטרנט | **מ-200.150.0.1 ל-200.130.0.1** ‏(ESP) | לא, מוצפן |
| ב-LAN של סכנין | מ-192.168.82.23 ל-192.168.50.1 | כן |

</div>

### ‏1.3 AAA

<div dir="rtl">

| | השאלה |
|---|---|
| ‎Authentication | מי אתה? |
| ‎Authorization | מה מותר לך לעשות? |
| ‎Accounting | מה עשית? |

</div>

<div dir="rtl">

| | ‎TACACS+‎ | ‎RADIUS |
|---|---|---|
| פורט | ‎TCP 49 | ‎UDP 1645 / 1812 |
| מצפין | את כל ההודעה | רק את הסיסמה |
| טוב ל | ניהול ציוד רשת | משתמשי Wi-Fi ו-VPN |

</div>

💬 **במילים פשוטות:** נכנסים לבניין של חברה. השומר בודק מי אתם (authentication), הכרטיס פותח רק חלק מהדלתות (authorization),
והמצלמה רושמת איפה הייתם (accounting).

**דוגמה — `ssh -l osemuser 192.168.10.254`:** הנתב שואל את שרת ה-TACACS+‎ "הסיסמה נכונה?". כן — נכנסים. אם השרת **לא עונה**, הנתב בודק את
המשתמשים המקומיים (`local`). אם השרת ענה "לא", **אין** הזדמנות שנייה.

### 1.4 השאר
- ‏**SSH** — ניהול מוצפן. ‏Telnet שולח סיסמאות כטקסט גלוי.
- ‏**NTP** — אותה שעה בכל מקום, אחרת היומנים חסרי ערך. עם אימות, כדי שאף אחד לא יזייף.
- ‏**Syslog** — כל ההודעות לשרת אחד.
- ‏**ASA** — חומת אש: מרמה 100 (inside) לרמה 0 (outside) מותר, בכיוון ההפוך **חסום**. ‏`inspect` מאפשר ל**תשובות** לחזור.

**דוגמה — איך ה-ASA מחליט:**

<div dir="rtl">

| חבילה | רמות | תוצאה |
|---|---|---|
| מ-PC-LAB-1 לשרת, חיבור חדש | מ-100 ל-0 | ‎✅ |
| מהשרת ל-PC-LAB-1, ה**תשובה** | מ-0 ל-100 | ✅ בזכות `inspect` |
| מ-PC-MGMT-1 ל-PC-LAB-1, חיבור חדש | מ-0 ל-100 | ‎❌ |

</div>

---

## 🔑 פותחים מכשיר
לוחצים על המכשיר ‏←‏ **CLI** (1) ‏←‏ לוחצים בטקסט ואז Enter ‏←‏ `Osem#Con` ‏←‏ `enable` ‏←‏ `Osem#En1`. עם תמונות: [שיעור 2](../lesson-02/).

![לוחצים על CLI](images/step-login-1.png)

**איך בנויה כל משימה:** ‏🌐 הרשת עכשיו ‏←‏ ❗ הבעיה ‏←‏ 💡 הפתרון ‏←‏ 📋 מבצעים לבד ‏←‏ 🖱 הפתרון המלא: על מה לוחצים, מה כותבים ומה חייבים לראות.

## משימה 1 — השרת
**📖 איך הגענו לכאן.** שלושה סניפים באינטרנט, וכמעט 30 מכשירים עם סיסמה משותפת אחת.

**🌐 הרשת עכשיו.** שלושה סניפים באינטרנט. מתחילים מהשרת של סכנין:

![1 השרת SRV-SAKHNIN](images/step-map-m1.png)

**❗ הבעיה.** כמעט 30 מכשירים עם אותה סיסמה, שכתובה על פתק. עובד עוזב: משנים בכולם. משהו קרה בלילה: כל מכשיר מראה שעה אחרת ושומר לעצמו את ההודעות. שירות ה-AAA ריק וכבוי:

![השירות AAA לפני: כבוי, בלי לקוחות ובלי משתמשים](images/step-aaa0.png)

**🎯 מה רוצים עכשיו.** מקום אחד למשתמשים (AAA), שעון אחד נכון (NTP) ויומן אחד (Syslog). המכשירים ישתמשו בהם במשימה 4.

**💡 הפתרון.** שרת אחד שבודק משתמשים (**AAA**), נותן את השעה (**NTP**) ואוסף את ההודעות (**Syslog**). עכשיו מכינים את השרת, ובמשימה 4 מחברים אליו את הנתבים.

**📋 מבצעים בפרויקט.** שני לקוחות AAA (שני הנתבים), משתמש אחד, NTP עם מפתח 1, ו-Syslog דולק.

### 🖱 הפתרון: על מה לוחצים ומה כותבים
לוחצים על **SRV-SAKHNIN** ‏←‏ **Services** (1) ‏←‏ ‏AAA ‏(2), ‏NTP ‏(3), ‏SYSLOG ‏(4):

![1 לשונית Services, 2 שירות AAA, 3 שירות NTP, 4 שירות SYSLOG](images/step-srv.png)

‏**SRV-SAKHNIN** ‏←‏ ‏Services ‏←‏ ‏**AAA** ‏←‏ ‏On (1). ‏Client Name (2), ‏Client IP (3), ‏Secret (4), ‏ServerType ‏←‏ ‏**Tacacs** ‏←‏ ‏**Add** (5):

<div dir="rtl">

| ‎Client Name | ‎Client IP | ‎Secret | ‎Type |
|---|---|---|---|
| ‎R-S-MAIN | ‎192.168.50.254 | ‎Osem#Aaa | ‎Tacacs |
| ‎R-S-BKP | ‎192.168.50.253 | ‎Osem#Aaa | ‎Tacacs |

</div>

למטה: Username (6) ‏`osemuser`, ‏Password ‏`Osem#User` ‏←‏ ‏**Add** (7).

‏![AAA](images/02-aaa.png)

‏**NTP** ‏←‏ ‏Authentication ‏**Enable** (1), ‏Key (2) ‏‎`1`, ‏Password (3) ‏`Osem#Ntp`. זה מוצג בתור ‎`01`, וזה עובד.

‏![NTP](images/03-ntp.png)

‏**SYSLOG** ‏←‏ בודקים שהוא On.

![השירות Syslog דולק](images/step-sys.png)

ההודעות של הנתבים מופיעות ברשימה הזו רק אחרי משימה 4.

<div dir="rtl">

| שדה | מה זה | חייב להתאים ל |
|---|---|---|
| ‎Client | הנתב שישאל את השרת | הכתובת שלו לכיוון השרת (VLAN 50) |
| ‎Secret | מפתח בין הנתב לשרת | ‎`tacacs-server host ... key` |
| ‎ServerType | השפה: Tacacs / Radius | `group tacacs+`‎ בנתב |
| ‎Username | מי שמתחבר | רק כאן, לא בנתב |

</div>

**⏭ מה הלאה.** לפני המכשירים, המחלקות: מי מגיע למי?

## משימה 2 — ACL באשדוד ובאילת
**📖 איך הגענו לכאן.** בשיעור 3 פתחנו הכול לכולם, כי רצינו שיעבוד.

**🌐 הרשת עכשיו.** אשדוד: הנהלת החשבונות ב-VLAN 62, ההנהלה ב-VLAN 60, השרת ב-63. אילת: ההרכבה ב-81, ההנהלה ב-80.

![1 הנתב R-A-MAIN, 2 הנתב R-A-BKP, 3 המחשב PC-A-ACC-1, 4 המחשב PC-A-MGMT-2, 5 הנתב R-E-MAIN, 6 הנתב R-E-BKP](images/step-map-m2.png)

**❗ הבעיה.** בשיעור 3 פתחנו הכול לכולם. מחשב בהנהלת החשבונות יכול לעשות ping למחשב של המנהל ולנסות להיכנס לכל שירות בשרת. נראה את זה בצילום הראשון.

**🎯 מה רוצים עכשיו.** כללים: הנהלת החשבונות מגיעה רק לשירותים שהיא צריכה, וההרכבה באילת לא מגיעה להנהלה.

**💡 הפתרון.** **ACL מורחב**, קרוב למקור: בממשק המשנה של VLAN 62, ב**שני** הנתבים (1.1).

**📋 מבצעים בפרויקט.** לפני שמסתכלים: כותבים במילים, שורה אחר שורה, מה מותר ומה אסור, בסדר הנכון. לא לשכוח איך מחשב מקבל כתובת.

### 🖱 הפתרון: על מה לוחצים ומה כותבים
**המטרה:** הנהלת החשבונות (VLAN 62) לא מגיעה להנהלה (VLAN 60), ומהשרת מקבלת רק web, ‏DNS ו-FTP.

לפני: מ-**PC-A-ACC-1** בודקים מה הכתובת של PC-A-MGMT-2 ועושים לו ping. עובד.

![לפני ה-ACL](images/04-acl-before.png)

ב-**R-A-MAIN וגם ב-R-A-BKP**:
```
configure terminal
access-list 110 permit udp any any eq bootps
access-list 110 deny ip 192.168.62.0 0.0.0.255 192.168.60.0 0.0.0.255
access-list 110 permit tcp 192.168.62.0 0.0.0.255 host 192.168.63.1 eq www
access-list 110 permit udp 192.168.62.0 0.0.0.255 host 192.168.63.1 eq domain
access-list 110 permit tcp 192.168.62.0 0.0.0.255 host 192.168.63.1 eq ftp
access-list 110 deny ip 192.168.62.0 0.0.0.255 192.168.63.0 0.0.0.255
access-list 110 permit ip 192.168.62.0 0.0.0.255 any
interface g0/0.62
ip access-group 110 in
end
```

‏**R-A-MAIN:**

![ה-ACL](images/06-acl.png)

‏**R-A-BKP, אותן פקודות:**

![הנתב R-A-BKP](images/step-m2-abkp.png)

❓ **למה צריך את השורה הראשונה?** למחשב שמבקש DHCP עדיין אין כתובת: הוא שולח מ-0.0.0.0, ואף שורה אחרת לא
מרשה את זה. בדקנו בלעדיה, בשני הנתבים: `ipconfig /renew` נתקע.

![בלי שורת bootps: אין כתובת](images/05-acl-dhcp-bug.png)

❓ **למה בשני הנתבים?** כל אחד מהם יכול להיות Active. בדקנו גם רק בראשי, בלי שורת bootps: ה-DHCP עדיין עבד, כי **הגיבוי** העביר
את הבקשה. ‏ACL בנתב אחד הוא מלא חורים.

✅ מ-PC-A-ACC-2: הנהלה — חסום, ping לשרת — חסום, אינטרנט — עובד, web — עובד.

![הבדיקות](images/07-acl-test.png)

![ה-Web מותר](images/08-acl-web.png)

✅ ב-R-A-MAIN: ‏`show access-lists` ‏←‏ המונים עולים.

![מספר ההתאמות](images/09-acl-show.png)

### 2.1 🔎 ה-FTP מתחבר, אבל `dir` נתקע. למה?
מ-**PC-A-ACC-2**: ‏`ftp 192.168.63.1`, משתמש `ashdod`, סיסמה `Osem#Ftp`. הכניסה מצליחה. עכשיו `dir`:

![נכנסנו, אבל הרשימה לא מגיעה](images/32-ftp-hang.png)

<details dir="rtl"><summary>תשובה</summary>

‏FTP משתמש ב**שני** חיבורים: פקודות בפורט 21, ונתונים בפורט אחר. ב-*passive mode* השרת בוחר פורט גבוה (מעל 1023) לנתונים. פתחנו
רק את 21, ולכן הנתונים נופלים על השורה `deny ip ... 192.168.63.0`.

</details>

התיקון, ב-**R-A-MAIN וב-R-A-BKP**. המספר 52 שם את השורה **לפני** ה-deny ‏(60):
```
configure terminal
ip access-list extended 110
52 permit tcp 192.168.62.0 0.0.0.255 host 192.168.63.1 gt 1023
end
copy running-config startup-config
```

![אותו דבר ב-R-A-BKP](images/step-ftp-abkp.png)

ב-R-A-MAIN בודקים עם `show access-lists`:

![השורה החדשה נמצאת לפני ה-deny](images/33-acl-ftp-fix.png)

✅ מ-PC-A-ACC-3 הרשימה מגיעה, ו-ping לשרת עדיין חסום. (יוצאים מ-FTP עם `quit`.)

![הפקודה dir עובדת](images/34-ftp-ok.png)

### 2.2 אילת

❗ אותה בעיה באילת: ההרכבה מגיעה להנהלה. 💡 אותו רעיון, שורת deny אחת.

**אילת** (הרכבה 81 לא מגיעה להנהלה 80), ב-**R-E-MAIN וב-R-E-BKP**:
```
configure terminal
access-list 120 permit udp any any eq bootps
access-list 120 deny ip 192.168.81.0 0.0.0.255 192.168.80.0 0.0.0.255
access-list 120 permit ip 192.168.81.0 0.0.0.255 any
interface g0/0.81
ip access-group 120 in
end
copy running-config startup-config
```

![הנתב R-E-MAIN](images/step-m2-emain.png)

![הנתב R-E-BKP](images/step-m2-ebkp.png)

<details dir="rtl" open><summary><b>📘 הסבר הפקודות של המשימה</b></summary>

<div dir="rtl">

| פקודה | מה היא עושה, ולמה היא כאן |
|---|---|
| ‎`access-list 110 permit udp any any eq bootps` | קודם כול מתירים DHCP, אחרת המחשבים ב-VLAN הזה מאבדים את הכתובת. |
| ‎`access-list 110 deny ip 192.168.62.0 0.0.0.255 192.168.60.0 0.0.0.255` | חוסם הכול מהרשת הראשונה לשנייה. |
| ‎`access-list 110 permit tcp 192.168.62.0 0.0.0.255 host 192.168.63.1 eq www` | מתירים את האתר של השרת (TCP 80), ורק מהרשת הזו. |
| ‎`access-list 110 permit udp 192.168.62.0 0.0.0.255 host 192.168.63.1 eq domain` | מתירים שאלות DNS לשרת (UDP 53). |
| ‎`access-list 110 permit tcp 192.168.62.0 0.0.0.255 host 192.168.63.1 eq ftp` | מתירים את חיבור ה**שליטה** של FTP ‏(TCP 21). חיבור הנתונים צריך שורה נוספת. |
| ‎`access-list 110 permit ip 192.168.62.0 0.0.0.255 any` | מתיר את כל השאר. בלי זה ה-`deny` הבלתי נראה בסוף חוסם הכול. |
| ‎`interface g0/0.62` | **ממשק משנה**: דלת וירטואלית על אותו פורט פיזי, אחת לכל VLAN. |
| ‎`ip access-group 110 in` | שם את הרשימה על הפורט; `in` = מה שנכנס לנתב מהרשת הזו. רשימה שלא על פורט לא עושה כלום. |
| ‎`ipconfig /renew` | המחשב מבקש שוב כתובת מ-DHCP. |
| ‎`show access-lists` | שורות הרשימה, וכמה חבילות פגשו כל אחת. |
| ‎`ip access-list extended 110` | פותח רשימה לפי שם או מספר, כדי להוסיף או להכניס שורות. |
| ‎`52 permit tcp 192.168.62.0 0.0.0.255 host 192.168.63.1 gt 1023` | מכניס שורה **בין** שורות קיימות (52 אחרי 50): הפורטים של נתוני FTP, מעל 1023. |
| ‎`copy running-config startup-config` | שומר את מה שבזיכרון לקובץ ההפעלה. בלי זה הפסקת חשמל מוחקת את העבודה. |

</div>

</details>

**⏭ מה הלאה.** בתוך הסניף יש סדר. בין הסניפים המידע שלנו עובר באינטרנט, קריא.

## משימה 3 — VPN סכנין ↔ אילת
**📖 איך הגענו לכאן.** סכנין ואילת באינטרנט, מאחורי NAT, ולא מגיעות לרשתות הפרטיות זו של זו.

**🌐 הרשת עכשיו.** סכנין ואילת, כל אחד מאחורי NAT, והאינטרנט באמצע:

![1 הנתב R-S-EXT, 2 הנתב R-E-EXT, 3 המחשב PC-E-MEET-1, 4 השרת SRV-SAKHNIN](images/step-map-m3.png)

**❗ הבעיה.** עובד באילת צריך את השרת בסכנין. ב-PC-E-MEET-1 ‏←‏ `ping 192.168.50.1`:

![הספק עונה: unreachable](images/step-m3-before.png)

הספק לא מכיר כתובות פרטיות. וגם אם היינו מפרסמים את השרת עם NAT סטטי, הכול היה עובר **בלי הצפנה** וכל אחד היה יכול לנסות להיכנס.

**🎯 מה רוצים עכשיו.** מנהרה מוצפנת דרך האינטרנט, כאילו יש ביניהן כבל פרטי.

**💡 הפתרון.** **IPsec VPN** בין שני אתרים: החבילה הפרטית נוסעת, מוצפנת, בתוך חבילה ציבורית (1.2).

**📋 מבצעים בפרויקט.** רישיון ‏←‏ מנהרה בשני הצדדים ‏←‏ בדיקה ‏←‏ מגלים למה נכשל ‏←‏ מתקנים. שני הצדדים חייבים להיות תמונת מראה.

### 🖱 הפתרון: על מה לוחצים ומה כותבים
### 3.1 הרישיון

❗ הנתב לא מכיר את פקודות `crypto`. 💡 מפעילים את רישיון האבטחה, שומרים ומפעילים מחדש.

ב-R-S-EXT מנסים `crypto isakmp policy 10`. ה-1941 לא מכיר את הפקודה:

![אין רישיון](images/10-no-licence.png)

ב-**R-S-EXT וב-R-E-EXT**:
```
configure terminal
license boot module c1900 technology-package securityk9
```
⚠️ **לא הודפס כלום?** זה קורה ב-Packet Tracer כשהנתב כבר הופעל מחדש קודם. כותבים **שוב את אותה פקודה**, ועכשיו מופיע ההסכם:

![1 בפעם הראשונה: כלום. 2 שוב אותה פקודה: ההסכם (בתמונה R-A-EXT, נראה אותו דבר בכל 1941)](images/step-lic-twice.png)

כשמופיע `ACCEPT? [yes/no]:`‎ עונים `yes`. חייבים לראות `Next reboot level = securityk9`. ואז:
```
end
copy running-config startup-config
reload
```

אחרי `yes`, ב-R-E-EXT:

![הנתב R-E-EXT קיבל את הרישיון](images/step-lic-e.png)

כשמופיע `Proceed with reload? [confirm]`‎ לוחצים **Enter**. הנתב עולה מחדש:

![הנתב עולה מחדש](images/step-reload.png)

ב-R-E-EXT אחרי ההפעלה מחדש:

![הרישיון עובד](images/step-lic-ok-e.png)

ב-R-S-EXT:

![הרישיון התקבל](images/11-licence.png)

אחרי ההפעלה מחדש נכנסים שוב: `show version | include security` ‏←‏ ‏`securityk9`

![הרישיון פעיל](images/12-licence-ok.png)

### 3.2 המנהרה

❗ לפני ההצפנה הנתבים חייבים להסכים על שפה ולזהות אחד את השני. 💡 שלב 1 (policy ומפתח), שלב 2 (transform-set), מה נכנס למנהרה (ACL), והכול נקשר ב-crypto map על הפורט היוצא.

**R-S-EXT:**
```
configure terminal
crypto isakmp policy 10
encryption aes 256
hash sha
authentication pre-share
group 5
lifetime 86400
exit
crypto isakmp key OsemVpn2026 address 200.150.0.1
crypto ipsec transform-set VPN-SET esp-aes 256 esp-sha-hmac
ip access-list extended VPN-S-E
permit ip 192.168.0.0 0.0.63.255 192.168.80.0 0.0.3.255
exit
crypto map VPN-MAP 10 ipsec-isakmp
set peer 200.150.0.1
set transform-set VPN-SET
match address VPN-S-E
exit
interface s0/0/1
crypto map VPN-MAP
end
```
‏**R-E-EXT** (תמונת מראה):
```
configure terminal
crypto isakmp policy 10
encryption aes 256
hash sha
authentication pre-share
group 5
lifetime 86400
exit
crypto isakmp key OsemVpn2026 address 200.130.0.1
crypto ipsec transform-set VPN-SET esp-aes 256 esp-sha-hmac
ip access-list extended VPN-E-S
permit ip 192.168.80.0 0.0.3.255 192.168.0.0 0.0.63.255
exit
crypto map VPN-MAP 10 ipsec-isakmp
set peer 200.130.0.1
set transform-set VPN-SET
match address VPN-E-S
exit
interface s0/0/0
crypto map VPN-MAP
end
```

![הנתב R-E-EXT](images/step-vpn-e.png)

וב-R-S-EXT:

![ההגדרה ב-R-S-EXT](images/13-vpn.png)

<div dir="rtl">

| פקודה | מה היא עושה |
|---|---|
| ‎`crypto isakmp policy 10` | שלב 1: חייב להיות זהה בשני הצדדים |
| ‎`crypto isakmp key` | אותו מפתח, עם הכתובת של **הצד השני** |
| ‎`transform-set` | איך מצפינים את הנתונים בשלב 2 |
| ‎`match address` | מה נכנס למנהרה; תמונת מראה בצד השני |
| `crypto map` על הממשק | מפעיל, על הפורט **היוצא** |

</div>

⚠️ משתמשים במפתח בלי ‎`#`‎. בבדיקות שלנו מפתח עם ‎`#`‎ לא העלה את המנהרה אף פעם.

### 3.3 🔎 זה לא עובד! למה?
‏**PC-E-MEET-1** ‏←‏ ‏`ping 192.168.50.1`. התשובה "Destination host unreachable" מגיעה מ**הספק**:

![ה-VPN נכשל](images/14-vpn-bug-pc.png)

נותנים לכיתה לחקור ב-R-E-EXT: ‏`show ip access-lists`, ‏`show crypto isakmp sa`, ‏`show ip nat translations`.

![מי לקח את החבילה?](images/15-vpn-bug.png)

<details dir="rtl"><summary>תשובה</summary>

לרשימת ה-VPN אין התאמות, ולרשימת ה-NAT יש 8. הנתב עושה **NAT לפני ההצפנה**: המקור הפך ל-200.150.0.20, ולכן
החבילה כבר לא מתאימה לרשימת ה-VPN והיא יצאה לאינטרנט, ושם אף אחד לא מכיר את 192.168.50.1. התיקון: אומרים
ל-NAT **לא** לתרגם תנועה לסניף השני. השורה חייבת להיות **לפני** ה-permit, ולכן נותנים לה את המספר 5.

</details>

### 3.4 התיקון
**R-S-EXT:**
```
configure terminal
ip access-list extended NAT-S
5 deny ip 192.168.0.0 0.0.63.255 192.168.80.0 0.0.3.255
end
clear ip nat translation *
copy running-config startup-config
```
**R-E-EXT:**
```
configure terminal
ip access-list extended NAT-E
5 deny ip 192.168.80.0 0.0.3.255 192.168.0.0 0.0.63.255
end
clear ip nat translation *
copy running-config startup-config
```

![הנתב R-E-EXT](images/step-nat-e.png)

וב-R-S-EXT:

![שורה 5 נמצאת לפני שורה 10](images/16-nat-exempt.png)

✅ שוב ping, **רק מאילת**. התשובה הראשונה יכולה ללכת לאיבוד בזמן שהמנהרה עולה.

![עובד](images/17-vpn-ok.png)

✅ ב-R-E-EXT: ‏`show crypto isakmp sa` ‏←‏ ‏**QM_IDLE**, וב-`show crypto ipsec sa` ‏←‏ ‏encaps ו-decaps עולים.

![המנהרה פעילה](images/18-vpn-sa.png)

💡 נתקע? מפעילים את המנהרה מחדש: בפורט היוצא של **שני** נתבי הקצה `no crypto map VPN-MAP` ואז `crypto map VPN-MAP`, ו-ping
מצד אחד בלבד. (בנתבים אמיתיים יש גם `clear crypto isakmp`. ב-Packet Tracer אין.)

<details dir="rtl" open><summary><b>📘 הסבר שאר הפקודות של המשימה</b></summary>

<div dir="rtl">

| פקודה | מה היא עושה, ולמה היא כאן |
|---|---|
| ‎`ping 192.168.50.1` | שולח 4 הודעות בדיקה. תשובות = הדרך עובדת ב**שני** הכיוונים. |
| ‎`license boot module c1900 technology-package securityk9` | מפעיל את חבילת האבטחה של ה-1941. בלעדיה אין פקודות `crypto`. |
| ‎`copy running-config startup-config` | שומר את מה שבזיכרון לקובץ ההפעלה. בלי זה הפסקת חשמל מוחקת את העבודה. |
| ‎`reload` | מפעיל את הנתב מחדש. רק אז הרישיון נכנס לתוקף. |
| ‎`show version \| include security` | פרטי המכשיר. החלק שאחרי הקו מראה רק שורות עם "security". |
| ‎`encryption aes 256` | ההצפנה של שלב 1: AES עם מפתח של 256 ביט. |
| ‎`hash sha` | ‏SHA בודק שאף אחד לא שינה את ההודעה בדרך. |
| ‎`authentication pre-share` | הנתבים מזדהים עם מפתח משותף (כתוב למטה). |
| ‎`group 5` | קבוצת Diffie-Hellman: איך הנתבים מסכימים על סוד מעל קו פתוח. |
| ‎`lifetime 86400` | אחרי כמה שניות מחליפים מפתחות (86400 = יממה). |
| ‎`crypto ipsec transform-set VPN-SET esp-aes 256 esp-sha-hmac` | שלב 2: איך הנתונים עצמם מוצפנים (AES 256) ונבדקים (SHA). |
| ‎`ip access-list extended VPN-S-E` | פותח רשימה לפי שם או מספר, כדי להוסיף או להכניס שורות. |
| ‎`permit ip 192.168.0.0 0.0.63.255 192.168.80.0 0.0.3.255` | התעבורה שנכנסת למנהרה: מהרשתות שלנו לשלהם. הצד השני כותב תמונת ראי. |
| ‎`crypto map VPN-MAP 10 ipsec-isakmp` | יוצר את המפה שמחברת הכול: מי, איך ומה. |
| ‎`set peer 200.150.0.1` | מי: הכתובת הציבורית של הצד השני. |
| ‎`set transform-set VPN-SET` | איך: באיזו הצפנה. |
| ‎`interface s0/0/1` | בוחרים פורט. כל מה שמתחת חל עליו, עד `exit`. |
| ‎`show ip access-lists` | שורות הרשימה, וכמה חבילות פגשו כל אחת. |
| ‎`show crypto isakmp sa` | שלב 1. `QM_IDLE` = תקין. |
| ‎`show ip nat translations` | מי תורגם לאיזו כתובת. |
| ‎`5 deny ip 192.168.0.0 0.0.63.255 192.168.80.0 0.0.3.255` | מכניס שורה **בהתחלה** (5 לפני 10): תעבורה למנהרה לא עוברת NAT. |
| ‎`clear ip nat translation *`‎ | מוחק תרגומים ישנים, כדי שהכלל החדש יעבוד מיד. |
| ‎`show crypto ipsec sa` | שלב 2. המונים `encaps` ו-`decaps` חייבים לגדול. |
| ‎`no crypto map VPN-MAP` | מוריד את המפה מהפורט: המנהרה נכבית. |
| ‎`clear crypto isakmp` | מוחק את המנהרה הישנה, כדי שתיבנה מחדש. |

</div>

</details>

**⏭ מה הלאה.** המידע בטוח. את הנתבים שמעבירים אותו עדיין אי אפשר לנהל בבטחה.

## משימה 4 — SSH, ‏AAA, ‏NTP ו-Syslog
**📖 איך הגענו לכאן.** השרת מכיר את המשתמשים ממשימה 1, והמכשירים עדיין לא שואלים אותו.

**🌐 הרשת עכשיו.** השרת מוכן ממשימה 1. עכשיו המכשירים לומדים להשתמש בו:

![1 הנתב R-S-MAIN, 2 הנתב R-S-BKP, 3 המחשב PC-MGMT-1, 4 המחשב PC-SAL-1, 5 המתג SW-S-MAIN](images/step-map-m4.png)

**❗ הבעיה.** ב-PC-MGMT-1 ‏←‏ `telnet 192.168.10.254`. הנתב פותח את הקו וסוגר אותו: אין בכלל ניהול מרחוק. ואם רק נוסיף סיסמה, Telnet ישלח אותה **בלי הצפנה**:

![החיבור נסגר](images/step-m4-before.png)

ב-R-S-MAIN, ‏`show clock`: השנה היא 1993, ו-NTP כבוי. יומן כזה לא מוכיח כלום:

![השנה 1993, ו-NTP לא מופעל](images/step-m4-clock.png)

**🎯 מה רוצים עכשיו.** ניהול מוצפן (SSH), שם אישי לכל כניסה (AAA), שעה אחת (NTP), יומן אחד (Syslog).

**💡 הפתרון.** SSH (מוצפן), AAA (המשתמש נבדק בשרת, ויש משתמש מקומי לגיבוי), NTP עם מפתח, Syslog, ו-access-class כדי שרק ההנהלה תיכנס (1.3, 1.4).

**📋 מבצעים בפרויקט.** הסדר חשוב: קודם משתמש מקומי, ורק אחר כך `aaa new-model`. למה?

### 🖱 הפתרון: על מה לוחצים ומה כותבים
### 4.1 ב-R-S-MAIN, ואותו דבר ב-R-S-BKP
```
configure terminal
ip domain-name osem.com
username admin privilege 15 secret Osem#Adm1
crypto key generate rsa general-keys modulus 1024
ip ssh version 2
aaa new-model
tacacs-server host 192.168.50.1 key Osem#Aaa
aaa authentication login default group tacacs+ local
aaa authorization exec default group tacacs+ local
aaa authentication login CONSOLE local
line console 0
login authentication CONSOLE
exit
access-list 10 permit 192.168.10.0 0.0.0.255
line vty 0 4
transport input ssh
login authentication default
access-class 10 in
exit
ntp authentication-key 1 md5 Osem#Ntp
ntp authenticate
ntp trusted-key 1
ntp server 192.168.50.1 key 1
ntp update-calendar
logging host 192.168.50.1
service timestamps log datetime msec
end
copy running-config startup-config
```

![1 — הנתב R-S-MAIN](images/step-ssh-smain.png)

![2 — הנתב R-S-BKP](images/step-ssh-sbkp.png)

<div dir="rtl">

| פקודה | מה היא עושה | למה |
|---|---|---|
| `username admin` **לפני** `aaa new-model` | משתמש מקומי | אחרת נועלים את עצמכם בחוץ |
| ‎`crypto key generate rsa ... 1024` | מפתחות ל-SSH | בלעדיהם אין SSH 2 |
| ‎`group tacacs+ local` | קודם השרת, ואם הוא לא עונה — המשתמש המקומי | כדי לא להיתקע |
| ‎`CONSOLE local` | הקונסול עובד עם המשתמש המקומי | עם הכבל תמיד נכנסים |
| ‎`access-class 10 in` | רק VLAN 10 מנהל | ‏ACL סטנדרטי קרוב ליעד |
| `ntp trusted-key` ו-`key 1` | מקבל שעה רק משרת חתום | |

</div>

⚠️ מעכשיו **הקונסול מבקש שם משתמש**: ‏`admin` / ‏`Osem#Adm1`.

### 4.2 בדיקה
1. ‏**PC-MGMT-1**: ‏`ssh -l osemuser 192.168.10.254`, סיסמה `Osem#User`, ואז `show users`. המשתמש קיים **רק בשרת**, כלומר AAA עובד.

   ‏![SSH דרך TACACS+‎](images/19-ssh-ok.png)
2. ‏`exit`, ואז `telnet 192.168.10.254` ‏←‏ נסגר.

   ![ה-Telnet נדחה](images/21-telnet.png)
3. ‏**PC-SAL-1**: ‏`ssh -l osemuser 192.168.20.254` ‏←‏ ‏**refused** ‏(access-class).

   ![לא מ-VLAN 20](images/20-ssh-refused.png)
4. ב-R-S-MAIN: ‏`show ntp status` ‏←‏ ‏**synchronized** (יכול לקחת כמה דקות).

   ‏![NTP](images/22-ntp-ok.png)
5. ב-R-S-MAIN: ‏`interface g0/1` ‏←‏ ‏`no shutdown` ‏←‏ ‏`shutdown`. בשרת ‏←‏ ‏SYSLOG: ההודעות הגיעו. שימו לב לקפיצה של התאריך מ-1993 להיום: NTP!

   ![שתי הודעות על המסך, ואותן הודעות נשלחות לשרת](images/step-sysgen.png)

   ‏![Syslog](images/23-syslog.png)

### 4.3 אשדוד ואילת

❗ אותה בעיה בעוד שני סניפים. 💡 אותן פקודות, וכל סניף עם השרת **שלו**.

אשדוד משתמשת ב-**RADIUS**, אילת ב-**TACACS+‎**. הסוג חייב להיות זהה בנתב ובשרת!

<details dir="rtl"><summary>R-A-MAIN, R-A-BKP (מדביקים אותו דבר בשניהם)</summary>

<div dir="ltr">

```
configure terminal
ip domain-name osem.com
username admin privilege 15 secret Osem#Adm1
crypto key generate rsa general-keys modulus 1024
ip ssh version 2
aaa new-model
radius-server host 192.168.63.1 key Osem#Aaa
aaa authentication login default group radius local
aaa authorization exec default group radius local
aaa authentication login CONSOLE local
line console 0
login authentication CONSOLE
exit
line vty 0 4
transport input ssh
login authentication default
exit
ntp authentication-key 2 md5 Osem#Ntp
ntp authenticate
ntp trusted-key 2
ntp server 192.168.63.1 key 2
ntp update-calendar
logging host 192.168.63.1
service timestamps log datetime msec
end
copy running-config startup-config
```

![הנתב R-A-MAIN](images/step-ssh-amain.png)

![הנתב R-A-BKP](images/step-ssh-abkp.png)

</div>

</details>

<details dir="rtl"><summary>R-E-MAIN, R-E-BKP (מדביקים אותו דבר בשניהם)</summary>

<div dir="ltr">

```
configure terminal
ip domain-name osem.com
username admin privilege 15 secret Osem#Adm1
crypto key generate rsa general-keys modulus 1024
ip ssh version 2
aaa new-model
tacacs-server host 192.168.83.1 key Osem#Aaa
aaa authentication login default group tacacs+ local
aaa authorization exec default group tacacs+ local
aaa authentication login CONSOLE local
line console 0
login authentication CONSOLE
exit
line vty 0 4
transport input ssh
login authentication default
exit
ntp authentication-key 3 md5 Osem#Ntp
ntp authenticate
ntp trusted-key 3
ntp server 192.168.83.1 key 3
ntp update-calendar
logging host 192.168.83.1
service timestamps log datetime msec
end
copy running-config startup-config
```

![הנתב R-E-MAIN](images/step-ssh-emain.png)

![הנתב R-E-BKP](images/step-ssh-ebkp.png)

</div>

</details>

### 4.4 מתגים ונתבי קצה (שיעורי בית)

❗ למתג שכבה 2 אין כתובת IP, ולכן אי אפשר לנהל אותו מרחוק. 💡 כתובת על ממשק VLAN, שער, ו-SSH עם המשתמש המקומי.

המכשירים:

<div dir="rtl">

| סוג | מכשירים | שורת ה-vty |
|---|---|---|
| נתבים | ‎ISP, R-S-EXT, R-A-EXT, R-E-EXT | ‎`line vty 0 4` |
| מתגים, סכנין | ‎SW-S-MAIN, SW-S-BKP, SW-S-MGMT, SW-S-SAL, SW-S-IT, MLS-S-ASM, MLS-S-SRV | ‎`line vty 0 15` |
| מתגים, אשדוד | ‎SW-A-MAIN, SW-A-BKP, SW-A-MGMT, SW-A-ASM, SW-A-ACC, MLS-A-SRV | ‎`line vty 0 15` |
| מתגים, אילת | ‎SW-E-MAIN, SW-E-BKP, SW-E-MGMT, SW-E-ASM, SW-E-MEET, MLS-E-SRV | ‎`line vty 0 15` |

</div>

**כל אחד מארבעת הנתבים:**
```
configure terminal
ip domain-name osem.com
username admin privilege 15 secret Osem#Adm1
crypto key generate rsa general-keys modulus 1024
ip ssh version 2
line vty 0 4
transport input ssh
login local
end
copy running-config startup-config
```

**כל אחד מ-19 המתגים:**
```
configure terminal
ip domain-name osem.com
username admin privilege 15 secret Osem#Adm1
crypto key generate rsa general-keys modulus 1024
ip ssh version 2
line vty 0 15
transport input ssh
login local
end
copy running-config startup-config
```

![המתג SW-S-MAIN](images/step-ssh-sw.png)

כתובת ניהול לשלושת המתגים הראשיים:

**SW-S-MAIN:**
```
configure terminal
interface vlan 10
ip address 192.168.10.240 255.255.255.0
no shutdown
exit
ip default-gateway 192.168.10.252
end
copy running-config startup-config
```

**SW-A-MAIN:**
```
configure terminal
interface vlan 60
ip address 192.168.60.240 255.255.255.0
no shutdown
exit
ip default-gateway 192.168.60.252
end
copy running-config startup-config
```

**SW-E-MAIN:**
```
configure terminal
interface vlan 80
ip address 192.168.80.240 255.255.255.0
no shutdown
exit
ip default-gateway 192.168.80.252
end
copy running-config startup-config
```
![כתובת הניהול](images/step-sw-ip.png)

✅ ‏`ssh -l admin 192.168.10.240`

‏![SSH למתג](images/24-ssh-switch.png)

<details dir="rtl" open><summary><b>📘 הסבר שאר הפקודות של המשימה</b></summary>

<div dir="rtl">

| פקודה | מה היא עושה, ולמה היא כאן |
|---|---|
| ‎`telnet 192.168.10.254` | ניהול מרחוק **בלי** הצפנה. כאן זה חייב להיכשל. |
| ‎`show clock` | השעה של המכשיר. ‎`*`‎ בהתחלה = לא מסונכרנת. |
| ‎`ip domain-name osem.com` | שם דומיין. SSH צריך אותו כדי לבנות את שם המפתח. |
| ‎`ip ssh version 2` | מתיר רק גרסה 2, המאובטחת. |
| ‎`tacacs-server host 192.168.50.1 key Osem#Aaa` | כתובת שרת ה-TACACS+, והמפתח המשותף איתו. |
| ‎`aaa authentication login default group tacacs+ local` | **מי אתה?** קודם שואלים את השרת; אם הוא לא עונה, המשתמש המקומי. |
| ‎`aaa authorization exec default group tacacs+ local` | **מה מותר לך?** השרת מחליט על ההרשאות אחרי הכניסה. |
| ‎`aaa authentication login CONSOLE local` | רשימה נוספת, רק לקונסול: משתמש מקומי, כדי שלעולם לא תינעלו בחוץ. |
| ‎`line console 0` | נכנסים להגדרות של פורט הקונסול (הכבל הכחול / לשונית CLI). |
| ‎`login authentication CONSOLE` | הקו הזה משתמש ברשימה ששמה CONSOLE. |
| ‎`access-list 10 permit 192.168.10.0 0.0.0.255` | רשימה סטנדרטית (רק מקור): VLAN 10, ההנהלה. |
| ‎`line vty 0 4` | נכנסים להגדרות של הקווים **מרחוק**. ‎`0 4` = חמישה חיבורים ביחד, ‎`0 15` = שישה עשר. |
| ‎`transport input ssh` | מרחוק נכנסים רק ב-SSH. ‏Telnet (הקריא) סגור. |
| ‎`login authentication default` | הקו הזה משתמש ברשימת ברירת המחדל: קודם השרת, אחר כך המשתמש המקומי. |
| ‎`ntp authentication-key 1 md5 Osem#Ntp` | המפתח שבו שרת הזמן חותם (מספר וטקסט). |
| ‎`ntp authenticate` | דורש חתימה: לא מאמינים לכל אחד לגבי השעה. |
| ‎`ntp server 192.168.50.1 key 1` | ממי לוקחים את השעה, ועם איזה מפתח. |
| ‎`ntp update-calendar` | מעדכן גם את שעון החומרה, כדי שהשעה תישמר אחרי אתחול. |
| ‎`logging host 192.168.50.1` | שולח את ההודעות של המכשיר לשרת ה-Syslog הזה. |
| ‎`service timestamps log datetime msec` | מוסיף תאריך, שעה ואלפיות שנייה לכל הודעה. |
| ‎`copy running-config startup-config` | שומר את מה שבזיכרון לקובץ ההפעלה. בלי זה הפסקת חשמל מוחקת את העבודה. |
| ‎`ssh -l osemuser 192.168.10.254` | ניהול מרחוק מוצפן: ‎`-l` ושם המשתמש, ואז כתובת המכשיר. |
| ‎`show users` | מי מחובר עכשיו, ומאיפה. |
| ‎`show ntp status` | האם השעון מסונכרן עם השרת. |
| ‎`interface g0/1` | בוחרים פורט. כל מה שמתחת חל עליו, עד `exit`. |
| ‎`no shutdown` | מדליק את הפורט. פורטים של נתב כבויים כברירת מחדל. |
| ‎`shutdown` | מכבה את הפורט. |
| ‎`radius-server host 192.168.63.1 key Osem#Aaa` | כתובת שרת ה-RADIUS, והמפתח המשותף איתו. |
| ‎`login local` | הקו מבקש **משתמש וסיסמה** מהרשימה שבתוך המכשיר. |
| ‎`interface vlan 10` | ממשק וירטואלי של ה-VLAN: הכתובת **של המכשיר עצמו** ב-VLAN הזה (לניהול, או צד ב-ASA). |
| ‎`ip address 192.168.10.240 255.255.255.0` | הכתובת והמסכה של הממשק. ברשת מקומית זו כתובת השער. |
| ‎`ip default-gateway 192.168.10.252` | השער **של המתג עצמו**, כדי שהתשובות שלו יצאו מה-VLAN. |

</div>

</details>

**⏭ מה הלאה.** נשארה פינה אחת: מעבדת הבדיקות, בלי שום הגנה.

## משימה 5 — חומת האש ASA
**📖 איך הגענו לכאן.** ‏ACL בודק כל חבילה לבד. המעבדה צריכה משהו חכם יותר.

**🌐 הרשת עכשיו.** מעבדת בדיקות (PC-LAB-1, ‏PC-LAB-2) מאחורי חומת אש שעדיין לא הוגדרה:

![1 חומת האש ASA-S, 2 המחשב PC-LAB-1, 3 המחשב PC-MGMT-1](images/step-map-m5.png)

**❗ הבעיה.** המעבדה צריכה להגיע לשרת, אבל אף אחד לא צריך להגיע **אל** המעבדה. ב-PC-LAB-1 ‏←‏ `ipconfig`, ‏`ping 192.168.50.1`: אין כתובת ואין רשת.

![הכתובת 0.0.0.0, וה-ping נכשל](images/step-m5-before.png)

נתב מעביר כל מה שלא נאסר, ולכן ב-ACL לבד צריך לרשום כל סכנה.

**🎯 מה רוצים עכשיו.** חומת אש שזוכרת שיחות: המעבדה יוצאת ומקבלת תשובות, ואף אחד לא נכנס.

**💡 הפתרון.** חומת אש עובדת הפוך: מבחוץ **הכול** אסור, אלא אם זו תשובה למישהו מבפנים (רמות אבטחה ו-`inspect`, ‏1.4).

**📋 מבצעים בפרויקט.** inside = 100, outside = 0, נתיב ברירת מחדל ל-VIP, ‏NAT, ‏DHCP למעבדה, ו-inspect ל-icmp, http, dns. נחשו מי יכול לעשות ping למי.

### 🖱 הפתרון: על מה לוחצים ומה כותבים
לוחצים על **ASA-S** ‏←‏ **CLI** ‏←‏ `enable` ‏←‏ **Enter** (אין סיסמה):

⚠️ אם פתחתם את הלשונית **Config** של ה-ASA, אולי כבר רואים `ciscoasa#`‎ או `ciscoasa(config)#`‎. אז לא כותבים שוב `enable`. מתוך ‎`(config)#`‎ כותבים קודם `end`.

![שורת הפקודה ciscoasa#](images/step-login.png)

‏**ASA-S** ‏←‏ ‏CLI. כותבים `enable`, ובסיסמה לוחצים רק **Enter**:
```
configure terminal
hostname ASA-S
interface Ethernet0/0
switchport access vlan 2
interface Ethernet0/1
switchport access vlan 1
interface Ethernet0/2
switchport access vlan 1
interface Vlan1
nameif inside
security-level 100
ip address 192.168.1.1 255.255.255.0
interface Vlan2
nameif outside
security-level 0
no ip address
ip address 192.168.10.15 255.255.255.0
exit
route outside 0.0.0.0 0.0.0.0 192.168.10.252
object network INSIDE-NET
subnet 192.168.1.0 255.255.255.0
nat (inside,outside) dynamic interface
end
```
![חלק ראשון](images/25-asa1.png)

```
configure terminal
no dhcpd auto_config outside
dhcpd address 192.168.1.10-192.168.1.30 inside
dhcpd dns 192.168.50.1
dhcpd enable inside
class-map inspection_default
match default-inspection-traffic
exit
policy-map global_policy
class inspection_default
inspect icmp
inspect http
inspect dns
exit
service-policy global_policy global
end
write memory
```
![חלק שני](images/26-asa2.png)

⚠️ ב-Packet Tracer הפקודה `exit` מתוך `object network` קופצת ישר ל-‎`#`‎, לכן כאן כותבים `end` ופותחים שוב `configure terminal`.

✅ ‏`show switch vlan` ו-`show interface ip brief`

‏![inside ו-outside](images/27-asa-vlan.png)

‏✅ **PC-LAB-1** ‏←‏ ‏IP Configuration ‏←‏ ‏**DHCP** (1): ‏192.168.1.10 מה-ASA. (ב-Packet Tracer ה-DNS יכול להישאר 0.0.0.0, לכן בודקים עם כתובות.) אחר כך `ping 192.168.50.1` עובד:

![כתובת מה-ASA](images/28-lab-dhcp.png)

![מבפנים החוצה](images/29-lab-ping.png)

✅ גולשים מ-PC-LAB-1 ל-`http://192.168.50.1`, ותוך 30 שניות ב-ASA: ‏`show xlate`

![ה-NAT של ה-ASA](images/30-xlate.png)

✅ **מבחוץ פנימה.** ‏PC-MGMT-1 ‏←‏ ‏`ping 192.168.1.10` נכשל. בהתחלה כי הנתב לא מכיר את הרשת ("unreachable" מהספק).
כדי שרק ה-ASA יחליט, מוסיפים **לצורך הבדיקה** ב-R-S-MAIN את `ip route 192.168.1.0 255.255.255.0 192.168.10.15` ועושים שוב ping:
‏**timed out**, ה-ASA חסם. אחר כך מוחקים עם `no ip route ...`‎.

![שני הניסיונות נכשלו](images/31-asa-block.png)

<div dir="rtl">

| פקודה | מה היא עושה | למה |
|---|---|---|
| ‎`nameif inside` / `outside` | נותנת לפורט תפקיד | ה-ASA עובד עם שמות, לא עם מספרים |
| ‎`security-level 100` / ‎`0` | כמה אנחנו סומכים על הצד הזה | מגבוה לנמוך מותר |
| ‎`route outside 0.0.0.0 0.0.0.0 192.168.10.252` | נתיב ברירת מחדל | אחד בלבד, ל-VIP של HSRP |
| `object network` ו-`nat ... dynamic interface` | ‏PAT דרך הפורט החיצוני | הסניף לא מכיר את 192.168.1.0 |
| ‎`dhcpd address ... inside` | ה-ASA הוא שרת DHCP | למחשבי המעבדה |
| ‎`inspect icmp` | זוכר pings שיצאו | אחרת התשובות נחסמות |

</div>

<details dir="rtl" open><summary><b>📘 הסבר שאר הפקודות של המשימה</b></summary>

<div dir="rtl">

| פקודה | מה היא עושה, ולמה היא כאן |
|---|---|
| ‎`ipconfig` | מראה את הכתובת, המסכה והשער של המחשב. |
| ‎`ping 192.168.50.1` | שולח 4 הודעות בדיקה. תשובות = הדרך עובדת ב**שני** הכיוונים. |
| ‎`hostname ASA-S` | נותן למכשיר שם, זה שרואים בשורת הפקודה. כך לא כותבים במכשיר הלא נכון. |
| ‎`interface Ethernet0/0` | בוחרים פורט. כל מה שמתחת חל עליו, עד `exit`. |
| ‎`switchport access vlan 2` | לאיזה VLAN הפורט שייך. |
| ‎`interface Vlan1` | ממשק וירטואלי של ה-VLAN: הכתובת **של המכשיר עצמו** ב-VLAN הזה (לניהול, או צד ב-ASA). |
| ‎`ip address 192.168.1.1 255.255.255.0` | הכתובת והמסכה של הממשק. ברשת מקומית זו כתובת השער. |
| ‎`no ip address` | מוחק את הכתובת הישנה, כדי לתת חדשה. |
| ‎`subnet 192.168.1.0 255.255.255.0` | איזו רשת היא האובייקט. |
| ‎`nat (inside,outside) dynamic interface` | ‏PAT: המעבדה יוצאת עם הכתובת החיצונית של ה-ASA. |
| ‎`no dhcpd auto_config outside` | מבטל הגדרה אוטומטית מהמפעל שמפריעה לנו. |
| ‎`dhcpd dns 192.168.50.1` | ה-DNS שהמעבדה מקבלת. |
| ‎`dhcpd enable inside` | מפעיל את שרת ה-DHCP של ה-ASA, בצד הפנימי. |
| ‎`class-map inspection_default` | בוחר תעבורה: "על מה מסתכלים?" |
| ‎`match default-inspection-traffic` | הפרוטוקולים הנפוצים, לפי הפורטים הרגילים שלהם. |
| ‎`policy-map global_policy` | המדיניות: "מה עושים איתה?" |
| ‎`class inspection_default` | עבור התעבורה שנבחרה למעלה: |
| ‎`service-policy global_policy global` | מפעיל את המדיניות, בכל הפורטים. |
| ‎`write memory` | אותה שמירה, כמו שכותבים ב-ASA. |
| ‎`show switch vlan` | ב-ASA: אילו פורטים באיזה VLAN. |
| ‎`show interface ip brief` | ב-ASA: הפורטים, הכתובות והמצב. |
| ‎`show xlate` | ב-ASA: התרגומים הפעילים. |

</div>

</details>

**⏭ מה הלאה.** הפרויקט שלם. עושים את הבדיקות הסופיות, ואז מתחילים את שלכם.

## 👀 רואים את זה קורה — ה-ACL והמנהרה
על מצב Simulation הסברנו ב[שיעור 1](../lesson-01/).

### א. ה-ACL זורק חבילה
ב-Realtime בודקים את הכתובת של PC-A-MGMT-2 (כאן 192.168.60.20). אחר כך **Simulation** ‏←‏ רק **ICMP** ‏←‏ עושים לה ping
מ-PC-A-ACC-1, ומתקדמים עד שמופיעה חבילה אדומה:

![התשובה של R-A-MAIN, באדום](images/sim-acl-map.png)

החבילה האדומה היא התשובה של R-A-MAIN. עכשיו פותחים את החבילה ש**נכנסה** ל-R-A-MAIN ‏←‏ לוחצים **Next Layer** פעמיים, עד שכבה 3:

![החבילה נדחתה ונזרקה](images/sim-acl.png)

תוכנת Packet Tracer מראה **את השורה המדויקת** שחסמה. זו הדרך הטובה ביותר למצוא טעות ב-ACL.

❓ כל ה-Out Layers ריקות. מה זה אומר?

<details dir="rtl"><summary>תשובה</summary>

החבילה נעצרה כאן. אין לה יציאה.

</details>

### ב. ה-VPN מסתיר את הכתובות
ב-Realtime: ‏`ping 192.168.50.1` מ-PC-E-MEET-1 עד שיש תשובה, כדי שהמנהרה תהיה למעלה. אחר כך **Simulation** ‏←‏ **ICMP** וגם
**IPSec** (לשונית Misc) ‏←‏ שוב ping, ופותחים את החבילה בשלושה מקומות:

**הנתב R-E-EXT, הכניסה למנהרה:**

![נכנסת החבילה הפרטית, יוצאת חבילת המנהרה](images/sim-vpn-in.png)

**הנתב ISP, באמצע האינטרנט:**

![הספק רואה רק את הכתובות הציבוריות](images/sim-vpn-isp.png)

**הנתב R-S-EXT, היציאה מהמנהרה:**

![החבילה המקורית חזרה](images/sim-vpn-out.png)

<div dir="rtl">

| איפה | מקור | יעד | רואים שזה ICMP? |
|---|---|---|---|
| אילת | ‎192.168.82.25 | ‎192.168.50.1 | כן |
| האינטרנט | ‎**200.150.0.1** | ‎**200.130.0.1** | **לא** |
| סכנין | ‎192.168.82.25 | ‎192.168.50.1 | כן |

</div>

```mermaid
sequenceDiagram
    participant E as R-E-EXT
    participant I as ISP
    participant S as R-S-EXT
    Note over E: wraps 192.168.82.25 to 192.168.50.1
    E->>I: 200.150.0.1 to 200.130.0.1
    I->>S: 200.150.0.1 to 200.130.0.1
    Note over S: unwraps the original packet
```

❓ השוו לשיעור 4. מה ההבדל בין זה לבין NAT?

<details dir="rtl"><summary>תשובה</summary>

‏NAT **מחליף** כתובת, ואת שאר החבילה אפשר לקרוא. ה-VPN שם את **כל** החבילה, מוצפנת, בתוך חבילה חדשה,
והצד השני מקבל אותה בדיוק כמו שהייתה.

</details>

✏️ **נסו:** ping ל-200.130.0.2 מ-PC-E-MEET-1. זה עובר במנהרה?

<details dir="rtl"><summary>תשובה</summary>

לא. היעד לא ברשימה של המנהרה, ולכן הוא יוצא עם NAT כרגיל, וב-ISP רואים ICMP.

</details>

## 🧯 לא עובד?

<div dir="rtl">

| מה רואים | כנראה | מה עושים |
|---|---|---|
| ‏`renew` נכשל אחרי ACL | אין שורת bootps, או שהיא רק בנתב אחד | `show access-lists` בשניהם |
| הפקודה `crypto` נותנת `Invalid input` | אין רישיון, או שלא עשו `reload` | `show version` ומחפשים security |
| ה-VPN לא עולה | מפתח, peer או policy שונים | משווים את שתי ההגדרות שורה שורה |
| המנהרה עלתה, ping נכשל | ה-NAT לוקח את החבילה | השורה ‎`5 deny` בשני הצדדים |
| ‏SSH נותן `Connection refused` | אין מפתח RSA, או access-class | `show ip ssh`, מתחברים מ-VLAN 10 |
| ננעלתם בחוץ | ‏AAA בלי משתמש מקומי | בקונסול: `admin` / `Osem#Adm1` |
| ‏NTP לא מסונכרן | המפתח, או מעט מדי זמן | אותו מספר מפתח בשרת, מחכים 5 דקות |

</div>

---

## בדיקות סופיות — כל הפרויקט

<div dir="rtl">

| נושא | בדיקה | התוצאה הנכונה |
|---|---|---|
| ‎VLAN / VTP | ‎`show vlan brief`, `show vtp status` | אותם VLAN-ים בסניף |
| ‎Trunk / STP | ‎`show interfaces trunk`, `show spanning-tree` | המתג הראשי הוא root |
| ‎HSRP | ‎`show standby brief` | ‏Active / Standby, והחלפה בנפילה |
| DHCP / DNS / web / FTP / דואר | מהמחשבים | הכול עובד |
| ‎DHCP Snooping | ‎`show ip dhcp snooping` | הפורטים המהימנים |
| ‎Port Security | ‏MAC זר | ‎‏err-disabled |
| ‎OSPF / EIGRP | ‎`show ip ospf neighbor`, `show ip eigrp neighbors` | ‏FULL / שני שכנים |
| ‎BGP | `show ip route bgp` בנתב EXT | נתיבי `B` לסניפים האחרים |
| ‎NAT | ‎`show ip nat translations` | סטטי, pool, ‏PAT |
| ‎VPN | ‎`show crypto isakmp sa` | ‎QM_IDLE |
| ‎ACL | ‎`show access-lists` | המונים עולים |
| ‎SSH / AAA | ‎`ssh -l osemuser` | נכנס. ‏Telnet נדחה |
| ‎NTP / Syslog | `show ntp status`, השרת | מסונכרן, יש הודעות |
| ‎ASA | ‎`show xlate` | מבפנים החוצה עובד, ההפך לא |

</div>

בסוף: שומרים בכל המכשירים, שומרים את הקובץ, **סוגרים את Packet Tracer, פותחים שוב** ובודקים שהכול נשמר.

## 🔎 מצאו את הטעות — מפרויקט אמיתי
1. ה-ACL היה רק בנתב הגיבוי.
2. הנתב באשדוד השתמש ב-RADIUS, והשרת הוגדר ל-TACACS.
3. ‏`ip ssh version 1` ומשתמשים עם `password 0`.
4. ה-VPN הצפין רק VLAN 10 ↔ VLAN 80, בלי החרגה מה-NAT.
5. ב-ASA היו שלושה נתיבי ברירת מחדל, אחד מהם לכיוון **inside**.

<details dir="rtl"><summary>תשובה</summary>

1. כל עוד הנתב הראשי הוא Active, ה-ACL לא עושה כלום.
2. הם לא מדברים באותה שפה, ולכן הכניסה תמיד נופלת למשתמש המקומי. אותו סוג ואותו מפתח בשני הצדדים.
3. ‏SSH 1 פרוץ, ו-password 0 קריא ב-`show run`. קודם יוצרים מפתחות RSA, אחר כך גרסה 2 ו-`secret`.
4. גם אם המנהרה עולה, ה-NAT לוקח את החבילות. כל הרשתות, ושורת `deny` ברשימת ה-NAT.
5. נתיב ברירת מחדל אחד בלבד, לכיוון outside, אל ה-**VIP** של HSRP.

</details>

## 🏋 תרגילים
1. ב-R-E-EXT מחליפים את המפתח ל-`Osem123` ומפעילים את המנהרה מחדש (`no crypto map VPN-MAP` ואז `crypto map VPN-MAP` ב-s0/0/0). ‏ping מאילת. מה מראה עכשיו `show crypto isakmp sa`? החזירו.
2. אפשרו להנהלת החשבונות (62) גם `ping` לשרת בלבד. איפה ברשימה השורה חייבת להיות?
3. עצרו את שירות ה-AAA בשרת והתחברו ב-SSH עם `admin`. למה זה עובד?

<details dir="rtl"><summary>תשובות (בדקנו אותן)</summary>

1. ה-ping נכשל, ובמקום `QM_IDLE` רואים `MM_KEY_EXCH ... (deleted)`‎: שלב 1 נעצר במפתח. בלי להפעיל מחדש את המנהרה שום דבר לא משתנה, כי המנהרה הישנה ממשיכה לעבוד! כדי להחזיר: `no crypto isakmp key Osem123 address 200.130.0.1`, המפתח המקורי, והפעלה מחדש.

   ![מפתח שגוי](images/35-wrong-key.png)
2. לפני ה-deny של 63.0 (שורה 60): ‏`ip access-list extended 110` ואז ‎`55 permit icmp 192.168.62.0 0.0.0.255 host 192.168.63.1`. מוחקים עם `no 55`.
3. המשתמש `osemuser` מקבל `Login invalid`, ו-`admin` נכנס: השרת לא עונה, ולכן משתמשים ב-`local`. מחזירים את השירות ל-On.

</details>

## 🎓 להסביר לבוחן
- למה הסדר של השורות ב-ACL חשוב? מהי השורה הבלתי נראית?
- מה זה שלב 1 ושלב 2? מה זה interesting traffic?
- למה חייבים להחריג את תנועת ה-VPN מה-NAT?
- ‏TACACS+‎ מול RADIUS: שלושה הבדלים.
- מה ההבדל בין ASA לנתב עם ACL? מה עושה `inspect`?

<details dir="rtl"><summary>תשובות לדוגמה</summary>

1. ההתאמה הראשונה קובעת. בסוף יש שורה בלתי נראית `deny ip any any`.
2. שלב 1: הנתבים מזדהים (מפתח) ובונים ערוץ מוגן. שלב 2: מצפין את הנתונים עצמם. ‏Interesting traffic: מה שה-ACL ב-`match address` מרשה.
3. ה-NAT קורה לפני ההצפנה: המקור משתנה, החבילה כבר לא מתאימה לרשימת ה-VPN, והיא יוצאת לא מוצפנת.
4. ‏TCP 49 מול UDP; מצפין הכול מול רק את הסיסמה; מפריד בין authentication ל-authorization, ולכן מתאים לניהול ציוד.
5. חומת אש זוכרת חיבורים (stateful) ויש לה רמות אבטחה. ‏ACL רגיל בודק כל חבילה בנפרד. ‏`inspect` עוקב אחרי פרוטוקול כדי שהתשובות שלו יחזרו.

</details>

## ✏️ מבחן יציאה (3 דקות)
1. ב-ACL יש רק שורה אחת: `deny ip host 1.1.1.1 any`. מה עובר?
2. איזה מצב מראה ששלב 1 תקין?
3. למה המשתמש המקומי חייב להיות קיים לפני `aaa new-model`?
4. מ-inside ‏(100) ל-outside ‏(0): מותר או חסום?
5. למה ליומן צריך NTP?

<details dir="rtl"><summary>תשובות</summary>

1. כלום, בגלל ה-deny הבלתי נראה.
2. ‏QM_IDLE.
3. כדי לא להינעל בחוץ.
4. מותר.
5. כדי שאפשר יהיה להשוות את השעות של כל המכשירים.

</details>

## ⏭ מה עשינו, ומה הלאה
**מה עשינו.** ארבע הבקשות של המנהל התגשמו: מסודרת (1–3), שורדת תקלות (2–4), מחברת סניפים (4), לא נותנת לזרים להיכנס (2–5).

**מסתכלים אחורה.** כל צעד ענה על בעיה שהצעד הקודם יצר. כששואלים *"למה עשיתם את זה?"*, התשובה תמיד מתחילה ב*"כי לפני זה..."*. זה בדיוק מה שבוחן רוצה לשמוע.

**מה הלאה.** **הפרויקט שלכם.** חברה אחרת, שמות וכתובות אחרים, ואותה דרך. קודם כותבים את הסיפור שלכם: מה המנהל ביקש?

## 🛠 הפרויקט שלכם
- [ ] שני ACL מורחבים ואחד סטנדרטי, ב**כל** נתב שיכול להיות Active.
- [ ] ‏VPN בין סניפים עם החרגה מה-NAT, בין הסניפים שנדרשים בהצעה **שלכם**.
- [ ] ‏SSH 2, ‏AAA מהשרת, משתמש מקומי לגיבוי, NTP עם מפתח, Syslog.
- [ ] ‏ASA עם inside/outside, ‏NAT ו-DHCP.
- [ ] טבלת הבדיקות הסופית עם צילום מסך לכל שורה, לספר הפרויקט.

➡ סיימתם? עושים את [הבדיקה הסופית](../from-zero/README.md#final): 14 בדיקות שמוכיחות שהפרויקט שלם.
