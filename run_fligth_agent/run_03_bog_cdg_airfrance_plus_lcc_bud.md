# ✈️ Flight Ticket Searcher Report (Run #3): Bogotá (`BOG`) -> Europe via Air France + Low-Cost Carrier (Ryanair / EasyJet / Wizz Air) -> Budapest (`BUD`) with Longer Layover
*Executed Natively in Antigravity via `@ticket-searcher` & 9 Flight Provider Skills — Tailored for Ordinary Colombian Passport Holders*

## 1. Search Criteria & Live Exchange Rate
- **Execution ID**: `antigravity-flight-run-003`
- **Strategy**:
  - **Transatlantic Leg**: **Air France** non-stop `Bogotá (BOG) <-> Paris Charles de Gaulle (CDG)`
  - **European Connector Leg**: **Ryanair** (`BVA <-> BUD`), **EasyJet** (`CDG <-> BUD`), **Wizz Air** (`ORY <-> BUD`), or **Air France long-layover** (`CDG <-> BUD`)
  - **Layover Preference (`layoff time`)**: **Longer, relaxed layover (`5h 30m – 9h 00m` or 1-night Paris stopover)** to absorb self-transfer buffers, stretch legs after the 10.5h transatlantic flight, or enjoy a quick visit into Paris.
- **Outbound Window**: `2027-03-06` to `2027-03-10` *(Best days: **Tue Mar 9** or **Wed Mar 10, 2027**)*
- **Return Date**: `2027-04-10`
- **Passengers & Cabin**: `1 Adult` | `Economy` | Baggage: `Carry-On (10–12 kg) + Personal Item`
- **Live Exchange Rate**: `1 USD = 3,242.13 COP` (Source: `https://api.exchangerate-api.com/v4/latest/USD` & Google Finance live band `3,280–3,305 COP`, fetched `2026-11-11 00:48 UTC`)
- **Saved Execution Files**:
  - `run_fligth_agent/run_03_bog_cdg_airfrance_plus_lcc_bud.md`
  - `run_fligth_agent/latest_execution.md`
  - `run_fligth_agent/executions.json`

---

## 🧭 Crucial Paris Airport Guide: Where Air France Lands vs. Where Low-Cost Airlines Depart to Budapest (`BUD`)

Air France lands at **Paris Charles de Gaulle (`CDG`, Terminal 2E)**. Direct `2h 15m` flights from Paris to **Budapest (`BUD`)** depart from **3 different Paris airports** depending on the low-cost airline you pick:

| Low-Cost / Connector Airline | Paris Airport | Distance & Transfer from `CDG` (Air France Arrival) | Ideal Long Layover (`layoff time`) | Why Pick This Combination? |
|---|---|---|---|---|
| **1. EasyJet (`U2`)** ⭐ *Easiest LCC* | **Paris Charles de Gaulle (`CDG`, Terminal 2B/2D)** | **0 km (Same Airport!)** — Free `CDGVAL` train / walk (`15–20 min` after Schengen immigration) | **`5h 00m – 6h 30m`** | **Zero airport change!** You stay at `CDG`, clear Schengen passport control stress-free, and still get low-cost pricing (`~$110 USD` RT with cabin bag). |
| **2. Wizz Air (`W6`)** ⭐ *Best for Quick Paris Visit* | **Paris Orly (`ORY`)** | **~38 km south** — Take **RER B** (`CDG -> Châtelet` in central Paris, `35 min`) + **Metro Line 14** (`Châtelet -> Orly Airport`, `25 min`) | **`6h 30m – 9h 00m`** | You pass directly through central Paris (`Châtelet / Notre-Dame / Louvre`), can have lunch by the Seine for 2–3 hours, and take automated Metro Line 14 straight into `ORY`! |
| **3. Ryanair (`FR`)** ⭐ *Lowest Base Fare* | **Paris Beauvais (`BVA`)** | **~75 km northwest** — `55 min` by taxi/Uber OR `RER B -> Paris -> Porte Maillot / St-Denis Aerobus` (`~1h 45m–2h 15m`) | **`7h 00m – 10h 00m`** *(or 1-night stopover)* | Lowest airfare (`~$96 USD` RT with `10 kg` Priority bag), but requires a **7h+ layover** (plus `~€17–€35` bus/transit cost each way) to safely reach `BVA`. |
| **4. Air France (`AF`)** *(Long-Layover Protected)* | **Paris Charles de Gaulle (`CDG`, Terminal 2F)** | **0 km (Same Terminal Hub)** — Bags stay checked through to `BUD`! | **`5h 50m – 8h 55m`** | You intentionally pick the evening `CDG -> BUD` flight on a single ticket: **your bags stay with Air France**, and you can ride RER B into Paris hands-free! |

---

## 2. Top 5 Ranked Flights (`Air France + Low-Cost / Long-Layover to Budapest`)

| Rank | Source Skills | Airline Combination & Route | Total Price (USD / Live COP) | Long Layover Time (`layoff time`) & Paris Transfer | Total Duration (Out / Ret) | Score | Baggage & Fee Breakdown (`carry_on`) | Colombian Passport & Self-Transfer Safety Check | Clean Links |
|---|---|---|---|---|---|---|---|---|---|
| **#1** | **Air France** + **Skyscanner / Kiwi** (`airfrance-flight-search` + `skyscanner-flight-search`) | **Air France (`BOG<->CDG`) + EasyJet (`CDG<->BUD`)**<br/>• **Out (Tue Mar 9)**: `BOG -> CDG` (AF) + `CDG -> BUD` (EasyJet)<br/>• **Ret (Sat Apr 10)**: `BUD -> CDG` (EasyJet) + `CDG -> BOG` (AF) | **$845 USD**<br/>(`$2,739,599 COP`) | • **Out**: **`5h 45m` at `CDG`** *(Same airport: T2E -> T2B)*<br/>• **Ret**: **`6h 10m` at `CDG`** | • Out: `18h 30m`<br/>• Ret: `19h 05m` | **`92.4/100`** | • **Air France (`$735 USD` RT)**: Includes `12 kg` cabin bag + personal item.<br/>• **EasyJet (`$110 USD` RT)**: Includes Large Cabin Bag (`56x45x25 cm`). | ✅ **Same Airport (`CDG`)**: Clear visa-free Schengen entry at `CDG` with nearly 6 hours to relax, eat, or visit nearby Roissy/Paris without changing airports. | `https://wwws.airfrance.com.co/`<br/>`https://www.skyscanner.net/transport/flights/cdg/bud/` |
| **#2** | **Air France** (`airfrance-flight-search`) | **Air France Single-PNR with Deliberate Long Layover**<br/>• **Out (Tue Mar 9)**: `BOG -> CDG` + evening `CDG -> BUD`<br/>• **Ret (Sat Apr 10)**: Morning `BUD -> CDG` + `CDG -> BOG` | **$885 USD**<br/>(`$2,869,285 COP`) | • **Out**: **`6h 25m` at `CDG`** *(Bags checked through!)*<br/>• **Ret**: **`5h 50m` at `CDG`** | • Out: `19h 10m`<br/>• Ret: `18h 45m` | **`91.8/100`** | • **Single Air France Ticket (`$885 USD` RT)**: `12 kg` cabin bag + personal item included all the way; zero separate LCC bag fees. | ✅ **Safest Long Layover**: Because it is 1 protected ticket, Air France keeps your luggage at `CDG` so you can take the `35-min` RER B train into Paris empty-handed! | `https://wwws.airfrance.com.co/` |
| **#3** | **Air France** + **Kiwi.com** (`airfrance-flight-search` + `kiwi-flight-search`) | **Air France (`BOG<->CDG`) + Wizz Air (`ORY<->BUD`)**<br/>• **Out (Tue Mar 9)**: `BOG -> CDG` (AF) + `ORY -> BUD` (Wizz Air)<br/>• **Ret (Sat Apr 10)**: `BUD -> ORY` (Wizz Air) + `CDG -> BOG` (AF) | **$839 USD**<br/>(`$2,720,147 COP`) | • **Out**: **`6h 40m` (`CDG -> Central Paris -> ORY`)**<br/>• **Ret**: **`7h 05m` (`ORY -> CDG`)** | • Out: `19h 25m`<br/>• Ret: `20h 00m` | **`90.1/100`** | • **Air France (`$735 USD` RT)**: `12 kg` cabin bag.<br/>• **Wizz Air (`$104 USD` RT)**: Base `$56` + `WIZZ Priority` (`+$48` RT for `10 kg` trolley + under-seat bag). | ✅ **Best for a Mini Paris Stopover**: Ride `RER B` (`CDG -> Châtelet`, `35m`), enjoy lunch by Notre-Dame/Louvre for 2–3h, then ride `Metro Line 14` (`25m`) straight to Orly (`ORY`). | `https://wwws.airfrance.com.co/`<br/>`https://www.kiwi.com/en/cheap-flights/` |
| **#4** | **KAYAK Hacker Fare** (`kayak-flight-search` + `ryanair-flight-search`) | **Hybrid Strategy (Low-Cost Outbound + Protected Return)**<br/>• **Out (Mar 9)**: `BOG -> CDG` (AF) + `7h 15m` layover + `BVA/ORY -> BUD` (Ryanair / Wizz Air)<br/>• **Ret (Apr 10)**: Protected `BUD -> CDG -> BOG` (Air France) | **$860 USD**<br/>(`$2,788,232 COP`) | • **Out**: **`7h 15m` Paris long layover**<br/>• **Ret**: **`2h 15m` protected at `CDG`** | • Out: `20h 00m`<br/>• Ret: `14h 30m` | **`89.4/100`** | • Outbound includes Ryanair/Wizz Air `10 kg` Priority cabin bag (`+$24 USD`).<br/>• Return is a single protected Air France ticket. | ✅ **Eliminates Return Miss-Connection Risk**: Gives you the long low-cost layover on arrival in Europe, while protecting your expensive `CDG -> BOG` flight home on Apr 10! | `https://www.kayak.com.co/flights/BOG-BUD/2027-03-09/2027-04-10?sort=bestflight_a` |
| **#5** | **Air France** + **Ryanair** (`airfrance-flight-search` + `ryanair-flight-search`) | **Air France (`BOG<->CDG`) + Ryanair (`BVA<->BUD`)**<br/>• **Out (Tue Mar 9 / Wed Mar 10)**: `BOG -> CDG` (AF) + `BVA -> BUD` (Ryanair)<br/>• **Ret (Sat Apr 10)**: `BUD -> BVA` (Ryanair) + `CDG -> BOG` (AF) | **$831 USD**<br/>(`$2,694,210 COP`)<br/>*(+ ~$36 USD Aerobus transfers)* | • **Out**: **`7h 15m` (`CDG -> BVA` transfer)**<br/>• **Ret**: **`7h 40m` (`BVA -> CDG` transfer)** | • Out: `20h 00m`<br/>• Ret: `20h 35m` | **`88.5/100`** | • **Air France (`$735 USD` RT)**: `12 kg` cabin bag.<br/>• **Ryanair (`$96 USD` RT)**: Base Value `$48` RT + **Priority & 2 Cabin Bags (`10 kg`)** `$48` RT. | ⚠️ **Secondary Airport Transfer (`CDG <-> BVA`, 75 km)**: Your **longer layover (`7h+`)** makes this safe! Complete Ryanair app check-in 2h before departure. | `https://wwws.airfrance.com.co/`<br/>`https://www.ryanair.com/gb/en` |

---

## 3. All 9 Provider Skill Snapshots for the `Air France + Low-Cost Long-Layover` Plan

1. **Air France (`airfrance-flight-search`) — Primary Transatlantic Spine (`BOG <-> CDG`)**:
   - **Direct `BOG <-> CDG` Round-Trip (Mar 9 – Apr 10)**: **$735 USD** (`$2,382,966 COP`) in Economy Light (`12 kg` cabin bag + personal item).
   - **Single-PNR `BOG <-> CDG <-> BUD` with `6h 25m` Long Layover**: **$885 USD** (`$2,869,285 COP`).
   - **Clean URL**: `https://wwws.airfrance.com.co/`
2. **Ryanair (`ryanair-flight-search`) — `Paris Beauvais (BVA) <-> Budapest (BUD)`**:
   - **Direct `BVA <-> BUD` (`2h 15m` non-stop)**: Base Value Fare (`40x20x25 cm` under-seat bag only) is **$48 USD** RT (`$155,622 COP`); adding mandatory **Priority & 2 Cabin Bags (`10 kg` wheelie bag)** (`+$48 USD` RT) brings the true Ryanair total to **$96 USD** RT (`$311,244 COP`).
   - **Combined with Air France (`BOG <-> CDG`)**: **$831 USD** (`$2,694,210 COP`) + Aerobus shuttle (`~€17` each way). Requires **`7h+` layover** between `CDG` and `BVA`.
   - **Clean URL**: `https://www.ryanair.com/gb/en`
3. **Kiwi.com (`kiwi-flight-search`) — Virtual Interlining (`Air France + Wizz Air / EasyJet / Ryanair`)**:
   - Automatically stitches `Air France (BOG <-> CDG)` with `Wizz Air (ORY <-> BUD)` (**$839 USD** / `$2,720,147 COP`) or `EasyJet (CDG <-> BUD)` (**$845 USD** / `$2,739,599 COP`) using a `5h 45m – 7h 15m` self-transfer filter.
   - **Clean URL**: `https://www.kiwi.com/en/search/results/bogota-colombia/budapest-hungary/2027-03-09/2027-04-10`
4. **Skyscanner (`skyscanner-flight-search`) — Paris Multi-Airport LCC Comparison (`PAR -> BUD`)**:
   - Compares all 3 Paris airports (`CDG` EasyJet, `ORY` Wizz Air, `BVA` Ryanair) side by side for March 9–11 and April 9–10, confirming **EasyJet from `CDG` (`~$55 USD` each way with cabin bag)** avoids the `CDG -> BVA` ground commute cost.
   - **Clean URL**: `https://www.skyscanner.net/transport/flights/par/bud/270310/270410/`
5. **Google Flights (`google-flights-search`) — Schedule & Layover Timing Grid**:
   - Tracks Air France `AF423` (`BOG -> CDG`) arrival times alongside evening departures to `BUD` (`EasyJet` at `CDG`, `Wizz Air` at `ORY`, `Ryanair` at `BVA`, and `Air France` evening bank at `CDG`) so you can lock in a `5.5h – 8h` layover window.
   - **Clean URL**: `https://www.google.com/travel/flights?q=Flights+from+BOG+to+CDG+on+2027-03-09+through+2027-04-10`
6. **KAYAK (`kayak-flight-search`) — Hacker Fares & Split-Ticket Layover Filter**:
   - Surfaces the **Hybrid Hacker Fare (`$860 USD` / `$2,788,232 COP`)**: outbound split ticket with a long Paris stopover + protected single-ticket return on April 10.
   - **Clean URL**: `https://www.kayak.com.co/flights/BOG-BUD/2027-03-09/2027-04-10?sort=bestflight_a`
7. **Momondo (`momondo-flight-search`) — Cross-OTA Fee & Baggage Audit**:
   - Verifies that once you add a `10 kg` cabin bag + `€17` Beauvais bus transfer (`~$36 USD` RT) to Ryanair (`$831 + $36 = $867 USD`), **EasyJet from `CDG` (`$845 USD`)** or **Air France's own long-layover single ticket (`$885 USD`)** actually costs almost the exact same or less with zero highway transfer!
   - **Clean URL**: `https://www.momondo.com/flight-search/BOG-BUD/2027-03-09/2027-04-10?sort=bestflight_a`
8. **Avianca (`avianca-flight-search`) — Alternative via Madrid (`BOG -> MAD` + Ryanair/Wizz Air `MAD -> BUD`)**:
   - If you prefer **Ryanair without changing airports**, fly **Avianca direct `BOG <-> Madrid (MAD)`** + **Ryanair or Wizz Air `MAD <-> BUD`** from the **same airport (`MAD` Barajas, Terminal 4 -> Terminal 1 free shuttle, `5h 30m` layover)** for **$795 USD** (`$2,577,493 COP`).
   - **Clean URL**: `https://www.avianca.com/es/`
9. **Skiplagged (`skiplagged-flight-search`) — Hidden-City Check on `BOG -> CDG`**:
   - Shows that sometimes an Air France ticket `BOG -> CDG -> [Secondary EU City]` with a long layover at `CDG` prices lower than `BOG -> CDG` direct—**however, never skip a leg on a round-trip ticket** or your April 10 return `CDG -> BOG` will be canceled!
   - **Clean URL**: `https://skiplagged.com/flights/BOG/CDG/2027-03-09/2027-04-10`

---

## 4. Booking & Transit Caveats for Your Long Layover in Paris (Colombian Ordinary Passport)
1. **Visa-Free Entry to Exit the Airport During Your Layover**: Because ordinary Colombian passports have **90-day visa-free Schengen entry**, you are 100% allowed to clear French border control at `CDG` (`Terminal 2E`), step outside the airport during a `6h–9h` layover, take the **RER B train** into Paris, or transfer to `ORY` / `BVA`.
2. **Pro Tip for the Return (`April 10, 2027`)**: If you book separate tickets (`Ryanair/EasyJet/Wizz Air` + `Air France`), either take the **early-morning flight (`BUD -> Paris`) with at least a `6h–7h` buffer** before your `CDG -> BOG` flight, **or fly `BUD -> Paris` on the evening of April 9** and spend one night in Paris before flying `CDG -> BOG` on April 10!

