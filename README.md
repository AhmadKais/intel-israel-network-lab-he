# אינטל ישראל — מעבדת רשת ארגונית (Cisco Packet Tracer)

פרויקט גמר שלומדים תוך כדי בנייה, למגמת הנדסאי תקשוב של משרד החינוך
(**שאלון 735918 — פרויקט גמר הנדסאים, רשתות תקשורת**).

תבנו ב-Cisco Packet Tracer רשת ארגונית של 3 סניפים עבור **אינטל ישראל**, מיני-פרויקט
אחד בכל פעם. כל שלב מסביר *למה*, נותן את המכשירים, הכבלים והפקודות המדויקים, מראה איך
**לבדוק** שהכול עובד, ומסתיים ב**אתגר** שפותרים לבד.

> **גרסה זו בעברית כוללת את שלושת הפרקים הראשונים בלבד (שלבים 00–02).**
> שאר השלבים יתורגמו בהמשך. עד אז הם זמינים בגרסה האנגלית (`intel-israel-network-lab`).
> בשתי הגרסאות אותם מכשירים, פורטים, כתובות וסיסמאות — אפשר לעבור ביניהן בכל שלב.

> **כלל אצבע:** **הקלידו את הפקודות, אל תדביקו אותן** — לפחות בפעם הראשונה שאתם פוגשים
> פקודה חדשה. ההקלדה היא מה שמלמד את האצבעות את IOS. הדביקו רק פקודות שכבר הקלדתם בעבר.

> **חשוב:** כל הפקודות, שמות המכשירים, הכתובות והסיסמאות נכתבים **באנגלית, בדיוק כפי שהם
> מופיעים כאן** — כולל אותיות גדולות וקטנות. לפני שאתם מקלידים ב-Packet Tracer, ודאו
> שהמקלדת על **אנגלית** (Alt+Shift או Win+רווח).

---

## החברה

| קוד | עיר | תפקיד | סגנון תכנון |
|---|---|---|---|
| **HFA** | חיפה (מת"ם) | **סניף ראשי (מטה)** — DMZ, חומת אש, רשת אלחוטית | 3 שכבות: access / distribution / core, ‏3 בניינים |
| **JLM** | ירושלים | סניף | **Collapsed core** על מתגי שכבה 3, ‏3 קומות |
| **KG** | קריית גת | סניף (מפעל) | רשת פנימית ב-**IPv6 בלבד**, תלת-שכבתי קומפקטי |

```mermaid
flowchart LR
  subgraph WAN["WAN / Internet — BGP between 3 ISPs, OSPF inside each ISP"]
    A["ISP-A<br/>AS 100"] --- B["ISP-B<br/>AS 200"]
    A --- C["ISP-C<br/>AS 300"]
    B --- C
  end
  HFA["HAIFA HQ<br/>OSPF multi-area + virtual link<br/>ASA + DMZ · WiFi · Static NAT"] --- A
  HFA -. "DSL backup" .- B
  JLM["JERUSALEM<br/>Collapsed core · EIGRP<br/>Dynamic NAT · CBAC"] --- B
  KG["KIRYAT GAT<br/>IPv6 · OSPFv3<br/>PAT (overload)"] --- C
  HFA <== "GRE over IPsec site-to-site VPN" ==> JLM
  HOME["Home worker"] --- C
  HOME -. "Remote-access VPN" .-> HFA
```

## מפת הדרכים — 17 מיני-פרויקטים

עבדו **לפי הסדר**. כל שלב מסתיים בקובץ `.pkt` שעובד ונשמר.

| # | שלב | מה לומדים | זמן |
|---|---|---|---|
| 00 | [מתחילים](steps/00-getting-started) | Packet Tracer, מצבי ה-CLI, איך עובדים עם המדריך | 2 שיעורים |
| 01 | [מתכננים את הרשת](steps/01-plan-the-network) | תכנון כתובות IP, טבלאות VLAN, שמות — **קודם על נייר** | 2 שיעורים |
| 02 | [המתג הראשון ו-VLANים](steps/02-first-switch-vlans) | הקשחה בסיסית, VLANים, פורטי access | 1–2 שיעורים |
| 03 | Trunks ו-VTP | ‏802.1Q trunks, ‏native VLAN, ‏VTP | *טרם תורגם* |
| 04 | EtherChannel ו-STP | ‏LACP, ‏Rapid-PVST+, ‏root bridge, ‏PortFast, ‏BPDU/Root guard | *טרם תורגם* |
| 05 | Inter-VLAN, ‏HSRP, ‏DHCP | ‏SVI, יתירות שער, DHCP על מתג שכבה 3 | *טרם תורגם* |
| 06 | אבטחת שכבה 2 | ‏Port-security, ‏DHCP snooping, הקשחה | *טרם תורגם* |
| 07 | ניהול ב-SSH | ‏VLAN ניהול, ‏SSH, ‏ACL על VTY | *טרם תורגם* |
| 08 | Core, ‏OSPF, שרתים | קישורים מנותבים, אזורי OSPF, ‏MD5, ‏AAA/TACACS+, ‏Syslog | *טרם תורגם* |
| 09 | בניינים B ו-C + virtual link | **אתם** בונים 2 בניינים; OSPF virtual link, סיכום נתיבים | *טרם תורגם* |
| 10 | רשת אלחוטית | WiFi לעובדים ולאורחים, ACL לבידוד אורחים | *טרם תורגם* |
| 11 | חומת אש ASA ו-DMZ | ‏inside/outside/DMZ, ‏security levels, ‏ACL, ‏6 שרתי DMZ, ‏NTP | *טרם תורגם* |
| 12 | ‏WAN: ספקים, BGP, ‏NAT | ‏eBGP, ‏OSPF בתוך AS, ‏static NAT + PAT, גיבוי DSL | *טרם תורגם* |
| 13 | ירושלים — collapsed core | ‏EIGRP + סיכום + אימות, ‏PAgP, שרת DHCP, ‏dynamic NAT, ‏CBAC | *טרם תורגם* |
| 14 | קריית גת — IPv6 | כתובות IPv6, ‏SLAAC + DHCPv6, ‏OSPFv3, ‏HSRPv6, ‏PAT | *טרם תורגם* |
| 15 | ‏VPN | ‏GRE over IPsec בין אתרים, VPN לגישה מרחוק | *טרם תורגם* |
| 16 | אינטגרציה סופית | חשבונות דואר, הרחבה ל-8 מחשבים למחלקה, תוכנית בדיקות מלאה, ספר הפרויקט | *טרם תורגם* |

## מסמכי עזר

- [docs/design.md](docs/design.md) — תוכנית הכתובות, ה-VLANים והשמות המלאה ("מקור האמת" שלכם)
- [docs/passwords.md](docs/passwords.md) — טבלת הסיסמאות (נדרשת גם בספר הפרויקט)

## איך בנוי כל שלב

1. **מטרה** — מה עובד בסוף השלב
2. **מבינים קודם** — התאוריה שצריך, בקצרה ובשפה פשוטה
3. **בונים** — אילו מכשירים לגרור, וטבלת כבלים
4. **מגדירים** — הפקודות, עם הסבר לכל שורה
5. **בודקים** — פקודות `show` ו-`ping`, ואיך נראית תוצאה תקינה
6. **נקודת ביקורת** — שמירה בשם `my-work/stepNN.pkt`
7. **אם משהו לא עובד** — טעויות נפוצות ואיך מתקנים
8. **אתגר** — פותרים לבד; התשובה מוסתרת בבלוק שנפתח בלחיצה

## שמירת ההתקדמות עם git (לא חובה)

```bash
git clone <this repo>
cd intel-israel-network-lab-he
# after each step:
git add my-work/step02.pkt
git commit -m "Step 02 done"
git push
```

נכתב עבור Packet Tracer **8.2.x** (מתאים גם לגרסה 9). הפקודות נכתבו לפי תחביר IOS 15
כפי ש-Packet Tracer מממש אותו.
