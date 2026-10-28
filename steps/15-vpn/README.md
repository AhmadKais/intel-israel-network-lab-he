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

## 🗺 המשימות שלכם בשלב הזה
**שיעור 1 — הרישיון והמנהרה**
- [ ] **משימה 1** — פותחים את שלב 14 ושומרים בשם שלב 15 (2 דקות)
- [ ] **משימה 2** — קודם רואים את הבעיה: ירושלים לא מגיעה לחיפה (5 דקות)
- [ ] **משימה 3** — מפעילים את רישיון האבטחה בשני נתבי הקצה (15 דקות)
- [ ] **משימה 4** — מנהרת ה-GRE בשני נתבי הקצה (15 דקות)

**שיעור 2 — הצפנה**
- [ ] **משימה 5** — ‏IPsec ב-R-HFA-EDGE ‏(15 דקות)
- [ ] **משימה 6** — ‏IPsec ב-R-JLM-EDGE ‏(10 דקות)
- [ ] **משימה 7** — מכניסים את ירושלים דרך ה-ASA + בודקים את ה-VPN בין האתרים (20 דקות)
- [ ] **משימה 8** — רואים את ההצפנה במצב Simulation ‏(10 דקות)

**שיעור 3 — העובד מהבית**
- [ ] **משימה 9** — ‏R-HFA-EDGE כשרת VPN לגישה מרחוק (15 דקות)
- [ ] **משימה 10** — לקוח ה-VPN של העובד מהבית (10 דקות)
- [ ] **משימה 11** — בדיקות סופיות ושמירה (10 דקות)
- [ ] **תרגילים** א ו-ב
- [ ] **🛠 הפרויקט שלכם**

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

### 1.7 חוק המראות
‏VPN בין אתרים = **שתי תמונות מראה**. כל מה שבצד של חיפה מצביע על הכתובת של ירושלים, ולהפך:

<div dir="rtl">

| | ‎R-HFA-EDGE | ‎R-JLM-EDGE |
|---|---|---|
| כתובת Tunnel0 | ‎172.16.12.**1** | ‎172.16.12.**2** |
| ‎`tunnel destination` / `set peer` / `isakmp key ... address` | ‎**200.2.1.2** | ‎**200.1.1.2** |
| ‎‏ACL ‏`permit gre host A host B` | ‎A = 200.1.1.2, B = 200.2.1.2 | ‎A = 200.2.1.2, B = 200.1.1.2 |
| נתיב לתוך המנהרה | ‎`10.20.0.0/16 → 172.16.12.2` | ‎`10.10.0.0/16 → 172.16.12.1` |
| ‏Policy, מפתח, ‏transform set | **זהים** | **זהים** |

</div>

<div dir="rtl">

> אין מה להציב בשלב הזה — נתבי הקצה, ה-ASA ו-PC-HOME-01 כבר קיימים.

</div>

---

## משימה 1 — פותחים את שלב 14 ושומרים בשם שלב 15 (איך? ‏←‏ M1)
‏**File → Open** ‏←‏ `my-work/step14.pkt` ‏←‏ **File → Save As** ‏←‏ `my-work/step15.pkt`.

---

## משימה 2 — קודם רואים את הבעיה
👉 **איפה:** ‏**PC-JLM-SAL-01** ‏←‏ Desktop ‏←‏ Command Prompt.

⌨️ מקלידים:
```
ping 10.10.16.1
```
✅ **אמורים לראות:** ‏`Request timed out` (או `Destination host unreachable`).

🧠 **למה?** ‏10.10.16.1 היא כתובת **פרטית** של חיפה. החבילה מגיעה ל-R-JLM-EDGE, עוברת NAT ונשלחת
לאינטרנט — ולאינטרנט אין נתיב ל-10.x. אחרי השלב הזה, אותו ping יעבוד.

---

## משימה 3 — מפעילים את רישיון האבטחה בשני נתבי הקצה
עושים את זה ב-**R-HFA-EDGE**, ואז חוזרים על זה ב-**R-JLM-EDGE**.

👉 **איפה:** הנתב ‏←‏ CLI ‏←‏ נכנסים (`admin` / `Intel#Adm1n`) ‏←‏ `R-...#`‎.

⌨️ מקלידים:
```
configure terminal
license boot module c2900 technology-package securityk9
```
הנתב מציג טקסט של רישיון ושואל `ACCEPT? [yes/no]:`‎ ‏←‏ מקלידים **`yes`** ‏←‏ Enter.

⌨️ מקלידים:
```
end
copy running-config startup-config
reload
```
לוחצים **Enter** כדי לאשר את האתחול. לוחצים **Fast Forward Time** עד שהנתב עולה, ונכנסים שוב.

🔍 **בודקים עכשיו:** ‏`show version` ‏←‏ בטבלת הרישיונות למטה `securityk9` הוא
‏**Permanent** / **Active** (או `RightToUse`).

❌ **פקודות `crypto` עדיין עונות ‎`% Invalid input`:** דילגתם על האתחול.

סמנו:
- [ ] ‏R-HFA-EDGE
- [ ] ‏R-JLM-EDGE

---

## משימה 4 — מנהרת ה-GRE בשני נתבי הקצה

### 4א — ‏R-HFA-EDGE
👉 **איפה:** ‏R-HFA-EDGE ‏←‏ `R-HFA-EDGE#`‎.

⌨️ מקלידים:
```
configure terminal
interface tunnel 0
 description GRE to R-JLM-EDGE (encrypted by IPsec)
 ip address 172.16.12.1 255.255.255.252
 tunnel source gi0/1
 tunnel destination 200.2.1.2
 exit
ip route 10.20.0.0 255.255.0.0 172.16.12.2
 end
copy running-config startup-config
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`interface tunnel 0` + `tunnel source` / `tunnel destination` | כבל וירטואלי מהכתובת הציבורית שלי לשלהם |
| ‎`ip route 10.20.0.0 255.255.0.0 172.16.12.2` | "הבלוק הפרטי של ירושלים נכנס למנהרה" (נתיב סטטי — דרישה 22.17) |

</div>

### 4ב — ‏R-JLM-EDGE (תמונת המראה)
👉 **איפה:** ‏R-JLM-EDGE ‏←‏ `R-JLM-EDGE#`‎.

⌨️ מקלידים:
```
configure terminal
interface tunnel 0
 description GRE to R-HFA-EDGE (encrypted by IPsec)
 ip address 172.16.12.2 255.255.255.252
 tunnel source gi0/1
 tunnel destination 200.1.1.2
 exit
ip route 10.10.0.0 255.255.0.0 172.16.12.1
 end
copy running-config startup-config
```
🔍 **בודקים עכשיו:** ב-R-JLM-EDGE ‏`ping 172.16.12.1` ‏←‏ ‎`!!!!!`‎ — המנהרה עובדת (עדיין **לא**
מוצפנת). ‏`show interfaces tunnel 0` ‏←‏ `Tunnel0 is up, line protocol is up`.

<div dir="rtl">

> ה-`redistribute static` משלב 13 נותן עכשיו גם את הנתיב ‎`10.10.0.0/16` ל-CC1/CC2 — כך שכל ירושלים
> יודעת ש"חיפה נמצאת דרך נתב הקצה". ה-ACL של CBAC ‏`WAN-IN` כבר מכניסה GRE.

</div>

❌ **‏Tunnel0 למעלה אבל ה-ping נכשל:** ב-R-JLM-EDGE בדקו שב-`WAN-IN` יש את השורה `permit gre`
(שלב 13, משימה 15א).

---

## משימה 5 — ‏IPsec ב-R-HFA-EDGE
👉 **איפה:** ‏R-HFA-EDGE ‏←‏ `configure terminal`.

### 5א — שלב 1: איך שני הנתבים סומכים זה על זה
⌨️ מקלידים:
```
crypto isakmp policy 10
 encryption aes 256
 hash sha
 authentication pre-share
 group 5
 lifetime 86400
 exit
crypto isakmp key Intel#S2S-Key address 200.2.1.2 no-xauth
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`crypto isakmp policy 10` ‏(encryption/hash/authentication/group) | איך בודקים זה את זה בשלב 1 (חייב להתאים בשני הצדדים) |
| ‎`crypto isakmp key KEY address PEER no-xauth` | הסוד המשותף עם העמית (peer) הזה; ‏`no-xauth` = זה נתב, אל תבקש ממנו שם משתמש |

</div>

✅ ייתכן שיופיע ‎`%CRYPTO-6-ISAKMP_ON_OFF: ISAKMP is ON` — טוב.

### 5ב — שלב 2: מה מצפינים ואיך
⌨️ מקלידים:
```
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
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`crypto ipsec transform-set ... esp-aes 256 esp-sha-hmac` | איך הנתונים מוצפנים (AES-256) ונבדקים (SHA) |
| ‎`crypto map VPN-MAP 10 ipsec-isakmp` / `set peer` / `match address` | "הצפן תעבורה שמתאימה ל-ACL הזו, לכיוון העמית הזה" |

</div>

<div dir="rtl">

> ‏PT עשוי להדפיס הודעה שמתחילה ב-‎`% NOTE: This new crypto map will remain disabled` — זה רגיל, מוסיפים את העמית ואת ה-ACL בשורות הבאות.

</div>

### 5ג — מדליקים את זה על ממשק האינטרנט
⌨️ מקלידים:
```
interface gi0/1
 crypto map VPN-MAP
 end
copy running-config startup-config
```

---

## משימה 6 — ‏IPsec ב-R-JLM-EDGE
👉 **איפה:** ‏R-JLM-EDGE ‏←‏ `configure terminal`.

כמו משימה 5, בתמונת מראה (ראו טבלה 1.7): העמית הוא **200.1.1.2** וה-ACL הפוכה.

⌨️ מקלידים:
```
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

---

## משימה 7 — מכניסים את ירושלים דרך ה-ASA + בודקים את ה-VPN בין האתרים

### 7א — החור ב-ASA
🧠 **למה:** החבילות של ירושלים יוצאות מהמנהרה ב-R-HFA-EDGE — בצד ה-**outside** של ה-ASA. ‏0 ‏←‏ 100
חסום, אלא אם מתירים.

👉 **איפה:** ‏ASA ‏←‏ `enable` ‏←‏ `Intel#En4ble`.

⌨️ מקלידים:
```
configure terminal
access-list OUTSIDE_IN extended permit ip 10.20.0.0 255.255.0.0 10.10.0.0 255.255.0.0
end
write memory
```
(‏10.10.0.0/16 כולל את ה-DMZ ‏10.10.200.0/24 — כך שירושלים מגיעה גם לרשת הפנימית **וגם** לשרתי
ה-DMZ.)

### 7ב — גורמים למנהרה לעלות
ההצפנה מתחילה רק כשתעבורה צריכה אותה. מ-**PC-JLM-SAL-01**: ‏`ping 10.10.16.1` — פינג אחד או שניים
ראשונים יכולים להיכשל בזמן שהמנהרה נבנית, ואז מגיעות תשובות. ✅
(זה ה-ping שנכשל במשימה 2!)

### 7ג — בנתבים
👉 **איפה:** ‏R-HFA-EDGE.

```
R-HFA-EDGE# show crypto isakmp sa
dst             src             state          conn-id status
200.2.1.2       200.1.1.2       QM_IDLE           1001 ACTIVE    <- phase 1 up with Jerusalem
R-HFA-EDGE# show crypto ipsec sa
    #pkts encaps: 57, #pkts encrypt: 57, ...        <- growing while you ping = encrypted
    #pkts decaps: 57, #pkts decrypt: 57, ...
R-HFA-EDGE# show ip route static                  <- S 10.20.0.0/16 via 172.16.12.2
```
ובנוסף ב-**CC1**: ‏`show ip route | include 10.10.0.0` ‏←‏ `D EX 10.10.0.0/16 via 10.20.4.1`.

❌ **אין `QM_IDLE`:** השוו את שני בלוקי `crypto isakmp policy 10` ואת המפתחות אות אחרי אות
(`show running-config | section crypto`).\
❌ **יש `QM_IDLE` אבל ה-ping נכשל:** השורה ב-ASA ‏(7א) או הנתיבים הסטטיים (משימה 4).

### 7ד — בדיקות

<div dir="rtl">

| ‎# | מאיפה | עושים | צפוי |
|---|---|---|---|
| ‎1 | ‎PC-JLM-SAL-01 | ‎`tracert 10.10.200.13` | 10.20.10.2 → 10.20.4.1 → **172.16.12.1** (המנהרה!) → … |
| ‎2 | ‎PC-JLM-SAL-01 | ‎‏Web Browser ‏←‏ `http://www.intel.lab` | ✅ גם ה-DNS ‏10.10.200.11 נגיש עכשיו |
| ‎3 | ‎PC-JLM-SAL-01 | ‎`nslookup ftp.intel.lab` | ‏10.10.200.15 (שירותי DMZ דרך VPN — דרישה 21) |
| ‎4 | ‎SWL3-JLM-CC1 | `show ntp status` (אחרי Fast Forward) | מסונכרן ל-10.10.200.14 (דרישה 20.8) |
| ‎5 | ‎PC-HFA-IT-01 | ‎`ssh -l admin 10.20.0.11` | ✅ ה-IT של המטה מנהל את ירושלים דרך ה-VPN |

</div>

---

## משימה 8 — רואים את ההצפנה במצב Simulation (איך? ‏←‏ M21)
1. לוחצים **Simulation** (למטה מימין) ‏←‏ **Edit Filters** ‏←‏ מסמנים **ICMP** (וגם ISAKMP/ESP אם יש).
2. מ-PC-JLM-SAL-01 עושים ping למחשב בחיפה.
3. לוחצים **Capture/Forward** צעד אחרי צעד. לוחצים על המעטפה של החבילה כשהיא על כבל **בין
   הספקים**.
4. מסתכלים על הכותרת החיצונית: ‎`200.2.1.2 → 200.1.1.2`, פרוטוקול **ESP**. הכתובות הפרטיות שבפנים
   לא נראות לספקים. 🔒
5. חוזרים ל-**Realtime**.

📝 צלמו את זה לספר (M22).

---

## משימה 9 — ‏R-HFA-EDGE כשרת VPN לגישה מרחוק
👉 **איפה:** ‏R-HFA-EDGE ‏←‏ `configure terminal`.

### 9א — מי רשאי להתחבר, ואילו כתובות הוא מקבל
⌨️ מקלידים:
```
aaa new-model
aaa authentication login default group tacacs+ local
aaa authentication login VPN-AUTH local
aaa authorization network VPN-GROUP local
username remote1 secret Intel#Remote1
ip local pool RA-POOL 172.16.250.10 172.16.250.100
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`aaa authentication login VPN-AUTH local` | משתמשי ה-VPN נבדקים מול המשתמשים המקומיים |
| ‎`ip local pool RA-POOL ...`‎ | כתובות לחלק למשתמשים מרוחקים |

</div>

### 9ב — שלב 1 ללקוחות, והקבוצה שהמחשב מתחבר אליה
⌨️ מקלידים:
```
crypto isakmp policy 20
 encryption aes 256
 hash sha
 authentication pre-share
 group 2
 exit
crypto isakmp client configuration group HQ-RA
 key Intel#RA-Group
 dns 10.10.200.11
 domain intel.lab
 pool RA-POOL
 exit
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`crypto isakmp client configuration group HQ-RA` | הקבוצה שלקוח ה-VPN מתחבר אליה (מפתח, ‏DNS, מאגר) |

</div>

### 9ג — שלב 2 ללקוחות, מתווסף לאותו crypto map
⌨️ מקלידים:
```
crypto ipsec transform-set RA-SET esp-aes 256 esp-sha-hmac
crypto dynamic-map RA-DYN 10
 set transform-set RA-SET
 reverse-route
 exit
crypto map VPN-MAP client authentication list VPN-AUTH
crypto map VPN-MAP isakmp authorization list VPN-GROUP
crypto map VPN-MAP client configuration address respond
crypto map VPN-MAP 65535 ipsec-isakmp dynamic RA-DYN
 end
copy running-config startup-config
```

<div dir="rtl">

| פקודה | בשפה פשוטה |
|---|---|
| ‎`crypto dynamic-map` + ‎`... 65535 ipsec-isakmp dynamic` | תבנית ללקוחות שאת הכתובת שלהם לא יודעים מראש |
| ‎`reverse-route` | מוסיף אוטומטית נתיב לכל לקוח שמתחבר |

</div>

<div dir="rtl">

> מספר **65535** = נבדק **אחרון**. ירושלים (מספר 10) חייבת להיבדק קודם.

</div>

### 9ד — ה-ASA: משתמשים מרוחקים רשאים להגיע למטה
👉 **איפה:** ‏ASA ‏←‏ `configure terminal`.

⌨️ מקלידים:
```
access-list OUTSIDE_IN extended permit ip 172.16.250.0 255.255.255.0 10.10.0.0 255.255.0.0
end
write memory
```
(רשימת ה-PAT ‏`NAT-HFA` משלב 12 כבר מדלגת על 172.16.250.0/24 — התכוננו לזה מראש.)

🔍 **בודקים עכשיו:** ב-R-JLM-EDGE עושים שוב ping למחשב בחיפה ‏←‏ עדיין עובד. הוספת גישה מרחוק אסור
שתשבור את ה-VPN בין האתרים.

---

## משימה 10 — לקוח ה-VPN של העובד מהבית
👉 **איפה:** ‏**PC-HOME-01** ‏←‏ **Desktop** ‏←‏ **VPN**.

1. ממלאים:

<div dir="rtl">

| שדה | ערך |
|---|---|
| ‎GroupName | ‎`HQ-RA` |
| ‎Group Key | ‎`Intel#RA-Group` |
| ‎Host IP (Server IP) | ‎`200.1.1.2` |
| ‎Username | ‎`remote1` |
| ‎Password | ‎`Intel#Remote1` |

</div>

2. לוחצים **Connect**.

✅ **אמורים לראות:** אחרי רגע, **"VPN is connected"**.

3. סוגרים את חלון ה-VPN ‏←‏ **Command Prompt** ‏←‏ `ipconfig` ‏←‏ רואים כתובת נוספת
   ‏‎`172.16.250.x` (כתובת המנהרה).

❌ **‏"authentication failed":** שגיאת כתיב בשם / במפתח של הקבוצה או במשתמש / בסיסמה; או שחסרה
השורה `aaa authorization network VPN-GROUP local`.

---

## משימה 11 — בדיקות סופיות ושמירה

<div dir="rtl">

| ‎# | מאיפה | עושים | צפוי |
|---|---|---|---|
| ‎1 | PC-HOME-01 ‏(VPN מחובר) | ‎`ping 10.10.1.10` | ‎✅ |
| ‎2 | PC-HOME-01 ‏(VPN מחובר) | ‎‏Web Browser ‏←‏ `http://www.intel.lab` | ‎✅ |
| ‎3 | ‎R-HFA-EDGE | ‎`show crypto isakmp sa` | שתי שורות `QM_IDLE`: ירושלים **וגם** ‎`200.3.50.10` (העובד מהבית) |
| ‎4 | ‎PC-HOME-01 | ‏VPN ‏←‏ **Disconnect**, ואז `ping 10.10.1.10` | ‎❌ |

</div>

💾 ‏`copy running-config startup-config` בשני נתבי הקצה, ‏`write memory` ב-ASA ‏←‏ **File → Save**.

---

## נקודת ביקורת
- [ ] ‏`QM_IDLE` מול ירושלים; מוני ה-encaps/decaps גדלים
- [ ] המחשבים בירושלים מגיעים לכתובות הפרטיות של חיפה ולשרתי ה-DMZ לפי שם
- [ ] ה-NTP של ירושלים מסונכרן לחיפה
- [ ] העובד מהבית מתחבר ומגיע לשרתי המטה

## אם משהו לא עובד

<div dir="rtl">

| בעיה | פתרון |
|---|---|
| פקודות `crypto` לא קיימות | הרישיון לא פעיל — משימה 3 ו-**reload** |
| שלב 1 אף פעם לא עולה (אין `QM_IDLE`) | אי-התאמה ב-policy (ההצפנה / ה-hash / ה-group חייבים להיות זהים בשני הצדדים) או מפתחות שונים |
| המנהרה למעלה, הפינגים נכשלים | חסר הנתיב הסטטי לתוך המנהרה; חסרה ב-ASA שורת ה-ACL ל-10.20.0.0/16 |
| ה-ACL של ירושלים חוסמת את ה-VPN | ‏WAN-IN חייבת להתיר isakmp, ‏esp **וגם** gre מ-200.1.1.2 |
| העמית ב-S2S מבקש שם משתמש / נשבר אחרי שהוספנו גישה מרחוק | חסר `no-xauth` בשורת `crypto isakmp key` |
| לקוח ה-VPN: ‏"authentication failed" | שגיאת כתיב בשם / במפתח של הקבוצה או במשתמש / בסיסמה; חסר `aaa authorization network VPN-GROUP local` |
| הלקוח מתחבר אבל לא מגיע למטה | חסרה ב-ASA ה-ACL ל-172.16.250.0/24 |

</div>

---

## 🏋 תרגילים

### תרגיל א — מפתח שגוי ⭐⭐
- 🎯 **המשימה:** לראות איך נראית אי-התאמה במפתח המשותף.
- 📁 **מתחילים מ:** ‏`step15.pkt` ‏←‏ **Save As** ‏`step15-exA.pkt`.
- 👣 **צעדים:**
  1. ב-R-JLM-EDGE: ‏`configure terminal` ‏←‏
     ‏`no crypto isakmp key Intel#S2S-Key address 200.1.1.2` ‏←‏
     ‏`crypto isakmp key WrongKey address 200.1.1.2 no-xauth` ‏←‏ `end` ‏←‏ `clear crypto isakmp`.
  2. מ-PC-JLM-SAL-01: ‏`ping 10.10.16.1`.
  3. ‏`show crypto isakmp sa` בשני נתבי הקצה.
- ✅ **גמרתם כש**אתם יודעים לומר איזה שלב נכשל ואיך אתם יודעים.

<details dir="rtl"><summary>💡 רמז</summary>

שלב 1 בודק זהות בעזרת המפתח. הסתכלו על העמודה `state`.
</details>
<details dir="rtl"><summary>✔ תשובה</summary>

הפינגים נכשלים. אין `QM_IDLE` — המצב נשאר משהו כמו `MM_NO_STATE` / ‏`MM_KEY_EXCH`, או שהשורה
נעלמת. שלב 1 (בדיקת הזהות) נכשל כי המפתחות שונים, ולכן שלב 2 אף פעם לא מתחיל ושום דבר לא מוצפן.
לשני הצדדים חייב להיות **אותו** מפתח.
</details>

### תרגיל ב — במה קריית גת עדיין יכולה להשתמש? ⭐⭐⭐
- 🎯 **המשימה:** לקריית גת אין VPN. בלי להוסיף אחד, באילו שירותי DMZ קריית גת עדיין יכולה להשתמש,
  ואיך?
- 📁 **מתחילים מ:** ‏`step15.pkt` שלכם (לא משנים כלום).
- 👣 **צעדים:** לכל שירות DMZ ‏(DNS, דואר, ‏web, ‏NTP, ‏FTP, ‏AAA) שואלים: האם הוא מפורסם באינטרנט
  (שלב 12)? האם קריית גת יכולה להגיע אליו עם גרסת ה-IP שיש לה (שלב 14)? בודקים מה שאפשר.
- ✅ **גמרתם כש**יש לכם טבלה של 6 שורות: שירות / כן או לא / למה.
<details dir="rtl"><summary>✔ תשובה</summary>

רק במה שמפורסם באינטרנט **וגם** נגיש ב-IPv4 מקריית גת:
- **‏NTP** — ל-DIST1 יש דרך IPv4 (קישור ה-legacy + ‏PAT) והוא מסתנכרן לכתובת הציבורית 200.1.10.4 ‏←‏
  דרישה 20.8 מתקיימת.
- **‏Web** — רק מכשירי ה-IPv4 מדור קודם יכולים לפתוח את 200.1.10.3; משתמשי IPv6 לא (תרגיל א של שלב 14).
- דואר / ‏DNS / ‏FTP / ‏AAA לא מפורסמים ‏←‏ לא. בגלל זה לקריית גת יש שרתי DNS, דואר, ‏syslog ו-AAA
  **משלה**. פתרון אמיתי יהיה מנהרה שלישית על IPv6 או DMZ ‏dual-stack — כתבו את הפשרה בספר הפרויקט.
</details>

---

## 🛠 הפרויקט שלכם

עשיתם את השלב הזה על הדוגמה של אינטל. עכשיו עשו אותו שוב בפרויקט **שלכם**, עם הערכים
מהתוכנית **שלכם** (`my-project/plan.md`). הפקודות זהות — רק הערכים משתנים.

- [ ] פותחים את `my-project/step14.pkt` ‏←‏ **Save As** ‏`my-project/step15.pkt`
- [ ] ממלאים טבלת "מראות" משלכם כמו 1.7
- [ ] רישיון + אתחול בשני נתבי הקצה
- [ ] מנהרת GRE + נתיבים; ‏ping דרך המנהרה
- [ ] ‏IPsec בשני הצדדים; חורים בחומת האש; ‏`QM_IDLE` ומונים שגדלים
- [ ] שרת גישה מרחוק + לקוח ה-VPN של המחשב הביתי

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
- **שיעור 3:** גישה מרחוק ‏←‏ לקוח VPN ‏←‏ בדיקות ‏←‏ תרגילים.
- **שאלות נפוצות של תלמידים**
  - *"למה הפינג הראשון הולך לאיבוד?"* — המנהרה נבנית לפי דרישה (שלב 1 + 2 לוקחים רגע).
  - *"למה מספר 65535 ל-dynamic map?"* — עמיתים מוגדרים (ירושלים, מספר 10) חייבים להיבדק קודם; התבנית
    של "כל אחד" חייבת להיות אחרונה.
- **טעויות אופייניות:** שכחת האתחול אחרי הרישיון; ‏ISAKMP policy שלא תואם; שכחת שורות ה-ACL ב-ASA.
