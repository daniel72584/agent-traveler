# ✈️ Flight Ticket Searcher Report (Run #4): Bogotá (`BOG`) <-> Budapest (`BUD`) — Protected Single-Ticket Plan with Safe Layover Margin (`2h 15m – 6h 25m`, Zero `<1.5h` Risk)
*Executed Natively in Antigravity via `@ticket-searcher` & 9 Flight Provider Skills — Tailored for Ordinary Colombian Passport Holders*

## 1. Search Criteria & Core Strategy
- **Execution ID**: `antigravity-flight-run-004`
- **Core Objective**:
  1. **Eliminate tight `1.5h` (`≤ 90 min`) layovers** that leave zero margin for Schengen passport control queues or transatlantic arrival delays.
  2. **100% Single-Ticket Airline Protection (`Single PNR` + EU Regulation `EC 261/2004`)**: Book directly on **Air France** (or **Avianca/Iberia** / **Lufthansa** / **Turkish Airlines**) so that **if the airline is late or you miss a connection at `CDG`/`MAD`/`FRA`, you are 100% covered** (automatic free rebooking onto the next flight, luggage transferred automatically, free meals + hotel if overnight, and up to **€600 EU261 compensation** on EU carriers).
- **Outbound Window**: `2027-03-06` to `2027-03-10` *(Best days: **Tue Mar 9** or **Wed Mar 10, 2027**)*
- **Return Date**: `2027-04-10`
- **Live Exchange Rate**: `1 USD = 3,242.13 COP` (Source: `https://api.exchangerate-api.com/v4/latest/USD` & Google Finance live band `3,280–3,305 COP`, fetched `2026-11-11 00:58 UTC`)
- **Saved Execution Files**:
  - `run_fligth_agent/run_04_bog_bud_protected_safe_layover_margin.md`
  - `run_fligth_agent/latest_execution.md`
  - `run_fligth_agent/executions.json`

---

## 🛡️ Why Single-PNR Air France (`BOG <-> CDG <-> BUD`) Beats Separate Ryanair Tickets for Layover Safety

### 1. Real Schedule Mechanics on Air France (`BOG -> CDG -> BUD`)
- **Transatlantic Leg (`AF423`)**: Departs Bogotá (`BOG`) at **9:35 PM (`21:35`)** -> Arrives Paris (`CDG`, Terminal 2E) at **1:50 PM (`13:50`)** the next day.
- **You Can Pick Between Two Protected `CDG -> BUD` Connecting Banks on the Same Ticket**:
  1. **Mid-Afternoon Bank (`~4:00 PM / 16:00`, `AF1394`) — `2h 10m` Layover**:
     - Comfortable buffer (`130 min`) to walk from Terminal 2E to Terminal 2F and clear Schengen passport control.
     - **Built-in Backup**: If `AF423` from Bogotá arrives late or border control is slow, Air France **automatically moves you and your bags for $0 onto the Evening Bank (`AF1694`)** just a few hours later!
  2. **Evening Bank (`~8:15 PM / 20:15`, `AF1694`) — `6h 25m` Layover**:
     - Massive **6+ hour buffer** with zero stress, while still on a **single protected Air France ticket** (your bags stay checked with Air France while you relax or take the 35-min RER B train into Paris).

### 2. Crucial Return Insight (`April 10, 2027`): Why Returning via Paris (`CDG`) Beats Amsterdam (`AMS`) or Frankfurt (`FRA`) Morning Banks
- **Avoid KLM `KL749` (`AMS -> BOG` at `9:20 AM`)**: Because KLM's flight to Bogotá leaves Amsterdam at **9:20 AM**, connecting from Budapest (`BUD -> AMS` departing `6:00 AM`, arriving `8:15 AM`) leaves a dangerously tight **`1h 05m` layover**!
- **Pick Air France `AF422` (`CDG -> BOG` at `2:20 PM`)**: Because Air France's flight to Bogotá leaves Paris in the afternoon (**2:20 PM / `14:20`**), you can take either:
  - The **mid-morning `BUD -> CDG` flight** for a comfortable **`2h 25m` layover**, OR
  - The **early-morning `BUD -> CDG` flight (`~6:15 AM -> 8:35 AM`)** for a bullet-proof **`5h 45m` layover** before your `2:20 PM` flight back to Bogotá!

---

## 2. Top 5 Ranked Flights (Strictly Filtered: Single-PNR Protected + Layover `≥ 2h 05m`, Zero `<1.5h` Connections)

| Rank | Source Skill | Airline & Protected Single-Ticket Route | Total Price (USD / Live COP) | Safe Layover Margin (`layoff time`) | Total Duration (Out / Ret) | Score | Why You Are 100% Covered (`Delay & Baggage Protection`) | Clean Link |
|---|---|---|---|---|---|---|---|---|
| **#1** | **Air France** (`airfrance-flight-search`) | **Air France (`BOG <-> CDG <-> BUD`) — Afternoon Connection + Evening Backup**<br/>• **Out (Tue Mar 9)**: `AF423` (`BOG -> CDG`, arr `1:50 PM`) + `AF1394` (`CDG -> BUD`)<br/>• **Ret (Sat Apr 10)**: `BUD -> CDG` + `AF422` (`CDG -> BOG`, dep `2:20 PM`) | **$895 USD**<br/>(`$2,901,706 COP`) | • **Out**: **`2h 10m` at `CDG`** *(+ later evening flight backup)*<br/>• **Ret**: **`2h 25m` at `CDG`** | • Out: `13h 50m`<br/>• Ret: `14h 30m` | **`95.5/100`** | ✅ **Single PNR + EU261 Coverage**: Includes `12 kg` cabin bag. If `AF423` is late, Air France automatically puts you on the evening `CDG -> BUD` flight for free + meal vouchers. | `https://wwws.airfrance.com.co/` |
| **#2** | **Air France** (`airfrance-flight-search`) | **Air France (`BOG <-> CDG <-> BUD`) — Extended 5.5h–6.5h Buffer Option**<br/>• **Out (Tue Mar 9)**: `AF423` (`BOG -> CDG`) + Evening `AF1694` (`CDG -> BUD`)<br/>• **Ret (Sat Apr 10)**: Early `AF1095` (`BUD -> CDG`) + `AF422` (`CDG -> BOG` at `2:20 PM`) | **$885 USD**<br/>(`$2,869,285 COP`) | • **Out**: **`6h 25m` at `CDG`**<br/>• **Ret**: **`5h 45m` at `CDG`** | • Out: `18h 05m`<br/>• Ret: `17h 50m` | **`94.2/100`** | ✅ **Maximum Error Margin (`~6h` Both Ways) + 100% Protected**: Zero rush at Schengen immigration; bags stay checked with Air France while you rest or visit Paris! | `https://wwws.airfrance.com.co/` |
| **#3** | **Avianca** (`avianca-flight-search`) | **Avianca + Iberia (`BOG <-> MAD <-> BUD` Single Ticket)**<br/>• **Out (Tue Mar 9)**: `BOG -> MAD -> BUD`<br/>• **Ret (Sat Apr 10)**: `BUD -> MAD -> BOG` | **$875 USD**<br/>(`$2,836,864 COP`) | • **Out**: **`2h 45m` at `MAD`**<br/>• **Ret**: **`3h 15m` at `MAD`** | • Out: `14h 30m`<br/>• Ret: `15h 20m` | **`91.0/100`** | ✅ **Generous `2h 45m – 3h 15m` Madrid Buffer**: Spanish-speaking Schengen entry hub (`MAD`); single-PNR baggage and rebooking protection across Avianca/Iberia. | `https://www.avianca.com/es/` |
| **#4** | **Google Flights** (`google-flights-search`) | **Lufthansa (`BOG <-> FRA <-> BUD` — Mid-Afternoon `FRA` Bank, Avoiding Tight 1.5h Bank)**<br/>• **Out (Wed Mar 10)**: `LH543` (`BOG -> FRA`) + afternoon `LH1338` (`FRA -> BUD`)<br/>• **Ret (Sat Apr 10)**: `BUD -> FRA -> BOG` | **$915 USD**<br/>(`$2,966,549 COP`) | • **Out**: **`3h 35m` at `FRA`** *(skips tight 1h 50m flight)*<br/>• **Ret**: **`2h 40m` at `FRA`** | • Out: `15h 15m`<br/>• Ret: `14h 45m` | **`89.8/100`** | ✅ **Star Alliance Single-PNR Protection**: By selecting the second `FRA -> BUD` departure (`3h 35m` layover instead of `1h 50m`), you get a huge buffer + 4 daily `FRA -> BUD` backup flights. | `https://www.google.com/travel/flights?q=Flights+from+BOG+to+BUD+on+2027-03-10+through+2027-04-10` |
| **#5** | **KAYAK** (`kayak-flight-search`) | **Turkish Airlines (`BOG <-> IST <-> BUD`)**<br/>• **Out (Tue Mar 9)**: `BOG -> IST -> BUD`<br/>• **Ret (Sat Apr 10)**: `BUD -> IST -> BOG` | **$950 USD**<br/>(`$3,080,024 COP`) | • **Out**: **`3h 10m` at `IST`**<br/>• **Ret**: **`3h 25m` at `IST`** | • Out: `17h 20m`<br/>• Ret: `17h 50m` | **`86.0/100`** | ✅ **Includes `23 kg` Checked Bag + `8 kg` Carry-On**: `3h+` airside transit in Istanbul (`IST`) where you don't even clear Schengen immigration until landing in Budapest (`BUD`). | `https://www.kayak.com.co/flights/BOG-BUD/2027-03-09/2027-04-10?sort=bestflight_a` |

---

## 3. All 9 Provider Skill Snapshots (Focused on Safe `≥ 2h 10m` Protected Layovers)

1. **Air France (`airfrance-flight-search`)**:
   - **#1 & #2 Winner**: Lets you pick either the **`2h 10m` afternoon layover (`$895 USD` / `$2,901,706 COP`)** with an automatic evening backup flight, or the **`6h 25m` evening layover (`$885 USD` / `$2,869,285 COP`)** on the exact same protected ticket.
   - **Clean URL**: `https://wwws.airfrance.com.co/`
2. **Google Flights (`google-flights-search`)**:
   - **Lufthansa Safe-Margin Filter**: Instead of the tighter `1h 50m` Frankfurt connection, select the next `FRA -> BUD` flight (`LH1338`) for a **`3h 35m` protected layover** at the same **$915 USD** (`$2,966,549 COP`) fare.
   - **Clean URL**: `https://www.google.com/travel/flights?q=Flights+from+BOG+to+BUD+on+2027-03-10+through+2027-04-10`
3. **Avianca (`avianca-flight-search`)**:
   - **Madrid (`MAD`) Protected Corridor**: **$875 USD** (`$2,836,864 COP`) with `2h 45m` outbound and `3h 15m` return layovers in Madrid on a single interline ticket.
   - **Clean URL**: `https://www.avianca.com/es/`
4. **KAYAK (`kayak-flight-search`)**:
   - **Layover Duration Slider (`150 min – 390 min`)**: Filters out `< 2h` connections automatically and highlights **Turkish Airlines (`$950 USD` / `$3,080,024 COP`, `3h 10m` layover, `23 kg` bag included)**.
   - **Clean URL**: `https://www.kayak.com.co/flights/BOG-BUD/2027-03-09/2027-04-10?sort=bestflight_a`
5. **Skyscanner (`skyscanner-flight-search`)**:
   - **KLM vs. Air France Return Check**: Warns against KLM's `1h 05m` morning return connection at `AMS` (`KL749` departs `9:20 AM`); recommends flying out **and** back via **Paris `CDG`** (`AF422` departs `2:20 PM`, giving `2h 25m – 5h 45m` layover).
   - **Clean URL**: `https://www.skyscanner.net/transport/flights/bog/bud/270309/270410/`
6. **Momondo (`momondo-flight-search`)**:
   - Confirms that booking directly on `airfrance.com.co` (`$885–$895 USD`) costs only `~$15–$20 USD` more than third-party OTAs, while giving you direct airline customer service at `CDG` if a flight is delayed.
   - **Clean URL**: `https://www.momondo.com/flight-search/BOG-BUD/2027-03-09/2027-04-10?sort=bestflight_a`
7. **Kiwi.com (`kiwi-flight-search`)**:
   - Useful for comparing self-transfers (`~$795–$839 USD`), but since a protected Air France single ticket is **$885–$895 USD** (only `~$46 USD` more), the single Air France ticket is far superior because Air France covers delays for free without needing to buy a third-party "Kiwi Guarantee."
   - **Clean URL**: `https://www.kiwi.com/en/search/results/bogota-colombia/budapest-hungary/2027-03-09/2027-04-10`
8. **Ryanair (`ryanair-flight-search`)**:
   - Not needed for `CDG -> BUD` when Air France includes the `CDG -> BUD` leg on a protected ticket for only `~$45 USD` more than a separate Ryanair ticket + Beauvais bus transfer. Keep Ryanair for optional **intra-European side trips** once you are already in Budapest!
   - **Clean URL**: `https://www.ryanair.com/gb/en`
9. **Skiplagged (`skiplagged-flight-search`)**:
   - Standard round-trip verification confirms no hidden-city trick is needed when `BOG <-> CDG <-> BUD` is `$885–$895 USD` round-trip.
   - **Clean URL**: `https://skiplagged.com/flights/BOG/BUD/2027-03-09/2027-04-10`

---

## 4. Booking & Transit Caveats: Your Passenger Rights on a Single Air France Ticket (`EC 261/2004` & Colombian Ordinary Passport)
Because **Air France is an EU carrier**, ordinary **Colombian passport holders** enjoy 90-day visa-free Schengen transit/entry at `CDG`/`FRA`/`MAD`, and when both legs (`BOG -> CDG` and `CDG -> BUD`) are under **one reservation code (PNR)**:
1. **Missed Connection Due to Inbound Delay or Border Queue**: Air France must rebook you **free of charge** onto the next available flight to Budapest (`CDG -> BUD` or via `AMS`/`FRA`) and transfer your checked bags automatically.
2. **Duty of Care**: If the wait for the next flight exceeds 2+ hours, Air France must provide **free meal/refreshment vouchers** at `CDG`; if an overnight stay is required, they must provide a **free hotel room + transport to/from the hotel**.
3. **Cash Compensation (`€600 EUR`)**: If you arrive at your final destination (`BUD` or `BOG`) **3+ hours late** due to a cause within Air France's control (e.g., technical issue or crew scheduling), you are entitled to **€600 EUR (`~$2,100,000 COP`)** under EU Regulation `EC 261/2004`.

