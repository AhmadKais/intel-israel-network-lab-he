# דף עזר לבדיקות

## הישרדות ב-CLI

<div dir="rtl">

| מקשים / פקודה | מה זה עושה |
|---|---|
| ‎`?`‎ | מציג מה אפשר להקליד כאן |
| ‎`Tab` | משלים את המילה |
| ‎`Ctrl+Shift+6` | עוצר ping / ‏traceroute או חיפוש DNS תקוע |
| ‎`Ctrl+Z` / `end` | חזרה ל-privileged EXEC |
| ‎`do <show cmd>`‎ | מריץ פקודת show מתוך מצב ההגדרות |
| ‎`show run \| section ospf` | מציג רק חלק מההגדרות |
| ‎`show run \| include hostname` | מחפש בהגדרות (כמו grep) |
| ‎`copy run start` / `wr` | **שמירה** (עשו את זה אחרי כל שלב!) |

</div>

## שכבה 2

<div dir="rtl">

| פקודה | מה מחפשים |
|---|---|
| ‎`show vlan brief` | ה-VLANים קיימים, הפורטים ב-VLAN הנכון |
| ‎`show interfaces trunk` | ה-trunk למעלה, ‏native VLAN 998, רשימת ה-VLANים המותרים |
| ‎`show vtp status` | דומיין, מצב, ‏revision number |
| ‎`show etherchannel summary` | ‏`Po1(SU)`‎ ופורטים חברים ‎`(P)`‎ |
| ‎`show spanning-tree vlan 10` | ‏"This bridge is the root" על המתג הנכון |
| ‎`show spanning-tree summary` | מצב rapid-pvst, ברירות המחדל של PortFast / ‏BPDU guard |
| ‎`show port-security interface fa0/1` | ‏Secure-up, מספר ההפרות |
| ‎`show ip dhcp snooping` / ‎`... binding` | פורטים מהימנים (trusted), ‏bindings שנלמדו |
| ‎`show mac address-table` | איזה MAC נמצא באיזה פורט |
| ‎`show cdp neighbors` | מי מחובר לאן |

</div>

## שכבה 3

<div dir="rtl">

| פקודה | מה מחפשים |
|---|---|
| ‎`show ip interface brief` | ‏up/up וכתובות IP נכונות |
| ‎`show standby brief` | ‎‏Active/Standby, ‏VIP, ‏priority, ‏`P` (preempt) |
| ‎`show ip route` | הקודים O / O IA / O E2 / D / D EX / S / B / C |
| ‎`show ip ospf neighbor` | מצב FULL |
| ‎`show ip ospf interface brief` | ה-area של כל ממשק |
| ‎`show ip ospf virtual-links` | ‎‏`Virtual Link ... is up` |
| ‎`show ip eigrp neighbors` | השכנים מופיעים |
| ‎`show ip bgp summary` | במצב השכן יש מספר (prefixes), לא Idle/Active |
| ‎`show ip bgp` | נתיבים עם ‎`*>`‎ (הטוב ביותר) |
| ‎`show ipv6 route` / `show ipv6 ospf neighbor` | המקבילות ב-IPv6 |
| ‎`show ip nat translations` | ‎‏inside local ↔ inside global |
| ‎`show ip dhcp binding` | הכתובות שחולקו |
| ‎`show crypto isakmp sa` | ‏`QM_IDLE` = שלב 1 למעלה |
| ‎`show crypto ipsec sa` | ‏‎`#pkts encaps/decaps` עולים |
| ‎`show access-lists` | מוני התאמות ‎`(N match(es))`‎ |

</div>

## ‏ASA

<div dir="rtl">

| פקודה | מה מחפשים |
|---|---|
| ‎`show nameif` | ‏inside/outside/dmz עם רמות האבטחה |
| ‎`show route` | נתיב ברירת מחדל + נתיבים פנימיים |
| ‎`show access-list` | מוני התאמות |
| ‎`show conn` | חיבורים פעילים דרך חומת האש |

</div>

## בדיקות ממחשב קצה (PC ‏←‏ Desktop ‏←‏ Command Prompt)

```
ipconfig /all          ipv6config
ping 10.10.200.13      ping -t 10.10.16.1   (continuous — stop with Ctrl+C)
tracert 200.1.100.11   nslookup www.intel.lab
ssh -l admin 10.10.19.11
```
(‏`ping -t` = ‏ping רציף — עוצרים עם Ctrl+C.)
