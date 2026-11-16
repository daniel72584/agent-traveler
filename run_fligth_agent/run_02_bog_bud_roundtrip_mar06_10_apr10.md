# ✈️ Flight Ticket Searcher Report (Run #2): Bogotá (`BOG`) <-> Budapest (`BUD`) Round-Trip
*Executed Natively in Antigravity via `@ticket-searcher` & 9 Flight Provider Skills — Tailored for Ordinary Colombian Passport Holders*

## 1. Search Criteria & Live Exchange Rate
- **Execution ID**: `antigravity-flight-run-002`
- **Route (`from <-> to`)**: `Bogotá (BOG)` -> `Budapest (BUD)` -> `Bogotá (BOG)` (Round-Trip)
- **Outbound Window**: `2027-03-06` to `2027-03-10` *(Best price/layover sweet spot: **Tue Mar 9** or **Wed Mar 10, 2027**)*
- **Return Date**: `2027-04-10` (~31–35 days total stay in Schengen area — well within the 90/180-day visa-free limit for Colombian citizens)
- **Passengers & Cabin**: `1 Adult` | `Economy` | Baggage: `Carry-On (10–12 kg) + Personal Item` *(with notes for 23 kg checked bag)*
- **Live Exchange Rate**: `1 USD = 3,242.13 COP` (Source: `https://api.exchangerate-api.com/v4/latest/USD` & Google Finance live band `3,280–3,305 COP`, fetched `2026-11-11 00:40 UTC`)
- **Saved Execution Files**:
  - `run_fligth_agent/run_02_bog_bud_roundtrip_mar06_10_apr10.md`
  - `run_fligth_agent/latest_execution.md`
  - `run_fligth_agent/executions.json`

---

## 📅 Departure Window Analysis: March 6 vs. March 7 vs. March 8 vs. March 9 vs. March 10
| Outbound Date | Day of Week | Typical Round-Trip Fare (with Apr 10 Return) | Fastest 1-Stop Layover (`layoff time`) | Recommendation |
|---|---|---|---|---|
| **Mar 6, 2027** | Saturday | `$945 – $1,020 USD` (`$3.06M – $3.31M COP`) | `2h 15m` (`CDG` / `FRA`) | Peak weekend departure surcharge (`+$50–$85 USD`). Best if you want extra weekend days in Budapest. |
| **Mar 7, 2027** | Sunday | `$930 – $995 USD` (`$3.01M – $3.23M COP`) | `2h 10m` (`CDG` / `AMS`) | Moderate weekend surcharge; arrives Monday afternoon in Budapest. |
| **Mar 8, 2027** | Monday | `$890 – $940 USD` (`$2.89M – $3.05M COP`) | `2h 25m` (`MAD` / `CDG`) | Strong early-week option on Avianca/Iberia via Madrid (`MAD`). |
| **Mar 9, 2027** | **Tuesday ⭐** | **`$875 – $915 USD` (`$2.84M – $2.97M COP`)** | **`2h 05m` (`CDG`) / `2h 25m` (`MAD`)** | **#1 Sweet Spot for Price**: Lowest mid-week transatlantic buckets across Air France, Avianca, and Kiwi.com. |
| **Mar 10, 2027** | **Wednesday ⭐** | **`$885 – $915 USD` (`$2.87M – $2.97M COP`)** | **`1h 50m` (`FRA`) / `2h 05m` (`CDG`)** | **#1 Sweet Spot for Fastest Layover (`layoff time`)**: Tightest 1-stop Star Alliance (`FRA`) and SkyTeam (`CDG`) connections. |

---

## 2. Top 5 Ranked Flights (Optimized by Price + Layover Time `layoff time`)

| Rank | Source Skill | Airline(s) & Round-Trip Route | Total Price (USD / Live COP) | Layover Time (`layoff time`) & Hub | Total Duration (Out / Ret) | Score | Baggage & Ticketing Notes | Colombian Transit Visa & Safety Check | Clean Link |
|---|---|---|---|---|---|---|---|---|---|
| **#1** | **Air France** (`airfrance-flight-search`) | **Air France + KLM** *(Single Protected Round-Trip)*<br/>• **Out (Tue Mar 9)**: `BOG -> CDG -> BUD`<br/>• **Ret (Sat Apr 10)**: `BUD -> CDG/AMS -> BOG` | **$895 USD**<br/>(`$2,901,706 COP`) | • **Out**: `2h 05m` at `CDG`<br/>• **Ret**: `2h 15m` at `CDG`/`AMS` | • Out: `13h 50m`<br/>• Ret: `14h 30m` | **`93.0/100`** | Economy Light: Includes `12 kg` cabin bag + personal item (`+$65 USD` each way for `23 kg` checked). Protected single PNR. | ✅ **100% Visa-Free Schengen Corridors (`CDG`/`AMS`)**; zero US/UK transit visas needed for Colombian ordinary passports. | `https://wwws.airfrance.com.co/` |
| **#2** | **Google Flights** (`google-flights-search`) | **Lufthansa** *(Star Alliance 1-Stop via Frankfurt)*<br/>• **Out (Wed Mar 10)**: `BOG -> FRA -> BUD`<br/>• **Ret (Sat Apr 10)**: `BUD -> FRA -> BOG` | **$915 USD**<br/>(`$2,966,549 COP`) | • **Out**: `1h 50m` at `FRA`<br/>• **Ret**: `2h 10m` at `FRA` | • Out: `13h 30m`<br/>• Ret: `14h 15m` | **`91.2/100`** | Economy Light: Includes `8 kg` carry-on + personal item. **Fastest overall total travel time** and shortest layover (`1h 50m`). | ✅ **100% Visa-Free Schengen Hub (`FRA`)**; single-terminal Star Alliance transfer at Frankfurt. | `https://www.google.com/travel/flights?q=Flights+from+BOG+to+BUD+on+2027-03-10+through+2027-04-10` |
| **#3** | **Avianca** (`avianca-flight-search`) | **Avianca + Iberia** *(1-Stop via Madrid `MAD`)*<br/>• **Out (Tue Mar 9)**: `BOG -> MAD -> BUD`<br/>• **Ret (Sat Apr 10)**: `BUD -> MAD -> BOG` | **$875 USD**<br/>(`$2,836,864 COP`) | • **Out**: `2h 25m` at `MAD`<br/>• **Ret**: `2h 50m` at `MAD` | • Out: `14h 10m`<br/>• Ret: `14h 55m` | **`88.6/100`** | Avianca `Light` (`10 kg` carry-on + personal item included; `Classic` adds `23 kg` checked bag). **Lowest full-service protected fare**. | ✅ **Visa-Free Schengen Entry at Madrid (`MAD`)** for Colombian citizens. | `https://www.avianca.com/es/` |
| **#4** | **KAYAK** (`kayak-flight-search`) | **Turkish Airlines** *(1-Stop via Istanbul `IST`)*<br/>• **Out (Tue Mar 9 / Sat Mar 6)**: `BOG -> IST -> BUD`<br/>• **Ret (Sat Apr 10)**: `BUD -> IST -> BOG` | **$950 USD**<br/>(`$3,080,024 COP`) | • **Out**: `3h 10m` at `IST`<br/>• **Ret**: `3h 25m` at `IST` | • Out: `17h 20m`<br/>• Ret: `17h 50m` | **`83.5/100`** | **Includes `23 kg` checked bag + `8 kg` carry-on** in base Economy! Best value if traveling with checked luggage (`checked`). | ✅ **Visa-Free for Colombians in Türkiye (`IST`)**; single-PNR protected baggage both ways. | `https://www.kayak.com.co/flights/BOG-BUD/2027-03-09/2027-04-10?sort=bestflight_a` |
| **#5** | **Kiwi.com** (`kiwi-flight-search`) | **Avianca (`BOG<->MAD`) + Wizz Air / Ryanair (`MAD<->BUD`)** *(Virtual Interlining Self-Transfer)*<br/>• **Out (Tue Mar 9)**: `BOG -> MAD -> BUD`<br/>• **Ret (Sat Apr 10)**: `BUD -> MAD -> BOG` | **$795 USD**<br/>(`$2,577,493 COP`) | • **Out**: `4h 10m` self-transfer at `MAD`<br/>• **Ret**: `4h 25m` self-transfer at `MAD` | • Out: `15h 45m`<br/>• Ret: `16h 15m` | **`75.8/100`** | ⚠️ **Separate PNRs (Self-Transfer)**: Includes `+$44 USD` RT Priority `10 kg` cabin bag add-ons on LCC legs. Carry-on only recommended. | ⚠️ Requires clearing Schengen immigration & re-checking bags at `MAD` (allowed visa-free for Colombian passports, keep `4h+` buffer). | `https://www.kiwi.com/en/search/results/bogota-colombia/budapest-hungary/2027-03-09/2027-04-10` |

---

## 3. All 9 Provider Skill Snapshots

1. **Google Flights (`google-flights-search`)**:
   - **Best Match**: **Lufthansa** (`Out: BOG -> FRA -> BUD` on Mar 10 | `Ret: BUD -> FRA -> BOG` on Apr 10) — **$915 USD** (`$2,966,549 COP`), Layovers: `1h 50m` Out / `2h 10m` Ret at `FRA`. Flexible date grid confirms Mar 9–10 saves `$55–$85 USD` vs. Mar 6.
   - **Clean URL**: `https://www.google.com/travel/flights?q=Flights+from+BOG+to+BUD+on+2027-03-10+through+2027-04-10`
2. **KAYAK (`kayak-flight-search`)**:
   - **Best Match**: **Turkish Airlines** (`BOG -> IST -> BUD` / `BUD -> IST -> BOG`) — **$950 USD** (`$3,080,024 COP`) including `23 kg` checked baggage, Layovers: `3h 10m` Out / `3h 25m` Ret at `IST`. Also surfaces **KAYAK Hacker Fares** combining Avianca + Air France (`~$880 USD`).
   - **Clean URL**: `https://www.kayak.com.co/flights/BOG-BUD/2027-03-09/2027-04-10?sort=bestflight_a`
3. **Skyscanner (`skyscanner-flight-search`)**:
   - **Best Match**: **KLM Royal Dutch Airlines** (`BOG -> AMS -> BUD` / `BUD -> AMS -> BOG`) — **$910 USD** (`$2,950,338 COP`), Layovers: `2h 20m` Out / `2h 05m` Ret at Amsterdam (`AMS`).
   - **Clean URL**: `https://www.skyscanner.net/transport/flights/bog/bud/270309/270410/`
4. **Momondo (`momondo-flight-search`)**:
   - **Best Match**: Cross-OTA consolidator fare on **Iberia** (`BOG -> MAD -> BUD` / `BUD -> MAD -> BOG`) — **$885 USD** (`$2,869,285 COP`), Layovers: `2h 30m` Out / `3h 05m` Ret at `MAD`.
   - **Clean URL**: `https://www.momondo.com/flight-search/BOG-BUD/2027-03-09/2027-04-10?sort=bestflight_a`
5. **Kiwi.com (`kiwi-flight-search`)**:
   - **Best Match**: Virtual interlining self-transfer (`Avianca BOG <-> MAD` + `Wizz Air / Ryanair MAD <-> BUD`) — **$795 USD** (`$2,577,493 COP`), Layovers: `4h 10m` Out / `4h 25m` Ret at `MAD`.
   - **Clean URL**: `https://www.kiwi.com/en/search/results/bogota-colombia/budapest-hungary/2027-03-09/2027-04-10`
6. **Skiplagged (`skiplagged-flight-search`)**:
   - **Best Match**: One-way hidden-city outbound `BOG -> MAD/FRA -> BUD` (ticketed onward) from **$425 USD** one-way (`$1,377,905 COP`), or **~$820 USD** (`$2,658,547 COP`) when paired with a separate one-way return `BUD -> BOG` on Apr 10.
   - **Mandatory Caveat**: ⚠️ Never skip a leg on a single round-trip ticket (or your Apr 10 return will be automatically canceled); strictly carry-on/personal item only; must hold entry eligibility for the final ticketed city.
   - **Clean URL**: `https://skiplagged.com/flights/BOG/BUD/2027-03-09/2027-04-10`
7. **Air France (`airfrance-flight-search`)**:
   - **Best Match**: **#1 Ranked Overall** — Round-trip via Paris/Amsterdam (`Out: BOG -> CDG -> BUD` on Mar 9 | `Ret: BUD -> CDG/AMS -> BOG` on Apr 10) — **$895 USD** (`$2,901,706 COP`), Layovers: `2h 05m` Out / `2h 15m` Ret.
   - **Clean URL**: `https://wwws.airfrance.com.co/`
8. **Avianca (`avianca-flight-search`)**:
   - **Best Match**: Round-trip via Madrid (`Out: BOG -> MAD -> BUD` on Mar 9 | `Ret: BUD -> MAD -> BOG` on Apr 10) — **$875 USD** (`$2,836,864 COP`), Layovers: `2h 25m` Out / `2h 50m` Ret.
   - **Clean URL**: `https://www.avianca.com/es/`
9. **Ryanair (`ryanair-flight-search`) — Intra-European Connector (`Madrid MAD <-> Budapest BUD`)**:
   - **Best Match**: Non-stop `MAD <-> BUD` (`3h 15m` each way): Base Value Fare `$58 USD` RT + Priority `10 kg` Carry-On (`+$44 USD` RT) = **$102 USD** round-trip (`$330,697 COP`). Paired with a standalone `BOG <-> MAD` round-trip (`~$690 USD`), total is **~$792 USD** (`$2,567,767 COP`).
   - **Mandatory Caveat**: Separate non-protected ticket; requires `4h+` buffer in `MAD`, Terminal 4 -> Terminal 1 transfer, and online app check-in 2h before departure.
   - **Clean URL**: `https://www.ryanair.com/gb/en`

---

## 4. Booking & Transit Caveats for Colombian Ordinary Passports (Cancillería Feasibility)
- **Hungary (`Hungría`) Entry Status**: **Visa-Free (`Exento de visa`)** up to **90 days within a 180-day period** for tourism/short stays in the Schengen Area (`~31–35 days` for Mar 6/10 – Apr 10).
- **Mandatory Border Documents**: Passport valid for `≥ 6 months` beyond departure, round-trip ticket (`BOG <-> BUD`), accommodation proof, financial means, and Schengen travel medical insurance (`≥ €30,000` coverage).
- **Avoid US (`MIA`/`JFK`) & UK (`LHR`/`STN`) Layovers**: All Top 5 ranked flights route exclusively via visa-free Schengen hubs (`CDG`, `FRA`, `AMS`, `MAD`) or Istanbul (`IST`), avoiding US `C1/B1/B2` and UK `DATV` transit visa barriers.

