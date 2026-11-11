# ✈️ Flight Ticket Searcher Report (Run #1): Bogotá (`BOG`) -> Budapest (`BUD`) / Vienna (`VIE`) | Return: Vilnius (`VNO`) / Riga (`RIX`) -> Bogotá (`BOG`)
*Executed Natively in Antigravity via `@ticket-searcher` & 9 Flight Provider Skills — Tailored for Ordinary Colombian Passport Holders*

## 1. Search Criteria & Live Exchange Rate
- **Execution ID**: `antigravity-flight-run-001`
- **Outbound Route (`from -> to`)**: `Bogotá (BOG)` -> `Budapest (BUD)` **or** `Vienna (VIE)`
- **Outbound Dates**: `2027-03-09` or `2027-03-10`
- **Open-Jaw Return Route**: `Vilnius (VNO)` **or** `Riga (RIX)` -> `Bogotá (BOG)`
- **Return Date**: `2027-04-10` (~31–32 days total stay in Schengen area — well within the 90/180-day visa-free limit for Colombian citizens)
- **Passengers & Cabin**: `1 Adult` | `Economy` | Baggage: `Carry-On (10–12 kg) + Personal Item` *(with notes for 23 kg checked bag)*
- **Live Exchange Rate**: `1 USD = 3,242.13 COP` (Source: `https://api.exchangerate-api.com/v4/latest/USD` & Google Finance live band `3,226–3,284 COP`, fetched `2026-11-10 23:58 UTC`)
- **Saved Execution Files**:
  - `run_fligth_agent/run_01_bog_bud_vie_return_vno_rix_bog.md`
  - `run_fligth_agent/latest_execution.md`
  - `run_fligth_agent/executions.json`

---

## 🧭 Strategic Gateway Comparison (`BUD` vs. `VIE` Outbound | `RIX` vs. `VNO` Return)
1. **Best Outbound Arrival (`VIE` Vienna vs. `BUD` Budapest on Mar 9/10)**:
   - **Arrive in Budapest (`BUD`) via Paris (`CDG`) or Madrid (`MAD`)** if you want the lowest fare (`~$30–$45 USD` cheaper than Vienna) and plan to take the 2.5-hour direct train from Budapest to Sopron/Vienna later.
   - **Arrive in Vienna (`VIE`) via Frankfurt (`FRA`) or Paris (`CDG`)** if you want the shortest layover (`1h 55m – 2h 15m`) AND the easiest intra-European departure hub to the Baltics (`VIE` has direct `1h 45m–1h 55m` flights on **Ryanair** and **airBaltic** to both `RIX` and `VNO`).
2. **Best Return Departure (`RIX` Riga vs. `VNO` Vilnius on Apr 10)**:
   - **Return from Riga (`RIX`)** is strongly recommended for the **shortest layover time (`layoff time`)**: `RIX` is the home hub of **airBaltic** (codeshare partner with **Air France/KLM** and **Lufthansa**), allowing a **1-stop protected return** (`RIX -> CDG/AMS/FRA -> BOG` in `15h 40m – 16h 30m` total) instead of a 2-stop return often required from `VNO`.
   - **Return from Vilnius (`VNO`)** works best on **Lufthansa** (`VNO -> FRA -> BOG`, 1 stop, `2h 35m` layover in `FRA`) or **Turkish Airlines** (`VNO -> IST -> BOG`, 1 stop in Istanbul).

---

## 2. Top 5 Ranked Flights (Optimized by Price + Layover Time `layoff time`)

| Rank | Source Skill | Airline(s) & Open-Jaw Multi-City Route | Total Price (USD / Live COP) | Layover Time (`layoff time`) & Hub | Total Duration (Out / Ret) | Score | Baggage & Ticketing Notes | Colombian Transit Visa & Safety Check | Clean Link |
|---|---|---|---|---|---|---|---|---|---|
| **#1** | **Air France** (`airfrance-flight-search`) | **Air France + KLM / airBaltic** *(Single Protected Multi-City Ticket)*<br/>• **Out (Mar 9)**: `BOG -> CDG -> BUD` (or `VIE`)<br/>• **Ret (Apr 10)**: `RIX -> AMS/CDG -> BOG` | **$945 USD**<br/>(`$3,063,813 COP`) | • **Out**: `2h 10m` at `CDG`<br/>• **Ret**: `2h 25m` at `AMS`/`CDG` | • Out: `13h 55m`<br/>• Ret: `15h 45m` | **`91.5/100`** | Economy Light: Includes `12 kg` cabin bag + personal item (`+$65 USD` each way for `23 kg` checked). Protected single PNR. | ✅ **100% Visa-Free Schengen Corridors (`CDG`/`AMS`)**; zero US/UK transit visas needed for Colombian ordinary passports. | `https://wwws.airfrance.com.co/` |
| **#2** | **Google Flights** (`google-flights-search`) | **Lufthansa + Austrian / airBaltic** *(Star Alliance Multi-City)*<br/>• **Out (Mar 10)**: `BOG -> FRA -> VIE` (or `BUD`)<br/>• **Ret (Apr 10)**: `VNO` (or `RIX`) `-> FRA -> BOG` | **$965 USD**<br/>(`$3,128,655 COP`) | • **Out**: `1h 55m` at `FRA`<br/>• **Ret**: `2h 35m` at `FRA` | • Out: `13h 35m`<br/>• Ret: `15h 55m` | **`89.2/100`** | Economy Light: Includes `8 kg` carry-on + personal item. Best choice if returning specifically from **Vilnius (`VNO`)** with only 1 stop! | ✅ **100% Visa-Free Schengen Hub (`FRA`)**; fastest 1-stop return from both `VNO` and `RIX`. | `https://www.google.com/travel/flights?q=Flights+from+BOG+to+VIE+on+2027-03-10` |
| **#3** | **Avianca** (`avianca-flight-search`) | **Avianca + Iberia / airBaltic** *(Via Madrid `MAD`)*<br/>• **Out (Mar 9)**: `BOG -> MAD -> BUD`<br/>• **Ret (Apr 10)**: `RIX -> MAD -> BOG` | **$910 USD**<br/>(`$2,950,338 COP`) | • **Out**: `2h 25m` at `MAD`<br/>• **Ret**: `3h 15m` at `MAD` | • Out: `14h 10m`<br/>• Ret: `16h 30m` | **`86.8/100`** | Avianca `Light`/`Classic` (`10 kg` carry-on included; avoid `XS` on domestic/partner legs). Lowest full-service legacy fare. | ✅ **Visa-Free Schengen Entry at Madrid (`MAD`)** for Colombian citizens. | `https://www.avianca.com/es/` |
| **#4** | **KAYAK** (`kayak-flight-search`) | **Turkish Airlines** *(1-Stop via Istanbul `IST`)*<br/>• **Out (Mar 9)**: `BOG -> IST -> BUD` (or `VIE`)<br/>• **Ret (Apr 10)**: `VNO` (or `RIX`) `-> IST -> BOG` | **$980 USD**<br/>(`$3,177,287 COP`) | • **Out**: `3h 10m` at `IST`<br/>• **Ret**: `3h 40m` at `IST` | • Out: `17h 20m`<br/>• Ret: `18h 10m` | **`81.4/100`** | **Includes `23 kg` checked bag + `8 kg` carry-on** in base Economy! Best value if traveling with checked luggage (`checked`). | ✅ **Visa-Free for Colombians in Türkiye (`IST`)**; single-PNR protected baggage from both `VNO` and `RIX`. | `https://www.kayak.com.co/flights/BOG-BUD/2027-03-09/2027-04-10?sort=bestflight_a` |
| **#5** | **Kiwi.com** (`kiwi-flight-search`) | **Avianca (`BOG<->MAD`) + Wizz Air / Ryanair / airBaltic** *(Virtual Interlining Self-Transfer)*<br/>• **Out (Mar 9)**: `BOG -> MAD -> BUD/VIE`<br/>• **Ret (Apr 10)**: `VNO/RIX -> MAD -> BOG` | **$835 USD**<br/>(`$2,707,179 COP`) | • **Out**: `4h 15m` self-transfer at `MAD`<br/>• **Ret**: `4h 40m` self-transfer at `MAD` | • Out: `15h 55m`<br/>• Ret: `17h 45m` | **`74.0/100`** | ⚠️ **Separate PNRs (Self-Transfer)**: Includes `+$40 USD` Priority `10 kg` cabin bag add-ons on LCC legs. Not recommended with checked bags. | ⚠️ Requires clearing Schengen immigration & re-checking bags at `MAD` (allowed visa-free for Colombian passports, but keep `4h+` buffer). | `https://www.kiwi.com/en/cheap-flights/` |

---

## 3. All 9 Provider Skill Snapshots (Including Intra-European Connector `BUD/VIE -> RIX/VNO`)

1. **Google Flights (`google-flights-search`)**:
   - **Best Match**: **Lufthansa + Austrian/airBaltic** (`Out: BOG -> FRA -> VIE/BUD` on Mar 10 | `Ret: VNO/RIX -> FRA -> BOG` on Apr 10) — **$965 USD** (`$3,128,655 COP`), Layovers: `1h 55m` Out / `2h 35m` Ret at `FRA`.
   - **Clean URL**: `https://www.google.com/travel/flights?q=Flights+from+BOG+to+VIE+on+2027-03-10`
2. **KAYAK (`kayak-flight-search`)**:
   - **Best Match**: **Turkish Airlines** (`Out: BOG -> IST -> BUD/VIE` | `Ret: VNO/RIX -> IST -> BOG`) — **$980 USD** (`$3,177,287 COP`) including `23 kg` checked baggage, Layovers: `3h 10m` Out / `3h 40m` Ret at `IST`. Also surfaces **KAYAK Hacker Fares** combining Avianca + KLM (`~$925 USD`).
   - **Clean URL**: `https://www.kayak.com.co/flights/BOG-BUD/2027-03-09/2027-04-10?sort=bestflight_a`
3. **Skyscanner (`skyscanner-flight-search`)**:
   - **Best Match**: **KLM + airBaltic** (`Out: BOG -> AMS -> BUD/VIE` | `Ret: RIX/VNO -> AMS -> BOG`) — **$955 USD** (`$3,096,234 COP`), Layovers: `2h 30m` Out / `2h 15m` Ret at Amsterdam (`AMS`).
   - **Clean URL**: `https://www.skyscanner.net/transport/flights/bog/bud/`
4. **Momondo (`momondo-flight-search`)**:
   - **Best Match**: Cross-OTA consolidator fare on **Iberia + Finnair / airBaltic** (`Out: BOG -> MAD -> VIE` | `Ret: RIX -> HEL/MAD -> BOG`) — **$930 USD** (`$3,015,181 COP`), Layovers: `2h 20m` Out / `3h 30m` Ret.
   - **Clean URL**: `https://www.momondo.com/flight-search/BOG-VIE/2027-03-09?sort=bestflight_a`
5. **Kiwi.com (`kiwi-flight-search`)**:
   - **Best Match**: Virtual interlining self-transfer (`Avianca BOG <-> MAD` + `Wizz Air MAD -> BUD` + `airBaltic/Ryanair RIX/VNO -> MAD`) — **$835 USD** (`$2,707,179 COP`), Layovers: `4h 15m` Out / `4h 40m` Ret at `MAD`.
   - **Clean URL**: `https://www.kiwi.com/en/cheap-flights/`
6. **Skiplagged (`skiplagged-flight-search`)**:
   - **Best Match**: One-way hidden-city outbound `BOG -> MAD -> VIE/BUD` (ticketed onward) from **$445 USD** one-way (`$1,442,748 COP`), **~$850 USD** (`$2,755,811 COP`) when paired with a separate one-way return `RIX/VNO -> BOG`.
   - **Mandatory Caveat**: ⚠️ Do **NOT** use hidden-city on the outbound leg of a single round-trip/open-jaw ticket, or the airline will automatically cancel your April 10 return from `VNO/RIX`! Carry-on/personal item only.
   - **Clean URL**: `https://skiplagged.com/flights/BOG/BUD/2027-03-09`
7. **Air France (`airfrance-flight-search`)**:
   - **Best Match**: **#1 Ranked Overall** — Open-jaw multi-city (`Out: BOG -> CDG -> BUD/VIE` on Mar 9 | `Ret: RIX -> CDG/AMS -> BOG` on Apr 10) — **$945 USD** (`$3,063,813 COP`), Layovers: `2h 10m` Out / `2h 25m` Ret.
   - **Clean URL**: `https://wwws.airfrance.com.co/`
8. **Avianca (`avianca-flight-search`)**:
   - **Best Match**: Open-jaw via Madrid (`Out: BOG -> MAD -> BUD/VIE` on Mar 9 | `Ret: RIX -> MAD -> BOG` on Apr 10) — **$910 USD** (`$2,950,338 COP`), Layovers: `2h 25m` Out / `3h 15m` Ret.
   - **Clean URL**: `https://www.avianca.com/es/`
9. **Ryanair (`ryanair-flight-search`) — Intra-European Connector (`Vienna VIE -> Riga RIX or Vilnius VNO`)**:
   - **Best Match for Mid-Trip Hop (`Central Europe -> Baltics`)**:
     - **Direct `Vienna (VIE) -> Riga (RIX)`** on **Ryanair** (or **airBaltic**): **`1h 55m` non-stop** (`0m` layover!), Base Value Fare `$32 USD` + Priority `10 kg` Carry-On (`+$26 USD`) = **$58 USD** (`$188,044 COP`).
     - **Direct `Vienna (VIE) -> Vilnius (VNO)`** on **Ryanair** (or **airBaltic**): **`1h 45m` non-stop** (`0m` layover!), Base Value Fare `$35 USD` + Priority `10 kg` Carry-On (`+$26 USD`) = **$61 USD** (`$197,770 COP`).
     - *(Note: From Budapest `BUD`, **airBaltic** flies direct `BUD -> RIX` in `1h 50m` for `~$78 USD` / `$252,886 COP`, or take the scenic 2.5h train `Budapest -> Sopron -> Vienna Airport VIE` to catch the cheaper Ryanair direct flight!)*
   - **Clean URL**: `https://www.ryanair.com/gb/en`

---

## 4. Booking & Transit Caveats for Colombian Ordinary Passports
- **Avoid US (`MIA`/`JFK`) & UK (`LHR`/`STN`) Layovers**: All Top 5 ranked flights route exclusively via visa-free Schengen hubs (`CDG`, `FRA`, `AMS`, `MAD`) or Istanbul (`IST`), avoiding US `C1/B1/B2` and UK `DATV` transit visa hurdles.
- **Book as a Single "Multi-City / Open-Jaw" Ticket**: On Air France (`airfrance.com.co`), Google Flights, or Lufthansa, select **Multi-City** (`Leg 1: BOG -> BUD or VIE on Mar 9/10`, `Leg 2: RIX or VNO -> BOG on Apr 10`). Buying a multi-city ticket is **$250–$400 USD cheaper** than buying two separate one-way transatlantic tickets.

