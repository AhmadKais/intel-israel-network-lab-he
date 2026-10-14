# שלב 14 — קריית גת: הסניף של IPv6

<div dir="rtl">

> ⏱ ‏4 שיעורים · 🎯 דרישות משרד החינוך 7, ‏10 (overload), ‏17, ‏20.x, ‏22.11 (בחירת התלמיד)\
> 📁 מתחילים מ: `my-work/step13.pkt`\
> 💾 שומרים בשם: `my-work/step14.pkt`

</div>

<div dir="rtl">

> ✅ **לפני שמתחילים:** כל הסעיפים בנקודת הביקורת של שלב 13 מסומנים, ועשיתם את
> תרגיל ה-🔁 שלו בפרויקט שלכם. אל תדלגו על שלבים — כל שלב בנוי על הקובץ של השלב הקודם.

</div>

## מה יהיה לכם בסוף השלב
הסניף השלישי מריץ **IPv6** לכל המשתמשים, השרתים והניהול: כתובות אוטומטיות (SLAAC + ‏stateless
DHCPv6), ניתוב **OSPFv3**, ‏**HSRP ל-IPv6**. ‏VLAN ‏IPv4 קטן אחד "מדור קודם" (legacy) מגיע לאינטרנט דרך
**PAT ‏(overload)** — סוג ה-NAT השלישי.

```
                          R-ISPC-PE (ISP-C, dual-stack)
                                │ 2001:DB8:C:1::/64 + 200.3.1.0/30
                           R-KG-EDGE    (OSPFv3, static defaults, PAT for VLAN 199)
                    Gi0/0 ╱         ╲ Gi0/2
          SWL3-KG-DIST1 ════ trunk ════ SWL3-KG-DIST2      OSPFv3 area 0, HSRPv6
           ╱    │    │   ╲            ╱    │    │   ╲
        ACC1  ACC2  ACC3  SW-KG-SRV   (each with a cable to BOTH DIST switches)
```
(‏R-KG-EDGE מחובר ל-ISP-C ‏(dual-stack) ומריץ OSPFv3, נתיבי ברירת מחדל סטטיים ו-PAT ל-VLAN 199. מתחתיו
‏DIST1 ו-DIST2, מחוברים ב-trunk, עם OSPFv3 ‏area 0 ו-HSRPv6. לכל מתג access ולמתג השרתים יש כבל לשני
מתגי ה-DIST.)

---

## חלק 1 — קודם מבינים (בשפה פשוטה)

### 1.1 למה IPv6?
ל-IPv4 יש בערך 4 מיליארד כתובות — והעולם גמר אותן. בגלל זה צריך כתובות פרטיות ו-NAT. ל-**IPv6** יש
340 אנדסיליון כתובות (מספר בן 39 ספרות): לכל מכשיר יכולה להיות כתובת **ציבורית וייחודית**. לא צריך
NAT. משרד החינוך דורש שסניף אחד יהיה כולו IPv6 (דרישה 7).

### 1.2 איך קוראים כתובת IPv6
‏128 ביט, שנכתבים כ-**8 קבוצות** של 4 ספרות הקסדצימליות (0–9, ‏A–F), מופרדות ב-‎`:`‎.
```
2001:0DB8:0030:0031:0000:0000:0000:0002
```
שני כללי קיצור:
1. משמיטים **אפסים מובילים** בכל קבוצה: ‎`0DB8 → DB8`, ‏‎`0030 → 30`, ‏‎`0002 → 2`.
2. מחליפים רצף **אחד** של קבוצות שכולן אפסים ב-‎`::`‎.
```
2001:DB8:30:31::2          (the same address)
```
(אותה כתובת.)
- ‏‎`/64` — כמו ‎`/24` ב-IPv4, אבל זה התקן ל**כל** רשת מקומית: ‏64 הביטים הראשונים הם הרשת, ו-64
  האחרונים הם המכשיר.
- ‏‎`2001:DB8::/32` הוא הטווח ששמור לתיעוד ולמעבדות (כמו 192.0.2.x).

### 1.3 התוכנית שלנו: מספר ה-VLAN נמצא בכתובת
לקריית גת שייך ‎`2001:DB8:30::/48`. כל VLAN מקבל ‎/64 שה**קבוצה הרביעית** שלו = **מספר ה-VLAN**:
‏VLAN 31 ‏←‏ ‎`2001:DB8:30:31::/64`, ‏VLAN 99 ‏←‏ ‎`2001:DB8:30:99::/64`. קל לקרוא.

<div dir="rtl">

| ‎‏VLAN | שם | ‎‏Prefix | ‎‏DIST1 | ‎‏DIST2 | שער |
|---|---|---|---|---|---|
| ‎31 | ‎FAB-OPS | ‎2001:DB8:30:31::/64 | ‎::2 | ‎::3 | ‎FE80::1 |
| ‎32 | ‎QUALITY | ‎2001:DB8:30:32::/64 | ‎::2 | ‎::3 | ‎FE80::1 |
| ‎33 | ‎MAINTENANCE | ‎2001:DB8:30:33::/64 | ‎::2 | ‎::3 | ‎FE80::1 |
| ‎34 | ‎SAFETY | ‎2001:DB8:30:34::/64 | ‎::2 | ‎::3 | ‎FE80::1 |
| ‎35 | ‎PLANNING | ‎2001:DB8:30:35::/64 | ‎::2 | ‎::3 | ‎FE80::1 |
| ‎36 | ‎TRAINING | ‎2001:DB8:30:36::/64 | ‎::2 | ‎::3 | ‎FE80::1 |
| ‎99 | ‎MGMT | ‎2001:DB8:30:99::/64 | ‎::2 | ‎::3 | ‎FE80::1 |
| ‎100 | ‎SERVERS | ‎2001:DB8:30:100::/64 | ‎::2 | ‎::3 | ‎FE80::1 |
| ‎199 | ‎LEGACY-IPV4 | ‎**10.30.199.0/24** | ‎.1 | ‎— | ‎10.30.199.1 |

</div>

### 1.4 כתובות link-local — ‏`FE80::`‎
לכל ממשק IPv6 יש אוטומטית כתובת **link-local** שמתחילה ב-`FE80`. היא עובדת רק על הקישור שלה (אף פעם
לא מנותבת). ‏IPv6 משתמש בהן לגילוי שכנים וככתובת של **שער ברירת המחדל**. אנחנו קובעים את השער
הווירטואלי לכתובת הקלה `FE80::1` בכל VLAN.

### 1.5 איך מחשב מקבל כתובת IPv6 בלי להקליד — SLAAC
1. הנתב שולח **Router Advertisements ‏(RA)**: "הרשת כאן היא 2001:DB8:30:31::/64, ואני השער שלך".
2. המחשב בונה לעצמו כתובת: ה-prefix + חלק מכשיר שהוא מייצר בעצמו.
זה **SLAAC** ‏(Stateless Address Auto-Configuration). לא צריך שרת DHCP בשביל הכתובת.

אבל SLAAC לא אומר למחשב מהו שרת ה-**DNS**. לכן מוסיפים **stateless DHCPv6**: ה-RA נושא דגל ("O-flag" =
‏*other information*) שאומר למחשבים: "בקשו מ-DHCPv6 את התוספות (DNS, דומיין)".
‏←‏ הבחירה של קריית גת ל-DHCP (דרישה 22.11, "סניף שלישי: בחירת התלמיד") = **SLAAC + ‏stateless DHCPv6
במתגי ה-distribution**.

### 1.6 ‏OSPFv3 ו-HSRP ל-IPv6
- **‏OSPFv3** = ‏OSPF ל-IPv6. אותם רעיונות (שכנים, מפה, areas); הגדרה אחרת: מפעילים אותו **על כל ממשק**
  (`ipv6 ospf 1 area 0`), לא עם שורות `network`. הוא צריך router-ID שנכתב כמו כתובת IPv4 ‏(3.3.3.1) —
  אין כתובת IPv4 שאפשר "לשאול" ממנה.
- **‏HSRP ל-IPv6** — רק גרסה 2; השער המשותף הוא כתובת **link-local** ‏(`FE80::1`).

### 1.7 שונה בכוונה

<div dir="rtl">

| | חיפה | ירושלים | **קריית גת** |
|---|---|---|---|
| ‎‏VTP | ‎‏server/client | ‎‏server/client | **‏transparent** (כל מתג מחזיק את ה-VLANים שלו) |
| ‎‏EtherChannel | ‎‏LACP | ‎‏PAgP | **אין** (trunk יחיד בין מתגי ה-DIST) |
| ‎‏NAT | ‎‏static ‏(+PAT) | ‎‏dynamic | ‎**‏PAT ‏(overload)** |

</div>

### 1.8 למה עדיין יש קצת IPv4
‏NAT קיים רק ב-IPv4. משרד החינוך מבקש סניף IPv6 אחד **וגם** NAT בכל סניף. התשובה שלנו: **‏VLAN 199**
אחד "מדור קודם" למכשירים ישנים שמדברים רק IPv4 (קוראי כרטיסים, מצלמות). רק הוא משתמש ב-PAT כדי להגיע
לאינטרנט. כל השאר IPv6. **אשרו את הפרשנות הזו עם המנחה שלכם.**

---

## חלק 2 — הכנה
‏**File → Open** ‏←‏ `my-work/step13.pkt` ‏←‏ **File → Save As** ‏←‏ `my-work/step14.pkt`.
ציירו מלבן עם התווית `KIRYAT GAT BRANCH (IPv6)`‎.

---

## חלק 3 — בונים (לחיצה אחרי לחיצה)

### 3.1 מכשירים

<div dir="rtl">

| דגם | ‎‏Display Name |
|---|---|
| ‎2911 | ‎`R-KG-EDGE` |
| ‎‏3650-24PS (+ **AC-POWER-SUPPLY**!) | ‎`SWL3-KG-DIST1`, `SWL3-KG-DIST2` |
| ‎2960 | ‎`SW-KG-ACC1`, `SW-KG-ACC2`, `SW-KG-ACC3`, `SW-KG-SRV` |
| ‎‏Server ×4 | ‎`SRV-KG-DNS`, `SRV-KG-MAIL`, `SRV-KG-SYSLOG`, `SRV-KG-AAA` |
| ‎‏PC ×12 | ‎`PC-KG-FAB-01/02`, `PC-KG-QUA-01/02`, `PC-KG-MNT-01/02`, `PC-KG-SAF-01/02`, `PC-KG-PLN-01/02`, `PC-KG-TRN-01/02` |
| ‎‏PC ×3 | ‎`PC-KG-ADMIN-01`, `PC-KG-LEGACY-01`, `PC-KG-LEGACY-02` |
| ‎‏Printer ×2 | ‎`PRN-KG-ACC2-01`, `PRN-KG-ACC3-01` |
| ‏Server ×1 (ברשת הביתית של ISP-C) | ‎`SRV-ISPC-WEB6` |

</div>

### 3.2 כבלים

<div dir="rtl">

| לוחצים קודם על | פורט | לוחצים אחר כך על | פורט | כבל |
|---|---|---|---|---|
| ‎SWL3-KG-DIST1 | ‎Gi1/0/1 | ‎SW-KG-ACC1 | ‎Gi0/1 | ‎Cross-Over |
| ‎SWL3-KG-DIST2 | ‎Gi1/0/1 | ‎SW-KG-ACC1 | ‎Gi0/2 | ‎Cross-Over |
| ‎SWL3-KG-DIST1 | ‎Gi1/0/2 | ‎SW-KG-ACC2 | ‎Gi0/1 | ‎Cross-Over |
| ‎SWL3-KG-DIST2 | ‎Gi1/0/2 | ‎SW-KG-ACC2 | ‎Gi0/2 | ‎Cross-Over |
| ‎SWL3-KG-DIST1 | ‎Gi1/0/3 | ‎SW-KG-ACC3 | ‎Gi0/1 | ‎Cross-Over |
| ‎SWL3-KG-DIST2 | ‎Gi1/0/3 | ‎SW-KG-ACC3 | ‎Gi0/2 | ‎Cross-Over |
| ‎SWL3-KG-DIST1 | ‎Gi1/0/4 | ‎SW-KG-SRV | ‎Gi0/1 | ‎Cross-Over |
| ‎SWL3-KG-DIST2 | ‎Gi1/0/4 | ‎SW-KG-SRV | ‎Gi0/2 | ‎Cross-Over |
| ‎SWL3-KG-DIST1 | ‎Gi1/0/24 | ‎SWL3-KG-DIST2 | ‎Gi1/0/24 | ‎Cross-Over |
| ‎SWL3-KG-DIST1 | ‎Gi1/1/1 | ‎R-KG-EDGE | ‎Gi0/0 | ‎Straight-Through |
| ‎SWL3-KG-DIST2 | ‎Gi1/1/1 | ‎R-KG-EDGE | ‎Gi0/2 | ‎Straight-Through |
| ‎R-KG-EDGE | ‎Gi0/1 | ‎R-ISPC-PE | ‎Gi0/1 | ‎Cross-Over |
| ‎SRV-ISPC-WEB6 | ‎Fa0 | ‎SW-ISPC-HOME | ‎Fa0/2 | ‎Straight-Through |

</div>

מכשירי קצה (Straight-Through):

<div dir="rtl">

| מכשיר | מתג | פורט |
|---|---|---|
| ‎PC-KG-FAB-01 / 02 | ‎SW-KG-ACC1 | ‎Fa0/1 / Fa0/2 |
| ‎PC-KG-QUA-01 / 02 | ‎SW-KG-ACC1 | ‎Fa0/11 / Fa0/12 |
| ‎PC-KG-LEGACY-01 / 02 | ‎SW-KG-ACC1 | ‎Fa0/21 / Fa0/22 |
| ‎PC-KG-ADMIN-01 | ‎SW-KG-ACC1 | ‎Fa0/23 |
| ‎PC-KG-MNT-01 / 02 | ‎SW-KG-ACC2 | ‎Fa0/1 / Fa0/2 |
| ‎PC-KG-SAF-01 / 02 | ‎SW-KG-ACC2 | ‎Fa0/11 / Fa0/12 |
| ‎PRN-KG-ACC2-01 | ‎SW-KG-ACC2 | ‎Fa0/21 |
| ‎PC-KG-PLN-01 / 02 | ‎SW-KG-ACC3 | ‎Fa0/1 / Fa0/2 |
| ‎PC-KG-TRN-01 / 02 | ‎SW-KG-ACC3 | ‎Fa0/11 / Fa0/12 |
| ‎PRN-KG-ACC3-01 | ‎SW-KG-ACC3 | ‎Fa0/21 |
| ‎SRV-KG-DNS / MAIL / SYSLOG / AAA | ‎SW-KG-SRV | ‎Fa0/1 / 2 / 3 / 4 |

</div>

### 3.3 כתובות הקישורים

<div dir="rtl">

| קישור | ‎‏IPv6 | ‎‏IPv4 |
|---|---|---|
| ‎R-KG-EDGE Gi0/0 ↔ DIST1 Gi1/1/1 | ‎2001:DB8:30:FF01::1 / ::2 (/64) | ‎10.30.4.1 / 10.30.4.2 (/30) |
| ‎R-KG-EDGE Gi0/2 ↔ DIST2 Gi1/1/1 | ‎2001:DB8:30:FF02::1 / ::2 (/64) | ‎— |
| ‎R-KG-EDGE Gi0/1 ↔ R-ISPC-PE Gi0/1 | ‎2001:DB8:C:1::2 / ::1 (/64) | ‎200.3.1.2 / 200.3.1.1 (/30) |

</div>

<div dir="rtl">

| מכשיר | ‏router-ID של OSPFv3 | כתובת ניהול IPv6 |
|---|---|---|
| ‎R-KG-EDGE | ‎3.3.3.1 | ‎2001:DB8:30:FF01::1 |
| ‎SWL3-KG-DIST1 / DIST2 | ‎3.3.3.2 / 3.3.3.3 | ‎2001:DB8:30:99::2 / ::3 |
| ‎SW-KG-ACC1 / ACC2 / ACC3 / SRV | ‎— | ‎2001:DB8:30:99::11 / ::12 / ::13 / ::14 |
| ‎PC-KG-ADMIN-01 | ‎— | ‎2001:DB8:30:99::100 |

</div>

---

## חלק 4 — מגדירים

### 4.0 לפני שמתחילים — IPv6 במתגים
נסו `configure terminal` ‏←‏ `ipv6 unicast-routing` במתג 3650, ו-`interface vlan 1` ‏←‏
‏`ipv6 address 2001:DB8::1/64` במתג 2960. אם פקודה **נדחית**, הפעילו IPv6 בתבנית הזיכרון של המתג (פעם
אחת לכל מתג), ואז אתחלו אותו:
```
configure terminal
sdm prefer dual-ipv4-and-ipv6 default
end
copy running-config startup-config
reload
```
(לחצו Enter כדי לאשר את האתחול. אם בדקתם עם `interface vlan 1`, מחקו אחר כך את כתובת הבדיקה:
‏`no ipv6 address 2001:DB8::1/64`.)

### 4.1 ‏SWL3-KG-DIST1 — הגדרה מלאה
```
enable
configure terminal
! ===== hardening =====
hostname SWL3-KG-DIST1
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
! ===== routing for both IP versions =====
ip routing
ipv6 unicast-routing
! ===== VTP transparent: VLANs are created here, locally =====
vtp mode transparent
vlan 31
 name FAB-OPS
vlan 32
 name QUALITY
vlan 33
 name MAINTENANCE
vlan 34
 name SAFETY
vlan 35
 name PLANNING
vlan 36
 name TRAINING
vlan 99
 name MGMT
vlan 100
 name SERVERS
vlan 199
 name LEGACY-IPV4
vlan 998
 name NATIVE
vlan 999
 name PARKING
 exit
spanning-tree mode rapid-pvst
spanning-tree vlan 31-36,99,100,199 root primary
! ===== trunks =====
interface range gi1/0/1 - 4
 description TRUNK to access switch
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 31-36,99,100,199,998
 switchport nonegotiate
 spanning-tree guard root
 no shutdown
interface gi1/0/24
 description TRUNK to SWL3-KG-DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 31-36,99,100,199,998
 switchport nonegotiate
 no shutdown
interface range gi1/0/5 - 23
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 exit
! ===== stateless DHCPv6: only DNS + domain =====
ipv6 dhcp pool KG-STATELESS
 dns-server 2001:DB8:30:100::10
 domain-name intel.lab
 exit
! ===== OSPFv3 process =====
ipv6 router ospf 1
 router-id 3.3.3.2
 exit
! ===== uplink to the edge (dual-stack) =====
interface gi1/1/1
 description to R-KG-EDGE Gi0/0
 no switchport
 ip address 10.30.4.2 255.255.255.252
 ipv6 address 2001:DB8:30:FF01::2/64
 ipv6 ospf 1 area 0
 no shutdown
! ===== user VLAN gateways: IPv6 + RA flags + DHCPv6 + HSRPv6 =====
interface vlan 31
 description GW FAB-OPS
 ipv6 address 2001:DB8:30:31::2/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 31 ipv6 FE80::1
 standby 31 priority 110
 standby 31 preempt
 no shutdown
interface vlan 32
 description GW QUALITY
 ipv6 address 2001:DB8:30:32::2/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 32 ipv6 FE80::1
 standby 32 priority 110
 standby 32 preempt
 no shutdown
interface vlan 33
 description GW MAINTENANCE
 ipv6 address 2001:DB8:30:33::2/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 33 ipv6 FE80::1
 standby 33 priority 110
 standby 33 preempt
 no shutdown
interface vlan 34
 description GW SAFETY
 ipv6 address 2001:DB8:30:34::2/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 34 ipv6 FE80::1
 standby 34 priority 110
 standby 34 preempt
 no shutdown
interface vlan 35
 description GW PLANNING
 ipv6 address 2001:DB8:30:35::2/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 35 ipv6 FE80::1
 standby 35 priority 110
 standby 35 preempt
 no shutdown
interface vlan 36
 description GW TRAINING
 ipv6 address 2001:DB8:30:36::2/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 36 ipv6 FE80::1
 standby 36 priority 110
 standby 36 preempt
 no shutdown
! ===== management and servers: static addresses, no DHCPv6 =====
interface vlan 99
 description GW MGMT
 ipv6 address 2001:DB8:30:99::2/64
 ipv6 ospf 1 area 0
 standby version 2
 standby 99 ipv6 FE80::1
 standby 99 priority 110
 standby 99 preempt
 no shutdown
interface vlan 100
 description GW SERVERS (+ OSPFv3 peering DIST1-DIST2)
 ipv6 address 2001:DB8:30:100::2/64
 ipv6 ospf 1 area 0
 standby version 2
 standby 100 ipv6 FE80::1
 standby 100 priority 110
 standby 100 preempt
 no shutdown
! ===== the legacy IPv4 VLAN (only on DIST1) =====
interface vlan 199
 description GW LEGACY-IPV4
 ip address 10.30.199.1 255.255.255.0
 no shutdown
 exit
ip route 0.0.0.0 0.0.0.0 10.30.4.1
! ===== OSPFv3: talk only on the uplink and the server VLAN =====
ipv6 router ospf 1
 passive-interface default
 no passive-interface gi1/1/1
 no passive-interface vlan 100
 exit
! ===== management =====
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
(‎`1024`)
```
ip ssh version 2
login block-for 120 attempts 3 within 60
ipv6 access-list MGMT6
 permit ipv6 2001:DB8:30:99::/64 any
 deny ipv6 any any log
 exit
line vty 0 15
 transport input ssh
 login local
 ipv6 access-class MGMT6 in
 exec-timeout 5 0
line console 0
 login local
 logging synchronous
 exit
service timestamps log datetime msec
logging host ipv6 2001:DB8:30:100::12
! branch NTP: syncs to Haifa's public NTP (static NAT, step 12) over IPv4
ntp server 200.1.10.4
 end
copy running-config startup-config
```
ההערות אומרות: הקשחה; ניתוב לשתי גרסאות ה-IP; ‏VTP ‏transparent — ה-VLANים נוצרים כאן, מקומית;
‏trunks; ‏stateless DHCPv6 — רק DNS + דומיין; תהליך OSPFv3; קישור כלפי מעלה לנתב הקצה (dual-stack);
שערים של VLANי המשתמשים: ‏IPv6 + דגלי RA + ‏DHCPv6 + ‏HSRPv6; ניהול ושרתים: כתובות קבועות, בלי DHCPv6;
ה-VLAN של IPv4 מדור קודם (רק ב-DIST1); ‏OSPFv3 — מדברים רק על הקישור כלפי מעלה ועל VLAN השרתים; ניהול.
‏NTP של הסניף מסתנכרן ל-NTP הציבורי של חיפה (static NAT, שלב 12) דרך IPv4.

### 4.2 ‏SWL3-KG-DIST2 — הגדרה מלאה
```
enable
configure terminal
hostname SWL3-KG-DIST2
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
ipv6 unicast-routing
vtp mode transparent
vlan 31
 name FAB-OPS
vlan 32
 name QUALITY
vlan 33
 name MAINTENANCE
vlan 34
 name SAFETY
vlan 35
 name PLANNING
vlan 36
 name TRAINING
vlan 99
 name MGMT
vlan 100
 name SERVERS
vlan 199
 name LEGACY-IPV4
vlan 998
 name NATIVE
vlan 999
 name PARKING
 exit
spanning-tree mode rapid-pvst
spanning-tree vlan 31-36,99,100,199 root secondary
interface range gi1/0/1 - 4
 description TRUNK to access switch
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 31-36,99,100,199,998
 switchport nonegotiate
 spanning-tree guard root
 no shutdown
interface gi1/0/24
 description TRUNK to SWL3-KG-DIST1
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 31-36,99,100,199,998
 switchport nonegotiate
 no shutdown
interface range gi1/0/5 - 23
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
 exit
ipv6 dhcp pool KG-STATELESS
 dns-server 2001:DB8:30:100::10
 domain-name intel.lab
 exit
ipv6 router ospf 1
 router-id 3.3.3.3
 exit
interface gi1/1/1
 description to R-KG-EDGE Gi0/2
 no switchport
 ipv6 address 2001:DB8:30:FF02::2/64
 ipv6 ospf 1 area 0
 no shutdown
interface vlan 31
 description GW FAB-OPS
 ipv6 address 2001:DB8:30:31::3/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 31 ipv6 FE80::1
 standby 31 priority 90
 standby 31 preempt
 no shutdown
interface vlan 32
 description GW QUALITY
 ipv6 address 2001:DB8:30:32::3/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 32 ipv6 FE80::1
 standby 32 priority 90
 standby 32 preempt
 no shutdown
interface vlan 33
 description GW MAINTENANCE
 ipv6 address 2001:DB8:30:33::3/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 33 ipv6 FE80::1
 standby 33 priority 90
 standby 33 preempt
 no shutdown
interface vlan 34
 description GW SAFETY
 ipv6 address 2001:DB8:30:34::3/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 34 ipv6 FE80::1
 standby 34 priority 90
 standby 34 preempt
 no shutdown
interface vlan 35
 description GW PLANNING
 ipv6 address 2001:DB8:30:35::3/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 35 ipv6 FE80::1
 standby 35 priority 90
 standby 35 preempt
 no shutdown
interface vlan 36
 description GW TRAINING
 ipv6 address 2001:DB8:30:36::3/64
 ipv6 ospf 1 area 0
 ipv6 nd other-config-flag
 ipv6 dhcp server KG-STATELESS
 standby version 2
 standby 36 ipv6 FE80::1
 standby 36 priority 90
 standby 36 preempt
 no shutdown
interface vlan 99
 description GW MGMT
 ipv6 address 2001:DB8:30:99::3/64
 ipv6 ospf 1 area 0
 standby version 2
 standby 99 ipv6 FE80::1
 standby 99 priority 90
 standby 99 preempt
 no shutdown
interface vlan 100
 description GW SERVERS (+ OSPFv3 peering DIST1-DIST2)
 ipv6 address 2001:DB8:30:100::3/64
 ipv6 ospf 1 area 0
 standby version 2
 standby 100 ipv6 FE80::1
 standby 100 priority 90
 standby 100 preempt
 no shutdown
 exit
ipv6 router ospf 1
 passive-interface default
 no passive-interface gi1/1/1
 no passive-interface vlan 100
 exit
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
(‎`1024`)
```
ip ssh version 2
login block-for 120 attempts 3 within 60
ipv6 access-list MGMT6
 permit ipv6 2001:DB8:30:99::/64 any
 deny ipv6 any any log
 exit
line vty 0 15
 transport input ssh
 login local
 ipv6 access-class MGMT6 in
 exec-timeout 5 0
line console 0
 login local
 logging synchronous
 exit
service timestamps log datetime msec
logging host ipv6 2001:DB8:30:100::12
 end
copy running-config startup-config
```

### 4.3 ‏SW-KG-ACC1 — הגדרה מלאה (Fab-Ops, ‏Quality, ‏legacy, מחשב המנהל)
```
enable
configure terminal
hostname SW-KG-ACC1
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vlan 31
 name FAB-OPS
vlan 32
 name QUALITY
vlan 99
 name MGMT
vlan 199
 name LEGACY-IPV4
vlan 998
 name NATIVE
vlan 999
 name PARKING
 exit
spanning-tree mode rapid-pvst
interface range gi0/1 - 2
 description TRUNK uplink to DIST1 / DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 31-36,99,100,199,998
 switchport nonegotiate
 no shutdown
interface range fa0/1 - 10
 description FAB-OPS users
 switchport mode access
 switchport access vlan 31
interface range fa0/11 - 20
 description QUALITY users
 switchport mode access
 switchport access vlan 32
interface range fa0/21 - 22
 description LEGACY IPv4 devices
 switchport mode access
 switchport access vlan 199
interface fa0/23
 description PC-KG-ADMIN-01 (management)
 switchport mode access
 switchport access vlan 99
interface range fa0/1 - 23
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
 no cdp enable
interface fa0/24
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
interface vlan 99
 description MANAGEMENT
 ipv6 address 2001:DB8:30:99::11/64
 no shutdown
 exit
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
(‎`1024`)
```
ip ssh version 2
login block-for 120 attempts 3 within 60
ipv6 access-list MGMT6
 permit ipv6 2001:DB8:30:99::/64 any
 deny ipv6 any any log
 exit
line vty 0 15
 transport input ssh
 login local
 ipv6 access-class MGMT6 in
 exec-timeout 5 0
line console 0
 login local
 logging synchronous
 exit
service timestamps log datetime msec
logging host ipv6 2001:DB8:30:100::12
 end
copy running-config startup-config
```

<div dir="rtl">

> מתג שכבה 2 לומד את שער ה-IPv6 שלו מה-Router Advertisements — לא צריך שורת `default-gateway`.
> ‏DHCP snooping הוא רק ל-IPv4, ולכן כאן פורטי ה-access מוגנים על ידי port-security, ‏BPDU Guard ו-VLAN
> החניה. (מתגים אמיתיים מוסיפים **RA Guard** ו-**DHCPv6 Guard** — לא קיימים ב-PT. ציינו את זה בספר הפרויקט.)

</div>

### 4.4 ‏SW-KG-ACC2 — הגדרה מלאה (Maintenance, ‏Safety, מדפסת)
```
enable
configure terminal
hostname SW-KG-ACC2
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vlan 33
 name MAINTENANCE
vlan 34
 name SAFETY
vlan 99
 name MGMT
vlan 998
 name NATIVE
vlan 999
 name PARKING
 exit
spanning-tree mode rapid-pvst
interface range gi0/1 - 2
 description TRUNK uplink to DIST1 / DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 31-36,99,100,199,998
 switchport nonegotiate
 no shutdown
interface range fa0/1 - 10
 description MAINTENANCE users
 switchport mode access
 switchport access vlan 33
interface range fa0/11 - 20
 description SAFETY users
 switchport mode access
 switchport access vlan 34
interface fa0/21
 description PRN-KG-ACC2-01
 switchport mode access
 switchport access vlan 33
interface range fa0/1 - 21
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
 no cdp enable
interface range fa0/22 - 24
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
interface vlan 99
 description MANAGEMENT
 ipv6 address 2001:DB8:30:99::12/64
 no shutdown
 exit
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
(‎`1024`)
```
ip ssh version 2
login block-for 120 attempts 3 within 60
ipv6 access-list MGMT6
 permit ipv6 2001:DB8:30:99::/64 any
 deny ipv6 any any log
 exit
line vty 0 15
 transport input ssh
 login local
 ipv6 access-class MGMT6 in
 exec-timeout 5 0
line console 0
 login local
 logging synchronous
 exit
service timestamps log datetime msec
logging host ipv6 2001:DB8:30:100::12
 end
copy running-config startup-config
```

### 4.5 ‏SW-KG-ACC3 — הגדרה מלאה (Planning, ‏Training, מדפסת)
הקלידו שוב את כל הבלוק של 4.4, כשהשורות האלה שונות:

<div dir="rtl">

| השורה ב-4.4 | הופכת ל |
|---|---|
| ‎`hostname SW-KG-ACC2` | ‎`hostname SW-KG-ACC3` |
| ‎`vlan 33` / `name MAINTENANCE` | ‎`vlan 35` / `name PLANNING` |
| ‎`vlan 34` / `name SAFETY` | ‎`vlan 36` / `name TRAINING` |
| ‎`description MAINTENANCE users` / `switchport access vlan 33` | ‎`description PLANNING users` / `switchport access vlan 35` |
| ‎`description SAFETY users` / `switchport access vlan 34` | ‎`description TRAINING users` / `switchport access vlan 36` |
| ‎`description PRN-KG-ACC2-01` / `switchport access vlan 33` | ‎`description PRN-KG-ACC3-01` / `switchport access vlan 35` |
| ‎`ipv6 address 2001:DB8:30:99::12/64` | ‎`ipv6 address 2001:DB8:30:99::13/64` |

</div>

### 4.6 ‏SW-KG-SRV — הגדרה מלאה
```
enable
configure terminal
hostname SW-KG-SRV
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
vtp mode transparent
vlan 99
 name MGMT
vlan 100
 name SERVERS
vlan 998
 name NATIVE
vlan 999
 name PARKING
 exit
spanning-tree mode rapid-pvst
interface range gi0/1 - 2
 description TRUNK uplink to DIST1 / DIST2
 switchport mode trunk
 switchport trunk native vlan 998
 switchport trunk allowed vlan 31-36,99,100,199,998
 switchport nonegotiate
 no shutdown
interface range fa0/1 - 4
 description servers
 switchport mode access
 switchport access vlan 100
 spanning-tree portfast
 spanning-tree bpduguard enable
interface range fa0/5 - 24
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
interface vlan 99
 description MANAGEMENT
 ipv6 address 2001:DB8:30:99::14/64
 no shutdown
 exit
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
(‎`1024`)
```
ip ssh version 2
login block-for 120 attempts 3 within 60
ipv6 access-list MGMT6
 permit ipv6 2001:DB8:30:99::/64 any
 deny ipv6 any any log
 exit
line vty 0 15
 transport input ssh
 login local
 ipv6 access-class MGMT6 in
 exec-timeout 5 0
line console 0
 login local
 exit
logging host ipv6 2001:DB8:30:100::12
 end
copy running-config startup-config
```

### 4.7 ‏R-KG-EDGE — הגדרה מלאה
```
enable
configure terminal
hostname R-KG-EDGE
no ip domain-lookup
enable secret Intel#En4ble
service password-encryption
banner motd #
*  Intel Israel - AUTHORIZED ACCESS ONLY - all activity is logged  *
#
ipv6 unicast-routing
ipv6 router ospf 1
 router-id 3.3.3.1
 exit
interface gi0/0
 description to SWL3-KG-DIST1
 ip address 10.30.4.1 255.255.255.252
 ip nat inside
 ipv6 address 2001:DB8:30:FF01::1/64
 ipv6 ospf 1 area 0
 no shutdown
interface gi0/2
 description to SWL3-KG-DIST2
 ipv6 address 2001:DB8:30:FF02::1/64
 ipv6 ospf 1 area 0
 no shutdown
interface gi0/1
 description WAN to R-ISPC-PE (dual-stack)
 ip address 200.3.1.2 255.255.255.252
 ip nat outside
 ipv6 address 2001:DB8:C:1::2/64
 no shutdown
 exit
! ===== static toward the WAN, both IP versions =====
ipv6 route ::/0 2001:DB8:C:1::1
ip route 0.0.0.0 0.0.0.0 200.3.1.1
ip route 10.30.199.0 255.255.255.0 10.30.4.2
! ===== tell the DIST switches about the IPv6 default route =====
ipv6 router ospf 1
 default-information originate
 exit
! ===== PAT (overload) for the legacy VLAN + DIST1's NTP =====
access-list 1 permit 10.30.199.0 0.0.0.255
access-list 1 permit 10.30.4.0 0.0.0.3
ip nat inside source list 1 interface gi0/1 overload
! ===== inbound IPv6 filter =====
ipv6 access-list WAN6-IN
 remark --- ICMPv6 is required by IPv6 itself (neighbour discovery) ---
 permit icmp any any
 remark --- replies from web and DNS servers ---
 permit tcp any eq www any
 permit udp any eq domain any
 deny ipv6 any any log
 exit
interface gi0/1
 ipv6 traffic-filter WAN6-IN in
 exit
! ===== management =====
ip domain-name intel.lab
username admin privilege 15 secret Intel#Adm1n
crypto key generate rsa
```
(‎`1024`)
```
ip ssh version 2
login block-for 120 attempts 3 within 60
ipv6 access-list MGMT6
 permit ipv6 2001:DB8:30:99::/64 any
 deny ipv6 any any log
 exit
line vty 0 15
 transport input ssh
 login local
 ipv6 access-class MGMT6 in
 exec-timeout 5 0
line console 0
 login local
 exit
service timestamps log datetime msec
logging host ipv6 2001:DB8:30:100::12
 end
copy running-config startup-config
```
ההערות אומרות: ניתוב סטטי לכיוון ה-WAN, בשתי גרסאות ה-IP; מספרים למתגי ה-DIST על נתיב ברירת המחדל של
IPv6; ‏PAT ‏(overload) ל-VLAN מדור קודם + ל-NTP של DIST1; מסנן IPv6 נכנס — ‏ICMPv6 נדרש על ידי IPv6 עצמו
(גילוי שכנים), ותשובות משרתי web ו-DNS; ניהול.

### 4.8 ‏R-ISPC-PE — מנתבים את בלוק ה-IPv6 של קריית גת
```
enable
configure terminal
ipv6 route 2001:DB8:30::/48 2001:DB8:C:1::2
end
copy running-config startup-config
```

### 4.9 שרתים ומכשירי קצה (לחיצה אחרי לחיצה)
**הגדרות IPv6 בשרת או במחשב:** ‏Desktop ‏←‏ **IP Configuration** ‏←‏ החלק **IPv6 Configuration**.

<div dir="rtl">

| מכשיר | הגדרת IPv6 | כתובת | שער | ‏DNS של IPv6 |
|---|---|---|---|---|
| ‎SRV-KG-DNS | ‎Static | ‎2001:DB8:30:100::10 / 64 | ‎FE80::1 | ‎2001:DB8:30:100::10 |
| ‎SRV-KG-MAIL | ‎Static | ‎2001:DB8:30:100::11 / 64 | ‎FE80::1 | ‎2001:DB8:30:100::10 |
| ‎SRV-KG-SYSLOG | ‎Static | ‎2001:DB8:30:100::12 / 64 | ‎FE80::1 | ‎2001:DB8:30:100::10 |
| ‎SRV-KG-AAA | ‎Static | ‎2001:DB8:30:100::13 / 64 | ‎FE80::1 | ‎2001:DB8:30:100::10 |
| ‎PC-KG-ADMIN-01 | ‎Static | ‎2001:DB8:30:99::100 / 64 | ‎FE80::1 | ‎2001:DB8:30:100::10 |
| כל 12 המחשבים של המחלקות | ‎**Automatic** | ‏(SLAAC ממלא) | | |
| ‎SRV-ISPC-WEB6 | ‎Static | ‎2001:DB8:C:50::80 / 64 | ‎FE80::1 | ‎— |

</div>

במכשירים שהם IPv6 בלבד, השאירו את שדות ה-**IPv4** ריקים.

**מחשבי legacy ‏(IPv4 בלבד):** ‏PC-KG-LEGACY-01 ‏‎`10.30.199.10`, ‏PC-KG-LEGACY-02 ‏‎`10.30.199.11`, מסיכה
‎`255.255.255.0`, שער ‎`10.30.199.1`, ‏DNS ‏‎`200.1.100.10`.

**מדפסות:** ‏Config ‏←‏ FastEthernet0 ‏←‏ IPv6 ‏←‏ **Automatic** ‏(SLAAC).

**שירותים:**
- **‏SRV-KG-DNS** ‏←‏ DNS **On** ‏←‏ רשומות מסוג **AAAA Record**:
  ‏`mail.kg.intel.lab → 2001:DB8:30:100::11`, ‏`www6.isp-web.com → 2001:DB8:C:50::80`.
- **‏SRV-KG-MAIL** ‏←‏ EMAIL ‏←‏ דומיין `kg.intel.lab` ‏←‏ Set (המשתמשים בשלב 16).
- **‏SRV-KG-SYSLOG** ‏←‏ SYSLOG **On**.
- **‏SRV-KG-AAA** ‏←‏ AAA **On** (ראו את ההערה למטה).
- **‏SRV-ISPC-WEB6** ‏←‏ HTTP ‏←‏ ערכו את `index.html` ‏←‏ ‎`<h1>IPv6 works!</h1>`‎ ‏←‏ Save.
- כבו בכל שרת את השירותים שלא צריך.

<div dir="rtl">

> **‏AAA על IPv6 ב-Packet Tracer.** התמיכה של PT ב-TACACS+/RADIUS על IPv6 מוגבלת, ולכן המכשירים של
> קריית גת למעלה משתמשים במסד המשתמשים ה**מקומי** (`login local`). שרת ה-AAA קיים בסניף (דרישה 20.10).
> אם גרסת ה-PT שלכם מקבלת את זה, נסו במתג:
> ‏`aaa new-model` ‏←‏ `tacacs server KG-AAA` ‏←‏ `address ipv6 2001:DB8:30:100::13` ‏←‏ `key Intel#Tac`
> ‏←‏ `exit` ‏←‏ `aaa authentication login default group tacacs+ local`, ורשמו את המתג ב-SRV-KG-AAA לפי
> כתובת ה-IPv6 שלו. כתבו בספר הפרויקט איזו דרך עבדה.
>
> אותו דבר לגבי `logging host ipv6 ...`‎: אם הפקודה נדחית, נסו `logging 2001:DB8:30:100::12`.

</div>

### 4.10 מה הפקודות החדשות אומרות

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`ipv6 unicast-routing` | "נתב IPv6 ושלח Router Advertisements" |
| ‎`ipv6 address 2001:DB8:30:31::2/64` | כתובת ה-IPv6 של הממשק הזה |
| ‎`ipv6 ospf 1 area 0` | "הממשק הזה מצטרף לתהליך OSPFv3 מספר 1, ‏area 0" |
| ‎`ipv6 router ospf 1` / `router-id 3.3.3.2` | הפעל OSPFv3, עם המזהה הזה |
| ‎`ipv6 nd other-config-flag` | הדלק את ה-**O-flag** ב-RAs: "בקשו מ-DHCPv6 את ה-DNS" |
| ‎`ipv6 dhcp pool KG-STATELESS` + `dns-server` | התוספות ש-stateless DHCPv6 מחלק |
| ‎`ipv6 dhcp server KG-STATELESS` | "ענה לשאלות DHCPv6 ב-VLAN הזה" |
| ‎`standby 31 ipv6 FE80::1` | ‏HSRP ל-IPv6: שער משותף FE80::1 |
| ‎`ipv6 route ::/0 2001:DB8:C:1::1` | נתיב ברירת מחדל של IPv6 (‏‎`::/0` = הכול) |
| ‎`ip nat inside source list 1 interface gi0/1 overload` | **‏PAT** — כל המכשירים מדור קודם חולקים את 200.3.1.2 |
| ‎`ipv6 traffic-filter WAN6-IN in` | מחילים ACL של IPv6 על ממשק |
| ‎`ipv6 access-class MGMT6 in` | רשימת האורחים של IPv6 לקווי ה-VTY |

</div>

---

## חלק 5 — בודקים את העבודה

```
SWL3-KG-DIST1# show ipv6 interface brief         <- every VLAN up with its 2001:DB8:30:x::2
SWL3-KG-DIST1# show standby brief
Vl31   31  110 P Active   local   FE80::...   FE80::1
SWL3-KG-DIST1# show ipv6 ospf neighbor           <- 3.3.3.1 (edge) and 3.3.3.3 (DIST2) FULL
SWL3-KG-DIST2# show ipv6 route
OE2 ::/0 [110/1] via FE80::..., GigabitEthernet1/1/1   <- default from the edge
R-KG-EDGE#     show ip nat translations          <- 200.3.1.2:port  10.30.199.10:port
```
(‏`show ipv6 interface brief` ‏←‏ כל VLAN למעלה עם ה-‎2001:DB8:30:x::2 שלו; ‏`show ipv6 ospf neighbor` ‏←‏
‏3.3.3.1 (נתב הקצה) ו-3.3.3.3 ‏(DIST2) במצב FULL; ב-DIST2 ‏`OE2 ::/0` = ברירת המחדל מנתב הקצה; בנתב הקצה
‏`show ip nat translations` ‏←‏ ‏200.3.1.2:port מול 10.30.199.10:port.)

<div dir="rtl">

| מאיפה | עושים | מה אמור לקרות |
|---|---|---|
| ‎PC-KG-FAB-01 | ב-Command Prompt: `ipconfig /all` | ‏IPv6 ‏‎`2001:DB8:30:31:…`‎, שער `FE80::1`, ‏DNS ‏‎`2001:DB8:30:100::10` |
| ‎PC-KG-FAB-01 | ‎`ping 2001:DB8:30:36::2` | ✅ ניתוב בין VLANים ב-IPv6 |
| ‎PC-KG-FAB-01 | ‎`ping 2001:DB8:30:100::10` | ✅ שרת ה-DNS |
| ‎PC-KG-FAB-01 | בדפדפן: Web Browser ‏←‏ `http://www6.isp-web.com` | ‎✅ "IPv6 works!" |
| ‎PC-KG-LEGACY-01 | ‎`ping 200.1.100.11` | ✅ דרך PAT |
| ‎PC-KG-ADMIN-01 | ‎`ssh -l admin 2001:DB8:30:99::11` | ‎✅ |
| ‎PC-KG-FAB-01 | ‎`ssh -l admin 2001:DB8:30:99::11` | ❌ נדחה (MGMT6) |
| ‎SWL3-KG-DIST1 | ‎`show ntp status` | מסונכרן ל-200.1.10.4 (אחרי Fast Forward) |

</div>

**בדיקת מעבר (failover) של HSRPv6:** קודם **File → Save**. אחר כך `ping -t 2001:DB8:30:100::10` ממחשב,
ודמו DIST1 מת על ידי מחיקתו (הכלי **Delete** ‏←‏ לחצו על DIST1) ‏←‏ ‏DIST2 הופך ל-Active עבור `FE80::1`,
והפינגים ממשיכים. בסוף **File → Open** לקובץ ששמרתם כדי להחזיר את DIST1.

---

## חלק 6 — שומרים
‏`copy running-config startup-config` בכל מקום ‏←‏ **File → Save**.

## נקודת ביקורת
- [ ] המחשבים מקבלים כתובות IPv6 אוטומטית, עם שער FE80::1 ושרת DNS
- [ ] שכני OSPFv3 במצב FULL; למתגי ה-DIST יש את נתיב ברירת המחדל ‎`::/0`
- [ ] גלישה ב-IPv6 ל-www6.isp-web.com עובדת
- [ ] מחשבי ה-legacy מגיעים לאינטרנט דרך PAT
- [ ] ה-failover של HSRPv6 עובד

## אם משהו לא עובד

<div dir="rtl">

| בעיה | פתרון |
|---|---|
| פקודות `ipv6 ...`‎ נדחות במתג | חלק 4.0 — ‏`sdm prefer dual-ipv4-and-ipv6 default` + ‏reload |
| ‏OSPFv3 לא מתחיל | אין `router-id` תחת `ipv6 router ospf 1` |
| המחשבים מקבלים רק כתובת `FE80::`‎ | חסר `ipv6 unicast-routing` ‏←‏ אין RAs; או שה-SVI של ה-VLAN למטה |
| למחשבים אין DNS | חסר `ipv6 nd other-config-flag` / ‏`ipv6 dhcp server`; או הקלידו את ה-DNS ידנית |
| ‏`standby 31 ipv6 FE80::1` נדחה | השתמשו ב-`standby 31 ipv6 autoconfig`, קראו את הכתובת הווירטואלית עם `show standby brief`, והשתמשו בה כשער של השרתים |
| ‏HSRP ל-IPv6 לא נתמך בכלל | ל-IPv6 יש יתירות שער משלו: שני מתגי ה-DIST שולחים RAs והמחשבים לומדים שני שערים. כתבו את זה בספר הפרויקט |
| כל ה-IPv6 מת אחרי ה-ACL בנתב הקצה | חסרה השורה `permit icmp any any` ‏(IPv6 צריך ICMPv6) |
| למחשב legacy אין אינטרנט | ‏`ip route 10.30.199.0 ...`‎ בנתב הקצה, ‏`ip route 0.0.0.0 ... 10.30.4.1` ב-DIST1, ‏NAT inside/outside |

</div>

## אתגר
למה מחשב בקריית גת לא מצליח לפתוח את `http://www.intel.lab` (האתר של חיפה), למרות שיש לו אינטרנט?
הציעו שני פתרונות מהעולם האמיתי.

<details dir="rtl"><summary>תשובה</summary>

ל-`www.intel.lab` יש רק כתובת **IPv4** ‏(200.1.10.3 ציבורית / 10.10.200.13 פרטית), והמחשבים בקריית גת
מדברים **רק IPv6**. מחשב שהוא IPv6 בלבד לא יכול לדבר עם שרת שהוא IPv4 בלבד בלי מתרגם. פתרונות
אמיתיים: (1) **NAT64 + ‏DNS64** בנתב הקצה של קריית גת; (2) להפוך את ה-DMZ של חיפה ל-**dual-stack**
(כתובת IPv6 + רשומת AAAA לשרת ה-web); (3) ‏reverse proxy. ‏PT לא תומך ב-NAT64 — תעדו את זה כפשרה
תכנונית שנובעת מהדרישה "סניף אחד כולו IPv6".
</details>

---

## 🛠 הפרויקט שלכם

עשיתם את השלב הזה על הדוגמה של אינטל. עכשיו עשו אותו שוב בפרויקט **שלכם**, עם הערכים
מהתוכנית **שלכם** (`my-project/plan.md`). הפקודות זהות — רק הערכים משתנים.

זה **סניף ה-IPv6** של הדוגמה. בנו את האתר השלישי **שלכם** מתוך חלקים ג–ה בתוכנית:

<div dir="rtl">

| בדוגמה | בפרויקט שלכם — לוקחים מ |
|---|---|
| ‏‎`2001:DB8:30::/48`, הכלל "מספר ה-VLAN = הקבוצה הרביעית" | תוכנית, חלק ג (ה-‎/48 שלכם — שמרו על כלל פשוט כמו זה) |
| ‏VLANים 31–36, ‏99, ‏100 | תוכנית, חלק ד (אתר 3) |
| ‏router-IDs של OSPFv3 ‏3.3.3.x | router-IDs משלכם |
| ‏HSRP ל-IPv6, שער וירטואלי `FE80::1` | להשאיר את השיטה, הקבוצות שלכם |
| ‎‏SLAAC / ‏stateless DHCPv6 | תוכנית, חלק ה (שורת ה-DHCP) |
| ‏VLAN ‏199 של IPv4 מדור קודם עם PAT | תוכנית, חלק ה (שורת ה-NAT) — בדקו את הפרשנות הזו עם המנחה, כמו שאומרת הערת התכנון ב-design.md |

</div>

משרד החינוך דורש אתר אחד שהוא **כולו IPv6** (דרישה 7).

**בדיקה:** ‏`show ipv6 ospf neighbor`; המחשבים מקבלים כתובת IPv6 מה-prefix שלכם; ‏ping מהאתר הזה לשרת
IPv6 באינטרנט עובד.

💾 שמרו בשם `my-project/step14.pkt`.

---

## 🎓 מסבירים לבוחן

בבחינה, הבוחן מצביע על הפרויקט **שלכם** ומבקש **להסביר** ו**להראות**. תרגלו כל שאלה
**בקול**, ואז הראו את התשובה בפרויקט שלכם — לא בדוגמה. כסו את התשובה, ענו בעצמכם, ורק אז
פתחו והשוו.

★1–★3 = שאלה ממאגר השאלות של משרד החינוך (רמת קושי 1–3).
◆ = לא במאגר, אבל בוחנים שואלים אותה לעיתים קרובות.

**1. ◆ מהם הסוגים העיקריים של כתובות IPv6?**

<details dir="rtl"><summary>תשובה</summary>

‏Global unicast ‏(‎`2000::/3`, ניתנת לניתוב באינטרנט), ‏link-local ‏(`FE80::/10`, רק על הקישור — משמשת
פרוטוקולי ניתוב וכשער), ‏multicast ‏(`FF00::/8`). ב-IPv6 אין broadcast.

**איפה מראים:** `show ipv6 interface brief`
</details>

**2. ◆ מה ההבדל בין SLAAC, ‏stateless DHCPv6 ו-stateful DHCPv6?**

<details dir="rtl"><summary>תשובה</summary>

‏SLAAC: המחשב בונה לעצמו כתובת מה-prefix של הנתב (Router Advertisement). ‏Stateless DHCPv6: הכתובת
מ-SLAAC, אבל מידע נוסף (DNS) משרת DHCPv6 (‏`ipv6 nd other-config-flag`). ‏Stateful DHCPv6: השרת עצמו
מחלק את הכתובת.

**איפה מראים:** מחשב ‏←‏ IP Configuration ‏←‏ IPv6 ‏(Automatic)
</details>

**3. ◆ במה OSPFv3 שונה מ-OSPFv2?**

<details dir="rtl"><summary>תשובה</summary>

הוא מנתב IPv6, מופעל **על כל ממשק** (`ipv6 ospf 1 area 0`) במקום עם פקודות `network`, משתמש בכתובות
link-local לשכנים, ועדיין צריך router-ID של 32 ביט שמוגדר ידנית כשאין כתובת IPv4.

**איפה מראים:** `show ipv6 ospf neighbor`, `show ipv6 route`
</details>

**4. ◆ איך HSRP עובד ב-IPv6?**

<details dir="rtl"><summary>תשובה</summary>

כמו ב-IPv4 (חובה `standby version 2`), אבל השער הווירטואלי הוא כתובת **link-local** (כאן `FE80::1`),
שהמחשבים לומדים כשער ברירת המחדל שלהם.

**איפה מראים:** `show standby brief`
</details>

**5. ★1 מהו PAT? למה יש בכלל NAT באתר IPv6?**

<details dir="rtl"><summary>תשובה</summary>

‏PAT מאפשר להרבה מחשבים פנימיים לחלוק כתובת IPv4 ציבורית אחת בעזרת מספרי פורט. ‏IPv6 לא צריך NAT
(יש מספיק כתובות); האתר הזה שומר VLAN ‏IPv4 קטן אחד מדור קודם, ורק הוא עובר PAT — כדי לעמוד בדרישה
ל-NAT בכל אתר (דרישה 10).

**איפה מראים:** `show ip nat translations`
</details>

---

## 🔁 עושים שוב — בלי המדריך

הבוחן יכול לבקש מכם להגדיר משהו שוב, מולו. תצליחו רק אם עשיתם את זה **בלי המדריך** לפני כן.
עשו את התרגיל הזה בפרויקט שלכם:

בעותק של הקובץ שלכם, מחקו את כתובות ה-IPv6 ואת OSPFv3 ממתג distribution אחד. בלי העמוד הזה, הגדירו
אותם שוב מתוך התוכנית שלכם. יעד: **‏15 דקות**. אחר כך הראו מחשב עם כתובת IPv6 מה-prefix שלכם ואת
`show ipv6 ospf neighbor`.

---

## 👩‍🏫 הערות למורה
- **שיעור 1:** ‏IPv6 — למה, איך קוראים ומקצרים כתובות (תרגלו 10 על הלוח), ‏‎/64, ‏link-local, תוכנית
  מספרי ה-VLAN שלנו ‏←‏ בנייה וחיווט.
- **שיעור 2:** ‏SLAAC + ‏stateless DHCPv6 (הראו את ה-RA ואת ה-DHCPv6 במצב Simulation, מסננים **ICMPv6**
  ו-**DHCPv6**), ‏OSPFv3, ‏HSRPv6 ‏←‏ ‏DIST1 ו-DIST2 (בזוגות: אחד מקליד את DIST1, השני את DIST2).
- **שיעור 3:** מתגי ה-access, מתג השרתים, נתב הקצה, השרתים.
- **שיעור 4:** בדיקות, ‏failover, ה-VLAN מדור קודם ו-PAT, הדיון באתגר (דו-קיום של IPv4 ו-IPv6).
- **שאלות נפוצות של תלמידים**
  - *"איפה מסיכת הרשת?"* — ה-‎`/64` הוא המסיכה. ב-IPv6 תמיד כותבים את אורך ה-prefix.
  - *"למה FE80::1 כשער ולא 2001:…::1?"* — נתבים מפרסמים את עצמם בכתובות link-local; היא אף פעם לא
    משתנה, גם אם ה-prefix הגלובלי משתנה.
  - *"בלי NAT בכלל?"* — לא צריך: כל כתובת IPv6 ייחודית. האבטחה באה מחומות אש ומ-ACLs.
- **טעויות אופייניות:** שכחת תבנית ה-SDM + ה-reload; שגיאות כתיב בכתובות IPv6 ארוכות (אפסים); ‏OSPFv3
  בלי router-ID; שכחת `permit icmp` ב-ACLs של IPv6.
