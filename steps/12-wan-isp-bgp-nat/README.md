# שלב 12 — ה-WAN: ‏3 ספקי אינטרנט, ‏BGP, ‏NAT וגיבוי DSL

<div dir="rtl">

> ⏱ ‏3–4 שיעורים · 🎯 דרישות משרד החינוך 1, ‏3, ‏4, ‏9, ‏10 (static), ‏22.12, ‏22.17, ‏23.1, ‏23.2, ‏23.3\
> 📁 מתחילים מ: `my-work/step11.pkt`\
> 💾 שומרים בשם: `my-work/step12.pkt`

</div>

<div dir="rtl">

> ✅ **לפני שמתחילים:** כל הסעיפים בנקודת הביקורת של שלב 11 מסומנים, ועשיתם את
> תרגיל ה-🔁 שלו בפרויקט שלכם. אל תדלגו על שלבים — כל שלב בנוי על הקובץ של השלב הקודם.

</div>

## מה יהיה לכם בסוף השלב
**אינטרנט** קטן: שלושה ספקים (ISPs) שמחליפים ביניהם נתיבים עם **BGP**, וכל אחד מריץ **OSPF**
בפנים. חיפה מחוברת: העובדים גולשים באינטרנט (**PAT**), האינטרנט יכול לפתוח את האתר של אינטל
(**static NAT**), ו**מודם DSL** הוא קו גיבוי.

```
          AS 100 (ISP-A)                AS 200 (ISP-B)               AS 300 (ISP-C)
   [R-ISPA-PE]─OSPF─[R-ISPA-BR]══eBGP══[R-ISPB-BR]─OSPF─[R-ISPB-PE]
     │      │             ╲               ╱                │     │
     │   internet          ╲════eBGP════[R-ISPC-BR]─OSPF─[R-ISPC-PE]
     │   servers            (eBGP B↔C too)               │      │
   R-HFA-EDGE ·········· DSL modem ····· cloud ──────────┘      home users
   (Haifa)          (backup line to ISP-B)           (Jerusalem — step 13) (Kiryat Gat — step 14)
```
(שלושה ספקים: ‏AS 100, ‏AS 200, ‏AS 300. בכל ספק נתב BR ונתב PE עם OSPF ביניהם, וה-BRs מחוברים
ב-eBGP במשולש. ‏R-HFA-EDGE (חיפה) מחובר ל-ISP-A, ובקו גיבוי דרך מודם DSL וענן ל-ISP-B. ירושלים
(שלב 13) מתחברת ל-ISP-B, וקריית גת (שלב 14) ומשתמשים ביתיים ל-ISP-C.)

---

## חלק 1 — קודם מבינים (בשפה פשוטה)

### 1.1 מה זה באמת "האינטרנט"
האינטרנט הוא אלפי רשתות ששייכות לחברות שונות (ספקים, אוניברסיטאות, Google…), וכולן מחוברות. כל
רשת כזו היא **AS — Autonomous System** (מערכת אוטונומית), עם מספר (כאן 100, ‏200, ‏300).

- **בתוך** AS, הנתבים משתמשים בפרוטוקול פנימי (**OSPF** או EIGRP) — כמו השלטים של העיר עצמה.
- **בין** ASים, הם משתמשים ב-**BGP** — הפרוטוקול של האינטרנט — כמו הסכמים בין מדינות על אילו
  כבישים מובילים לאן.

משרד החינוך מבקש בדיוק את זה: ‏WAN שמריץ BGP (דרישות 1, ‏3), עם OSPF/EIGRP בתוך הספקים (דרישה 4).

### 1.2 שלושת הספקים שלנו
לכל ספק יש שני נתבים:
- **‏BR ‏(border router, נתב גבול)** — מדבר **BGP** עם הספקים האחרים.
- **‏PE ‏(provider edge, נתב קצה של הספק)** — מחבר את ה**לקוחות** (הסניפים שלנו). מדבר רק OSPF בתוך
  הספק שלו.

<div dir="rtl">

| ספק | ‎‏AS | בלוק הכתובות שלו | לקוח |
|---|---|---|---|
| ‎ISP-A | ‎100 | ‎200.1.0.0/16 | חיפה (+ שרתי האינטרנט) |
| ‎ISP-B | ‎200 | ‎200.2.0.0/16 | ירושלים (+ גיבוי ה-DSL של חיפה) |
| ‎ISP-C | ‎300 | ‎200.3.0.0/16 | קריית גת (+ משתמשים ביתיים) |

</div>

שלושת ה-BRs מחוברים ב**משולש** — אם קישור אחד נשבר, ‏BGP משתמש בדרך השנייה (יתירות בין סניפים,
דרישה 23.1).

### 1.3 ‏BGP במילים פשוטות
- שכני BGP נכתבים **ידנית**: ‏`neighbor 200.0.12.2 remote-as 200` = "הנתב בכתובת הזו שייך ל-AS 200 —
  בוא נדבר".
- כל ספק **מפרסם את הבלוק שלו**: ‏`network 200.1.0.0 mask 255.255.0.0`.
- ‏BGP מפרסם רק בלוק ש**קיים בדיוק** בטבלת הניתוב. לכן מוסיפים נתיב "שומר מקום" ל-**Null0** (חור
  שחור): ‏`ip route 200.1.0.0 255.255.0.0 null0`. נתיבים אמיתיים ומפורטים יותר בתוך הבלוק עדיין
  מנצחים, כי הנתב תמיד מעדיף את **ההתאמה הארוכה ביותר** (longest match).

### 1.4 לקוחות משתמשים בנתיבים סטטיים
נתבי הקצה שלנו לא מריצים שום פרוטוקול ניתוב מול הספק. הם משתמשים ב**נתיב ברירת מחדל סטטי אחד**:
"כל מה שאני לא מכיר ‏←‏ לספק". כך אנחנו **אף פעם** לא מספרים לאינטרנט על הרשתות הפנימיות שלנו
(דרישה 22.17). הספק, מצידו, מחזיק נתיב סטטי לכיוון הכתובות הציבוריות של הלקוח.

### 1.5 ‏NAT — פרטי בפנים, ציבורי בחוץ
כתובות ה-10.x שלנו הן **פרטיות**: הן לא קיימות באינטרנט. **‏NAT** ‏(Network Address Translation,
תרגום כתובות) בנתב הקצה מחליף אותן בכתובות **ציבוריות** כשהחבילות יוצאות.

<div dir="rtl">

| סוג | איך זה עובד | השוואה | איפה |
|---|---|---|---|
| ‎**‏Static NAT** | כתובת פרטית אחת ↔ כתובת ציבורית אחת, קבוע | קו טלפון ישיר למשרד אחד | חיפה: שרת ה-web ‏‎`10.10.200.13 ↔ 200.1.10.3` |
| ‎**‏Dynamic NAT** | כתובות פרטיות מקבלות כתובת ציבורית מתוך **מאגר** (pool), אחת לכל אחת, כל עוד הן בשימוש | מאגר משותף של קווים חיצוניים | ירושלים (שלב 13) |
| ‎**‏PAT ‏(overload)** | כולם חולקים כתובת ציבורית **אחת**; הנתב מבדיל ביניהם לפי **מספר פורט** | מרכזיה של חברה: מספר ציבורי אחד, הרבה שלוחות | חיפה לגלישה; קריית גת (שלב 14) |

</div>

משרד החינוך רוצה את שלושתם, אחד לכל סניף (דרישה 10). **השיטה של חיפה היא static NAT**; היא גם
משתמשת ב-PAT כדי שהעובדים יוכלו לגלוש (דרישה 22.12).

‏Static NAT הוא הסיבה שהאינטרנט יכול להגיע לאתר שלנו: מבקר פותח `http://www.intel.lab` ‏←‏ ה-DNS של
האינטרנט אומר ‎`200.1.10.3` ‏←‏ החבילה מגיעה לנתב הקצה שלנו ‏←‏ ‏NAT מחליף אותה ל-‎`10.10.200.13` ‏←‏
ה-ASA מעביר אותה ל-DMZ.

אנחנו גם מפרסמים את שרת ה-NTP בכתובת ‎`200.1.10.4` (רק פורט 123) עבור קריית גת בשלב 14.

### 1.6 גיבוי DSL ו-floating static route
משרד החינוך רוצה ספק שמגיעים אליו דרך **מודם DSL** (דרישה 23.2). אנחנו משתמשים בו כקו ה**גיבוי** של
חיפה, דרך ספק אחר (ISP-B).

**‏Floating static route** (נתיב סטטי "צף") הוא נתיב גיבוי עם "ציון אמון" גרוע יותר (administrative
distance): ‏`ip route 0.0.0.0 0.0.0.0 200.2.9.1 10`. לנתיב הרגיל יש distance 1; לזה יש 10, ולכן הוא
**נשאר מוסתר** כל עוד הראשי עובד, ומופיע אוטומטית אם הראשי נעלם.

---

## חלק 2 — הכנה
‏**File → Open** ‏←‏ `my-work/step11.pkt` ‏←‏ **File → Save As** ‏←‏ `my-work/step12.pkt`.
ציירו בצד ימין אזור גדול בצורת ענן (אליפסה) עם התווית `INTERNET / WAN`.

---

## חלק 3 — בונים (לחיצה אחרי לחיצה)

### 3.1 מכשירים

<div dir="rtl">

| איפה | דגם | ‎‏Display Name |
|---|---|---|
| ‎Network Devices → Routers | ‎**2911** ×6 | ‎`R-ISPA-BR`, `R-ISPA-PE`, `R-ISPB-BR`, `R-ISPB-PE`, `R-ISPC-BR`, `R-ISPC-PE` |
| ‎Network Devices → Switches | ‎**2960** ×2 | ‎`SW-ISPA-NET`, `SW-ISPC-HOME` |
| ‎End Devices | ‎**Server** ×3 | ‎`SRV-ISP-DNS`, `SRV-ISP-WEB1`, `SRV-ISP-WEB2` |
| ‎End Devices | ‎**PC** | ‎`PC-HOME-01` |
| ‎Network Devices → **WAN Emulation** | ‎**DSL-Modem** | ‎`DSL-HFA` |
| ‎Network Devices → **WAN Emulation** | ‎**Cloud** | ‎`CLOUD-DSL` |

</div>

### 3.2 כבלים
נתב ↔ נתב = **Cross-Over**. נתב/שרת/מחשב ↔ מתג = **Straight-Through**.

<div dir="rtl">

| ‎# | לוחצים קודם על | פורט | לוחצים אחר כך על | פורט | כבל |
|---|---|---|---|---|---|
| ‎1 | ‎R-ISPA-BR | ‎Gi0/0 | ‎R-ISPA-PE | ‎Gi0/0 | ‎Cross-Over |
| ‎2 | ‎R-ISPB-BR | ‎Gi0/0 | ‎R-ISPB-PE | ‎Gi0/0 | ‎Cross-Over |
| ‎3 | ‎R-ISPC-BR | ‎Gi0/0 | ‎R-ISPC-PE | ‎Gi0/0 | ‎Cross-Over |
| ‎4 | ‎R-ISPA-BR | ‎Gi0/1 | ‎R-ISPB-BR | ‎Gi0/1 | ‎Cross-Over |
| ‎5 | ‎R-ISPA-BR | ‎Gi0/2 | ‎R-ISPC-BR | ‎Gi0/1 | ‎Cross-Over |
| ‎6 | ‎R-ISPB-BR | ‎Gi0/2 | ‎R-ISPC-BR | ‎Gi0/2 | ‎Cross-Over |
| ‎7 | ‎R-ISPA-PE | ‎Gi0/1 | ‎**R-HFA-EDGE** | ‎**Gi0/1** | ‎Cross-Over |
| ‎8 | ‎R-ISPA-PE | ‎Gi0/2 | ‎SW-ISPA-NET | ‎Gi0/1 | ‎Straight |
| ‎9 | ‎SRV-ISP-DNS / WEB1 / WEB2 | ‎Fa0 | ‎SW-ISPA-NET | ‎Fa0/1 / Fa0/2 / Fa0/3 | ‎Straight |
| ‎10 | ‎R-ISPC-PE | ‎Gi0/2 | ‎SW-ISPC-HOME | ‎Gi0/1 | ‎Straight |
| ‎11 | ‎PC-HOME-01 | ‎Fa0 | ‎SW-ISPC-HOME | ‎Fa0/1 | ‎Straight |
| ‎12 | ‎R-HFA-EDGE | ‎**Gi0/2** | ‎DSL-HFA | ‎**Port 1** (Ethernet) | ‎Straight |
| ‎13 | ‎DSL-HFA | **Port 0** (טלפון) | ‎CLOUD-DSL | ‎**Modem4** | **Phone** (ב-Connections) |
| ‎14 | ‎CLOUD-DSL | ‎**Ethernet6** | ‎R-ISPB-PE | ‎**Gi0/2** | ‎Straight |

</div>

### 3.3 מגדירים את הענן
‏CLOUD-DSL ‏←‏ הלשונית **Config** ‏←‏ ברשימה משמאל **DSL** ‏←‏ *From Port* ‏**Modem4**, *To Port*
‏**Ethernet6** ‏←‏ **Add**. עכשיו הענן מעביר את כל מה שמגיע מהמודם לנתב של ISP-B.

### 3.4 תוכנית הכתובות של ה-WAN

<div dir="rtl">

| נתב | ‎‏Gi0/0 | ‎‏Gi0/1 | ‎‏Gi0/2 |
|---|---|---|---|
| ‎R-ISPA-BR | ‎200.1.0.1/30 | ‎200.0.12.1/30 | ‎200.0.13.1/30 |
| ‎R-ISPA-PE | ‎200.1.0.2/30 | 200.1.1.1/30 לחיפה | 200.1.100.1/24 לשרתים |
| ‎R-ISPB-BR | ‎200.2.0.1/30 | ‎200.0.12.2/30 | ‎200.0.23.1/30 |
| ‎R-ISPB-PE | ‎200.2.0.2/30 | 200.2.1.1/30 לירושלים | 200.2.9.1/30 ל-DSL (גיבוי חיפה) |
| ‎R-ISPC-BR | ‎200.3.0.1/30 | ‎200.0.13.2/30 | ‎200.0.23.2/30 |
| ‎R-ISPC-PE | ‎200.3.0.2/30 | 200.3.1.1/30 לקריית גת | 200.3.50.1/24 למשתמשים ביתיים |
| ‎R-HFA-EDGE | ‎10.10.7.1/30 (ASA) | ‎**200.1.1.2/30** (ISP-A) | ‎**200.2.9.2/30** (DSL) |

</div>

---

## חלק 4 — מגדירים

<div dir="rtl">

> בכל נתב חדש: עונים **`no`** ל-"initial configuration dialog".
> נתבי הספקים שייכים ל"חברות אחרות", ולכן הם מקבלים רק את הבסיס: שם, ‏secret, ‏banner (משרד החינוך
> רוצה banner על **כל** הנתבים).

</div>

### 4.1 ‏R-ISPA-BR ‏(AS 100)
```
enable
configure terminal
hostname R-ISPA-BR
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  ISP-A (AS 100) - AUTHORIZED ACCESS ONLY  *
#
interface gi0/0
 description to R-ISPA-PE
 ip address 200.1.0.1 255.255.255.252
 no shutdown
interface gi0/1
 description eBGP to R-ISPB-BR (AS 200)
 ip address 200.0.12.1 255.255.255.252
 no shutdown
interface gi0/2
 description eBGP to R-ISPC-BR (AS 300)
 ip address 200.0.13.1 255.255.255.252
 no shutdown
 exit
! placeholder so BGP can announce our /16
ip route 200.1.0.0 255.255.0.0 null0
! OSPF inside AS 100
router ospf 10
 router-id 1.1.1.1
 network 200.1.0.0 0.0.0.3 area 0
 ! tell the PE: "send me what you don't know"
 default-information originate always
 exit
! BGP with the other providers
router bgp 100
 bgp router-id 1.1.1.1
 neighbor 200.0.12.2 remote-as 200
 neighbor 200.0.13.2 remote-as 300
 network 200.1.0.0 mask 255.255.0.0
 end
copy running-config startup-config
```
ההערות אומרות: שומר מקום כדי ש-BGP יוכל לפרסם את ה-‎/16 שלנו; ‏OSPF בתוך AS 100; אומרים ל-PE: "שלח
אליי את מה שאתה לא מכיר"; ‏BGP עם הספקים האחרים.

### 4.2 ‏R-ISPA-PE
```
enable
configure terminal
hostname R-ISPA-PE
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  ISP-A (AS 100) - AUTHORIZED ACCESS ONLY  *
#
interface gi0/0
 description to R-ISPA-BR
 ip address 200.1.0.2 255.255.255.252
 no shutdown
interface gi0/1
 description customer: Intel Haifa
 ip address 200.1.1.1 255.255.255.252
 no shutdown
interface gi0/2
 description internet services LAN
 ip address 200.1.100.1 255.255.255.0
 no shutdown
 exit
! Intel Haifa's public static-NAT block is behind the customer's router
ip route 200.1.10.0 255.255.255.248 200.1.1.2
router ospf 10
 router-id 1.1.1.2
 passive-interface gi0/1
 passive-interface gi0/2
 network 200.1.0.0 0.0.0.3 area 0
 network 200.1.1.0 0.0.0.3 area 0
 network 200.1.100.0 0.0.0.255 area 0
 redistribute static subnets
 end
copy running-config startup-config
```
ההערה אומרת: בלוק ה-static NAT הציבורי של אינטל חיפה נמצא מאחורי הנתב של הלקוח.

### 4.3 ‏R-ISPB-BR ‏(AS 200)
```
enable
configure terminal
hostname R-ISPB-BR
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  ISP-B (AS 200) - AUTHORIZED ACCESS ONLY  *
#
interface gi0/0
 description to R-ISPB-PE
 ip address 200.2.0.1 255.255.255.252
 no shutdown
interface gi0/1
 description eBGP to R-ISPA-BR (AS 100)
 ip address 200.0.12.2 255.255.255.252
 no shutdown
interface gi0/2
 description eBGP to R-ISPC-BR (AS 300)
 ip address 200.0.23.1 255.255.255.252
 no shutdown
 exit
ip route 200.2.0.0 255.255.0.0 null0
router ospf 10
 router-id 2.2.2.1
 network 200.2.0.0 0.0.0.3 area 0
 default-information originate always
 exit
router bgp 200
 bgp router-id 2.2.2.1
 neighbor 200.0.12.1 remote-as 100
 neighbor 200.0.23.2 remote-as 300
 network 200.2.0.0 mask 255.255.0.0
 end
copy running-config startup-config
```

### 4.4 ‏R-ISPB-PE
```
enable
configure terminal
hostname R-ISPB-PE
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  ISP-B (AS 200) - AUTHORIZED ACCESS ONLY  *
#
interface gi0/0
 description to R-ISPB-BR
 ip address 200.2.0.2 255.255.255.252
 no shutdown
interface gi0/1
 description customer: Intel Jerusalem (step 13)
 ip address 200.2.1.1 255.255.255.252
 no shutdown
interface gi0/2
 description DSL customer: Intel Haifa backup
 ip address 200.2.9.1 255.255.255.252
 no shutdown
 exit
! Jerusalem's dynamic-NAT pool (step 13)
ip route 200.2.10.0 255.255.255.248 200.2.1.2
router ospf 10
 router-id 2.2.2.2
 passive-interface gi0/1
 passive-interface gi0/2
 network 200.2.0.0 0.0.0.3 area 0
 network 200.2.1.0 0.0.0.3 area 0
 network 200.2.9.0 0.0.0.3 area 0
 redistribute static subnets
 end
copy running-config startup-config
```
ההערה אומרת: מאגר ה-dynamic NAT של ירושלים (שלב 13).

### 4.5 ‏R-ISPC-BR ‏(AS 300)
```
enable
configure terminal
hostname R-ISPC-BR
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  ISP-C (AS 300) - AUTHORIZED ACCESS ONLY  *
#
interface gi0/0
 description to R-ISPC-PE
 ip address 200.3.0.1 255.255.255.252
 no shutdown
interface gi0/1
 description eBGP to R-ISPA-BR (AS 100)
 ip address 200.0.13.2 255.255.255.252
 no shutdown
interface gi0/2
 description eBGP to R-ISPB-BR (AS 200)
 ip address 200.0.23.2 255.255.255.252
 no shutdown
 exit
ip route 200.3.0.0 255.255.0.0 null0
router ospf 10
 router-id 3.3.0.1
 network 200.3.0.0 0.0.0.3 area 0
 default-information originate always
 exit
router bgp 300
 bgp router-id 3.3.0.1
 neighbor 200.0.13.1 remote-as 100
 neighbor 200.0.23.1 remote-as 200
 network 200.3.0.0 mask 255.255.0.0
 end
copy running-config startup-config
```

### 4.6 ‏R-ISPC-PE ‏(dual-stack: ‏IPv4 + ‏IPv6 לכיוון הלקוחות שלו)
```
enable
configure terminal
hostname R-ISPC-PE
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  ISP-C (AS 300) - AUTHORIZED ACCESS ONLY  *
#
ipv6 unicast-routing
interface gi0/0
 description to R-ISPC-BR
 ip address 200.3.0.2 255.255.255.252
 no shutdown
interface gi0/1
 description customer: Intel Kiryat Gat (step 14)
 ip address 200.3.1.1 255.255.255.252
 ipv6 address 2001:DB8:C:1::1/64
 no shutdown
interface gi0/2
 description home users
 ip address 200.3.50.1 255.255.255.0
 ipv6 address 2001:DB8:C:50::1/64
 ipv6 address FE80::1 link-local
 no shutdown
 exit
router ospf 10
 router-id 3.3.0.2
 passive-interface gi0/1
 passive-interface gi0/2
 network 200.3.0.0 0.0.0.3 area 0
 network 200.3.1.0 0.0.0.3 area 0
 network 200.3.50.0 0.0.0.255 area 0
 end
copy running-config startup-config
```

### 4.7 שרתי האינטרנט והמחשב הביתי
**הגדרות IP** ‏(Desktop ‏←‏ IP Configuration ‏←‏ Static):

<div dir="rtl">

| מכשיר | ‎‏IP | מסיכה | שער | ‎‏DNS |
|---|---|---|---|---|
| ‎SRV-ISP-DNS | ‎200.1.100.10 | ‎255.255.255.0 | ‎200.1.100.1 | ‎200.1.100.10 |
| ‎SRV-ISP-WEB1 | ‎200.1.100.11 | ‎255.255.255.0 | ‎200.1.100.1 | ‎200.1.100.10 |
| ‎SRV-ISP-WEB2 | ‎200.1.100.12 | ‎255.255.255.0 | ‎200.1.100.1 | ‎200.1.100.10 |
| ‎PC-HOME-01 | ‎200.3.50.10 | ‎255.255.255.0 | ‎200.3.50.1 | ‎200.1.100.10 |

</div>

- **‏SRV-ISP-DNS** ‏←‏ Services ‏←‏ DNS **On** ‏←‏ רשומות A:
  ‏`www.isp-web1.com → 200.1.100.11`, ‏`www.isp-web2.com → 200.1.100.12`,
  **`www.intel.lab → 200.1.10.3`** (הכתובת ה**ציבורית** של האתר שלנו!). שאר השירותים Off.
- **‏SRV-ISP-WEB1** ‏←‏ Services ‏←‏ HTTP ‏←‏ ערכו את `index.html` ‏←‏ ‎`<h1>ISP Web Server 1</h1>`‎ ‏←‏ Save.
- **‏SRV-ISP-WEB2** ‏←‏ אותו דבר עם ‎`<h1>ISP Web Server 2</h1>`‎.
- ‏`SW-ISPA-NET` ו-`SW-ISPC-HOME`: רק משנים את השם — לא צריך להגדיר אותם.

### 4.8 ‏R-HFA-EDGE — צד ה-WAN, ‏NAT וגיבוי ה-DSL
התחברו (`admin` / `Intel#Adm1n`):
```
enable
configure terminal
interface gi0/0
 ip nat inside
interface gi0/1
 description PRIMARY to R-ISPA-PE
 ip address 200.1.1.2 255.255.255.252
 ip nat outside
 no shutdown
interface gi0/2
 description BACKUP via DSL to R-ISPB-PE
 ip address 200.2.9.2 255.255.255.252
 ip nat outside
 no shutdown
 exit

! ---------- static routing toward the WAN (req. 22.17) ----------
ip route 0.0.0.0 0.0.0.0 200.1.1.1
! floating static = backup (distance 10)
ip route 0.0.0.0 0.0.0.0 200.2.9.1 10

! ---------- PAT: all of HQ browses as 200.1.1.2 ----------
ip access-list extended NAT-HFA
 remark --- remote-access VPN users are NOT translated (step 15) ---
 deny ip 10.10.0.0 0.0.255.255 172.16.250.0 0.0.0.255
 permit ip 10.10.0.0 0.0.255.255 any
 exit
ip nat inside source list NAT-HFA interface gi0/1 overload

! ---------- static NAT: publish the web server and NTP ----------
ip nat inside source static 10.10.200.13 200.1.10.3
ip nat inside source static udp 10.10.200.14 123 200.1.10.4 123
 end
copy running-config startup-config
```
ההערות אומרות: ניתוב סטטי לכיוון ה-WAN (דרישה 22.17); ‏floating static = גיבוי (distance 10);
‏PAT — כל המטה גולש בתור 200.1.1.2; משתמשי VPN בגישה מרחוק **לא** מתורגמים (שלב 15); ‏static NAT —
מפרסמים את שרת ה-web ואת ה-NTP.

### 4.9 ‏ASA — פותחים את החורים לאתר ול-NTP
```
enable
configure terminal
access-list OUTSIDE_IN extended permit tcp any host 10.10.200.13 eq www
access-list OUTSIDE_IN extended permit udp any host 10.10.200.14 eq ntp
end
write memory
```
(ה-ASA רואה את כתובת השרת ה**אמיתית** — נתב הקצה כבר תרגם אותה בחזרה.)

### 4.10 מה הפקודות החדשות אומרות

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`router bgp 100` | "הפעל BGP; אני AS 100" |
| ‎`neighbor 200.0.12.2 remote-as 200` | "הנתב בכתובת 200.0.12.2 נמצא ב-AS 200 — היו שותפי BGP" |
| ‎`network 200.1.0.0 mask 255.255.0.0` | "פרסם את הבלוק שלי לעולם" |
| ‎`ip route 200.1.0.0 255.255.0.0 null0` | נתיב שומר מקום, כדי שהבלוק יהיה קיים בטבלה |
| ‎`default-information originate always` | "אמור לשכני ה-OSPF שלי: שלחו אליי תעבורה לא מוכרת" |
| ‎`redistribute static subnets` | "שתף בתוך OSPF את הנתיבים הסטטיים שלי (בלוקים של לקוחות)" |
| ‎`ip nat inside` / `ip nat outside` | איזה צד של הנתב פרטי / ציבורי |
| ‎`ip nat inside source list NAT-HFA interface gi0/1 overload` | "תרגם את כל מי שברשימה לכתובת של Gi0/1, בעזרת פורטים" = **PAT** |
| ‎`ip nat inside source static 10.10.200.13 200.1.10.3` | "השרת הזה הוא תמיד הכתובת הציבורית הזו" = **static NAT** |
| ‎`ip route 0.0.0.0 0.0.0.0 200.2.9.1 10` | נתיב ברירת מחדל לגיבוי (floating static) |

</div>

---

## חלק 5 — בודקים את העבודה

### 5.1 ‏BGP
לחצו כמה פעמים על **Fast Forward Time** ‏(BGP עולה לאט). על **R-ISPA-BR**:
```
show ip bgp summary
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
200.0.12.2      4   200      10      10        4    0    0 00:02:10        2
200.0.13.2      4   300      10      10        4    0    0 00:02:05        2
```
✅ בעמודה האחרונה יש **מספר** ‏←‏ השותפות פעילה. (‏`Active` או `Idle` = לא פעילה.)
```
show ip bgp
   Network          Next Hop            Metric LocPrf Weight Path
*> 200.1.0.0/16     0.0.0.0                  0         32768 i
*> 200.2.0.0/16     200.0.12.2               0             0 200 i
*  200.3.0.0/16     200.0.12.2                             0 200 300 i
*>                  200.0.13.2               0             0 300 i
```
‏‎`*>`‎ = הנתיב הטוב ביותר. העמודה `Path` היא רשימת ה-ASים בדרך. ל-200.3.0.0 יש שני נתיבים: ישיר (300)
ודרך ISP-B ‏(200 300) — הגיבוי.

על **R-ISPA-PE**: ‏`show ip route` ‏←‏ `O*E2 0.0.0.0/0` (מה-BR) ו-`S 200.1.10.0/29 via 200.1.1.2`.

### 5.2 אינטרנט מחיפה

<div dir="rtl">

| מאיפה | עושים | מה אמור לקרות |
|---|---|---|
| מחשב ENG | בדפדפן: Web Browser ‏←‏ `http://www.isp-web1.com` | ‎✅ "ISP Web Server 1" |
| מחשב ENG | ‎`ping 200.1.100.12` | ‎✅ |
| ‎LT-HFA-GUEST-01 | בדפדפן: Web Browser ‏←‏ `http://www.isp-web2.com` | ✅ לאורחים יש אינטרנט |
| ‎R-HFA-EDGE | ‎`show ip nat translations` | שורות כמו `icmp 200.1.1.2:5 10.10.16.11:5 …`‎ ‏(PAT) + שתי השורות הסטטיות |

</div>

### 5.3 האינטרנט מגיע לאתר של אינטל

<div dir="rtl">

| מאיפה | עושים | מה אמור לקרות |
|---|---|---|
| ‎PC-HOME-01 | בדפדפן: Web Browser ‏←‏ `http://www.intel.lab` | ✅ "Intel Israel - Intranet" — דרך 200.1.10.3 |
| ‎PC-HOME-01 | ‎`ping 10.10.16.1` | ❌ כתובות פרטיות לא קיימות באינטרנט |

</div>

### 5.4 בדיקות יתירות
1. **משולש ה-BGP:** כבו את הקישור ISPA-BR ↔ ISPC-BR (ב-R-ISPA-BR: ‏`interface gi0/2` ‏←‏ `shutdown`).
   אחרי דקה (Fast Forward), ‏`show ip bgp` ‏←‏ ל-200.3.0.0/16 יש עכשיו רק ‎`200 300`. ‏PC-HOME-01 עדיין
   פותח את www.intel.lab ✅. ‏`no shutdown` בחזרה.
2. **גיבוי ה-DSL:** ב-R-HFA-EDGE ‏`ping 200.2.0.1 repeat 1000` (עוצרים עם Ctrl+Shift+6), ותוך כדי כבו
   את Gi0/1. ‏`show ip route` ‏←‏ `S* 0.0.0.0/0 [10/0] via 200.2.9.1` — הגיבוי השתלט דרך המודם.
   ‏`no shutdown` ל-Gi0/1 ‏←‏ הראשי חוזר.
   (מגבלה: ה-PAT קשור ל-Gi0/1, ולכן ה**משתמשים** לא גולשים דרך ה-DSL — ראו את האתגר.)

---

## חלק 6 — שומרים
‏`copy running-config startup-config` בכל הנתבים, ‏`write memory` ב-ASA ‏←‏ **File → Save**.

## נקודת ביקורת
- [ ] ‏6 שותפויות BGP פעילות (2 לכל BR)
- [ ] המחשבים בחיפה גולשים לשני שרתי ה-web של הספק
- [ ] המחשב הביתי פותח את www.intel.lab
- [ ] תרגומי NAT נראים ב-R-HFA-EDGE
- [ ] נתיב הגיבוי של ה-DSL מופיע כשהראשי למטה

## אם משהו לא עובד

<div dir="rtl">

| בעיה | פתרון |
|---|---|
| שכן BGP תקוע ב-**Active/Idle** | ‏IP או מספר AS שגוי של השכן, או שהקישור למטה (‏`show ip interface brief`). קודם עשו ping לשכן |
| בלוק חסר ב-`show ip bgp` | ה-`network ... mask` לא תואם **בדיוק** לנתיב — בדקו את נתיב ה-null0 ואת המסיכה |
| חיפה לא גולשת אבל נתב הקצה כן | חסר `ip nat inside` על Gi0/0, או שה-ACL של ה-NAT לא תופסת את 10.10.x |
| המחשב הביתי לא פותח את www.intel.lab | רשומת ה-DNS של הספק (חייבת להיות 200.1.10.3); ‏`ip route 200.1.10.0 ...`‎ + ‏`redistribute static subnets` ב-R-ISPA-PE; שורת ה-ACL ל-www ב-ASA |
| קישור ה-DSL אדום | חסר המיפוי של ה-DSL בענן (3.3), או שכבל הטלפון בפורט הלא נכון של המודם |

</div>

## אתגר
גרמו גם ל**משתמשים** לשרוד נפילה של הקישור הראשי, על ידי הוספת כלל PAT שני ל-Gi0/2.
רמז: שני כללי `ip nat inside source list` עם אותה ACL מתנגשים — השתמשו ב-**route-maps**.

<details dir="rtl"><summary>תשובה</summary>

<div dir="ltr">

```
route-map NAT-PRIMARY permit 10
 match ip address NAT-HFA
 match interface gi0/1
route-map NAT-BACKUP permit 10
 match ip address NAT-HFA
 match interface gi0/2
no ip nat inside source list NAT-HFA interface gi0/1 overload
ip nat inside source route-map NAT-PRIMARY interface gi0/1 overload
ip nat inside source route-map NAT-BACKUP interface gi0/2 overload
```

</div>

התמיכה של Packet Tracer ב-`ip nat ... route-map` תלויה בגרסה. אם הפקודה נדחית, כתבו בספר הפרויקט
שגיבוי ה-DSL משרת את הנתב עצמו, ושבעולם האמיתי הפתרון הוא NAT עם route-map.
</details>

---

## 🛠 הפרויקט שלכם

עשיתם את השלב הזה על הדוגמה של אינטל. עכשיו עשו אותו שוב בפרויקט **שלכם**, עם הערכים
מהתוכנית **שלכם** (`my-project/plan.md`). הפקודות זהות — רק הערכים משתנים.

<div dir="rtl">

| בדוגמה | בפרויקט שלכם — לוקחים מ |
|---|---|
| מספרי ה-AS של הספקים 100 / 200 / 300 | מספרי AS משלכם |
| בלוקים ציבוריים ‎`200.1/2/3.0.0/16`, בין הספקים ‎`200.0.0.0/16` | תוכנית, חלק ג (בלוקי הספקים שלכם) |
| ‏Static NAT לשרתי ה-web וה-NTP, ‏PAT לגלישה | תוכנית, חלק ה (שורת ה-NAT — static באתר אחד, dynamic באתר אחר, overload בשלישי — דרישה 10) |
| גיבוי DSL עם floating static route | תוכנית, חלק ה (שורת גיבוי ה-WAN) |
| ניתוב סטטי מהאתר ל-WAN | להשאיר — משרד החינוך דורש (דרישה 22.17) |

</div>

**בדיקה:** ‏`show ip bgp summary` מראה שכל שכן במצב established; מחשב פנימי פותח דף אינטרנט;
‏`show ip nat translations` מציג את הכתובות שלכם.

💾 שמרו בשם `my-project/step12.pkt`.

---

## 🎓 מסבירים לבוחן

בבחינה, הבוחן מצביע על הפרויקט **שלכם** ומבקש **להסביר** ו**להראות**. תרגלו כל שאלה
**בקול**, ואז הראו את התשובה בפרויקט שלכם — לא בדוגמה. כסו את התשובה, ענו בעצמכם, ורק אז
פתחו והשוו.

★1–★3 = שאלה ממאגר השאלות של משרד החינוך (רמת קושי 1–3).
◆ = לא במאגר, אבל בוחנים שואלים אותה לעיתים קרובות.

**1. ★1 מה תפקידו של NAT? מהם 3 הסוגים ובמה הם שונים?**

<details dir="rtl"><summary>תשובה</summary>

‏NAT מתרגם כתובות פרטיות לציבוריות (ובחזרה), כדי שרשתות פרטיות יוכלו להגיע לאינטרנט וכדי לחסוך
כתובות ציבוריות. **‏Static**: פרטית אחת ↔ ציבורית אחת, קבוע — לשרת שהאינטרנט חייב להגיע אליו.
**‏Dynamic**: כתובות פרטיות לוקחות כתובת פנויה ממאגר של כתובות ציבוריות. **‏Overload ‏(PAT)**: הרבה
כתובות פרטיות חולקות כתובת ציבורית אחת, ומופרדות לפי מספרי פורט.

**איפה מראים:** `show running-config | include nat`, `show ip nat translations`
</details>

**2. ★1 מהו PAT?**

<details dir="rtl"><summary>תשובה</summary>

‏Port Address Translation ‏(NAT overload): הרבה מחשבים פנימיים חולקים IP ציבורי אחד; הנתב מבדיל בין
השיחות שלהם לפי מספר פורט המקור.

**איפה מראים:** `show ip nat translations` ‏←‏ אותו IP ציבורי עם פורטים שונים
</details>

**3. ★1 הצג את הגדרות ה-NAT בפרויקט שלך.**

<details dir="rtl"><summary>תשובה</summary>

‏`ip nat inside` / `ip nat outside` על הממשקים; ‏`ip nat inside source static …`‎ לכל שרת שמפורסם;
ה-ACL של הכתובות הפנימיות + ‏`ip nat inside source list … interface … overload` לגלישה.

**איפה מראים:** `show running-config`, `show ip nat translations`
</details>

**4. ★2 איזו פקודה מציגה את טבלת הניתוב של BGP?**

<details dir="rtl"><summary>תשובה</summary>

‏`show ip bgp` (טבלת BGP); ‏`show ip bgp summary` (השכנים והמצב שלהם).

**איפה מראים:** בנתב של ספק
</details>

**5. ★2 מה ההבדל בין IGP ל-EGP? מהי מערכת אוטונומית (AS)?**

<details dir="rtl"><summary>תשובה</summary>

‏AS הוא רשת תחת ניהול אחד עם מדיניות ניתוב אחת, שמזוהה במספר AS. ‏IGP ‏(OSPF, ‏EIGRP) מנתב **בתוך**
AS; ‏EGP ‏(BGP) מנתב **בין** ASים.

**איפה מראים:** `show ip bgp summary` ‏←‏ מספרי AS
</details>

**6. ★2 מה ההבדל בין iBGP ל-eBGP?**

<details dir="rtl"><summary>תשובה</summary>

‏eBGP: בין נתבים ב-ASים **שונים** (administrative distance ‏20). ‏iBGP: בין נתבים **באותו** AS
‏(administrative distance ‏200).

**איפה מראים:** `show ip bgp summary`
</details>

**7. ★2 איזו תכונה (attribute) של BGP מונעת לולאות?**

<details dir="rtl"><summary>תשובה</summary>

‏AS_PATH: רשימת ה-ASים שהנתיב עבר דרכם. נתב שרואה את מספר ה-AS שלו בנתיב דוחה את הנתיב.

**איפה מראים:** `show ip bgp` ‏←‏ העמודה Path
</details>

**8. ★3 איזו תכונה קובעת את נקודת היציאה מה-AS? מהם MED ו-Weight?**

<details dir="rtl"><summary>תשובה</summary>

‏LOCAL_PREF קובע איזה נתב הוא ה**יציאה** מה-AS שלכם (הגבוה מנצח, משותף בתוך ה-AS). ‏MED אומר ל-**AS
שכן** איזו כניסה ל-AS שלכם אתם מעדיפים (הנמוך מנצח). ‏Weight קיים רק אצל Cisco, מקומי לנתב אחד,
ונבדק ראשון (הגבוה מנצח).

**איפה מראים:** —
</details>

**9. ◆ למה הניתוב מהאתר ל-WAN סטטי ולא דרך ה-IGP? מהו floating static route?**

<details dir="rtl"><summary>תשובה</summary>

כדי שמידע הניתוב הפנימי לא ייחשף לספק, ושהספק לא יוכל להכניס נתיבים לחברה (דרישה 22.17). ‏Floating
static route הוא נתיב גיבוי עם administrative distance גבוה יותר (למשל ‎`… 10`): משתמשים בו רק כשהנתיב
הראשי נעלם — כאן, קו הגיבוי של ה-DSL.

**איפה מראים:** `show ip route static`; כבו את הקישור הראשי והסתכלו שוב
</details>

---

## 🔁 עושים שוב — בלי המדריך

הבוחן יכול לבקש מכם להגדיר משהו שוב, מולו. תצליחו רק אם עשיתם את זה **בלי המדריך** לפני כן.
עשו את התרגיל הזה בפרויקט שלכם:

בעותק של הקובץ שלכם, מחקו את שורות ה-NAT מנתב הקצה. בלי העמוד הזה, כתבו אותן שוב מתוך התוכנית
שלכם (inside/outside, ‏static NAT לשרת שלכם, ‏PAT לגלישה). יעד: **‏10 דקות**. אחר כך גלשו ממחשב, פתחו
את השרת שלכם מצד האינטרנט, והראו `show ip nat translations`. הסבירו שכן BGP אחד עם
`show ip bgp summary`.

---

## 👩‍🏫 הערות למורה
- **שיעור 1:** האינטרנט כרשת של ASים; ‏BGP מול OSPF (כבישים בינלאומיים מול כבישי עיר); בנייה
  וחיווט (14 כבלים!) ‏←‏ הגדרת ISP-A.
- **שיעור 2:** ‏ISP-B ו-ISP-C ‏←‏ בדיקות BGP (‏`show ip bgp`, קריאת ה-AS path) ‏←‏ בדיקת משולש ה-BGP.
- **שיעור 3:** סוגי NAT עם ההשוואה למרכזיה ‏←‏ NAT בנתב הקצה ‏←‏ החורים ב-ASA ‏←‏ בדיקות 5.2–5.3.
- **שיעור 4:** מודם DSL + ענן + ‏floating static ‏←‏ בדיקת הגיבוי ‏←‏ אתגר.
- **מראים NAT במצב Simulation:** ‏ping ממחשב ל-200.1.100.11, לוחצים על החבילה לפני ואחרי R-HFA-EDGE —
  כתובת המקור משתנה מ-10.10.16.x ל-200.1.1.2.
- **שאלות נפוצות של תלמידים**
  - *"למה BGP לוקח כל כך הרבה זמן?"* — הוא מתוכנן ליציבות, לא למהירות. לחצו Fast Forward.
  - *"למה לא להריץ OSPF מול הספק?"* — היינו מספרים לאינטרנט את המפה הפנימית שלנו — בעיה של אבטחה
    ושל יציבות. נתיב ברירת מחדל סטטי אחד מספיק.
- **טעויות אופייניות:** ‏cross-over מול straight בין נתבים; מספרי AS עם שגיאת כתיב; שכחת `ip nat inside`
  על הממשק הפנימי.
