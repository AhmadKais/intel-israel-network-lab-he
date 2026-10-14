# שלב 11 — חומת אש ASA, ‏DMZ ושרת ה-NTP הראשי

<div dir="rtl">

> ⏱ ‏3 שיעורים · 🎯 דרישות משרד החינוך 11, ‏12, ‏21, ‏20.8, ‏22.13\
> 📁 מתחילים מ: `my-work/step10.pkt`\
> 💾 שומרים בשם: `my-work/step11.pkt`

</div>

<div dir="rtl">

> ✅ **לפני שמתחילים:** כל הסעיפים בנקודת הביקורת של שלב 10 מסומנים, ועשיתם את
> תרגיל ה-🔁 שלו בפרויקט שלכם. אל תדלגו על שלבים — כל שלב בנוי על הקובץ של השלב הקודם.

</div>

## מה יהיה לכם בסוף השלב
**חומת אש ASA 5506-X** מחלקת את המטה בחיפה לשלושה אזורי אבטחה, וב-**DMZ** יושבים ששת השרתים
שמשרד החינוך דורש (DNS, ‏Email, ‏Web, ‏NTP, ‏FTP, ‏AAA). **נתב קצה** (edge router) מחכה בצד החיצוני,
מוכן לאינטרנט (שלב 12). כל מכשיר במטה לוקח את השעה מ**שרת ה-NTP הראשי**.

```
                         R-HFA-EDGE  (Gi0/0 10.10.7.1)          -> internet in step 12
                              │ Gi1/1  OUTSIDE (level 0)  10.10.7.2
                       ┌──────┴──────┐
     inside (100)  Gi1/2│ ASA-HFA-FW1 │Gi1/3  DMZ (level 50)
     10.10.1.254   ────┘             └────  10.10.200.1 ── SW-HFA-DMZ ── 6 servers
           │                                                   (10.10.200.11 – .16)
     SW-HFA-SRV Fa0/24  (VLAN 100 — the cores route everything unknown here)
```
(‏R-HFA-EDGE מחובר לצד ה-OUTSIDE של ה-ASA ‏(רמה 0) — האינטרנט יגיע בשלב 12. צד ה-inside ‏(100) של
ה-ASA ‏10.10.1.254 מחובר ל-SW-HFA-SRV פורט Fa0/24 ‏(VLAN 100 — מתגי ה-core מנתבים לכאן כל יעד לא
מוכר). צד ה-DMZ ‏(רמה 50) ‏10.10.200.1 מחובר ל-SW-HFA-DMZ ולששת השרתים ‏(10.10.200.11 – ‏.16).)

---

## חלק 1 — קודם מבינים (בשפה פשוטה)

### 1.1 מה חומת אש עושה
חומת אש (firewall) יושבת בין רשתות ומחליטה, חבילה אחרי חבילה, מה מותר לעבור. בניגוד לנתב (שרק
מוצא את הדרך), התפקיד של חומת אש הוא **להגיד לא**.

### 1.2 אזורים ורמות אבטחה
ה-ASA נותן לכל ממשק **שם** ו**רמת אמון** (security level) בין 0 ל-100:

<div dir="rtl">

| אזור | השם ב-ASA | רמה | מה יש שם |
|---|---|---|---|
| ‏Inside (פנים) | ‎`inside` | ‎**100** | כל הרשת המקומית — הכי אמין |
| ‎‏DMZ | ‎`dmz` | ‎**50** | שרתים שהאינטרנט רשאי להגיע אליהם |
| ‏Outside (חוץ) | ‎`outside` | ‎**0** | לכיוון האינטרנט — לא אמין |

</div>

**הכלל:** תעבורה מרמה **גבוהה** לרמה **נמוכה** **מותרת**; מ**נמוכה לגבוהה** היא **חסומה** — אלא
אם ACL מתירה אותה.

<div dir="rtl">

| מ ‏←‏ אל | ברירת מחדל |
|---|---|
| מ-inside ל-DMZ, מ-inside ל-outside | ✅ מותר |
| מה-DMZ ל-inside | ❌ חסום |
| מ-outside ל-DMZ / ל-inside | ❌ חסום (פותחים חורים מדויקים עם ACL) |

</div>

השוואה: בניין משרדים. עובדים (inside) רשאים ללכת לקבלה (DMZ) ולצאת לרחוב (outside). מבקרים מהרחוב
רשאים להיכנס רק לקבלה — ורק אם הם ברשימה. אף אחד מהקבלה לא נכנס למשרדים.

### 1.3 ‏Stateful — התשובות חוזרות אוטומטית
ה-ASA **זוכר** כל שיחה שהתחילה מבפנים. כשהתשובה חוזרת מבחוץ, ה-ASA מזהה אותה ומכניס אותה — בלי
צורך ב-ACL. ‏Ping הוא היוצא מן הכלל (הוא לא "שיחה" אמיתית), ולכן אומרים ל-ASA **לבדוק** (inspect)
את ICMP, ואז גם תשובות ה-ping חוזרות.

### 1.4 בשביל מה ה-DMZ?
שרתים שהאינטרנט חייב להגיע אליהם (כמו האתר) הם המכונות שמותקפות הכי הרבה. אם אחד מהם נפרץ, התוקף
נוחת ב-**DMZ** — ומה-DMZ הוא **לא יכול לפתוח חיבורים פנימה** (רמה 50 ‏←‏ 100 חסומה). הנזק נשאר
ב"קבלה".

משרד החינוך דורש שישה שרתי DMZ בסניף הראשי (דרישה 21):

<div dir="rtl">

| שרת | ‎‏IP | שירות |
|---|---|---|
| ‎SRV-HFA-DMZ-DNS | ‎10.10.200.11 | מתרגם שמות (`www.intel.lab`) לכתובות IP |
| ‎SRV-HFA-DMZ-MAIL | ‎10.10.200.12 | דואר אלקטרוני של החברה (‎`@intel.lab`) |
| ‎SRV-HFA-DMZ-WEB | ‎10.10.200.13 | אתר החברה |
| ‎SRV-HFA-DMZ-NTP | ‎10.10.200.14 | **השעון הראשי** של החברה |
| ‎SRV-HFA-DMZ-FTP | ‎10.10.200.15 | העברת קבצים |
| ‎SRV-HFA-DMZ-AAA | ‎10.10.200.16 | אימות מרכזי (למשתמשים מרוחקים) |

</div>

### 1.5 ‏NTP — כולם מסכימים על השעה
יומנים מ-50 מכשירים לא שווים כלום אם לכל מכשיר יש שעון אחר ("הקישור נפל ב-… באיזו שעה?"). **‏NTP**
מסנכרן את כל השעונים ל**שרת NTP** אחד. ‏SRV-HFA-DMZ-NTP הוא שרת ה-NTP הראשי; הסניפים האחרים יסתנכרנו
אליו בהמשך (דרישה 20.8).

### 1.6 נתב הקצה ו"מי עושה NAT"
**נתב הקצה** ‏(R-HFA-EDGE) יחבר את המטה לאינטרנט בשלב 12. כל תרגום הכתובות (NAT) קורה שם — **לא**
ב-ASA. ה-ASA רק מסנן ומנתב. כך הכתובות הפרטיות עוברות את חומת האש בלי שינוי, ו-VPN צריך את זה
בשלב 15.

### 1.7 איך התעבורה מוצאת את ה-ASA
מתגי ה-core לא מכירים את האינטרנט. נותנים להם **נתיב ברירת מחדל** (default route — "כל מה שאני לא
מכיר ‏←‏ ל-ASA"), ו-OSPF מפיץ אותו לכל מתג במטה (`default-information originate`).

---

## חלק 2 — הכנה
**File → Open** ‏←‏ `my-work/step10.pkt` ‏←‏ **File → Save As** ‏←‏ `my-work/step11.pkt`.

---

## חלק 3 — בונים (לחיצה אחרי לחיצה)

### 3.1 מכשירים

<div dir="rtl">

| איפה | דגם | ‎‏Display Name |
|---|---|---|
| ‎Network Devices → **Security** | ‎**5506-X** | ‎`ASA-HFA-FW1` |
| ‎Network Devices → **Routers** | ‎**2911** | ‎`R-HFA-EDGE` |
| ‎Network Devices → Switches | ‎**2960** | ‎`SW-HFA-DMZ` |
| ‎End Devices → End Devices | ‎**‏Server** ×6 | ששת השמות מסעיף 1.4 |

</div>

ציירו מלבן עם התווית `HAIFA - DMZ` סביב מתג ה-DMZ והשרתים שלו.

### 3.2 כבלים

<div dir="rtl">

| לוחצים קודם על | פורט | לוחצים אחר כך על | פורט | כבל |
|---|---|---|---|---|
| ‎SW-HFA-SRV | ‎**Fa0/24** | ‎ASA-HFA-FW1 | ‎**GigabitEthernet1/2** | ‎Straight-Through |
| ‎ASA-HFA-FW1 | ‎**GigabitEthernet1/3** | ‎SW-HFA-DMZ | ‎**GigabitEthernet0/1** | ‎Straight-Through |
| ‎ASA-HFA-FW1 | ‎**GigabitEthernet1/1** | ‎R-HFA-EDGE | ‎**GigabitEthernet0/0** | ‎Straight-Through |
| ‎SRV-HFA-DMZ-DNS | ‎Fa0 | ‎SW-HFA-DMZ | ‎Fa0/1 | ‎Straight-Through |
| ‎SRV-HFA-DMZ-MAIL | ‎Fa0 | ‎SW-HFA-DMZ | ‎Fa0/2 | ‎Straight-Through |
| ‎SRV-HFA-DMZ-WEB | ‎Fa0 | ‎SW-HFA-DMZ | ‎Fa0/3 | ‎Straight-Through |
| ‎SRV-HFA-DMZ-NTP | ‎Fa0 | ‎SW-HFA-DMZ | ‎Fa0/4 | ‎Straight-Through |
| ‎SRV-HFA-DMZ-FTP | ‎Fa0 | ‎SW-HFA-DMZ | ‎Fa0/5 | ‎Straight-Through |
| ‎SRV-HFA-DMZ-AAA | ‎Fa0 | ‎SW-HFA-DMZ | ‎Fa0/6 | ‎Straight-Through |

</div>

(ה-ASA מתנהג כמו מכשיר מסוג נתב: ב-PT כבל Straight-Through למתגים ולנתבים עובד. אם קישור נשאר
אדום, נסו Cross-Over.)

---

## חלק 4 — מגדירים

### 4.1 ‏ASA-HFA-FW1
לחצו עליו ‏←‏ **CLI**. ה-prompt של ה-ASA הוא `ciscoasa>`‎.
```
enable
```
‏`Password:`‎ ‏←‏ פשוט לחצו **Enter** (ריק ב-ASA חדש).
```
configure terminal
hostname ASA-HFA-FW1
enable password Intel#En4ble
domain-name intel.lab
! the factory config runs a DHCP server on "inside" — turn it off
no dhcpd enable inside

! ---------- the three zones ----------
interface gigabitEthernet 1/1
 nameif outside
 security-level 0
 ip address 10.10.7.2 255.255.255.252
 no shutdown
interface gigabitEthernet 1/2
 nameif inside
 security-level 100
 ip address 10.10.1.254 255.255.255.0
 no shutdown
interface gigabitEthernet 1/3
 nameif dmz
 security-level 50
 ip address 10.10.200.1 255.255.255.0
 no shutdown
 exit

! ---------- routing ----------
! everything unknown -> the edge router
route outside 0.0.0.0 0.0.0.0 10.10.7.1
! all of HQ is behind the cores (VLAN 100 gateway)
route inside 10.10.0.0 255.255.0.0 10.10.1.1

! ---------- inspection: let replies (ping, DNS, web, FTP) come back ----------
class-map inspection_default
 match default-inspection-traffic
 exit
policy-map global_policy
 class inspection_default
  inspect icmp
  inspect dns
  inspect http
  inspect ftp
  exit
 exit
service-policy global_policy global

! ---------- the holes from outside (more in steps 12 and 15) ----------
! the edge router sends its logs, logins and time requests inward
access-list OUTSIDE_IN extended permit udp host 10.10.7.1 host 10.10.1.10 eq syslog
access-list OUTSIDE_IN extended permit tcp host 10.10.7.1 host 10.10.1.11 eq tacacs
access-list OUTSIDE_IN extended permit udp host 10.10.7.1 host 10.10.200.14 eq ntp
access-group OUTSIDE_IN in interface outside

! ---------- SSH to the ASA, only from the admin networks ----------
username admin password Intel#Adm1n
aaa authentication ssh console LOCAL
crypto key generate rsa modulus 1024
ssh 10.10.19.0 255.255.255.0 inside
ssh 10.10.35.0 255.255.255.0 inside
ssh 10.10.51.0 255.255.255.0 inside
ssh 10.10.49.0 255.255.255.0 inside
ssh timeout 5
end
write memory
```
ההערות אומרות: ההגדרות מהמפעל מפעילות שרת DHCP על "inside" — מכבים אותו; שלושת האזורים; ניתוב —
כל יעד לא מוכר ‏←‏ לנתב הקצה, וכל המטה נמצא מאחורי מתגי ה-core (השער של VLAN 100); ‏inspection —
מאפשר לתשובות (ping, ‏DNS, ‏web, ‏FTP) לחזור; החורים מבחוץ (עוד בשלבים 12 ו-15) — נתב הקצה שולח
פנימה את היומנים, ההתחברויות ובקשות השעה שלו; ‏SSH ל-ASA, רק מרשתות הניהול.

<div dir="rtl">

> אם `service-policy global_policy global` אומר שהוא כבר קיים — בסדר, ב-ASA של PT הוא קיים כברירת
> מחדל. אם `crypto key generate` שואל אם להחליף את המפתחות, ענו `yes`.

</div>

**רשות (אם ה-PT שלכם מקבל את זה) — יומני ה-ASA נשלחים ל-Syslog:**
```
configure terminal
logging enable
logging trap informational
logging host inside 10.10.1.10
end
write memory
```

### 4.2 ‏CORE1 ו-CORE2 — נתיב ברירת המחדל
ב**שני** מתגי ה-core:
```
enable
configure terminal
ip route 0.0.0.0 0.0.0.0 10.10.1.254
router ospf 1
 default-information originate
 end
copy running-config startup-config
```

### 4.3 ‏R-HFA-EDGE — חלק ראשון (הצד הפנימי)
לחצו עליו ‏←‏ **CLI**. נתב חדש שואל:
`Would you like to enter the initial configuration dialog? [yes/no]:`‎ ‏←‏ הקלידו **`no`**, ‏Enter.
לחצו שוב Enter ‏←‏ `Router>`‎.
```
enable
configure terminal
hostname R-HFA-EDGE
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
interface gi0/0
 description to ASA-HFA-FW1 outside
 ip address 10.10.7.1 255.255.255.252
 no shutdown
 exit
! all of HQ is behind the ASA
ip route 10.10.0.0 255.255.0.0 10.10.7.2

! ---------- management ----------
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
(‎`1024`)
```
ip ssh version 2
login block-for 120 attempts 3 within 60
ip access-list standard MGMT-ONLY
 permit 10.10.19.0 0.0.0.255
 permit 10.10.35.0 0.0.0.255
 permit 10.10.51.0 0.0.0.255
 permit 10.10.49.0 0.0.0.255
 deny any log
 exit
service timestamps log datetime msec
logging trap informational
logging host 10.10.1.10
ntp server 10.10.200.14
aaa new-model
tacacs-server host 10.10.1.11 key Intel#Tac
aaa authentication login default group tacacs+ local
line vty 0 15
 transport input ssh
 login authentication default
 access-class MGMT-ONLY in
 exec-timeout 5 0
line console 0
 login authentication default
 logging synchronous
 end
copy running-config startup-config
```
ההערות אומרות: כל המטה נמצא מאחורי ה-ASA; ניהול.

אחר כך ב-**SRV-HFA-AAA → Services → AAA → Network Configuration** הוסיפו: `R-HFA-EDGE`, ‏‎`10.10.7.1`,
‏`Intel#Tac`, **Tacacs**.

### 4.4 ‏SW-HFA-DMZ
```
enable
configure terminal
hostname SW-HFA-DMZ
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
username admin privilege 15 secret Intel#Adm1n
line console 0
 login local
 exit
interface range fa0/1 - 6
 description DMZ servers
 switchport mode access
 spanning-tree portfast
 spanning-tree bpduguard enable
interface range fa0/7 - 24
 description UNUSED
 shutdown
interface gi0/2
 description UNUSED
 shutdown
 end
copy running-config startup-config
```

<div dir="rtl">

> **בלי כתובת IP — בכוונה.** ל-DMZ אסור להגיע פנימה, ולכן את המתג הזה מנהלים רק מה-console. כתבו את
> החלטת התכנון הזו בספר הפרויקט.

</div>

### 4.5 ששת שרתי ה-DMZ (לחיצה אחרי לחיצה)
**הגדרות IP** — כל שרת ‏←‏ **Desktop → IP Configuration → Static**:

<div dir="rtl">

| שרת | ‎‏IPv4 | מסיכה | שער | ‎‏DNS |
|---|---|---|---|---|
| ‎SRV-HFA-DMZ-DNS | ‎10.10.200.11 | ‎255.255.255.0 | ‎10.10.200.1 | ‎10.10.200.11 |
| ‎SRV-HFA-DMZ-MAIL | ‎10.10.200.12 | ‎255.255.255.0 | ‎10.10.200.1 | ‎10.10.200.11 |
| ‎SRV-HFA-DMZ-WEB | ‎10.10.200.13 | ‎255.255.255.0 | ‎10.10.200.1 | ‎10.10.200.11 |
| ‎SRV-HFA-DMZ-NTP | ‎10.10.200.14 | ‎255.255.255.0 | ‎10.10.200.1 | ‎10.10.200.11 |
| ‎SRV-HFA-DMZ-FTP | ‎10.10.200.15 | ‎255.255.255.0 | ‎10.10.200.1 | ‎10.10.200.11 |
| ‎SRV-HFA-DMZ-AAA | ‎10.10.200.16 | ‎255.255.255.0 | ‎10.10.200.1 | ‎10.10.200.11 |

</div>

**תפקיד אחד לכל שרת** — בכל שרת ‏←‏ הלשונית **Services**: העבירו ל-**Off** כל שירות חוץ משלו (ב-PT
הרבה שירותים דולקים כברירת מחדל).

**‏SRV-HFA-DMZ-NTP** ‏←‏ Services ‏←‏ **NTP** ‏←‏ **On**. בדקו את התאריך והשעה שמוצגים.

**‏SRV-HFA-DMZ-DNS** ‏←‏ Services ‏←‏ **DNS** ‏←‏ **On**. הוסיפו כל רשומה: הקלידו את ה-*Name*, בחרו
*Type* ‏**A Record**, הקלידו את ה-*Address* ‏←‏ **Add**:

<div dir="rtl">

| ‎‏Name | ‎‏Address |
|---|---|
| ‎`www.intel.lab` | ‎10.10.200.13 |
| ‎`mail.intel.lab` | ‎10.10.200.12 |
| ‎`ftp.intel.lab` | ‎10.10.200.15 |
| ‎`ntp.intel.lab` | ‎10.10.200.14 |
| ‎`www.isp-web1.com` | ‎200.1.100.11 |
| ‎`www.isp-web2.com` | ‎200.1.100.12 |

</div>

(שרת ה-DNS של PT לא יודע לשאול שרתי DNS אחרים, ולכן מעתיקים אליו גם את שמות האינטרנט של שלב 12.)

**‏SRV-HFA-DMZ-WEB** ‏←‏ Services ‏←‏ **HTTP** ‏(On) ‏←‏ ברשימת הקבצים לחצו על **index.html** ‏←‏ **(edit)**
‏←‏ שנו את הטקסט ל-‎`<h1>Intel Israel - Intranet</h1>`‎ ‏←‏ **Save** ‏←‏ **Yes**.

**‏SRV-HFA-DMZ-MAIL** ‏←‏ Services ‏←‏ **EMAIL** ‏←‏ *Domain Name*: ‏`intel.lab` ‏←‏ **Set**. (המשתמשים בשלב 16.)

**‏SRV-HFA-DMZ-FTP** ‏←‏ Services ‏←‏ **FTP** ‏(On) ‏←‏ *Username* ‏`ftpadmin`, *Password* ‏`Intel#Ftp`,
סמנו את כל ההרשאות (Write, ‏Read, ‏Delete, ‏Rename, ‏List) ‏←‏ **Add**. בחרו את משתמש ברירת המחדל
‏`cisco` ‏←‏ **Remove**.

**‏SRV-HFA-DMZ-AAA** ‏←‏ Services ‏←‏ **AAA** ‏←‏ **On** (הוא ישרת משתמשי גישה מרחוק; עדיין אין מה להוסיף).

### 4.6 ‏NTP בכל מתג במטה
ב**כל 15 המתגים בחיפה** (‏ACC + DIST של A/B/C, ‏CORE1/2, ‏SW-HFA-SRV):
```
enable
configure terminal
ntp server 10.10.200.14
end
copy running-config startup-config
```

### 4.7 מה הפקודות החדשות אומרות

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`nameif outside` | תן לממשק הזה של ה-ASA שם של אזור |
| ‎`security-level 0` | רמת האמון שלו |
| ‎`route outside 0.0.0.0 0.0.0.0 10.10.7.1` | "יעדים לא מוכרים: צא דרך `outside` אל 10.10.7.1" |
| ‎`inspect icmp` | "זכור את הפינגים כדי שהתשובות שלהם יוכלו לחזור" |
| ‎`access-list OUTSIDE_IN extended permit ...`‎ | חור בחומת האש בדיוק לתעבורה הזו |
| ‎`access-group OUTSIDE_IN in interface outside` | "בדוק מול הרשימה הזו תעבורה שנכנסת מבחוץ" |
| ‎`ssh 10.10.19.0 255.255.255.0 inside` | "התר SSH ל-ASA מהרשת הזו, בצד הפנימי" |
| ‎`ip route 0.0.0.0 0.0.0.0 10.10.1.254` ‏(core) | "כל מה שלא מוכר הולך ל-ASA" — **נתיב ברירת מחדל** |
| ‎`default-information originate` | "ספר לכל שכני ה-OSPF על נתיב ברירת המחדל שלי" |
| ‎`ntp server 10.10.200.14` | "קח את השעה מהשעון הזה" |

</div>

---

## חלק 5 — בודקים את העבודה

### 5.1 ה-ASA
```
ASA-HFA-FW1# show nameif
Interface                Name                     Security
GigabitEthernet1/1       outside                    0
GigabitEthernet1/2       inside                   100
GigabitEthernet1/3       dmz                       50
ASA-HFA-FW1# show route
S*   0.0.0.0 0.0.0.0 [1/0] via 10.10.7.1, outside
S    10.10.0.0 255.255.0.0 [1/0] via 10.10.1.1, inside
C    10.10.1.0 255.255.255.0 is directly connected, inside
...
```

### 5.2 נתיב ברירת המחדל הגיע לכל מתג
על **A-DIST1**: ‏`show ip route | include 0.0.0.0` ‏←‏ `O*E2 0.0.0.0/0 ... via 10.10.4.2 ...`‎ ✅

### 5.3 בדיקות דרך חומת האש

<div dir="rtl">

| מאיפה | מקלידים | מה אמור לקרות | למה |
|---|---|---|---|
| מחשב ENG | ‎`ping 10.10.200.13` | ‎✅ | מ-inside ‏(100) ל-DMZ ‏(50) |
| מחשב ENG | בדפדפן: Desktop ‏←‏ **Web Browser** ‏←‏ `http://www.intel.lab` ‏←‏ Go | ✅ דף האינטראנט | ‏DNS + ‏HTTP דרך ה-ASA |
| מחשב ENG | ‎`nslookup www.intel.lab` | ‎`10.10.200.13` | ‏DNS עובד |
| מחשב ENG | ‎`ping 10.10.7.1` | ‎✅ | מ-inside ל-outside |
| ‎SRV-HFA-DMZ-WEB | ‎`ping 10.10.16.1` | ‎❌ | מה-DMZ ‏(50) ל-inside ‏(100) |
| ‎R-HFA-EDGE | ‎`ping 10.10.200.13` | ‎❌ | מ-outside ל-DMZ, לא ב-ACL |
| כל מתג | ‎`show ntp status` | ‎`Clock is synchronized ... reference is 10.10.200.14` | ‎‏NTP |
| כל מתג | ‎`show clock` | אותה שעה כמו בשרת ה-NTP | |

</div>

ב-ASA, בזמן שאתם גולשים ממחשב: ‏`show conn` מציג את החיבורים הפעילים.

<div dir="rtl">

> ‏NTP יכול לקחת כמה דקות של זמן מדומה — לחצו כמה פעמים על **Fast Forward Time**.

</div>

---

## חלק 6 — שומרים
‏`write memory` ב-ASA, ‏`copy running-config startup-config` בכל השאר ‏←‏ **File → Save**.

## נקודת ביקורת
- [ ] ‏`show nameif` מציג את שלושת האזורים
- [ ] המחשבים גולשים ל-`http://www.intel.lab`
- [ ] ה-DMZ לא מגיע פנימה
- [ ] כל המתגים מסונכרנים ל-10.10.200.14

## אם משהו לא עובד

<div dir="rtl">

| בעיה | פתרון |
|---|---|
| ממשקי ה-ASA מתעלמים מתעבורה | חסר `nameif` — ממשק ASA בלי שם לא עושה כלום |
| המחשבים מקבלים כתובות ‎`192.168.1.x` | שרת ה-DHCP של ה-ASA מהמפעל: ‏`no dhcpd enable inside` |
| גלישה עובדת אבל ping ל-DMZ נכשל | חסר `inspect icmp` |
| המחשבים לא מגיעים לשום דבר מעבר ל-core | חסר נתיב ברירת מחדל או `default-information originate` במתגי ה-core |
| הדף מציג "Host Name Unresolved" | שירות ה-DNS בשרת כבוי, שגיאת כתיב ברשומה, או שה-DNS של המחשב הוא לא 10.10.200.11 (חדשו את ה-DHCP) |
| ‎‏`show ntp status` = unsynchronized | חכו (Fast Forward); בדקו שהשירות דולק בשרת ה-NTP; ‏ping ל-10.10.200.14 מהמתג |
| נתב הקצה לא מצליח להתחבר דרך TACACS | חסרה ב-ASA שורת ACL ל-tacacs, או ש-R-HFA-EDGE לא רשום בשרת ה-AAA |

</div>

## אתגר
האקר משתלט על SRV-HFA-DMZ-WEB. כתבו שלושה דברים שהוא **יכול** להגיע אליהם ושלושה שהוא **לא יכול**.
הוכיחו שניים מהם עם ping מה-Command Prompt של שרת ה-web.

<details dir="rtl"><summary>תשובה</summary>

**יכול:** לשרתי ה-DMZ האחרים (אותה רשת משנה — אין חומת אש ביניהם), לממשק ה-DMZ של ה-ASA, ולצד
החיצוני (נתב הקצה, והאינטרנט אחרי שלב 12).
**לא יכול:** לשום רשת פנימית — משתמשים (10.10.16.x…), חוות השרתים (10.10.1.x), ה-VLANים של הניהול —
כי DMZ ‏(50) ‏←‏ ‏inside ‏(100) חסום ואף ACL לא פותחת את זה.
לספר הפרויקט: ברשתות אמיתיות מפרידים גם את שרתי ה-DMZ זה מזה ("private VLANs") — ‏PT לא תומך בזה
טוב, אז ציינו את זה כמגבלה ידועה.
</details>

---

## 🛠 הפרויקט שלכם

עשיתם את השלב הזה על הדוגמה של אינטל. עכשיו עשו אותו שוב בפרויקט **שלכם**, עם הערכים
מהתוכנית **שלכם** (`my-project/plan.md`). הפקודות זהות — רק הערכים משתנים.

<div dir="rtl">

| בדוגמה | בפרויקט שלכם — לוקחים מ |
|---|---|
| ‏DMZ ‏‎`10.10.200.0/24` ו-6 השרתים | תוכנית, חלק ג/ד — רשת ה-DMZ שלכם וכתובות השרתים (**רשימת** השרתים נקבעה על ידי משרד החינוך, דרישה 21) |
| ‏inside / outside / dmz, רמות 100 / 0 / 50 | להשאיר (זה המודל הסטנדרטי של ASA) |
| קישור ה-ASA ‏‎`10.10.7.0/30` | ‏‎/30 משלכם |
| כללי ה-ACL | כתובים מחדש עבור הכתובות **שלכם** |
| שרת ה-NTP הראשי ב-DMZ | כתובת שרת ה-NTP שלכם; כל האתרים שלכם מסתנכרנים ממנו (דרישה 20.8) |

</div>

**בדיקה:** הריצו את הטבלה של 5.3 עם הכתובות **שלכם** — ה-inside מגיע ל-DMZ, ה-DMZ לא מגיע ל-inside,
ה-outside לא מגיע ל-DMZ; ‏`show nameif` מציג את שלושת הממשקים שלכם; ‏`show ntp status` במתג מציג את
שרת ה-NTP שלכם.

💾 שמרו בשם `my-project/step11.pkt`.

---

## 🎓 מסבירים לבוחן

בבחינה, הבוחן מצביע על הפרויקט **שלכם** ומבקש **להסביר** ו**להראות**. תרגלו כל שאלה
**בקול**, ואז הראו את התשובה בפרויקט שלכם — לא בדוגמה. כסו את התשובה, ענו בעצמכם, ורק אז
פתחו והשוו.

★1–★3 = שאלה ממאגר השאלות של משרד החינוך (רמת קושי 1–3).
◆ = לא במאגר, אבל בוחנים שואלים אותה לעיתים קרובות.

**1. ★1 מהו ASA?**

<details dir="rtl"><summary>תשובה</summary>

‏Adaptive Security Appliance — חומת האש של Cisco. הוא בודק תעבורה בין אזורים (inside, ‏outside,
‏DMZ) ומתיר רק את מה שהמדיניות מתירה. הוא **stateful**: תעבורה חוזרת של חיבור מותר מותרת אוטומטית.

**איפה מראים:** `show nameif`, `show conn`
</details>

**2. ★1 מהו DMZ?**

<details dir="rtl"><summary>תשובה</summary>

אזור נפרד לשרתים שהאינטרנט חייב להגיע אליהם (web, ‏mail, ‏DNS…). אם אחד מהם נפרץ, התוקף עדיין
מחוץ לרשת הפנימית.

**איפה מראים:** `show nameif` ‏←‏ dmz
</details>

**3. ★1 לחומת אש יש 3 ממשקים: inside, ‏DMZ, ‏outside. איזו רמת אבטחה נותנים לכל אחד?**

<details dir="rtl"><summary>תשובה</summary>

‏inside ‏100, ‏DMZ ‏50, ‏outside ‏0. תעבורה מרמה גבוהה לרמה נמוכה מותרת כברירת מחדל; מנמוכה לגבוהה
צריך ACL.

**איפה מראים:** `show nameif`
</details>

**4. ★1 מה תפקידו של שרת HTTP? באיזה פורט? מהו HTTPS ומה ההבדל?**

<details dir="rtl"><summary>תשובה</summary>

מגיש דפי אינטרנט. ‏HTTP = ‏TCP 80, טקסט גלוי. ‏HTTPS = ‏TCP 443, ‏HTTP מוצפן עם TLS (תעודה) — אי אפשר
לקרוא סיסמאות ונתונים בדרך.

**איפה מראים:** ‏Server ‏←‏ Services ‏←‏ HTTP / HTTPS
</details>

**5. ★1 מה תפקידו של שרת DNS? באיזה פורט? הצג את ההגדרות שלו.**

<details dir="rtl"><summary>תשובה</summary>

מתרגם שמות לכתובות IP ‏(`www.intel.lab` ‏←‏ ‎`10.10.200.13`). ‏UDP 53 ‏(TCP 53 להעברות גדולות).

**איפה מראים:** ‏Server ‏←‏ Services ‏←‏ DNS (הרשומות); מחשב ‏←‏ `nslookup <name>`‎
</details>

**6. ★1 מה תפקידו של שרת FTP? באיזה פורט? הצג את ההגדרות שלו.**

<details dir="rtl"><summary>תשובה</summary>

העברת קבצים. ‏TCP 21 (בקרה) ו-TCP 20 (נתונים). המשתמשים וההרשאות שלהם מוגדרים בשרת.

**איפה מראים:** ‏Server ‏←‏ Services ‏←‏ FTP; מחשב ‏←‏ `ftp <IP>`‎
</details>

**7. ★1 מה תפקידו של שרת דואר? הצג את ההגדרות שלו.**

<details dir="rtl"><summary>תשובה</summary>

שולח ושומר דואר אלקטרוני: ‏SMTP ‏(TCP 25) לשליחה, ‏POP3 ‏(TCP 110) להורדה ללקוח. בשרת מוגדרים שם
הדומיין וחשבונות המשתמשים.

**איפה מראים:** ‏Server ‏←‏ Services ‏←‏ EMAIL; מחשב ‏←‏ Desktop ‏←‏ Email
</details>

**8. ★3 כיצד ACL יכולה לאפשר גלישה באינטרנט אבל לחסום אתרים מסוימים?**

<details dir="rtl"><summary>תשובה</summary>

‏ACL מורחבת: ‏`deny tcp <users> host <site IP> eq 80` ו-`eq 443` לכל אתר חסום, ואחר כך
‏`permit ip <users> any`. מחילים אותה הכי קרוב שאפשר למשתמשים.

**איפה מראים:** —
</details>

**9. ★3 כיצד ACLs יכולות לעזור להגן על רשת מפני התקפות DDoS?**

<details dir="rtl"><summary>תשובה</summary>

על הממשק החיצוני: מתירים רק את השירותים שמפרסמים (למשל TCP 80/443 לשרת ה-web) וחוסמים את כל השאר;
זורקים חבילות שמגיעות מבחוץ עם כתובת מקור פרטית או עם הכתובות שלכם (התחזות, spoofing). ‏ACL מקטינה
את החשיפה, אבל לבד היא לא יכולה לעצור הצפה גדולה — הספק צריך לסנן אותה.

**איפה מראים:** ה-ACL על הממשק החיצוני של ה-ASA
</details>

**10. ★3 בטבלת הניתוב, מה ההבדל בין E1 ל-E2? מה ברירת המחדל?**

<details dir="rtl"><summary>תשובה</summary>

שניהם נתיבים חיצוניים (סוג 5). ‏E2 (ברירת המחדל): העלות נשארת רק העלות החיצונית — היא לא גדלה בתוך
OSPF. ‏E1: העלות הפנימית של OSPF מתווספת לאורך הדרך. נתיב ברירת המחדל שהפרויקט הזה שולח לתוך OSPF
מופיע כ-`O*E2`.

**איפה מראים:** `show ip route` במתג distribution ‏←‏ `O*E2 0.0.0.0/0`
</details>

---

## 🔁 עושים שוב — בלי המדריך

הבוחן יכול לבקש מכם להגדיר משהו שוב, מולו. תצליחו רק אם עשיתם את זה **בלי המדריך** לפני כן.
עשו את התרגיל הזה בפרויקט שלכם:

בעותק של הקובץ שלכם, החליפו את ה-ASA ב-ASA חדש מרשימת המכשירים. בלי העמוד הזה, הגדירו את שלושת
הממשקים עם השמות, הרמות והכתובות מהתוכנית שלכם, את הנתיבים ואת ה-ACL. יעד: **‏20 דקות**. אחר כך
הריצו את טבלת הבדיקות של 5.3 עם הכתובות שלכם והסבירו כל ✅ וכל ❌.

---

## 👩‍🏫 הערות למורה
- **שיעור 1:** חומת אש מול נתב; אזורים וההשוואה לבניין משרדים; ‏stateful; למה DMZ ‏←‏ בנייה וחיווט
  ‏←‏ הגדרת ה-ASA.
- **שיעור 2:** נתיב ברירת מחדל + ‏`default-information originate` ‏←‏ נתב הקצה (הנתב הראשון בקורס:
  "initial configuration dialog" ‏←‏ `no`) ‏←‏ מתג ה-DMZ.
- **שיעור 3:** ששת השרתים (הרבה לחיצות — חלקו את הכיתה: כל תלמיד מגדיר שני שרתים ומסביר אותם) ‏←‏
  ‏NTP ‏←‏ בדיקות ‏←‏ אתגר.
- **שאלות נפוצות של תלמידים**
  - *"למה למתג ה-DMZ אין IP?"* — ניהול שלו מבפנים היה דורש חור מה-DMZ פנימה, וזה מבטל את הרעיון
    של DMZ. ניהול רק מה-console הוא הבחירה הבטוחה.
  - *"למה `write memory` ב-ASA?"* — זו הגרסה של ה-ASA ל-`copy run start`.
- **טעויות אופייניות:** שכחת `nameif`; בלבול בחיווט של Gi1/1, ‏Gi1/2, ‏Gi1/3 של ה-ASA; השארת DHCP
  דולק ב-ASA; רשומות DNS עם שגיאת כתיב (`www.intel.lab` לעומת `www.intel.lab.`‎).
