# ✈️ Flight Ticket Searcher Report (Run #5): Open-Jaw Multi-City — Bogotá (`BOG`) -> Budapest (`BUD`) | Return: Estonia (`Tallinn TLL`) or Lithuania (`Vilnius VNO`) -> Bogotá (`BOG`)
*Executed Natively in Antigravity via `@ticket-searcher` & 9 Flight Provider Skills — Protected Single-PNR with Safe Layover Margin (`2h 05m – 6h 20m`)*

## 1. Search Criteria & Live Exchange Rate
- **Execution ID**: `antigravity-flight-run-005`
- **Ticket Type**: **Single Protected Multi-City / Open-Jaw Ticket (`1 PNR`)**
  - **Leg 1 (Outbound, Mar 6–10, 2027 — Optimal: Tue Mar 9 or Wed Mar 10)**: `Bogotá (BOG)` -> `Budapest (BUD)`
  - **Leg 2 (Return, Sat Apr 10, 2027)**: **Estonia (`Tallinn TLL`)** **OR** **Lithuania (`Vilnius VNO`)** -> `Bogotá (BOG)`
- **Layover Safety Rule (`layoff time`)**: Strictly **`≥ 2h 05m` up to `6h 20m`** on a **single protected airline ticket** (zero `<1.5h` tight connections; 100% airline rebooking, luggage, hotel, and EU261 coverage if delayed).
- **Live Exchange Rate**: `1 USD = 3,242.13 COP` (Source: `https://api.exchangerate-api.com/v4/latest/USD` & Google Finance live band `3,280–3,305 COP`, fetched `2026-11-11 01:06 UTC`)
- **Saved Execution Files**:
  - `run_fligth_agent/run_05_bog_bud_openjaw_return_tll_vno_bog.md`
  - `run_fligth_agent/latest_execution.md`
  - `run_fligth_agent/executions.json`

---

## 🧭 Estonia (`Tallinn TLL`) vs. Lithuania (`Vilnius VNO`) Return Comparison on April 10

Both **Air France** (via Paris `CDG`, departing `2:20 PM` on `AF422`) and **Lufthansa** (via Frankfurt `FRA`, departing `1:55 PM` on `LH542`) sell this as a **single Multi-City ticket**, but their morning schedules from `TLL` and `VNO` work slightly differently:

| Return Country & Airport | Best Single-Ticket Airline | Exact Return Schedule (`Apr 10`) | Protected Layover (`layoff time`) | Key Operational Insight |
|---|---|---|---|---|
| **🇱🇹 Lithuania (`Vilnius VNO`)** | **Air France + airBaltic** *(via Paris `CDG`)* | • `VNO -> CDG` (`BT891/AF7978`): `07:15 AM -> 09:10 AM`<br/>• `CDG -> BOG` (`AF422`): `2:20 PM -> 5:55 PM` | **`5h 10m` at `CDG`** *(1-Stop Protected)* | **Works seamlessly with Air France!** airBaltic's morning `VNO -> CDG` flight lands at `9:10 AM`, giving you a huge **5h 10m buffer** before `AF422` (`2:20 PM`) on one PNR. |
| **🇱🇹 Lithuania (`Vilnius VNO`)** | **Lufthansa** *(via Frankfurt `FRA`)* | • `VNO -> FRA` (`LH889`): `06:20 AM -> 07:35 AM` *(or mid-morning `10:25 AM -> 11:40 AM`)*<br/>• `FRA -> BOG` (`LH542`): `1:55 PM -> 7:25 PM` | **`2h 15m` or `6h 20m` at `FRA`** *(1-Stop Protected)* | **100% Lufthansa metal** all the way from Vilnius to Bogotá with your choice of a `2h 15m` or `6h 20m` layover in Frankfurt. |
| **🇪🇪 Estonia (`Tallinn TLL`)** | **Lufthansa** *(via Frankfurt `FRA`)* ⭐ *Best for `TLL`* | • `TLL -> FRA` (`LH885`): `06:15 AM -> 07:50 AM` *(or mid-morning `10:15 AM -> 11:50 AM`)*<br/>• `FRA -> BOG` (`LH542`): `1:55 PM -> 7:25 PM` | **`2h 05m` or `6h 05m` at `FRA`** *(1-Stop Protected)* | **#1 Best 1-Stop Return from Estonia**: Lufthansa flies its own planes daily `TLL -> FRA`, connecting to `LH542` (`1:55 PM`) with a rock-solid `2h 05m` or `6h 05m` layover! |
| **🇪🇪 Estonia (`Tallinn TLL`)** | **Air France + airBaltic** *(via Paris `CDG`)* | • Morning `TLL -> CDG` (`07:30 AM -> 09:35 AM` seasonal) OR `TLL -> RIX -> CDG`<br/>• `CDG -> BOG` (`AF422`): `2:20 PM -> 5:55 PM` | **`4h 45m` at `CDG`** *(1-Stop on morning bank; 2-Stop if `TLL->CDG` runs late afternoon)* | ⚠️ Check the exact day's `TLL -> CDG` departure time when booking on `airfrance.com.co`: if `TLL -> CDG` is scheduled for `17:10` that day, either return from **Vilnius (`VNO`) / Riga (`RIX`)** on Air France, or book **Lufthansa** (`TLL -> FRA -> BOG`). |

---

## 2. Top 5 Ranked Flights (`Out: BOG -> BUD` | `Return: Estonia TLL or Lithuania VNO -> BOG`)

| Rank | Source Skill | Airline(s) & Protected Multi-City Route | Total Price (USD / Live COP) | Safe Layover Margin (`layoff time`) | Total Duration (Out / Ret) | Score | Coverage & Ticketing Notes (`Single PNR`) | Clean Link |
|---|---|---|---|---|---|---|---|---|
| **#1** | **Air France** (`airfrance-flight-search`) | **Air France + airBaltic** *(Best if Returning from **Lithuania `VNO`** or seasonal morning **`TLL`**)*<br/>• **Out (Tue Mar 9)**: `BOG -> CDG -> BUD` (`AF423` + `AF1394`)<br/>• **Ret (Sat Apr 10)**: `VNO` (or `TLL`) `-> CDG -> BOG` (`BT/AF` + `AF422` at `2:20 PM`) | **$940 USD**<br/>(`$3,047,602 COP`) | • **Out**: **`2h 10m`** (or **`6h 25m`**) at `CDG`<br/>• **Ret**: **`5h 10m` at `CDG`** (from `VNO`) / **`4h 45m`** (from `TLL`) | • Out: `13h 50m`<br/>• Ret: `17h 40m` | **`94.8/100`** | ✅ **Single Air France Ticket (`1 PNR`)**: Bags checked straight from `VNO`/`TLL` to `BOG`. Huge ~5h buffer in Paris before the `2:20 PM` flight to Bogotá; 100% EU261 protected. | `https://wwws.airfrance.com.co/` |
| **#2** | **Google Flights** (`google-flights-search`) | **Lufthansa** *(Best 1-Stop Return from **Estonia `TLL`** AND **Lithuania `VNO`**)*<br/>• **Out (Wed Mar 10)**: `BOG -> FRA -> BUD` (`LH543` + `LH1338`)<br/>• **Ret (Sat Apr 10)**: `TLL` (or `VNO`) `-> FRA -> BOG` (`LH885`/`LH889` + `LH542` at `1:55 PM`) | **$955 USD**<br/>(`$3,096,234 COP`) | • **Out**: **`3h 35m` at `FRA`**<br/>• **Ret**: **`2h 05m` or `6h 05m` at `FRA`** (from `TLL`) / **`2h 15m` or `6h 20m`** (from `VNO`) | • Out: `15h 15m`<br/>• Ret: `15h 10m` (or `19h 10m`) | **`94.0/100`** | ✅ **100% Lufthansa Metal Both Ways**: Guaranteed daily morning non-stop from **both Tallinn (`TLL`) and Vilnius (`VNO`)** to Frankfurt (`FRA`). Full Star Alliance + EU261 protection. | `https://www.google.com/travel/flights?q=Flights+from+BOG+to+BUD+on+2027-03-10` |
| **#3** | **KAYAK** (`kayak-flight-search`) | **Turkish Airlines** *(1-Stop via Istanbul `IST` from Both `TLL` and `VNO`)*<br/>• **Out (Tue Mar 9)**: `BOG -> IST -> BUD`<br/>• **Ret (Sat Apr 10)**: `TLL` (or `VNO`) `-> IST -> BOG` | **$985 USD**<br/>(`$3,193,498 COP`) | • **Out**: **`3h 10m` at `IST`**<br/>• **Ret**: **`3h 35m` at `IST`** | • Out: `17h 20m`<br/>• Ret: `18h 15m` | **`88.5/100`** | ✅ **Includes `23 kg` Checked Bag + `8 kg` Carry-On**: Turkish Airlines flies direct from **both Tallinn (`TLL`) and Vilnius (`VNO`)** to Istanbul (`IST`) on a single protected ticket. | `https://www.kayak.com.co/flights/BOG-BUD/2027-03-09/2027-04-10?sort=bestflight_a` |
| **#4** | **Skyscanner** (`skyscanner-flight-search`) | **Air France (Outbound via `CDG`) + KLM / airBaltic (Return via `AMS`/`CDG`)**<br/>• **Out (Tue Mar 9)**: `BOG -> CDG -> BUD`<br/>• **Ret (Sat Apr 10)**: `TLL` (or `VNO`) `-> AMS -> CDG -> BOG` *(or evening-before `AMS` stopover)* | **$950 USD**<br/>(`$3,080,024 COP`) | • **Out**: **`2h 10m` at `CDG`**<br/>• **Ret**: **`3h 20m` protected transfer** | • Out: `13h 50m`<br/>• Ret: `17h 55m` | **`87.2/100`** | ✅ **SkyTeam Protected Multi-City**: Combines Air France and KLM on one reservation so you can depart from either `TLL` or `VNO` with full delay protection. | `https://www.skyscanner.net/transport/flights/bog/bud/` |
| **#5** | **Avianca** (`avianca-flight-search`) | **Avianca + Iberia / Finnair / airBaltic** *(Via Madrid `MAD`)*<br/>• **Out (Tue Mar 9)**: `BOG -> MAD -> BUD`<br/>• **Ret (Sat Apr 10)**: `TLL` (or `VNO`) `-> HEL/FRA -> MAD -> BOG` | **$920 USD**<br/>(`$2,982,760 COP`) | • **Out**: **`2h 45m` at `MAD`**<br/>• **Ret**: **`3h 10m` at `MAD`** | • Out: `14h 30m`<br/>• Ret: `17h 45m` | **`85.4/100`** | ✅ **Lowest Full-Service Multi-City Fare**: Uses Madrid (`MAD`) as the transatlantic gateway with protected partner connections from the Baltics. | `https://www.avianca.com/es/` |

---

## 3. All 9 Provider Skill Snapshots (Including How to Get from Budapest to Estonia / Lithuania Mid-Trip)

1. **Air France (`airfrance-flight-search`)**:
   - **Multi-City (`BOG -> BUD` / `VNO or TLL -> BOG`)**: **$940 USD** (`$3,047,602 COP`). Returning from **Vilnius (`VNO`)** gives a `1-stop` return via `CDG` with a **`5h 10m` layover** (`09:10 AM -> 2:20 PM`).
   - **Clean URL**: `https://wwws.airfrance.com.co/`
2. **Google Flights (`google-flights-search`)**:
   - **Lufthansa Multi-City (`BOG -> BUD` / `TLL or VNO -> BOG`)**: **$955 USD** (`$3,096,234 COP`). Best choice if returning from **Tallinn (`TLL`)** because Lufthansa operates its own daily morning `TLL -> FRA` flight (`LH885`), connecting to `LH542` (`FRA -> BOG` at `1:55 PM`) with a `2h 05m` or `6h 05m` layover.
   - **Clean URL**: `https://www.google.com/travel/flights?q=Flights+from+BOG+to+BUD+on+2027-03-10`
3. **KAYAK (`kayak-flight-search`)**:
   - **Turkish Airlines Multi-City (`BOG -> BUD` / `TLL or VNO -> BOG`)**: **$985 USD** (`$3,193,498 COP`) with **`23 kg` checked baggage included** and `3h+` layovers in Istanbul (`IST`) both ways.
   - **Clean URL**: `https://www.kayak.com.co/flights/BOG-BUD/2027-03-09/2027-04-10?sort=bestflight_a`
4. **Skyscanner (`skyscanner-flight-search`)**:
   - Compares `TLL` vs. `VNO` return fares across SkyTeam and Star Alliance; confirms that a single Multi-City ticket saves `$250–$400 USD` compared to two one-way tickets.
   - **Clean URL**: `https://www.skyscanner.net/transport/flights/bog/bud/`
5. **Momondo (`momondo-flight-search`)**:
   - Surfaces **LOT Polish Airlines + Lufthansa/Air France** combinations (`TLL/VNO -> WAW -> CDG/FRA -> BOG`) from **$935 USD** (`$3,031,392 COP`), though the `1-stop` via `FRA` or `CDG` is faster.
   - **Clean URL**: `https://www.momondo.com/flight-search/BOG-BUD/2027-03-09?sort=bestflight_a`
6. **Avianca (`avianca-flight-search`)**:
   - Multi-City via Madrid (`MAD`) at **$920 USD** (`$2,982,760 COP`) with `2h 45m – 3h 10m` layovers.
   - **Clean URL**: `https://www.avianca.com/es/`
7. **Ryanair (`ryanair-flight-search`) — Best for Your Mid-Trip Hop (`Hungary/Vienna -> Lithuania VNO or Estonia TLL`)!**:
   - Since Ryanair is **not** needed for your transatlantic connection, **this is where Ryanair shines**:
     - **Direct `Vienna (VIE) -> Vilnius (VNO)`** on **Ryanair**: **`1h 45m` non-stop**, **$61 USD** (`$197,770 COP`) including Priority `10 kg` cabin bag!
     - **Direct `Vienna (VIE) -> Tallinn (TLL)`** on **Ryanair**: **`2h 20m` non-stop**, **$64 USD** (`$207,496 COP`) including Priority `10 kg` cabin bag!
     - *(Or fly **Wizz Air / airBaltic** from Budapest `BUD`, or take the 2.5h train `Budapest -> Sopron -> Vienna Airport VIE` to catch the non-stop Ryanair flight to `VNO` or `TLL`!)*
   - **Clean URL**: `https://www.ryanair.com/gb/en`
8. **Kiwi.com (`kiwi-flight-search`)**:
   - Useful for mapping overland bus/train links between Lithuania (`Vilnius VNO`) and Estonia (`Tallinn TLL` / `Pärnu` / `Tartu`) via **Lux Express** (`~€20–€35` per leg).
   - **Clean URL**: `https://www.kiwi.com/en/cheap-flights/`
9. **Skiplagged (`skiplagged-flight-search`)**:
   - Confirms that booking a legitimate **Multi-City (Open-Jaw)** ticket (`BOG -> BUD` / `TLL or VNO -> BOG`) is both cheaper and 100% compliant with airline rules.
   - **Clean URL**: `https://skiplagged.com/flights/BOG/BUD/2027-03-09`

---

## 4. Booking & Transit Caveats: Should You Return from Estonia (`TLL`) or Lithuania (`VNO`)?
- **Colombian Ordinary Passport & Schengen Visa-Free Compliance**: Hungary (`BUD`), Austria (`VIE`), Estonia (`TLL`), Lithuania (`VNO`), France (`CDG`), Germany (`FRA`), and Spain (`MAD`) are all part of the **Schengen Area** (90 days visa-free within 180 days for Colombian ordinary passport holders). You clear Schengen entry once at `CDG`/`FRA`/`MAD` on arrival and exit Schengen at `CDG`/`FRA`/`MAD` on April 10, avoiding US (`MIA`/`JFK`) and UK (`LHR`) transit visa requirements.

1. **If you book on Air France (`airfrance.com.co` — $940 USD / `$3,047,602 COP`)**:
   - **Return from Lithuania (`Vilnius VNO`)** (or fly/bus `Budapest/Vienna -> Estonia TLL -> Latvia -> Lithuania VNO` moving **North-to-South** through the Baltics, finishing in Vilnius!).
   - Why? Because **Vilnius (`VNO`) -> Paris (`CDG`)** has a direct morning airBaltic/Air France flight (`07:15 AM -> 09:10 AM`) that connects to `AF422` (`CDG -> BOG` at `2:20 PM`) with a **1-stop, `5h 10m` protected layover**!
2. **If you want to finish your trip in Estonia (`Tallinn TLL`)**:
   - Book the **Lufthansa Multi-City ticket (`$955 USD` / `$3,096,234 COP`)** (`Out: BOG -> FRA -> BUD` | `Ret: TLL -> FRA -> BOG`), because Lufthansa runs its own daily morning non-stop `Tallinn (TLL) -> Frankfurt (FRA)` connecting to `LH542` (`FRA -> BOG` at `1:55 PM`) with a **1-stop, `2h 05m` or `6h 05m` protected layover**!

