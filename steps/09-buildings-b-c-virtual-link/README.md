# שלב 09 — בניינים B ו-C + ‏virtual link של OSPF

<div dir="rtl">

> ⏱ ‏4 שיעורים · 🎯 דרישות משרד החינוך 8, ‏22.16, ‏22.15, ‏20.1, ‏20.2\
> 📁 מתחילים מ: `my-work/step08.pkt`\
> 💾 שומרים בשם: `my-work/step09.pkt`

</div>

<div dir="rtl">

> ✅ **לפני שמתחילים:** כל הסעיפים בנקודת הביקורת של שלב 08 מסומנים, ועשיתם את
> תרגיל ה-🔁 שלו בפרויקט שלכם. אל תדלגו על שלבים — כל שלב בנוי על הקובץ של השלב הקודם.

</div>

## מה יהיה לכם בסוף השלב
הרשת המקומית של המטה בחיפה **שלמה**: ‏3 בניינים, ‏6 מחלקות, תכנון תלת-שכבתי, ‏OSPF areas
‏0/1/2/3. בניין C מחובר רק לבניין B, ולכן תפגשו בעיית OSPF אמיתית ותפתרו אותה עם
**virtual link** (קישור וירטואלי).

```
                       CORE1 ═══════ CORE2                        AREA 0
                    ╱    │    ╲    ╱   │    ╲
       A-DIST1/2 (area 1)      B-DIST1 ═ B-DIST2 (ABRs 0/2)       AREA 2 links
                                 │   ╲  ╱   │
                                 │    ╳     │         10.10.36.x/30
                                 │   ╱  ╲   │
                              C-DIST1 ═ C-DIST2 (ABRs 2/3)        AREA 3
                    ······ virtual links B-DIST ⇄ C-DIST through area 2 ······
```
(למעלה: ‏CORE1 ו-CORE2 ב-area 0. ‏A-DIST ב-area 1. ‏B-DIST1/2 הם ABR בין area 0 ל-area 2. ‏C-DIST1/2 הם
ABR בין area 2 ל-area 3, מחוברים ל-B בקישורי ‎10.10.36.x/30. הקו המנוקד = ה-virtual links דרך area 2.)

<div dir="rtl">

> **איך משתמשים בשלב הזה בכיתה:** בניינים B ו-C חוזרים על כל מה שעשינו בשלבים 02–08.
> תלמידים חזקים יכולים לנסות להגדיר כל מכשיר **לפני** שהם מסתכלים על ההגדרות שלו למטה — זו
> החזרה הכי טובה על הקורס. כל השאר מקלידים מתוך המדריך.

</div>

---

## חלק 1 — קודם מבינים (בשפה פשוטה)

### 1.1 אותו מתכון, בניינים חדשים
בניינים B ו-C בנויים בדיוק לפי המתכון של בניין A:

<div dir="rtl">

| שכבה | בניין A | בניין B | בניין C |
|---|---|---|---|
| דומיין VTP | ‎HFA-A | ‎**HFA-B** | ‎**HFA-C** |
| מחלקות | הנדסה (10), כספים (20) | **משאבי אנוש (40), שיווק (50)** | **מו"פ (70), IT ‏(80)** |
| ‏VLAN מדפסות | ‎30 | ‎**60** | ‎**90** |
| ‏VLAN ניהול 99 | ‎10.10.19.0/24 | ‎**10.10.35.0/24** | ‎**10.10.51.0/24** |
| ‎‏OSPF area | ‎1 (10.10.16.0/20) | ‎**2 (10.10.32.0/20)** | ‎**3 (10.10.48.0/20)** |
| הקישורים כלפי מעלה הולכים אל | ה-core | ה-core | **בניין B** ⚠️ |

</div>

ל-VLAN 99 יש אותו **מספר** בכל בניין אבל **רשת משנה אחרת** — זה בסדר, כי הבניינים מחוברים
בקישורים מנותבים: ‏VLANים לא עוברים מבניין לבניין.

### 1.2 הבעיה: בניין C לא נוגע ב-area 0
ל-OSPF יש כלל נוקשה: **כל area חייב להתחבר ל-area 0** (עמוד השדרה, backbone). נתיבים בין
areas עוברים רק *דרך* area 0 — כמו ערים שמותר להן לסחור זו עם זו רק דרך הכביש הארצי.

בניין C ‏(area 3) מחובר רק ל-area 2 של בניין B. לכן:
- ל-C-DIST1/2 אין רגל ב-area 0 ‏←‏ הם לא יכולים להעביר את הנתיבים של area 3 לעמוד השדרה;
- בניין C הופך ל**אי**: אף אחד מחוץ ל-area 2 לא מגיע אליו, והוא לא מגיע לשרתים.

קודם **תראו** את זה קורה, ואחר כך תתקנו.

### 1.3 הפתרון: virtual link
**‏Virtual link** הוא חתיכה לוגית של area 0 ש"עוברת במנהרה" דרך area אחר (area ה-**transit**,
המעבר — כאן area 2), בין שני ABRs:
- קצה אחד בנתב שיושב ב-**area 0 + area 2** ‏←‏ B-DIST1/2 (‏router-IDs ‏10.10.5.21 / ‏.22)
- הקצה השני בנתב שיושב ב-**area 2 + area 3** ‏←‏ C-DIST1/2 (‏router-IDs ‏10.10.63.1 / ‏.2)

השוואה: לעיירה של בניין C אין יציאה לכביש הארצי, אז חותמים על הסכם עם העיירה השכנה שאחד
הכבישים שלה ייחשב **כאילו** הוא כביש ארצי.

הפקודה משתמשת ב-**router-ID** של הקצה השני — לא בכתובת של ממשק:
`area 2 virtual-link 10.10.63.1`. בונים את כל 4 הצירופים (B1↔C1, ‏B1↔C2, ‏B2↔C1, ‏B2↔C2),
כך שגם אם מתג אחד נופל, ‏area 3 נשאר מחובר.

<div dir="rtl">

> דרישה 22.16 מבקשת בדיוק את זה: "OSPF מרובה areas בסניף אחד, כולל מבנה שמחייב virtual link".

</div>

### 1.4 למה הקישורים בין B ל-C ממוספרים 10.10.36.x
הם שייכים ל-area 2, ולכן הם מקבלים כתובות **בתוך הבלוק של area 2** ‏(10.10.32.0/20). כך הסיכום
של B ‏‎`10.10.32.0/20` מכסה גם אותם, והם לא "דולפים" ל-core כנתיבים נוספים. ה-loopbacks של בניין
C ‏(10.10.63.x) נמצאים בתוך הבלוק של **area 3** מאותה סיבה.

---

## חלק 2 — הכנה
**File → Open** ‏←‏ `my-work/step08.pkt` ‏←‏ **File → Save As** ‏←‏ `my-work/step09.pkt`.

---

## חלק 3 — בונים (לחיצה אחרי לחיצה)

### 3.1 המכשירים של בניין B (במלבן "BUILDING B")

<div dir="rtl">

| דגם | ‎‏Display Name |
|---|---|
| ‎‏3650-24PS (+ **AC-POWER-SUPPLY**!) | ‎`SWL3-HFA-B-DIST1`, `SWL3-HFA-B-DIST2` |
| ‎2960 | ‎`SW-HFA-B-ACC1`, `SW-HFA-B-ACC2` |
| ‎‏PC ×4 | ‎`PC-HFA-HR-01`, `PC-HFA-HR-02`, `PC-HFA-MKT-01`, `PC-HFA-MKT-02` |
| ‎‏Printer | ‎`PRN-HFA-B-01` |

</div>

### 3.2 המכשירים של בניין C (במלבן "BUILDING C")

<div dir="rtl">

| דגם | ‎‏Display Name |
|---|---|
| ‎‏3650-24PS (+ **AC-POWER-SUPPLY**!) | ‎`SWL3-HFA-C-DIST1`, `SWL3-HFA-C-DIST2` |
| ‎2960 | ‎`SW-HFA-C-ACC1`, `SW-HFA-C-ACC2` |
| ‎‏PC ×4 | ‎`PC-HFA-RND-01`, `PC-HFA-RND-02`, `PC-HFA-IT-01`, `PC-HFA-IT-02` |
| ‎‏Printer | ‎`PRN-HFA-C-01` |

</div>

### 3.3 כבלים — בניין B (מתג ↔ מתג: **Cross-Over**; מכשיר קצה ↔ מתג: **Straight-Through**)

<div dir="rtl">

| לוחצים קודם על | פורט | לוחצים אחר כך על | פורט |
|---|---|---|---|
| ‎SW-HFA-B-ACC1 | ‎Gi0/1 | ‎SWL3-HFA-B-DIST1 | ‎Gi1/0/1 |
| ‎SW-HFA-B-ACC1 | ‎Gi0/2 | ‎SWL3-HFA-B-DIST2 | ‎Gi1/0/1 |
| ‎SW-HFA-B-ACC2 | ‎Gi0/1 | ‎SWL3-HFA-B-DIST1 | ‎Gi1/0/2 |
| ‎SW-HFA-B-ACC2 | ‎Gi0/2 | ‎SWL3-HFA-B-DIST2 | ‎Gi1/0/2 |
| ‎SWL3-HFA-B-DIST1 | ‎Gi1/0/23 | ‎SWL3-HFA-B-DIST2 | ‎Gi1/0/23 |
| ‎SWL3-HFA-B-DIST1 | ‎Gi1/0/24 | ‎SWL3-HFA-B-DIST2 | ‎Gi1/0/24 |
| ‎SWL3-HFA-B-DIST1 | ‎**Gi1/1/1** | ‎SWL3-HFA-CORE1 | ‎**Gi1/0/3** |
| ‎SWL3-HFA-B-DIST1 | ‎**Gi1/1/2** | ‎SWL3-HFA-CORE2 | ‎**Gi1/0/3** |
| ‎SWL3-HFA-B-DIST2 | ‎**Gi1/1/1** | ‎SWL3-HFA-CORE1 | ‎**Gi1/0/4** |
| ‎SWL3-HFA-B-DIST2 | ‎**Gi1/1/2** | ‎SWL3-HFA-CORE2 | ‎**Gi1/0/4** |
| ‎PC-HFA-HR-01 | ‎Fa0 | ‎SW-HFA-B-ACC1 | ‎Fa0/1 |
| ‎PC-HFA-HR-02 | ‎Fa0 | ‎SW-HFA-B-ACC2 | ‎Fa0/1 |
| ‎PC-HFA-MKT-01 | ‎Fa0 | ‎SW-HFA-B-ACC1 | ‎Fa0/11 |
| ‎PC-HFA-MKT-02 | ‎Fa0 | ‎SW-HFA-B-ACC2 | ‎Fa0/11 |
| ‎PRN-HFA-B-01 | ‎Fa0 | ‎SW-HFA-B-ACC1 | ‎Fa0/21 |

</div>

### 3.4 כבלים — בניין C (הקישורים כלפי מעלה שלו הולכים ל**בניין B**)

<div dir="rtl">

| לוחצים קודם על | פורט | לוחצים אחר כך על | פורט |
|---|---|---|---|
| ‎SW-HFA-C-ACC1 | ‎Gi0/1 | ‎SWL3-HFA-C-DIST1 | ‎Gi1/0/1 |
| ‎SW-HFA-C-ACC1 | ‎Gi0/2 | ‎SWL3-HFA-C-DIST2 | ‎Gi1/0/1 |
| ‎SW-HFA-C-ACC2 | ‎Gi0/1 | ‎SWL3-HFA-C-DIST1 | ‎Gi1/0/2 |
| ‎SW-HFA-C-ACC2 | ‎Gi0/2 | ‎SWL3-HFA-C-DIST2 | ‎Gi1/0/2 |
| ‎SWL3-HFA-C-DIST1 | ‎Gi1/0/23 | ‎SWL3-HFA-C-DIST2 | ‎Gi1/0/23 |
| ‎SWL3-HFA-C-DIST1 | ‎Gi1/0/24 | ‎SWL3-HFA-C-DIST2 | ‎Gi1/0/24 |
| ‎SWL3-HFA-C-DIST1 | ‎**Gi1/1/1** | ‎SWL3-HFA-B-DIST1 | ‎**Gi1/1/3** |
| ‎SWL3-HFA-C-DIST1 | ‎**Gi1/1/2** | ‎SWL3-HFA-B-DIST2 | ‎**Gi1/1/3** |
| ‎SWL3-HFA-C-DIST2 | ‎**Gi1/1/1** | ‎SWL3-HFA-B-DIST1 | ‎**Gi1/1/4** |
| ‎SWL3-HFA-C-DIST2 | ‎**Gi1/1/2** | ‎SWL3-HFA-B-DIST2 | ‎**Gi1/1/4** |
| ‎PC-HFA-RND-01 | ‎Fa0 | ‎SW-HFA-C-ACC1 | ‎Fa0/1 |
| ‎PC-HFA-RND-02 | ‎Fa0 | ‎SW-HFA-C-ACC2 | ‎Fa0/1 |
| ‎PC-HFA-IT-01 | ‎Fa0 | ‎SW-HFA-C-ACC1 | ‎Fa0/11 |
| ‎PC-HFA-IT-02 | ‎Fa0 | ‎SW-HFA-C-ACC2 | ‎Fa0/11 |
| ‎PRN-HFA-C-01 | ‎Fa0 | ‎SW-HFA-C-ACC1 | ‎Fa0/21 |

</div>

### 3.5 תוכנית הכתובות של השלב הזה

<div dir="rtl">

| קישור | רשת משנה | צד 1 | צד 2 | ‎‏Area |
|---|---|---|---|---|
| ‎B-DIST1 Gi1/1/1 ↔ CORE1 Gi1/0/3 | ‎10.10.4.16/30 | ‎B-DIST1 .17 | ‎CORE1 .18 | ‎0 |
| ‎B-DIST1 Gi1/1/2 ↔ CORE2 Gi1/0/3 | ‎10.10.4.20/30 | ‎B-DIST1 .21 | ‎CORE2 .22 | ‎0 |
| ‎B-DIST2 Gi1/1/1 ↔ CORE1 Gi1/0/4 | ‎10.10.4.24/30 | ‎B-DIST2 .25 | ‎CORE1 .26 | ‎0 |
| ‎B-DIST2 Gi1/1/2 ↔ CORE2 Gi1/0/4 | ‎10.10.4.28/30 | ‎B-DIST2 .29 | ‎CORE2 .30 | ‎0 |
| ‎B-DIST1 Gi1/1/3 ↔ C-DIST1 Gi1/1/1 | ‎10.10.36.0/30 | ‎B-DIST1 .1 | ‎C-DIST1 .2 | ‎2 |
| ‎B-DIST2 Gi1/1/3 ↔ C-DIST1 Gi1/1/2 | ‎10.10.36.4/30 | ‎B-DIST2 .5 | ‎C-DIST1 .6 | ‎2 |
| ‎B-DIST1 Gi1/1/4 ↔ C-DIST2 Gi1/1/1 | ‎10.10.36.8/30 | ‎B-DIST1 .9 | ‎C-DIST2 .10 | ‎2 |
| ‎B-DIST2 Gi1/1/4 ↔ C-DIST2 Gi1/1/2 | ‎10.10.36.12/30 | ‎B-DIST2 .13 | ‎C-DIST2 .14 | ‎2 |

</div>

<div dir="rtl">

| מכשיר | ‎‏Loopback0 / ‏router-ID | ניהול (VLAN 99) |
|---|---|---|
| ‎SWL3-HFA-B-DIST1 / DIST2 | ‎10.10.5.21 / 10.10.5.22 | ‎10.10.35.2 / .3 (VIP .1) |
| ‎SW-HFA-B-ACC1 / ACC2 | ‎— | ‎10.10.35.11 / .12 |
| ‎SWL3-HFA-C-DIST1 / DIST2 | ‎10.10.63.1 / 10.10.63.2 | ‎10.10.51.2 / .3 (VIP .1) |
| ‎SW-HFA-C-ACC1 / ACC2 | ‎— | ‎10.10.51.11 / .12 |

</div>

<div dir="rtl">

| ‎‏VLAN | שם | רשת משנה | ראשי (STP root + ‏HSRP active) |
|---|---|---|---|
| ‎40 | ‎HR | ‎10.10.32.0/24 | ‎B-DIST1 |
| ‎50 | ‎MARKETING | ‎10.10.33.0/24 | ‎B-DIST2 |
| ‎60 | ‎PRINTERS-B | ‎10.10.34.0/24 | ‎B-DIST1 |
| ‎99 | ‎MGMT-B | ‎10.10.35.0/24 | ‎B-DIST1 |
| ‎70 | ‎RND | ‎10.10.48.0/24 | ‎C-DIST1 |
| ‎80 | ‎IT | ‎10.10.49.0/24 | ‎C-DIST2 |
| ‎90 | ‎PRINTERS-C | ‎10.10.50.0/24 | ‎C-DIST1 |
| ‎99 | ‎MGMT-C | ‎10.10.51.0/24 | ‎C-DIST1 |

</div>

### 3.6 רשימת האורחים הסופית לניהול
מעכשיו מותר לנהל את ציוד הרשת מ**כל שלושת ה-VLANים של הניהול** ומ**מחלקת IT**. כל המכשירים
החדשים מקבלים את ה-ACL הזו; בחלק 7 מעדכנים את הישנים:
```
ip access-list standard MGMT-ONLY
 permit 10.10.19.0 0.0.0.255
 permit 10.10.35.0 0.0.0.255
 permit 10.10.51.0 0.0.0.255
 permit 10.10.49.0 0.0.0.255
 deny any log
```

---

## חלק 4 — מגדירים את בניין B

נכנסים לכל מתג חדש עם **Enter** (עדיין אין סיסמאות). כשבלוק מכיל `crypto key generate rsa`,
עונים **‎`1024`**.

### 4.1 ‏SWL3-HFA-B-DIST1 — הגדרה מלאה
```
enable
configure terminal
! ===== hardening =====
hostname SWL3-HFA-B-DIST1
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
! ===== VTP server of building B + VLANs =====
vtp domain HFA-B
vtp version 2
vtp password Intel#Vtp
vtp mode server
vlan 40
 name HR
vlan 50
 name MARKETING
vlan 60
 name PRINTERS-B
vlan 99
 name MGMT-B
vlan 998
 name NATIVE
vlan 999
 name PARKING
 exit
! ===== Spanning Tree =====
spanning-tree mode rapid-pvst
spanning-tree vlan 40,60,99 root primary
spanning-tree vlan 50 root secondary
! ===== trunks to the access switches + Root Guard =====
interface range gi1/0/1 - 2
 description TRUNK to access switch
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 40,50,60,99,998
 switchport nonegotiate
 spanning-tree guard root
 no shutdown
! ===== EtherChannel to B-DIST2 =====
interface range gi1/0/23 - 24
 description Po1 member to SWL3-HFA-B-DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 40,50,60,99,998
 switchport nonegotiate
 channel-group 1 mode active
 no shutdown
interface port-channel 1
 description EtherChannel to SWL3-HFA-B-DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 40,50,60,99,998
 switchport nonegotiate
! ===== unused =====
interface range gi1/0/3 - 22
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 exit
! ===== gateways (SVIs + HSRP) =====
ip routing
interface vlan 40
 description GW HR
 ip address 10.10.32.2 255.255.255.0
 standby version 2
 standby 40 ip 10.10.32.1
 standby 40 priority 110
 standby 40 preempt
 no shutdown
interface vlan 50
 description GW MARKETING
 ip address 10.10.33.2 255.255.255.0
 standby version 2
 standby 50 ip 10.10.33.1
 standby 50 priority 90
 standby 50 preempt
 no shutdown
interface vlan 60
 description GW PRINTERS-B
 ip address 10.10.34.2 255.255.255.0
 standby version 2
 standby 60 ip 10.10.34.1
 standby 60 priority 110
 standby 60 preempt
 no shutdown
interface vlan 99
 description GW MGMT-B
 ip address 10.10.35.2 255.255.255.0
 standby version 2
 standby 99 ip 10.10.35.1
 standby 99 priority 110
 standby 99 preempt
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
 exit
! ===== DHCP split scope: this switch gives .11-.130 =====
ip dhcp excluded-address 10.10.32.1 10.10.32.10
ip dhcp excluded-address 10.10.32.131 10.10.32.254
ip dhcp excluded-address 10.10.33.1 10.10.33.10
ip dhcp excluded-address 10.10.33.131 10.10.33.254
ip dhcp pool HFA-HR
 network 10.10.32.0 255.255.255.0
 default-router 10.10.32.1
 dns-server 10.10.200.11
 domain-name intel.lab
ip dhcp pool HFA-MARKETING
 network 10.10.33.0 255.255.255.0
 default-router 10.10.33.1
 dns-server 10.10.200.11
 domain-name intel.lab
 exit
! ===== routed uplinks: to the core (area 0) and to building C (area 2) =====
interface loopback 0
 ip address 10.10.5.21 255.255.255.255
interface gi1/1/1
 description to SWL3-HFA-CORE1 Gi1/0/3
 no switchport
 ip address 10.10.4.17 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/1/2
 description to SWL3-HFA-CORE2 Gi1/0/3
 no switchport
 ip address 10.10.4.21 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/1/3
 description to SWL3-HFA-C-DIST1 Gi1/1/1
 no switchport
 ip address 10.10.36.1 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/1/4
 description to SWL3-HFA-C-DIST2 Gi1/1/1
 no switchport
 ip address 10.10.36.9 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
 exit
! ===== OSPF: ABR between area 0 and area 2 =====
router ospf 1
 router-id 10.10.5.21
 passive-interface default
 no passive-interface gi1/1/1
 no passive-interface gi1/1/2
 no passive-interface gi1/1/3
 no passive-interface gi1/1/4
 no passive-interface vlan 99
 network 10.10.0.0 0.0.15.255 area 0
 network 10.10.32.0 0.0.15.255 area 2
 area 2 range 10.10.32.0 255.255.240.0
 exit
! ===== management: SSH, ACL, AAA, Syslog =====
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
(‎`1024`)
```
ip ssh version 2
ip ssh time-out 60
ip ssh authentication-retries 3
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
aaa new-model
tacacs-server host 10.10.1.11 key Intel#Tac
aaa authentication login default group tacacs+ local
ip tacacs source-interface loopback 0
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
ההערות אומרות: הקשחה; שרת VTP של בניין B + ‏VLANים; ‏Spanning Tree; ‏trunks למתגי ה-access +
‏Root Guard; ‏EtherChannel ל-B-DIST2; פורטים לא בשימוש; שערים (SVIs + ‏HSRP); ‏DHCP בטווח מפוצל —
המתג הזה נותן ‎.11–.130; קישורים מנותבים ל-core ‏(area 0) ולבניין C ‏(area 2); ‏OSPF — ‏ABR בין
area 0 ל-area 2; ניהול: ‏SSH, ‏ACL, ‏AAA, ‏Syslog. כל חלק כאן כבר מוכר לכם משלבים 02–08.

<div dir="rtl">

> כמו בשלב 07: אם מתג דוחה את `login block-for ...`‎, דלגו על השורה הזו באותו מתג.

</div>

### 4.2 ‏SWL3-HFA-B-DIST2 — הגדרה מלאה
```
enable
configure terminal
hostname SWL3-HFA-B-DIST2
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vtp domain HFA-B
vtp version 2
vtp password Intel#Vtp
vtp mode client
spanning-tree mode rapid-pvst
spanning-tree vlan 50 root primary
spanning-tree vlan 40,60,99 root secondary
interface range gi1/0/1 - 2
 description TRUNK to access switch
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 40,50,60,99,998
 switchport nonegotiate
 spanning-tree guard root
 no shutdown
interface range gi1/0/23 - 24
 description Po1 member to SWL3-HFA-B-DIST1
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 40,50,60,99,998
 switchport nonegotiate
 channel-group 1 mode active
 no shutdown
interface port-channel 1
 description EtherChannel to SWL3-HFA-B-DIST1
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 40,50,60,99,998
 switchport nonegotiate
interface range gi1/0/3 - 22
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 exit
ip routing
interface vlan 40
 description GW HR
 ip address 10.10.32.3 255.255.255.0
 standby version 2
 standby 40 ip 10.10.32.1
 standby 40 priority 90
 standby 40 preempt
 no shutdown
interface vlan 50
 description GW MARKETING
 ip address 10.10.33.3 255.255.255.0
 standby version 2
 standby 50 ip 10.10.33.1
 standby 50 priority 110
 standby 50 preempt
 no shutdown
interface vlan 60
 description GW PRINTERS-B
 ip address 10.10.34.3 255.255.255.0
 standby version 2
 standby 60 ip 10.10.34.1
 standby 60 priority 90
 standby 60 preempt
 no shutdown
interface vlan 99
 description GW MGMT-B
 ip address 10.10.35.3 255.255.255.0
 standby version 2
 standby 99 ip 10.10.35.1
 standby 99 priority 90
 standby 99 preempt
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
 exit
! DHCP: this switch gives .131-.254
ip dhcp excluded-address 10.10.32.1 10.10.32.130
ip dhcp excluded-address 10.10.33.1 10.10.33.130
ip dhcp pool HFA-HR
 network 10.10.32.0 255.255.255.0
 default-router 10.10.32.1
 dns-server 10.10.200.11
 domain-name intel.lab
ip dhcp pool HFA-MARKETING
 network 10.10.33.0 255.255.255.0
 default-router 10.10.33.1
 dns-server 10.10.200.11
 domain-name intel.lab
 exit
interface loopback 0
 ip address 10.10.5.22 255.255.255.255
interface gi1/1/1
 description to SWL3-HFA-CORE1 Gi1/0/4
 no switchport
 ip address 10.10.4.25 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/1/2
 description to SWL3-HFA-CORE2 Gi1/0/4
 no switchport
 ip address 10.10.4.29 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/1/3
 description to SWL3-HFA-C-DIST1 Gi1/1/2
 no switchport
 ip address 10.10.36.5 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/1/4
 description to SWL3-HFA-C-DIST2 Gi1/1/2
 no switchport
 ip address 10.10.36.13 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
 exit
router ospf 1
 router-id 10.10.5.22
 passive-interface default
 no passive-interface gi1/1/1
 no passive-interface gi1/1/2
 no passive-interface gi1/1/3
 no passive-interface gi1/1/4
 no passive-interface vlan 99
 network 10.10.0.0 0.0.15.255 area 0
 network 10.10.32.0 0.0.15.255 area 2
 area 2 range 10.10.32.0 255.255.240.0
 exit
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
(‎`1024`)
```
ip ssh version 2
ip ssh time-out 60
ip ssh authentication-retries 3
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
aaa new-model
tacacs-server host 10.10.1.11 key Intel#Tac
aaa authentication login default group tacacs+ local
ip tacacs source-interface loopback 0
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

### 4.3 ‏SW-HFA-B-ACC1 — הגדרה מלאה
```
enable
configure terminal
hostname SW-HFA-B-ACC1
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vtp domain HFA-B
vtp version 2
vtp password Intel#Vtp
vtp mode client
spanning-tree mode rapid-pvst
! ===== uplinks =====
interface range gi0/1 - 2
 description TRUNK uplink to B-DIST1 / B-DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 40,50,60,99,998
 switchport nonegotiate
 ip dhcp snooping trust
 no shutdown
! ===== users =====
interface range fa0/1 - 10
 description HR users
 switchport mode access
 switchport access vlan 40
interface range fa0/11 - 20
 description MARKETING users
 switchport mode access
 switchport access vlan 50
interface range fa0/1 - 20
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
 ip dhcp snooping limit rate 10
 no cdp enable
! ===== printer =====
interface fa0/21
 description PRN-HFA-B-01
 switchport mode access
 switchport access vlan 60
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
 no cdp enable
! ===== unused =====
interface range fa0/22 - 24
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 exit
! ===== DHCP snooping =====
ip dhcp snooping
ip dhcp snooping vlan 40,50,60,99
no ip dhcp snooping information option
! ===== management =====
interface vlan 99
 description MANAGEMENT
 ip address 10.10.35.11 255.255.255.0
 no shutdown
 exit
ip default-gateway 10.10.35.1
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
(‎`1024`)
```
ip ssh version 2
ip ssh time-out 60
ip ssh authentication-retries 3
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

### 4.4 ‏SW-HFA-B-ACC2 — הגדרה מלאה
בדיוק כמו 4.3, עם **שני שינויים**:
- ‏`hostname SW-HFA-B-ACC2`
- ‏`ip address 10.10.35.12 255.255.255.0` תחת `interface vlan 99`

(הקלידו שוב את כל הבלוק מ-4.3 עם שתי השורות האלה מוחלפות.)

### 4.5 ‏CORE1 ו-CORE2 — פותחים את הפורטים לכיוון בניין B
**‏SWL3-HFA-CORE1:**
```
enable
configure terminal
interface gi1/0/3
 description to SWL3-HFA-B-DIST1 Gi1/1/1
 no switchport
 ip address 10.10.4.18 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/0/4
 description to SWL3-HFA-B-DIST2 Gi1/1/1
 no switchport
 ip address 10.10.4.26 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
 exit
router ospf 1
 no passive-interface gi1/0/3
 no passive-interface gi1/0/4
 end
copy running-config startup-config
```
**‏SWL3-HFA-CORE2:** אותו דבר, עם ‎`10.10.4.22` על Gi1/0/3 (תיאור `to SWL3-HFA-B-DIST1 Gi1/1/2`)
ו-‎`10.10.4.30` על Gi1/0/4 (תיאור `to SWL3-HFA-B-DIST2 Gi1/1/2`).

### 4.6 מכשירי הקצה של בניין B
- **מחשבים** (HR-01/02, ‏MKT-01/02): ‏Desktop ‏←‏ IP Configuration ‏←‏ **DHCP**.
- **‏PRN-HFA-B-01**: ‏Config ‏←‏ FastEthernet0 ‏←‏ IP ‎`10.10.34.10`, מסיכה ‎`255.255.255.0`;
  ‏Config ‏←‏ Settings ‏←‏ Gateway ‎`10.10.34.1`.

### 4.7 בודקים את בניין B לפני שממשיכים
- ‏CORE1: ‏`show ip route ospf` ‏←‏ `O IA 10.10.32.0/20` דרך B-DIST1 **וגם** B-DIST2 ✅
- מחשב HR מקבל ‎`10.10.32.x`; ‏`ping` למחשב הנדסה בבניין A ✅
- ‏B-DIST1: ‏`show standby brief`, ‏`show etherchannel summary`, ‏`show ip ospf neighbor` ‏(CORE1, ‏CORE2, ‏B-DIST2)

---

## חלק 5 — מגדירים את בניין C (קודם **בלי** ה-virtual link)

### 5.1 ‏SWL3-HFA-C-DIST1 — הגדרה מלאה
```
enable
configure terminal
hostname SWL3-HFA-C-DIST1
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp domain HFA-C
vtp version 2
vtp password Intel#Vtp
vtp mode server
vlan 70
 name RND
vlan 80
 name IT
vlan 90
 name PRINTERS-C
vlan 99
 name MGMT-C
vlan 998
 name NATIVE
vlan 999
 name PARKING
 exit
spanning-tree mode rapid-pvst
spanning-tree vlan 70,90,99 root primary
spanning-tree vlan 80 root secondary
interface range gi1/0/1 - 2
 description TRUNK to access switch
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 70,80,90,99,998
 switchport nonegotiate
 spanning-tree guard root
 no shutdown
interface range gi1/0/23 - 24
 description Po1 member to SWL3-HFA-C-DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 70,80,90,99,998
 switchport nonegotiate
 channel-group 1 mode active
 no shutdown
interface port-channel 1
 description EtherChannel to SWL3-HFA-C-DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 70,80,90,99,998
 switchport nonegotiate
interface range gi1/0/3 - 22
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 exit
ip routing
interface vlan 70
 description GW RND
 ip address 10.10.48.2 255.255.255.0
 standby version 2
 standby 70 ip 10.10.48.1
 standby 70 priority 110
 standby 70 preempt
 no shutdown
interface vlan 80
 description GW IT
 ip address 10.10.49.2 255.255.255.0
 standby version 2
 standby 80 ip 10.10.49.1
 standby 80 priority 90
 standby 80 preempt
 no shutdown
interface vlan 90
 description GW PRINTERS-C
 ip address 10.10.50.2 255.255.255.0
 standby version 2
 standby 90 ip 10.10.50.1
 standby 90 priority 110
 standby 90 preempt
 no shutdown
interface vlan 99
 description GW MGMT-C
 ip address 10.10.51.2 255.255.255.0
 standby version 2
 standby 99 ip 10.10.51.1
 standby 99 priority 110
 standby 99 preempt
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
 exit
ip dhcp excluded-address 10.10.48.1 10.10.48.10
ip dhcp excluded-address 10.10.48.131 10.10.48.254
ip dhcp excluded-address 10.10.49.1 10.10.49.10
ip dhcp excluded-address 10.10.49.131 10.10.49.254
ip dhcp pool HFA-RND
 network 10.10.48.0 255.255.255.0
 default-router 10.10.48.1
 dns-server 10.10.200.11
 domain-name intel.lab
ip dhcp pool HFA-IT
 network 10.10.49.0 255.255.255.0
 default-router 10.10.49.1
 dns-server 10.10.200.11
 domain-name intel.lab
 exit
! ===== loopback inside AREA 3's block =====
interface loopback 0
 ip address 10.10.63.1 255.255.255.255
! ===== uplinks to building B (area 2) =====
interface gi1/1/1
 description to SWL3-HFA-B-DIST1 Gi1/1/3
 no switchport
 ip address 10.10.36.2 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/1/2
 description to SWL3-HFA-B-DIST2 Gi1/1/3
 no switchport
 ip address 10.10.36.6 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
 exit
! ===== OSPF: ABR between area 2 and area 3 (no area 0 here!) =====
router ospf 1
 router-id 10.10.63.1
 passive-interface default
 no passive-interface gi1/1/1
 no passive-interface gi1/1/2
 no passive-interface vlan 99
 network 10.10.36.0 0.0.0.15 area 2
 network 10.10.48.0 0.0.15.255 area 3
 area 3 range 10.10.48.0 255.255.240.0
 exit
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
(‎`1024`)
```
ip ssh version 2
ip ssh time-out 60
ip ssh authentication-retries 3
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
aaa new-model
tacacs-server host 10.10.1.11 key Intel#Tac
aaa authentication login default group tacacs+ local
ip tacacs source-interface loopback 0
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
ההערות אומרות: ה-loopback נמצא בתוך הבלוק של **area 3**; קישורים כלפי מעלה לבניין B ‏(area 2);
‏OSPF — ‏ABR בין area 2 ל-area 3 (**אין כאן area 0!**).

### 5.2 ‏SWL3-HFA-C-DIST2 — הגדרה מלאה
```
enable
configure terminal
hostname SWL3-HFA-C-DIST2
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vtp domain HFA-C
vtp version 2
vtp password Intel#Vtp
vtp mode client
spanning-tree mode rapid-pvst
spanning-tree vlan 80 root primary
spanning-tree vlan 70,90,99 root secondary
interface range gi1/0/1 - 2
 description TRUNK to access switch
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 70,80,90,99,998
 switchport nonegotiate
 spanning-tree guard root
 no shutdown
interface range gi1/0/23 - 24
 description Po1 member to SWL3-HFA-C-DIST1
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 70,80,90,99,998
 switchport nonegotiate
 channel-group 1 mode active
 no shutdown
interface port-channel 1
 description EtherChannel to SWL3-HFA-C-DIST1
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 70,80,90,99,998
 switchport nonegotiate
interface range gi1/0/3 - 22
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 exit
ip routing
interface vlan 70
 description GW RND
 ip address 10.10.48.3 255.255.255.0
 standby version 2
 standby 70 ip 10.10.48.1
 standby 70 priority 90
 standby 70 preempt
 no shutdown
interface vlan 80
 description GW IT
 ip address 10.10.49.3 255.255.255.0
 standby version 2
 standby 80 ip 10.10.49.1
 standby 80 priority 110
 standby 80 preempt
 no shutdown
interface vlan 90
 description GW PRINTERS-C
 ip address 10.10.50.3 255.255.255.0
 standby version 2
 standby 90 ip 10.10.50.1
 standby 90 priority 90
 standby 90 preempt
 no shutdown
interface vlan 99
 description GW MGMT-C
 ip address 10.10.51.3 255.255.255.0
 standby version 2
 standby 99 ip 10.10.51.1
 standby 99 priority 90
 standby 99 preempt
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
 exit
ip dhcp excluded-address 10.10.48.1 10.10.48.130
ip dhcp excluded-address 10.10.49.1 10.10.49.130
ip dhcp pool HFA-RND
 network 10.10.48.0 255.255.255.0
 default-router 10.10.48.1
 dns-server 10.10.200.11
 domain-name intel.lab
ip dhcp pool HFA-IT
 network 10.10.49.0 255.255.255.0
 default-router 10.10.49.1
 dns-server 10.10.200.11
 domain-name intel.lab
 exit
interface loopback 0
 ip address 10.10.63.2 255.255.255.255
interface gi1/1/1
 description to SWL3-HFA-B-DIST1 Gi1/1/4
 no switchport
 ip address 10.10.36.10 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
interface gi1/1/2
 description to SWL3-HFA-B-DIST2 Gi1/1/4
 no switchport
 ip address 10.10.36.14 255.255.255.252
 ip ospf message-digest-key 1 md5 Intel#Ospf
 ip ospf authentication message-digest
 no shutdown
 exit
router ospf 1
 router-id 10.10.63.2
 passive-interface default
 no passive-interface gi1/1/1
 no passive-interface gi1/1/2
 no passive-interface vlan 99
 network 10.10.36.0 0.0.0.15 area 2
 network 10.10.48.0 0.0.15.255 area 3
 area 3 range 10.10.48.0 255.255.240.0
 exit
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
(‎`1024`)
```
ip ssh version 2
ip ssh time-out 60
ip ssh authentication-retries 3
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
aaa new-model
tacacs-server host 10.10.1.11 key Intel#Tac
aaa authentication login default group tacacs+ local
ip tacacs source-interface loopback 0
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

### 5.3 ‏SW-HFA-C-ACC1 — הגדרה מלאה
```
enable
configure terminal
hostname SW-HFA-C-ACC1
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vtp domain HFA-C
vtp version 2
vtp password Intel#Vtp
vtp mode client
spanning-tree mode rapid-pvst
interface range gi0/1 - 2
 description TRUNK uplink to C-DIST1 / C-DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 70,80,90,99,998
 switchport nonegotiate
 ip dhcp snooping trust
 no shutdown
interface range fa0/1 - 10
 description RND users
 switchport mode access
 switchport access vlan 70
interface range fa0/11 - 20
 description IT users
 switchport mode access
 switchport access vlan 80
interface range fa0/1 - 20
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
 ip dhcp snooping limit rate 10
 no cdp enable
interface fa0/21
 description PRN-HFA-C-01
 switchport mode access
 switchport access vlan 90
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
 no cdp enable
interface range fa0/22 - 24
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 exit
ip dhcp snooping
ip dhcp snooping vlan 70,80,90,99
no ip dhcp snooping information option
interface vlan 99
 description MANAGEMENT
 ip address 10.10.51.11 255.255.255.0
 no shutdown
 exit
ip default-gateway 10.10.51.1
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
(‎`1024`)
```
ip ssh version 2
ip ssh time-out 60
ip ssh authentication-retries 3
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

### 5.4 ‏SW-HFA-C-ACC2 — הגדרה מלאה
כמו 5.3 עם: `hostname SW-HFA-C-ACC2` ו-`ip address 10.10.51.12 255.255.255.0`.

### 5.5 מכשירי הקצה של בניין C
- מחשבים (RND-01/02, ‏IT-01/02) ‏←‏ **DHCP**.
- ‏PRN-HFA-C-01 ‏←‏ IP ‎`10.10.50.10` / ‎`255.255.255.0`, שער ‎`10.10.50.1`.

### 5.6 רואים את הבעיה 🔍
לחצו כמה פעמים על **Fast Forward Time**, ואז:
- **‏B-DIST1** ‏`show ip ospf neighbor` ‏←‏ ‏C-DIST1 ו-C-DIST2 הם שכנים במצב FULL ‏(area 2 עובד).
- **‏CORE1** ‏`show ip route | include 10.10.48` ‏←‏ **כלום**. ה-core לא רואה את area 3.
- **‏PC-HFA-RND-01** ‏←‏ `ping 10.10.1.10` (שרת ה-Syslog) ‏←‏ ❌ Request timed out.
- **‏C-DIST1** ‏`show ip route` ‏←‏ אין נתיבי `O IA` מ-areas 0 ו-1 — האי שלם.

זה הכלל מסעיף 1.2 בפעולה. עכשיו מתקנים.

---

## חלק 6 — ה-virtual links

**‏SWL3-HFA-B-DIST1** ו-**SWL3-HFA-B-DIST2** (‏ABRs בין 0 ל-2) — הקלידו בשניהם:
```
enable
configure terminal
router ospf 1
 area 2 virtual-link 10.10.63.1
 area 2 virtual-link 10.10.63.2
 end
copy running-config startup-config
```
**‏SWL3-HFA-C-DIST1** ו-**SWL3-HFA-C-DIST2** (‏ABRs בין 2 ל-3) — הקלידו בשניהם:
```
enable
configure terminal
router ospf 1
 area 2 virtual-link 10.10.5.21
 area 2 virtual-link 10.10.5.22
 end
copy running-config startup-config
```
לחצו על **Fast Forward Time**. תראו ‎`%OSPF-5-ADJCHG: Process 1, Nbr 10.10.63.1 on OSPF_VL0 from LOADING to FULL`.

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`area 2 virtual-link 10.10.63.1` | "בנה חתיכה של area 0 **דרך area 2**, אל הנתב שה-router-ID שלו הוא 10.10.63.1" |

</div>

---

## חלק 7 — מעדכנים את המכשירים הישנים

### 7.1 ה-ACL הסופית לניהול על 7 המכשירים הישנים
על **ACC1, ‏ACC2, ‏DIST1, ‏DIST2 (בניין A), ‏CORE1, ‏CORE2, ‏SW-HFA-SRV**:
```
enable
configure terminal
ip access-list standard MGMT-ONLY
 no deny any log
 permit 10.10.35.0 0.0.0.255
 permit 10.10.51.0 0.0.0.255
 permit 10.10.49.0 0.0.0.255
 deny any log
 end
copy running-config startup-config
```

<div dir="rtl">

> למה מוחקים קודם את ה-`deny`? שורות חדשות נוספות ב**תחתית** של ACL עם שם. אם ה-`deny any` היה
> נשאר מעליהן, אף חבילה לא הייתה מגיעה ל-permits החדשים.

</div>

בדיקה: `show access-lists MGMT-ONLY` ‏←‏ 4 שורות permit, ואחריהן ה-deny.

### 7.2 רושמים את 8 המכשירים החדשים בשרת SRV-HFA-AAA
‏SRV-HFA-AAA ‏←‏ **Services → AAA → Network Configuration** ‏←‏ מוסיפים (‏secret `Intel#Tac`, סוג **Tacacs**):

<div dir="rtl">

| ‎‏Client Name | ‎‏Client IP |
|---|---|
| ‎SWL3-HFA-B-DIST1 | ‎10.10.5.21 |
| ‎SWL3-HFA-B-DIST2 | ‎10.10.5.22 |
| ‎SW-HFA-B-ACC1 | ‎10.10.35.11 |
| ‎SW-HFA-B-ACC2 | ‎10.10.35.12 |
| ‎SWL3-HFA-C-DIST1 | ‎10.10.63.1 |
| ‎SWL3-HFA-C-DIST2 | ‎10.10.63.2 |
| ‎SW-HFA-C-ACC1 | ‎10.10.51.11 |
| ‎SW-HFA-C-ACC2 | ‎10.10.51.12 |

</div>

---

## חלק 8 — בודקים את העבודה

### 8.1 ה-virtual links
על **B-DIST1**: ‏`show ip ospf virtual-links`
```
Virtual Link OSPF_VL0 to router 10.10.63.1 is up
  Transit area 2, via interface GigabitEthernet1/1/3, Cost of using 1
  ...
Virtual Link OSPF_VL1 to router 10.10.63.2 is up
```

### 8.2 ה-core רואה עכשיו כל בניין כנתיב אחד
על **CORE1**: ‏`show ip route ospf`
```
O IA  10.10.16.0/20 ...   <- building A (area 1)
O IA  10.10.32.0/20 ...   <- building B (area 2)
O IA  10.10.48.0/20 ...   <- building C (area 3) — arrived through the virtual link!
```
(בניין A ‏(area 1), בניין B ‏(area 2), ובניין C ‏(area 3) — שהגיע דרך ה-virtual link!)

### 8.3 בדיקות ping ו-SSH

<div dir="rtl">

| מאיפה | מקלידים | מה אמור לקרות |
|---|---|---|
| ‎PC-HFA-RND-01 | ‎`ping 10.10.1.10` | ✅ (נכשל לפני ה-virtual link) |
| ‎PC-HFA-IT-01 | `ping` למחשב הנדסה בבניין A | ‎✅ |
| ‎PC-HFA-HR-01 | `ping` למחשב מו"פ | ‎✅ |
| ‎PC-HFA-IT-01 | `ssh -l admin 10.10.19.11` ‏(ACC1 בבניין A) | ✅ ל-IT מותר לנהל את הציוד |
| ‎PC-HFA-RND-01 | ‎`ssh -l admin 10.10.51.11` | ❌ נדחה (לא ברשימת האורחים) |

</div>

---

## חלק 9 — שומרים
‏`copy running-config startup-config` בכל המתגים ששיניתם ‏←‏ **File → Save**.

## נקודת ביקורת
- [ ] המחשבים בבניינים B ו-C מקבלים כתובות DHCP ממתגי ה-DIST של הבניין שלהם
- [ ] כל 4 ה-virtual links במצב up
- [ ] ל-CORE1 יש בדיוק שלושה נתיבי `O IA` של ‎/20
- [ ] כל מחשב בכל בניין מגיע לשרתים
- [ ] ‏IT יכולים להתחבר ב-SSH לכל מתג; מו"פ לא

## אם משהו לא עובד

<div dir="rtl">

| בעיה | פתרון |
|---|---|
| ה-virtual link נשאר down | השתמשתם ב-**IP של ממשק** במקום ב-**router-ID**; או שאזור המעבר הוא לא ‎`2`; או של-C-DIST עדיין אין שכן במצב FULL ב-area 2 |
| ל-C-DIST אין שכנים ב-area 2 | שגיאת כתיב במפתח ה-MD5 על קישור ‎10.10.36.x, או שחסר `network 10.10.36.0 0.0.0.15 area 2` |
| ה-core רואה הרבה נתיבים קטנים מ-area 2 | חסר `area 2 range 10.10.32.0 255.255.240.0` ב-B-DIST1/2 |
| המחשבים בבניין C לא מקבלים כתובת | שגיאת כתיב בדומיין ה-VTP ‏`HFA-C` במתג access, או snooping בלי `trust` על הקישורים כלפי מעלה |
| אזהרות ‎`% Access VLAN does not exist` | נורמלי בזמן ש-VTP לומד — ראו שלב 03 |

</div>

## אתגר
מחקו את הסיכום של area 2 ב-B-DIST1 וב-B-DIST2 (‏`router ospf 1` ‏←‏ `no area 2 range 10.10.32.0 255.255.240.0`).
הסתכלו על טבלת הניתוב של CORE1. כמה שורות נוספו, ולמה קישורי ה-‎`10.10.36.x` ביניהן? החזירו את
הסיכום.

<details dir="rtl"><summary>תשובה</summary>

בלי הסיכום, כל רשת של area 2 מפורסמת בנפרד כ-`O IA`: ‏4 ה-VLANים (40, ‏50, ‏60, ‏99) **וגם**
ארבעת קישורי ה-‎/30 לבניין C — בערך 8 שורות במקום אחת. גם קישורי ה-‎/30 הם רשתות של area 2. עם
הסיכום הם מוסתרים בתוך 10.10.32.0/20 — ובגלל זה מספרנו אותם 10.10.36.x ולא 10.10.4.x.
</details>

---

## 🛠 הפרויקט שלכם

עשיתם את השלב הזה על הדוגמה של אינטל. עכשיו עשו אותו שוב בפרויקט **שלכם**, עם הערכים
מהתוכנית **שלכם** (`my-project/plan.md`). הפקודות זהות — רק הערכים משתנים.

השלב הזה הוא כבר "עשו בעצמכם" על הדוגמה. בפרויקט שלכם:

<div dir="rtl">

| בדוגמה | בפרויקט שלכם — לוקחים מ |
|---|---|
| בניינים B ו-C וה-VLANים שלהם 40–90 | תוכנית, חלק ד (הבניינים / המחלקות האחרים של המטה שלכם) |
| דומייני VTP ‏`HFA-B`, ‏`HFA-C` | דומיין אחד לכל בניין, בשמות שלכם |
| ‏Area 3 לא נוגע ב-area 0 ‏←‏ ‏virtual link דרך area 2 | משרד החינוך דורש OSPF virtual link (דרישה 8): בתכנון שלכם חייב להיות area אחד שמגיע ל-area 0 רק דרך area אחר |
| סיכום לכל area | ה-‎/20 שלכם לכל area |

</div>

**בדיקה:** ‏`show ip ospf virtual-links` מראה שהקישור **up**; כל מחלקה במטה מצליחה ping לכל
מחלקה אחרת.

💾 שמרו בשם `my-project/step09.pkt`.

---

## 🎓 מסבירים לבוחן

בבחינה, הבוחן מצביע על הפרויקט **שלכם** ומבקש **להסביר** ו**להראות**. תרגלו כל שאלה
**בקול**, ואז הראו את התשובה בפרויקט שלכם — לא בדוגמה. כסו את התשובה, ענו בעצמכם, ורק אז
פתחו והשוו.

★1–★3 = שאלה ממאגר השאלות של משרד החינוך (רמת קושי 1–3).
◆ = לא במאגר, אבל בוחנים שואלים אותה לעיתים קרובות.

**1. ★3 היכן הגדרת virtual link? מדוע?**

<details dir="rtl"><summary>תשובה</summary>

כל OSPF area חייב לגעת ב-area 0. הבניין שה-area שלו לא מחובר ישירות ל-area 0 מצורף לעמוד השדרה
**דרך** area מעבר (transit): ‏`area <transit> virtual-link <router-ID של ה-ABR השני>`‎ בשני ה-ABRs.
משרד החינוך דורש את המבנה הזה (דרישות 8, ‏22.16).

**איפה מראים:** `show ip ospf virtual-links` ‏←‏ "is up"
</details>

**2. ◆ למה area המעבר של virtual link לא יכול להיות stub?**

<details dir="rtl"><summary>תשובה</summary>

‏Virtual link צריך מידע ניתוב מלא ב-area המעבר; ‏stub areas חוסמים אותו, ולכן virtual link יכול
לעבור רק דרך area רגיל.

**איפה מראים:** —
</details>

**3. ★3 מהו STUB area? אילו LSAs הוא חוסם ואילו הוא מקבל?**

<details dir="rtl"><summary>תשובה</summary>

‏Area שלא מקבל נתיבים חיצוניים: ‏LSAs מסוג 4 ו-5 חסומים; הוא מקבל סוגים 1, ‏2, ‏3 ונתיב ברירת
מחדל מה-ABR. מגדירים עם `area X stub` ב**כל** הנתבים של ה-area.

**איפה מראים:** —
</details>

**4. ★3 מהו TOTALLY STUBBY area, ואיך הופכים stub area ל-totally stubby?**

<details dir="rtl"><summary>תשובה</summary>

הוא חוסם גם LSAs מסוג 3 (בין areas); ה-area מקבל רק סוגים 1, ‏2 ונתיב ברירת מחדל. רק ב-ABR:
‏`area X stub no-summary`.

**איפה מראים:** —
</details>

**5. ★3 מהו NSSA, ואיך הופכים אותו ל-totally NSSA?**

<details dir="rtl"><summary>תשובה</summary>

‏Not-So-Stubby Area: כמו stub, אבל נתב בתוכו רשאי להכניס נתיבים חיצוניים. הם עוברים כ-LSAs מסוג 7,
וה-ABR ממיר אותם לסוג 5. ‏Totally NSSA: ‏`area X nssa no-summary` ב-ABR.

**איפה מראים:** —
</details>

**6. ◆ איך מסכמים area ב-OSPF?**

<details dir="rtl"><summary>תשובה</summary>

ב-ABR: ‏`area <N> range <network> <mask>`‎ — נתיב אחד לכל ה-‎/20 של הבניין נשלח לעמוד השדרה.

**איפה מראים:** `show ip route` במתג core ‏←‏ ‏`O IA` אחד לכל בניין
</details>

---

## 🔁 עושים שוב — בלי המדריך

הבוחן יכול לבקש מכם להגדיר משהו שוב, מולו. תצליחו רק אם עשיתם את זה **בלי המדריך** לפני כן.
עשו את התרגיל הזה בפרויקט שלכם:

בעותק של קובץ שלב 09 שלכם, מחקו את ה-virtual link בשני ה-ABRs. הראו שה-area המרוחק כבר לא
נגיש (`show ip route`), ואז הוסיפו שוב את ה-virtual link בלי העמוד הזה. יעד: **‏5 דקות**. הסבירו
לבוחן למה ה-area צריך אותו.

---

## 👩‍🏫 הערות למורה
- **שיעור 1:** משחק חזרה — התלמידים אומרים מאיזה שלב מגיע כל בלוק בהגדרות של B-DIST1 (הקשחה = 02,
  ‏VTP = 03, ‏STP/EtherChannel = 04, ‏SVIs/HSRP/DHCP = 05, …). אחר כך בונים ומחווטים את שני הבניינים.
- **שיעור 2:** מגדירים את בניין B; בודקים את 4.7.
- **שיעור 3:** מגדירים את בניין C; **עוצרים ב-5.6** ונותנים לכיתה לגלות את הבעיה. שואלים: "שכני
  ה-OSPF במצב FULL — אז למה ה-core לא רואה את area 3?" מובילים אותם לכלל "כל area חייב לגעת
  ב-area 0".
- **שיעור 4:** ‏virtual links ‏←‏ בדיקות ‏←‏ ה-ACL הסופית ‏←‏ אתגר.
- **שאלות נפוצות של תלמידים**
  - *"למה לא פשוט לחבר את בניין C ל-core?"* — בקמפוס אמיתי זה התכנון הטוב יותר! בונים כך כי משרד
    החינוך דורש virtual link ‏(22.16). כתבו את זה בספר הפרויקט.
  - *"למה router-ID ולא כתובת IP?"* — ה-virtual link הוא בין שני *נתבים*, לא בין שני ממשקים.
    ‏OSPF מזהה נתבים לפי router-ID.
- **טעויות אופייניות:** ספקי כוח חסרים (4 מתגי 3650 חדשים!); הצד הלא נכון של ה-‎/30 בקישורים בין B
  ל-C; שכחה לעדכן את ה-ACL במכשירים הישנים.
