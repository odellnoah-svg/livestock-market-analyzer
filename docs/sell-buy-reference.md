# Sell-Buy Marketing Reference

**Purpose:** Knowledge base for the Livestock Market Analyzer's recommendation engine. Distilled from Doug Ferguson's sell-buy marketing class (Jan 2026) and the Value of Gain workbook. All formulas here are implementable; decision rules are tagged for the rules engine.

---

## 1. Core Principles (govern all recommendations)

1. **Profit is a cost of production.** Profit is budgeted as an expense (BPCOG) before evaluating any trade, never hoped for afterward.
2. **Sell the overvalued, buy or keep the undervalued.** Nothing is over/undervalued in isolation — only relative to something else (Law of Relativity). All analysis is relationship analysis.
3. **Marketing is a continuum of inventory liquidation and replenishment.** Selling only generates cash flow; profit is paired with replenishment. **Never recommend a sell without an identified replacement** (unless deliberately reducing inventory for feed/capacity reasons).
4. **Deal with today.** Real-time cash flow reckoning: no forecasts, no cycles, no board, no "what we paid." Current price relationships are the only input. What was paid for owned animals has no bearing on what to do now.
5. **If you own animals and are not willing to sell them, you have effectively bought them today at today's price.** Owned inventory is continuously re-evaluated at current market.
6. **Always have money and grass.** Cattle are the least essential leg of the inventory triangle (feed and money are the base). Never recommend trades that exhaust cash or exceed grazing capacity.
7. **Take small profits often.** Turnover drives cash flow. A qualifying trade at modest excess profit beats holding for a bigger one.
8. **Volatility is the friend; not all weight classes move at the same rate.** Divergence between classes is the trade signal.

---

## 2. Cost Foundation

### Cost of Gain (COG)
```
COG ($/lb) = Total cost attached to the animals sold ÷ total lbs gained
```
Total cost includes: feed (charged at the HIGHER of market value or cost of production, including opportunity cost of owned pasture/land rent), yardage/overhead allocation, pharma, freight, sale costs (commission), interest, death loss, salary. Everything flowing out of the account.

**Yardage method:** total annual overhead ÷ head ÷ 365 = $/head/day, then pad (+$0.05/head/day cushion). Example: $89,865 overhead ÷ 500 head ÷ 365 = $0.49 → use $0.54.

### Break Profit Cost of Gain (BPCOG)
```
BPCOG = COG × (1 + profit%)      profit% range: 10%–30%
```
- <10% profit is not enough; >30% disqualifies too many good buy-backs.
- The workbook default is 30% (×1.3). Class examples range $1.10–$2.00+ BPCOG.
- **BPCOG is the fulcrum.** Finding the Efficient Market Value of replacements hinges on it.
- Breeding stock version: cost is a **monthly charge** ($/head/month, profit included), not $/lb.

### BPCOG adjustments when swapping sex/class (from a steer sale)
| Buy-back class | Adjustment |
|---|---|
| Steers → steers | none |
| Steers → heifers | bump COG +$0.09–0.15/lb (more at high price levels; class used +$0.30 at 2026 prices). Heifer gain slows at puberty. |
| Steers → bulls | same bump as heifers (castration cost, tetanus, post-castration gain lag). Require extra purchase discount. |
| Heifers sold → steer buy-back | **keep the heifer card as-is.** Never bump COG down; COG comes from the animal sold. |

---

## 3. Value of Gain (VOG)

```
VOG ($/lb) = (heavier $/hd − lighter $/hd) ÷ (heavier wt − lighter wt)
```
computed from same-day market quotes for adjacent weight classes.

- **VOG is NOT trading.** It answers: *does it pay to put weight on?* and *which cattle can we add value to fastest?* (virgin buy targeting).
- Decision rule: `VOG > BPCOG` → the market is paying you to feed; favor lighter purchases / holding to grow. `VOG < BPCOG` → the market is not paying for gain in that weight span; favor buying weight instead of feeding it on — but see §7 (do not exit to cash; relationships > VOG).
- VOG varies sharply by weight span and by market on the same day (class example: $2.78 in TN vs $1.48 in Bassett NE, same week). Compute per span, per market.
- **Manipulated VOG check:** any added-input plan (e.g., creep) must be evaluated with (a) the price slide against the heavier out-weight, (b) condition/fleshy discounts, and (c) the feed's effect on COG — not at the current flat price.

---

## 4. The Cattle Square (trade evaluation)

The core sell-buy computation. For a proposed sell → buy-back pair:

```
Gross Sale $/hd = sell weight × sell price
Gross Buy  $/hd = buy weight × buy price
Net $/hd        = Gross Sale − Gross Buy
Net Weight      = sell weight − buy weight
ROG ($/lb)      = Net $/hd ÷ Net Weight          (Return on the Gain)
Excess Profit $/hd = (ROG − BPCOG) × Net Weight
```

- If sell price = buy price ($/lb), then ROG = that price.
- **Qualifying trade:** ROG ≥ BPCOG (profit target already embedded in BPCOG; excess profit ≥ 0 means target is hit). Recommendations then rank by excess profit $/hd, with a secondary lens on cash-per-head freed and turnover speed.
- Two valid buy-backs can differ: nearer weight = higher ROG, lighter weight = more cash out per head and stretches feed. Both can hit target — surface both, note the tradeoff.

### Leapfrog trades (buy heavier than sold)
When buying back a heavier animal cheaper on $/hd or nearly even: Net Weight is negative; a negative ROG minus BPCOG times negative pounds yields captured value. Class example: sell 530# @ $3.80 = $2,014; buy 595# @ $3.30 = $1,963.50 → captured ≈ $148/hd (the $50.50 cash + 65 lbs of gain acquired below cost). **Rule:** flag any case where a heavier class sells at/below the $/hd of a lighter owned class ("we don't build cards for leapfrogs — be paying attention").

---

## 5. Efficient Market Value (EMV) & Barn Cards

**EMV = the maximum bid on a replacement that still hits the profit target.**

```
EMV $/hd  = Gross Sale $/hd − BPCOG × (sell wt − buy wt)
EMV $/lb  = EMV $/hd ÷ buy weight
```
(Equivalent workbook form: max buy $/lb = (BPCOG × (buyWt − sellWt) + sell $/hd) ÷ buyWt — same equation for lighter or heavier buy-backs.)

**Barn card:** given an executed/priced sell, tabulate EMV $/lb across the candidate buy weight range (e.g., 350–600# in 50# steps), one column per class (steers @ base BPCOG; heifers/bulls @ bumped BPCOG). The card is compared live against actual quotes: any class quoted **below** its EMV is a qualifying buy-back.

Card behavior checks (validation + insight):
- High COG → card favors buying weight (cheaper to buy lbs than feed them on).
- Low COG → card favors light cattle and feeding.
- COG > sell price → **inverted card** (slide runs the opposite way) — flag explicitly.

---

## 6. Breeding Stock: Intrinsic Value (IV)

Boil every female down to core value so the whole female spectrum is comparable:

```
IV = Cull value + Calf value(s) − Cost to Carry
   Cull value   = cow weight × slaughter (kill) price for her type
   Calf value   = calf sale weight × price (use avg of steer & heifer price)
   Cost to Carry = months owned until calf sale × $/month (profit included)
```
- Months = months until calving + months to target calf sale age (class sells at 8 months / ~500#).
- 3-in-1 (pair + bred): count both calves' value; carry through second calf split.
- Anything paid above IV is **blue-sky premium**.
- Re-assess continuously; assume eventual liquidation of the cow (the "10-year calculator is out" — no multi-year payback forecasting).

### Over/undervalued test
```
Deviation = Actual Value (AV, ring price) − IV
```
- AV > IV → overvalued → **sell candidate**
- AV < IV → undervalued → **buy candidate**
- Rank a sale's offering by deviation (Female Value Deviation view).

### Class-swap trade test (breeding ↔ breeding, stocker ↔ breeding)
```
IV given up  = Sell IV − Buy IV
AV received  = Sell AV − Buy AV
Good trade when AV received > IV given up  ("the number on the right is higher")
```
For stocker ↔ breeding swaps, value the stocker at its **IV to fats** (comparison-animal formula does not apply):
```
Stocker IV $/hd = Fat $/hd − BPCOG × (fat wt − stocker wt)
```
Cows eat more than stockers — carry-cost realism check on any stocker→cow recommendation.

### Known structural relationships (priors for the engine)
- The 10-year paradigm and calving-window demand put persistent premiums on young bred females and preferred calving windows; buyers rarely discount for months-still-to-carry. First-calf heifers are historically the most overvalued class.
- Open-cow problem play: sell open cull, buy back a bred weigh-up class for near-even money.
- Party girls / undesirables: IV them honestly (lighter weaning, discounts); often worth more split or after a straighten-out coupon.

---

## 7. Holding, Money, and Timing Rules

- **VOG < COG is not a reason to exit to cash.** Selling and holding money ("money undervalued") loses to inflation and re-entry risk (Bismarck example: 60 head out, 49 head back). If a pattern of undervalued-money sells emerges, the problem is cost/relationship literacy — pause trading, fix inputs.
- Held inventory that can't trade profitably today: hold and keep re-checking (class: held sorted-off head until a qualifying trade appeared). Deal with today, every day.
- Narrow the sell→buy window to minimize market-move risk; exposure in sell-buy is the gap between legs, not the ownership period.
- **Capacity rule:** if at capacity on pens, money, feed, or labor — no buy recommendations; consider sells that create slack. Below capacity = able to buy opportunistically and drought-resilient.
- **Drought play:** don't just disperse (everyone sells together, then rebuilds together). Trade down in forage demand (e.g., pairs → stockers head-for-head), stay invested, trade back when relationships favor it.
- Location/venue math: comparing venues requires shrink %, freight $/loaded mile, commission, fees → needed $/lb difference to break even. Pencil shrink at home vs actual shrink hauling. Net > gross price.

---

## 8. Recommendation Engine Outputs (what the analyzer should produce)

Given: current inventory (class, head, weights, COG/BPCOG per enterprise), current market quotes (per barn), seasonal indexes, and constraints (cash, feed, capacity):

1. **Barn card per owned class** — EMV table vs live quotes; highlight qualifying buy-backs (quote < EMV) with excess profit $/hd and $/lot.
2. **Relationship matrix** — current $/lb and $/hd across weight classes/species per market, vs 3–5yr rolling norms for each relationship (the norm makes over/undervalued quantitative).
3. **VOG panel** — per weight span per market vs user BPCOG; feed-or-buy-weight signal.
4. **Female Value Deviation** — IV vs AV across reported breeding classes; sell/buy candidates ranked.
5. **Trade candidates** — ranked qualifying cattle squares from owned inventory into current quotes, incl. leapfrog flags, sex-swap BPCOG adjustments, and venue-net math where multi-barn.
6. **Seasonal overlay** — where the current relationship sits vs its seasonal pattern (context only; never a hold-and-hope justification — Principle 4 governs).
7. **Constraint check** — every recommendation validated against money-and-grass and capacity rules before display.

---

## 9. Formula Quick Sheet

| Quantity | Formula |
|---|---|
| COG | total cost ÷ lbs gained |
| BPCOG | COG × (1 + profit%), profit% ∈ [0.10, 0.30] |
| VOG | Δ$/hd ÷ Δwt (adjacent classes, same day/market) |
| ROG | (sell $/hd − buy $/hd) ÷ (sell wt − buy wt) |
| Excess profit | (ROG − BPCOG) × net lbs |
| EMV $/hd | sell $/hd − BPCOG × (sell wt − buy wt) |
| EMV $/lb | EMV $/hd ÷ buy wt |
| Breeding IV | cull $ + calf $ − (months × $/mo) |
| Deviation | AV − IV |
| Swap test | good if (Sell AV − Buy AV) > (Sell IV − Buy IV) |
| Stocker IV to fats | fat $/hd − BPCOG × (fat wt − stocker wt) |

---

*Source: Doug Ferguson sell-buy marketing class materials (scanned slides, Jan 2026, OCR extracted) and Calf_weight_distribution__VOG__Sell-Buy.xlsx (Value of Gain sheet). Raw OCR text retained alongside this document for verification.*
