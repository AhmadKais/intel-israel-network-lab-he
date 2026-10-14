# מלכודות של Packet Tracer

‏Packet Tracer הוא *סימולטור*: הוא מממש רק חלק מ-IOS, ולפעמים בתחביר ישן יותר. כשפקודה נדחית
(‎`% Invalid input detected at '^' marker`), בדקו את הרשימה הזו לפני שאתם מניחים שטעיתם.

## חומרה

<div dir="rtl">

| בעיה | פתרון |
|---|---|
| **למתג 3650 אין חשמל / כל הפורטים למטה** | הלשונית Physical ‏←‏ גררו את המודול **AC-POWER-SUPPLY** לחריץ הריק. כל 3650 צריך את זה. |
| לנתב יש מעט מדי פורטים | ל-2911 יש Gi0/0-0/2. כבו ‏←‏ הוסיפו מודול HWIC/EHWIC ‏←‏ הדליקו. |
| מחשב נייד לא יודע WiFi | הלשונית Physical ‏←‏ כבו ‏←‏ הוציאו את מודול ה-Ethernet ‏←‏ גררו פנימה **WPC300N** ‏←‏ הדליקו. |
| איזה כבל? | בזמן הלמידה השתמשו בכבל **הברק (Automatic)**, ואז בדקו עם `show cdp neighbors` שהפורטים תואמים לטבלת הכבלים. בין מודם ה-DSL לענן משתמשים בכבל ה-**Phone**. |

</div>

## פקודות

<div dir="rtl">

| הפקודה שנכשלת | מה עושים |
|---|---|
| `switchport trunk encapsulation dot1q` במתג 3650 | ‏3650 תומך רק ב-dot1q — פשוט דלגו עליה והשתמשו ב-`switchport mode trunk`. במתג 3560 היא **חובה** לפני `mode trunk`. |
| `ipv6 unicast-routing` / `ipv6 address` נדחות במתג | ‏`sdm prefer dual-ipv4-and-ipv6 default` ‏←‏ `wr` ‏←‏ `reload`. במתג 2960 השתמשו ב-`sdm prefer lanbase-routing` אם הראשונה לא קיימת. |
| `logging host 10.10.1.10` נדחית | תחביר ישן יותר: `logging 10.10.1.10`. |
| הבלוק `tacacs server NAME` נדחה | תחביר ישן יותר: `tacacs-server host 10.10.1.11 key Intel#Tac`. |
| `ip tacacs source-interface Loopback0` נדחית | רשמו את המכשיר בשרת ה-AAA עם ה-IP של הממשק שדרכו הוא *מגיע* לשרת (בדרך כלל ה-IP של הקישור כלפי מעלה). |
| `crypto key generate rsa` שואלת על גודל | עונים ‎`1024` ‏(SSH v2 צריך לפחות 768). |
| `crypto isakmp ...`‎ / `crypto map` לא קיימות בנתב | מפעילים את רישיון האבטחה: `license boot module c2900 technology-package securityk9` ‏←‏ מאשרים ‏←‏ `wr` ‏←‏ `reload`. |
| ה-ASA דוחה את בקשת ה-`enable password` | סיסמת ה-enable של ה-ASA ריקה בהדלקה הראשונה — פשוט לחצו Enter. |
| ה-ASA ממשיך לחלק כתובות 192.168.1.x | בהגדרות ברירת המחדל יש שרת DHCP על `inside`: ‏`no dhcpd enable inside`. |
| `standby 31 ipv6 FE80::1` נדחית | השתמשו ב-`standby 31 ipv6 autoconfig`, קראו את כתובת ה-link-local הווירטואלית עם `show standby brief`, והשתמשו בה כשער הסטטי בשרתים. |
| ‏HSRP ל-IPv6 לא נתמך בגרסת ה-PT שלכם | ל-IPv6 כבר יש יתירות שער מובנית: שני מתגי ה-DIST שולחים Router Advertisements, ולכן המכשירים לומדים שני נתבי ברירת מחדל. תעדו את זה בספר הפרויקט. |
| ‏`passive-interface default` של OSPFv3 נדחית | השמיטו את שורות ה-`passive-interface`. אז OSPFv3 שולח hellos גם ל-VLANי המשתמשים — שום דבר לא נשבר, כי אף נתב לא מקשיב שם, וה-prefixes של ה-VLANים עדיין מפורסמים. כתבו בספר הפרויקט שממשקים פסיביים לא היו זמינים. |
| `ip summary-address eigrp` נדחית במתג | שימו את הפקודה על הממשק המנותב הפיזי (`Gi1/1/1`), לא על ה-SVI. |
| ‏`spanning-tree guard root` לא מופיעה | היא שם — בדקו עם `show running-config interface gi1/0/1`; כשהיא פועלת, ‏`show spanning-tree vlan 10` מראה שהפורט חסום. |

</div>

## התנהגות

<div dir="rtl">

| סימפטום | הסיבה / הפתרון |
|---|---|
| ה-ping הראשון מראה 1–2 כישלונות (timeouts) | ‏ARP עדיין מתברר. עשו ping שוב. |
| הכול ירוק אבל המחשבים מקבלים 169.254.x.x | ‏DHCP snooping זרק את ההצעה: שכחתם `ip dhcp snooping trust` על הקישור כלפי מעלה, או שכחתם `no ip dhcp snooping information option` ‏(option 82). |
| שכני OSPF תקועים ב-INIT/EXSTART | אי-התאמה במפתח ה-MD5 או ב-area, או שצד אחד פסיבי. |
| נראה שהשינויים לא נכנסים לתוקף | לחצו כמה פעמים על כפתור **Fast Forward Time**; ‏STP / ‏OSPF / ‏BGP צריכים זמן מדומה כדי להתייצב. |
| הקובץ נהיה איטי עם 150+ מכשירים | שמרו לעיתים קרובות, סגרו תוכנות אחרות, והשתמשו רק במצב **Realtime**. |
| ‏VTP מחק את כל ה-VLANים שלכם | מתג עם revision number גבוה יותר הצטרף לדומיין. לפני שמצרפים מתג כלשהו, הגדירו `vtp mode transparent` ואז חזרה ל-`client` — זה מאפס את ה-revision ל-0. |

</div>
