# טבלת סיסמאות

<div dir="rtl">

> **אלה הסיסמאות של הדוגמה.** בפרויקט שלכם חייבות להיות סיסמאות משלכם — מלאו את חלק ו
> ב-[project-plan-template.md](project-plan-template.md).

</div>

ספר הפרויקט חייב לכלול טבלת סיסמאות. אלה סיסמאות של **מעבדה** — לעולם אל תשתמשו בהן
ברשת אמיתית.

<div dir="rtl">

> הקלידו כל סיסמה **בדיוק** כפי שהיא כתובה — באנגלית, כולל אותיות גדולות/קטנות וסימנים.

</div>

<div dir="rtl">

| מטרה | איפה | ערך |
|---|---|---|
| ‏Privileged EXEC (מצב ‎`#`‎) | ‏`enable secret` בכל נתב/מתג | ‎`Intel#En4ble` |
| קו ה-console (לפני AAA) | ‎`line console 0` | ‎`Intel#Con` |
| משתמש מנהל מקומי (SSH + גיבוי ל-AAA) | ‎`username admin privilege 15 secret` | ‎`Intel#Adm1n` |
| מפתח משותף TACACS+ | מכשירים ↔ שרת AAA | ‎`Intel#Tac` |
| מפתח משותף RADIUS (לא חובה, WPA2-Enterprise) | נקודת גישה ↔ שרת AAA | ‎`Intel#Rad` |
| סיסמת VTP | כל המתגים | ‎`Intel#Vtp` |
| מפתח OSPF MD5 מספר 1 | קישורים מנותבים בחיפה | ‎`Intel#Ospf` |
| ‏key chain של EIGRP MD5 | ירושלים | ‎`Intel#Eigrp` |
| ‏WiFi — עובדים (`INTEL-CORP`) | ‎AP-HFA-A-EMP | ‎`IntelCorp#2026` |
| ‏WiFi — אורחים (`INTEL-GUEST`) | ‎AP-HFA-A-GUEST | ‎`WelcomeGuest2026` |
| ‏enable של ה-ASA | ‎ASA-HFA-FW1 | ‎`Intel#En4ble` |
| מפתח משותף ל-VPN בין אתרים | ‎R-HFA-EDGE ↔ R-JLM-EDGE | ‎`Intel#S2S-Key` |
| מפתח הקבוצה `HQ-RA` ל-VPN מרחוק | ‎R-HFA-EDGE | ‎`Intel#RA-Group` |
| משתמש VPN מרחוק | ‎`remote1` | ‎`Intel#Remote1` |
| משתמשי דואר (כולם) | ‎SRV-HFA-DMZ-MAIL / SRV-KG-MAIL | ‎`Mail#2026` |
| משתמש FTP ‏`ftpadmin` | ‎SRV-HFA-DMZ-FTP | ‎`Intel#Ftp` |

</div>

בשלבים 00–02 משתמשים רק בשתי השורות הראשונות: `Intel#En4ble` ו-`Intel#Con`.
