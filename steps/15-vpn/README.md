# שלב 15 — ‏VPN: ‏site-to-site ‏(GRE over IPsec) + גישה מרחוק

<div dir="rtl">

> ⏱ ‏2–3 שיעורים · 🎯 דרישות משרד החינוך 2, ‏21, ‏23.4, ‏20.8\
> 📁 מתחילים מ: `my-work/step14.pkt`\
> 💾 שומרים בשם: `my-work/step15.pkt`

</div>

<div dir="rtl">

> ✅ **לפני שמתחילים:** כל הסעיפים בנקודת הביקורת של שלב 14 מסומנים, ועשיתם את
> תרגיל ה-🔁 שלו בפרויקט שלכם. אל תדלגו על שלבים — כל שלב בנוי על הקובץ של השלב הקודם.

</div>

## מה יהיה לכם בסוף השלב
1. **חיפה ↔ ירושלים** מדברות עם הכתובות ה**פרטיות** שלהן דרך **מנהרה מוצפנת** שעוברת באינטרנט.
   המשתמשים בירושלים מגיעים לשרתי ה-DMZ של חיפה (DNS, דואר, ‏web, ‏NTP, ‏FTP, ‏AAA).
2. **עובד מהבית** מתחבר ללקוח ה-VPN שבמחשב שלו אל חיפה, ועובד כאילו הוא במשרד.

```
   Haifa LAN 10.10.0.0/16                                           Jerusalem LAN 10.20.0.0/16
        │                                                                   │
   R-HFA-EDGE ══════ Tunnel0 172.16.12.1 ⇄ 172.16.12.2 (GRE, encrypted by IPsec) ══════ R-JLM-EDGE
   200.1.1.2            ... across ISP-A ⇄ ISP-B (the internet sees only ESP) ...        200.2.1.2
        ▲
        ╚═══════ remote-access VPN ═══════ PC-HOME-01 (200.3.50.10, gets 172.16.250.x)
```
(‏R-HFA-EDGE ‏(200.1.1.2) ו-R-JLM-EDGE ‏(200.2.1.2) מחוברים ב-Tunnel0 ‏172.16.12.1 ⇄ 172.16.12.2 — ‏GRE
שמוצפן ב-IPsec. דרך ISP-A ו-ISP-B האינטרנט רואה רק ESP. בנוסף, PC-HOME-01 ‏(200.3.50.10) מתחבר לחיפה
ב-VPN של גישה מרחוק ומקבל כתובת 172.16.250.x.)

---

## חלק 1 — קודם מבינים (בשפה פשוטה)

### 1.1 למה VPN?
חיפה וירושלים מחוברות דרך **האינטרנט**:
- כתובות פרטיות (10.x) **לא יכולות** לעבור באינטרנט (שלב 12);
- כל מה שנשלח שם אחרים יכולים **לקרוא** בדרך.

**‏VPN ‏(Virtual Private Network, רשת פרטית וירטואלית)** פותר את שתי הבעיות: הוא בונה **מנהרה** —
החבילה הפרטית מוכנסת **בתוך** חבילה ציבורית, ו**מוצפנת**. השוואה: שמים מכתב בתוך קופסה משוריינת
ונעולה ושולחים את הקופסה בדואר רגיל. הדואר רואה רק את הכתובת שעל הקופסה מבחוץ.

### 1.2 ‏IPsec — המנעול
**‏IPsec** מצפין את החבילות ומאמת אותן. הוא מתחיל בשני שלבים (phases):

<div dir="rtl">

| שלב | מה קורה | פקודות |
|---|---|---|
| ‎**‏Phase 1 ‏(ISAKMP / IKE)** | שני הנתבים בודקים זה את זהות זה (מפתח משותף מראש, pre-shared key) ומסכימים איך לדבר בבטחה | ‎`crypto isakmp policy`, `crypto isakmp key` |
| ‎**‏Phase 2 ‏(IPsec SA)** | הם מסכימים איך להצפין את ה**נתונים** (ESP + ‏AES + ‏SHA) | ‎`crypto ipsec transform-set` |

</div>

**‏crypto map** על ממשק האינטרנט אומר **איזו** תעבורה להצפין ו**למי**.

### 1.3 ‏GRE — המנהרה
**‏GRE** יוצר ממשק וירטואלי (`Tunnel0`) בין שתי כתובות ציבוריות, כמו כבל פרטי דרך האינטרנט. ‏GRE לבד
לא מצפין — לכן **מצפינים את חבילות ה-GRE עם IPsec**: **‏GRE over IPsec**.

### 1.4 למה GRE + ‏IPsec ולא IPsec לבד? (שאלה מצוינת לבחינה)
בגלל ה-**static NAT** בחיפה (שלב 12). שרת ה-web תמיד מתורגם 10.10.200.13 ↔ 200.1.10.3. עם IPsec רגיל,
התשובה של שרת ה-web למחשב בירושלים הייתה **מתורגמת לפני ההצפנה** — כתובת שגויה — הכול נשבר.
עם GRE, התשובה יוצאת דרך `Tunnel0`, שהוא **לא** ממשק NAT ‏←‏ היא לא מתורגמת ‏←‏ הכתובות הפרטיות נשארות
פרטיות מקצה לקצה. הבעיה נפתרה.

### 1.5 ‏VPN לגישה מרחוק
המחשב של עובד מהבית הוא לא נתב. נתב הקצה משמש כ**שרת VPN** ‏("Easy VPN"):
1. לקוח ה-VPN במחשב מתחבר עם שם **קבוצה** + מפתח קבוצה, ועם **שם משתמש** + סיסמה;
2. הנתב נותן למחשב כתובת ממאגר (‎`172.16.250.10 – .100`) ואת שרת ה-DNS;
3. התעבורה של המחשב למטה עוברת דרך המנהרה המוצפנת (דרישה 23.4).

### 1.6 רישיון האבטחה
פקודות ההצפנה ב-Cisco 2911 צריכות את הרישיון **securityk9**. ב-PT מפעילים אותו עם פקודה אחת ואתחול.

---

## חלק 2 — הכנה
‏**File → Open** ‏←‏ `my-work/step14.pkt` ‏←‏ **File → Save As** ‏←‏ `my-work/step15.pkt`.

## חלק 3 — בונים
אין מה להוסיף — נתבי הקצה, ה-ASA ו-PC-HOME-01 כבר קיימים.

---

## חלק 4 — מגדירים

### 4.1 מפעילים את רישיון האבטחה — ב-R-HFA-EDGE **וגם** ב-R-JLM-EDGE
```
enable
configure terminal
license boot module c2900 technology-package securityk9
```
הנתב מציג טקסט של רישיון ושואל `ACCEPT? [yes/no]:`‎ ‏←‏ הקלידו **`yes`**.
```
end
copy running-config startup-config
reload
```
לחצו **Enter** כדי לאשר את האתחול. חכו שהנתב יעלה (Fast Forward Time), והתחברו שוב.
בדיקה: `show version` ‏←‏ בטבלת הרישיונות `securityk9` הוא **Permanent** / **Active**.

### 4.2 ‏R-HFA-EDGE — ‏site-to-site (הצד של חיפה)
```
enable
configure terminal
! ===== 1. the GRE tunnel =====
interface tunnel 0
 description GRE to R-JLM-EDGE (encrypted by IPsec)
 ip address 172.16.12.1 255.255.255.252
 tunnel source gi0/1
 tunnel destination 200.2.1.2
 exit
! Jerusalem's private block goes into the tunnel (a static route - req. 22.17)
ip route 10.20.0.0 255.255.0.0 172.16.12.2

! ===== 2. IPsec phase 1 =====
crypto isakmp policy 10
 encryption aes 256
 hash sha
 authentication pre-share
 group 5
 lifetime 86400
 exit
! the shared secret with Jerusalem; no-xauth = it's a router, don't ask it for a username
crypto isakmp key Intel#S2S-Key address 200.2.1.2 no-xauth

! ===== 3. IPsec phase 2 =====
crypto ipsec transform-set S2S-SET esp-aes 256 esp-sha-hmac
ip access-list extended S2S-GRE
 remark --- encrypt the GRE packets between the two edges ---
 permit gre host 200.1.1.2 host 200.2.1.2
 exit
crypto map VPN-MAP 10 ipsec-isakmp
 set peer 200.2.1.2
 set transform-set S2S-SET
 match address S2S-GRE
 exit
! ===== 4. apply on the internet interface =====
interface gi0/1
 crypto map VPN-MAP
 end
copy running-config startup-config
```
ההערות אומרות: 1. מנהרת ה-GRE — הבלוק הפרטי של ירושלים נכנס למנהרה (נתיב סטטי — דרישה 22.17);
2. ‏IPsec שלב 1 — הסוד המשותף עם ירושלים; ‏no-xauth = זה נתב, לא לבקש ממנו שם משתמש; 3. ‏IPsec שלב 2 —
מצפינים את חבילות ה-GRE בין שני נתבי הקצה; 4. מחילים על ממשק האינטרנט.

תראו ‎`%CRYPTO-6-ISAKMP_ON_OFF: ISAKMP is ON` — טוב.

### 4.3 ‏R-JLM-EDGE — ‏site-to-site (תמונת המראה)
```
enable
configure terminal
interface tunnel 0
 description GRE to R-HFA-EDGE (encrypted by IPsec)
 ip address 172.16.12.2 255.255.255.252
 tunnel source gi0/1
 tunnel destination 200.1.1.2
 exit
ip route 10.10.0.0 255.255.0.0 172.16.12.1

crypto isakmp policy 10
 encryption aes 256
 hash sha
 authentication pre-share
 group 5
 lifetime 86400
 exit
crypto isakmp key Intel#S2S-Key address 200.1.1.2 no-xauth
crypto ipsec transform-set S2S-SET esp-aes 256 esp-sha-hmac
ip access-list extended S2S-GRE
 permit gre host 200.2.1.2 host 200.1.1.2
 exit
crypto map VPN-MAP 10 ipsec-isakmp
 set peer 200.1.1.2
 set transform-set S2S-SET
 match address S2S-GRE
 exit
interface gi0/1
 crypto map VPN-MAP
 end
copy running-config startup-config
```

<div dir="rtl">

> ה-`redistribute static` משלב 13 נותן עכשיו גם את הנתיב ‎`10.10.0.0/16` ל-CC1/CC2 — כך כל ירושלים
> יודעת ש"חיפה נמצאת דרך נתב הקצה". ה-ACL של CBAC ‏`WAN-IN` כבר מכניסה את ה-VPN.

</div>

### 4.4 ‏ASA — מכניסים את ירושלים
```
enable
configure terminal
access-list OUTSIDE_IN extended permit ip 10.20.0.0 255.255.0.0 10.10.0.0 255.255.0.0
end
write memory
```
(‏10.10.0.0/16 כולל את ה-DMZ ‏10.10.200.0/24 — כך ירושלים מגיעה לרשת הפנימית **וגם** לשרתי ה-DMZ.)

### 4.5 ‏R-HFA-EDGE — שרת VPN לגישה מרחוק
```
enable
configure terminal
! ===== who may log in =====
aaa new-model
aaa authentication login default group tacacs+ local
aaa authentication login VPN-AUTH local
aaa authorization network VPN-GROUP local
username remote1 secret Intel#Remote1
! ===== addresses for remote users =====
ip local pool RA-POOL 172.16.250.10 172.16.250.100
! ===== phase 1 for clients =====
crypto isakmp policy 20
 encryption aes 256
 hash sha
 authentication pre-share
 group 2
 exit
! ===== the group the PC logs into =====
crypto isakmp client configuration group HQ-RA
 key Intel#RA-Group
 dns 10.10.200.11
 domain intel.lab
 pool RA-POOL
 exit
! ===== phase 2 for clients =====
crypto ipsec transform-set RA-SET esp-aes 256 esp-sha-hmac
crypto dynamic-map RA-DYN 10
 set transform-set RA-SET
 reverse-route
 exit
! ===== add the clients to the same crypto map =====
crypto map VPN-MAP client authentication list VPN-AUTH
crypto map VPN-MAP isakmp authorization list VPN-GROUP
crypto map VPN-MAP client configuration address respond
crypto map VPN-MAP 65535 ipsec-isakmp dynamic RA-DYN
 end
copy running-config startup-config
```
ההערות אומרות: מי רשאי להתחבר; כתובות למשתמשים מרוחקים; שלב 1 ללקוחות; הקבוצה שהמחשב מתחבר אליה;
שלב 2 ללקוחות; מוסיפים את הלקוחות לאותו crypto map.

וב-**ASA** — משתמשים מרוחקים רשאים להגיע למטה:
```
configure terminal
access-list OUTSIDE_IN extended permit ip 172.16.250.0 255.255.255.0 10.10.0.0 255.255.0.0
end
write memory
```
(רשימת ה-PAT ‏`NAT-HFA` משלב 12 כבר מדלגת על 172.16.250.0/24 — התכוננו לזה.)

### 4.6 לקוח ה-VPN של העובד מהבית (לחיצה אחרי לחיצה)
1. לחצו על **PC-HOME-01** ‏←‏ **Desktop** ‏←‏ **VPN**.
2. מלאו:

<div dir="rtl">

| שדה | ערך |
|---|---|
| ‎GroupName | ‎`HQ-RA` |
| ‎Group Key | ‎`Intel#RA-Group` |
| ‎Host IP (Server IP) | ‎`200.1.1.2` |
| ‎Username | ‎`remote1` |
| ‎Password | ‎`Intel#Remote1` |

</div>

3. לחצו **Connect** ‏←‏ אחרי רגע: **"VPN is connected"**.
4. סגרו את חלון ה-VPN ‏←‏ Command Prompt ‏←‏ `ipconfig` ‏←‏ תראו כתובת נוספת ‎`172.16.250.x`.

### 4.7 מה הפקודות החדשות אומרות

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`license boot module ... securityk9` | פתיחת יכולות ההצפנה (צריך אתחול) |
| ‎`interface tunnel 0` + `tunnel source` / `tunnel destination` | כבל וירטואלי מהכתובת הציבורית שלי לשלהם |
| ‎`crypto isakmp policy 10` ‏(encryption/hash/authentication/group) | איך בודקים זה את זה בשלב 1 (חייב להתאים בשני הצדדים) |
| ‎`crypto isakmp key KEY address PEER no-xauth` | הסוד המשותף עם העמית (peer) הזה, בלי לבקש שם משתמש |
| ‎`crypto ipsec transform-set ... esp-aes 256 esp-sha-hmac` | איך הנתונים מוצפנים (AES-256) ונבדקים (SHA) |
| ‎`crypto map VPN-MAP 10 ipsec-isakmp` / `set peer` / `match address` | "הצפן תעבורה שמתאימה ל-ACL הזו, לכיוון העמית הזה" |
| `interface gi0/1` ואז `crypto map VPN-MAP` | הדלקת ההצפנה על ממשק האינטרנט |
| ‎`ip local pool RA-POOL ...`‎ | כתובות לחלק למשתמשים מרוחקים |
| ‎`crypto isakmp client configuration group HQ-RA` | הקבוצה שלקוח ה-VPN מתחבר אליה (מפתח, ‏DNS, מאגר) |
| ‎`crypto dynamic-map` + ‎`... 65535 ipsec-isakmp dynamic` | תבנית ללקוחות שאת הכתובת שלהם לא יודעים מראש |
| ‎`reverse-route` | מוסיף אוטומטית נתיב לכל לקוח שמתחבר |

</div>

---

## חלק 5 — בודקים את העבודה

### 5.1 גורמים למנהרה לעלות
המנהרה עולה רק כשתעבורה צריכה אותה. מ-**PC-JLM-SAL-01**: ‏`ping 10.10.16.1` — פינג אחד או שניים
ראשונים יכולים להיכשל בזמן שהמנהרה נבנית, ואז מגיעות תשובות.

### 5.2 בנתבים
```
R-HFA-EDGE# show crypto isakmp sa
dst             src             state          conn-id status
200.2.1.2       200.1.1.2       QM_IDLE           1001 ACTIVE    <- phase 1 up with Jerusalem
200.1.1.2       200.3.50.10     QM_IDLE           1002 ACTIVE    <- the teleworker (when connected)
R-HFA-EDGE# show crypto ipsec sa
    #pkts encaps: 57, #pkts encrypt: 57, ...        <- growing while you ping = encrypted
    #pkts decaps: 57, #pkts decrypt: 57, ...
R-HFA-EDGE# show interfaces tunnel 0              <- Tunnel0 is up, line protocol is up
R-HFA-EDGE# show ip route static                  <- S 10.20.0.0/16 via 172.16.12.2
SWL3-JLM-CC1# show ip route | include 10.10.0.0  <- D EX 10.10.0.0/16 via 10.20.4.1
```
(שלב 1 פעיל מול ירושלים, והעובד מהבית (כשהוא מחובר); מוני ה-encaps/decaps גדלים בזמן ה-ping = מוצפן;
‏Tunnel0 למעלה; הנתיב הסטטי 10.20.0.0/16 דרך 172.16.12.2; ב-CC1 ‏`D EX 10.10.0.0/16` דרך 10.20.4.1.)

### 5.3 בדיקות

<div dir="rtl">

| מאיפה | עושים | מה אמור לקרות |
|---|---|---|
| ‎PC-JLM-SAL-01 | ‎`ping 10.10.16.1` | ✅ כתובת **פרטית** של חיפה — דרך ה-VPN |
| ‎PC-JLM-SAL-01 | ‎`tracert 10.10.200.13` | 10.20.10.2 → 10.20.4.1 → **172.16.12.1** (המנהרה!) → … |
| ‎PC-JLM-SAL-01 | בדפדפן: Web Browser ‏←‏ `http://www.intel.lab` | ✅ גם ה-DNS ‏10.10.200.11 נגיש עכשיו |
| ‎PC-JLM-SAL-01 | ‎`nslookup ftp.intel.lab` | ‏10.10.200.15 (שירותי DMZ דרך VPN — דרישה 21) |
| ‎SWL3-JLM-CC1 | ‎`show ntp status` | מסונכרן ל-10.10.200.14 (דרישה 20.8) |
| ‎PC-HFA-IT-01 | ‎`ssh -l admin 10.20.0.11` | ✅ ה-IT של המטה מנהל את ירושלים דרך ה-VPN |
| PC-HOME-01 (VPN מחובר) | `ping 10.10.1.10`, גלישה ל-`www.intel.lab` | ‎✅ |
| PC-HOME-01 (VPN מנותק) | ‎`ping 10.10.1.10` | ‎❌ |

</div>

### 5.4 רואים את ההצפנה (מצב Simulation)
1. ‏**Simulation** ‏←‏ **Edit Filters** ‏←‏ **ICMP** (וגם ISAKMP/ESP אם יש).
2. מ-PC-JLM-SAL-01 עשו ping למחשב בחיפה. עקבו אחרי החבילה.
3. לחצו עליה כשהיא על כבל **בין הספקים** ‏←‏ הכותרת החיצונית היא ‎`200.2.1.2 → 200.1.1.2`, פרוטוקול
   **ESP**. הכתובות הפרטיות שבפנים לא נראות לספקים. 🔒
4. חזרה ל-**Realtime**.

---

## חלק 6 — שומרים
‏`copy running-config startup-config` בשני נתבי הקצה, ‏`write memory` ב-ASA ‏←‏ **File → Save**.

## נקודת ביקורת
- [ ] ‏`QM_IDLE` מול ירושלים; מוני ה-encaps/decaps גדלים
- [ ] המחשבים בירושלים מגיעים לכתובות הפרטיות של חיפה ולשרתי ה-DMZ לפי שם
- [ ] ה-NTP של ירושלים מסונכרן לחיפה
- [ ] העובד מהבית מתחבר ומגיע לשרתי המטה

## אם משהו לא עובד

<div dir="rtl">

| בעיה | פתרון |
|---|---|
| פקודות `crypto` לא קיימות | הרישיון לא פעיל — 4.1 ו-**reload** |
| שלב 1 אף פעם לא עולה (אין `QM_IDLE`) | אי-התאמה ב-policy (ההצפנה / ה-hash / ה-group חייבים להיות זהים בשני הצדדים) או מפתחות שונים |
| המנהרה למעלה, הפינגים נכשלים | חסר הנתיב הסטטי לתוך המנהרה; חסרה ב-ASA שורת ה-ACL ל-10.20.0.0/16 |
| ה-ACL של ירושלים חוסמת את ה-VPN | ‏WAN-IN חייבת להתיר isakmp, ‏esp **וגם** gre מ-200.1.1.2 |
| העמית ב-S2S מבקש שם משתמש / נשבר אחרי שהוספנו גישה מרחוק | חסר `no-xauth` בשורת `crypto isakmp key` |
| לקוח ה-VPN: ‏"authentication failed" | שגיאת כתיב בשם / במפתח של הקבוצה או במשתמש / בסיסמה; חסר `aaa authorization network VPN-GROUP local` |
| הלקוח מתחבר אבל לא מגיע למטה | חסרה ב-ASA ה-ACL ל-172.16.250.0/24 |

</div>

## אתגר
לקריית גת אין VPN. בלי להוסיף אחד, באילו שירותי DMZ קריית גת עדיין יכולה להשתמש, ואיך?

<details dir="rtl"><summary>תשובה</summary>

רק במה שמפורסם באינטרנט **וגם** נגיש ב-IPv4 מקריית גת:
- **‏NTP** — ל-DIST1 יש דרך IPv4 (קישור ה-legacy + ‏PAT) והוא מסתנכרן לכתובת הציבורית 200.1.10.4 ‏←‏
  דרישה 20.8 מתקיימת.
- **‏Web** — רק מכשירי ה-IPv4 מדור קודם יכולים לפתוח את 200.1.10.3; משתמשי IPv6 לא (האתגר של שלב 14).
- דואר / ‏DNS / ‏FTP / ‏AAA לא מפורסמים ‏←‏ לא. בגלל זה לקריית גת יש שרתי DNS, דואר, ‏syslog ו-AAA
  **משלה**. פתרון אמיתי יהיה מנהרה שלישית על IPv6 או DMZ ‏dual-stack — כתבו את הפשרה בספר הפרויקט.
</details>

---

## 🛠 הפרויקט שלכם

עשיתם את השלב הזה על הדוגמה של אינטל. עכשיו עשו אותו שוב בפרויקט **שלכם**, עם הערכים
מהתוכנית **שלכם** (`my-project/plan.md`). הפקודות זהות — רק הערכים משתנים.

<div dir="rtl">

| בדוגמה | בפרויקט שלכם — לוקחים מ |
|---|---|
| מנהרת GRE ‏‎`172.16.12.0/30` בין המטה לסניף 2 | ‏‎/30 משלכם למנהרה, בין שני אתרי ה-IPv4 **שלכם** (דרישה 2) |
| מפתח משותף `Intel#S2S-Key` | תוכנית, חלק ו |
| קבוצת גישה מרחוק `HQ-RA`, מאגר `RA-POOL 172.16.250.10–100`, משתמש `remote1` | שם הקבוצה שלכם, המאגר שלכם, המשתמש והסיסמאות שלכם (דרישה 23.4) |

</div>

**בדיקה:** ‏`show crypto isakmp sa` מראה `QM_IDLE`; ‏ping בין שני האתרים עובר דרך המנהרה; המחשב הביתי
מתחבר עם לקוח ה-VPN ומגיע למטה.

💾 שמרו בשם `my-project/step15.pkt`.

---

## 🎓 מסבירים לבוחן

בבחינה, הבוחן מצביע על הפרויקט **שלכם** ומבקש **להסביר** ו**להראות**. תרגלו כל שאלה
**בקול**, ואז הראו את התשובה בפרויקט שלכם — לא בדוגמה. כסו את התשובה, ענו בעצמכם, ורק אז
פתחו והשוו.

★1–★3 = שאלה ממאגר השאלות של משרד החינוך (רמת קושי 1–3).
◆ = לא במאגר, אבל בוחנים שואלים אותה לעיתים קרובות.

**1. ★2 מהו VPN ‏site-to-site? מהו VPN לגישה מרחוק (remote access)?**

<details dir="rtl"><summary>תשובה</summary>

‏Site-to-site: מנהרה מוצפנת קבועה בין שני נתבים, שמחברת שני משרדים; המשתמשים לא מרגישים כלום. גישה
מרחוק: משתמש אחד (בבית) מריץ לקוח VPN ומתחבר לשרת ה-VPN של החברה דרך האינטרנט.

**איפה מראים:** `show crypto isakmp sa`; המחשב הביתי ‏←‏ Desktop ‏←‏ VPN
</details>

**2. ★2 מה קורה בשלב 1 של הקמת ה-VPN? הראה את זה בפרויקט.**

<details dir="rtl"><summary>תשובה</summary>

‏IKE שלב 1 ‏(ISAKMP): שני העמיתים מסכימים על policy — הצפנה (AES), ‏hash ‏(SHA), אימות (pre-shared
key), קבוצת Diffie-Hellman, ‏lifetime — מאמתים זה את זה ובונים ערוץ מאובטח. אחר כך שלב 2 מנהל משא ומתן
על ה-IPsec SAs ‏(transform set) שמצפינים את נתוני המשתמשים.

**איפה מראים:** `show crypto isakmp sa` ‏←‏ `QM_IDLE`; ‏`show crypto ipsec sa` ‏←‏ מוני encrypted/decrypted
</details>

**3. ★3 מהו Diffie-Hellman?**

<details dir="rtl"><summary>תשובה</summary>

שיטה שבה שני צדדים יוצרים את **אותו מפתח סודי** דרך רשת לא מאובטחת, בלי לשלוח אף פעם את המפתח עצמו.
קבוצת ה-DH קובעת את חוזק המפתח.

**איפה מראים:** `show running-config` ‏←‏ `crypto isakmp policy` ‏←‏ `group`
</details>

**4. ★3 מה ההבדל בין הצפנה סימטרית לא-סימטרית? תן דוגמאות לפרוטוקולים מכל סוג.**

<details dir="rtl"><summary>תשובה</summary>

סימטרית: אותו מפתח מצפין ומפענח — מהירה (AES, ‏3DES, ‏DES). א-סימטרית: מפתח ציבורי ומפתח פרטי — איטית,
משמשת להחלפת מפתחות ולחתימות (RSA, ‏Diffie-Hellman, ‏ECC).

**איפה מראים:** —
</details>

**5. ★2 מהי שלמות (integrity), ואילו פרוטוקולים עושים hashing?**

<details dir="rtl"><summary>תשובה</summary>

שלמות = הוכחה שהנתונים לא שונו בדרך. ‏hash ‏("טביעת אצבע") של הנתונים נשלח איתם; כל שינוי נותן hash
אחר. ‏MD5, ‏SHA-1, ‏SHA-256 (ב-VPN בתור HMAC).

**איפה מראים:** `crypto ipsec transform-set` ‏←‏ `esp-sha-hmac`
</details>

**6. ◆ למה GRE over IPsec ולא רק IPsec?**

<details dir="rtl"><summary>תשובה</summary>

‏IPsec לבד נושא רק IP ‏unicast; פרוטוקולי ניתוב משתמשים ב-multicast. ‏GRE עוטף הכול (כולל multicast)
בממשק מנהרה, ו-IPsec מצפין את חבילות ה-GRE. (ובפרויקט הזה יש סיבה נוספת: ה-static NAT בחיפה — סעיף 1.4.)

**איפה מראים:** `show interfaces tunnel 0`
</details>

---

## 🔁 עושים שוב — בלי המדריך

הבוחן יכול לבקש מכם להגדיר משהו שוב, מולו. תצליחו רק אם עשיתם את זה **בלי המדריך** לפני כן.
עשו את התרגיל הזה בפרויקט שלכם:

בעותק של הקובץ שלכם, מחקו את הגדרות ה-crypto מקצה אחד של המנהרה. בלי העמוד הזה, כתבו אותן שוב מתוך
התוכנית שלכם (policy, מפתח, ‏transform set, ‏ACL או profile, החלה על הממשק). יעד: **‏15 דקות**. אחר כך
עשו ping דרך המנהרה והראו `show crypto isakmp sa` ואת המונים של `show crypto ipsec sa`.

---

## 👩‍🏫 הערות למורה
- **שיעור 1:** למה VPN (ההשוואה לקופסה המשוריינת), שלבי IPsec, ‏GRE, *למה GRE over IPsec* (הסיפור של
  ה-static NAT) ‏←‏ רישיון + אתחול בשני נתבי הקצה.
- **שיעור 2:** הגדרת site-to-site ‏←‏ בדיקות ‏←‏ ההצפנה במצב Simulation על המקרן.
- **שיעור 3:** גישה מרחוק ‏←‏ לקוח VPN ‏←‏ בדיקות ‏←‏ אתגר.
- **שאלות נפוצות של תלמידים**
  - *"למה הפינג הראשון הולך לאיבוד?"* — המנהרה נבנית לפי דרישה (שלב 1 + 2 לוקחים רגע).
  - *"למה מספר 65535 ל-dynamic map?"* — עמיתים מוגדרים (ירושלים, מספר 10) חייבים להיבדק קודם; התבנית
    של "כל אחד" חייבת להיות אחרונה.
- **טעויות אופייניות:** שכחת האתחול אחרי הרישיון; ‏ISAKMP policy שלא תואם; שכחת שורות ה-ACL ב-ASA.
