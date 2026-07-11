# HRNN Challenger Comparison

Research comparison only. Not used in production forecasts.

Generated: 2026-07-11T12:54:21+00:00

## Implementation status

Deterministic HRNN-style challenger artifact. Full PyTorch MAP checkpoint sweep remains a follow-up using this schema.

## Window C headline scoreboard

| Model | Headline NSA MAE | Headline SA MAE | Core NSA MAE | Core SA MAE |
|---|---:|---:|---:|---:|
| Legacy proxy (not full model) | 0.0011 | 0.0011 | 0.0012 | 0.0012 |
| Production Tier 1 fallback | 0.0012 | 0.0011 | 0.0012 | 0.0012 |
| Production Tier 3 fallback | 0.0011 | 0.0011 | 0.0012 | 0.0012 |
| HRNN | 0.0012 | 0.0012 | 0.0014 | 0.0015 |
| I-GRU | 0.0012 | 0.0012 | 0.0012 | 0.0013 |
| Seasonal AR | 0.0011 | 0.0011 | 0.0012 | 0.0012 |

## Component league table

| Component | Verdict | Best model | Weight | Production MAE | HRNN MAE | I-GRU MAE | Seasonal AR MAE |
|---|---|---|---:|---:|---:|---:|---:|
| Electricity | SEASONAL AR WINS | Seasonal AR | 2.506 | 0.0110 | 0.0112 | 0.0120 | 0.0078 |
| Lodging away from home | SEASONAL AR WINS | Seasonal AR | 1.483 | 0.0217 | 0.0217 | 0.0214 | 0.0191 |
| Airline fares | SEASONAL AR WINS | Seasonal AR | 1.107 | 0.0369 | 0.0385 | 0.0397 | 0.0341 |
| Women's suits and separates | SEASONAL AR WINS | Seasonal AR | 0.389 | 0.0220 | 0.0246 | 0.0252 | 0.0141 |
| Household furnishings and operations | SEASONAL AR WINS | Seasonal AR | 4.202 | 0.0037 | 0.0039 | 0.0040 | 0.0032 |
| Hospital and related services | SEASONAL AR WINS | Seasonal AR | 2.595 | 0.0045 | 0.0045 | 0.0047 | 0.0037 |
| Women's dresses | SEASONAL AR WINS | Seasonal AR | 0.111 | 0.0352 | 0.0385 | 0.0400 | 0.0226 |
| Car and truck rental | SEASONAL AR WINS | Seasonal AR | 0.140 | 0.0367 | 0.0377 | 0.0382 | 0.0276 |
| Jewelry | SEASONAL AR WINS | Seasonal AR | 0.146 | 0.0325 | 0.0340 | 0.0351 | 0.0239 |
| Girls' apparel | SEASONAL AR WINS | Seasonal AR | 0.150 | 0.0285 | 0.0308 | 0.0316 | 0.0208 |
| Other fresh fruits | SEASONAL AR WINS | Seasonal AR | 0.315 | 0.0159 | 0.0162 | 0.0170 | 0.0123 |
| Tuition, other school fees, and childcare | SEASONAL AR WINS | Seasonal AR | 2.487 | 0.0019 | 0.0020 | 0.0019 | 0.0015 |
| Prescription drugs | SEASONAL AR WINS | Seasonal AR | 0.917 | 0.0056 | 0.0055 | 0.0058 | 0.0046 |
| Men's shirts and sweaters | SEASONAL AR WINS | Seasonal AR | 0.131 | 0.0225 | 0.0244 | 0.0256 | 0.0157 |
| Spices, seasonings, condiments, sauces | SEASONAL AR WINS | Seasonal AR | 0.318 | 0.0091 | 0.0089 | 0.0099 | 0.0066 |
| Motor vehicle fees | SEASONAL AR WINS | Seasonal AR | 0.511 | 0.0066 | 0.0071 | 0.0070 | 0.0050 |
| Carbonated drinks | SEASONAL AR WINS | Seasonal AR | 0.326 | 0.0110 | 0.0108 | 0.0116 | 0.0086 |
| Other goods and services | TIE | Seasonal AR | 2.892 | 0.0032 | 0.0030 | 0.0033 | 0.0029 |
| Men's pants and shorts | SEASONAL AR WINS | Seasonal AR | 0.121 | 0.0209 | 0.0209 | 0.0221 | 0.0155 |
| Sporting goods | SEASONAL AR WINS | Seasonal AR | 0.520 | 0.0072 | 0.0070 | 0.0074 | 0.0059 |
| Women's footwear | SEASONAL AR WINS | Seasonal AR | 0.276 | 0.0103 | 0.0112 | 0.0115 | 0.0080 |
| Women's underwear, nightwear, swimwear and accessories | SEASONAL AR WINS | Seasonal AR | 0.244 | 0.0147 | 0.0150 | 0.0156 | 0.0123 |
| Health insurance | I-GRU WINS | I-GRU | 0.826 | 0.0087 | 0.0111 | 0.0080 | 0.0144 |
| Other recreation services | TIE | Seasonal AR | 1.791 | 0.0055 | 0.0053 | 0.0057 | 0.0052 |
| Women's outerwear | SEASONAL AR WINS | Seasonal AR | 0.067 | 0.0309 | 0.0315 | 0.0328 | 0.0232 |
| Intracity transportation | SEASONAL AR WINS | Seasonal AR | 0.348 | 0.0087 | 0.0090 | 0.0089 | 0.0073 |
| Men's suits, sport coats, and outerwear | SEASONAL AR WINS | Seasonal AR | 0.099 | 0.0250 | 0.0249 | 0.0262 | 0.0201 |
| Fuel oil | HRNN WINS | HRNN | 0.117 | 0.0555 | 0.0515 | 0.0530 | 0.0550 |
| Frozen and freeze dried prepared foods | SEASONAL AR WINS | Seasonal AR | 0.290 | 0.0097 | 0.0094 | 0.0101 | 0.0083 |
| Food at employee sites and schools | HRNN WINS | HRNN | 0.063 | 0.0273 | 0.0210 | 0.0229 | 0.0249 |
| Boys' apparel | SEASONAL AR WINS | Seasonal AR | 0.120 | 0.0186 | 0.0188 | 0.0197 | 0.0153 |
| Communication | TIE | Seasonal AR | 3.177 | 0.0033 | 0.0036 | 0.0034 | 0.0032 |
| Water and sewerage maintenance | SEASONAL AR WINS | Seasonal AR | 0.777 | 0.0025 | 0.0025 | 0.0027 | 0.0020 |
| Men's footwear | SEASONAL AR WINS | Seasonal AR | 0.191 | 0.0112 | 0.0118 | 0.0121 | 0.0092 |
| Fresh fish and seafood | SEASONAL AR WINS | Seasonal AR | 0.169 | 0.0094 | 0.0092 | 0.0100 | 0.0071 |
| Ham | SEASONAL AR WINS | Seasonal AR | 0.067 | 0.0211 | 0.0215 | 0.0229 | 0.0154 |
| Processed fish and seafood | SEASONAL AR WINS | Seasonal AR | 0.147 | 0.0108 | 0.0103 | 0.0115 | 0.0083 |
| Other miscellaneous foods | TIE | Seasonal AR | 0.567 | 0.0072 | 0.0067 | 0.0075 | 0.0066 |
| Owners' equivalent rent of residences | TIE | I-GRU | 25.700 | 0.0008 | 0.0009 | 0.0008 | 0.0012 |
| Used cars and trucks | TIE | HRNN | 2.628 | 0.0109 | 0.0108 | 0.0114 | 0.0124 |
| Newspapers and magazines | SEASONAL AR WINS | Seasonal AR | 0.054 | 0.0274 | 0.0252 | 0.0283 | 0.0220 |
| Other intercity transportation | SEASONAL AR WINS | Seasonal AR | 0.232 | 0.0160 | 0.0159 | 0.0166 | 0.0148 |
| Pet services including veterinary | SEASONAL AR WINS | Seasonal AR | 0.540 | 0.0059 | 0.0058 | 0.0060 | 0.0054 |
| Men's underwear, nightwear, swimwear and accessories | SEASONAL AR WINS | Seasonal AR | 0.133 | 0.0129 | 0.0125 | 0.0135 | 0.0108 |
| Other recreational goods | SEASONAL AR WINS | Seasonal AR | 0.381 | 0.0072 | 0.0071 | 0.0074 | 0.0064 |
| Apples | SEASONAL AR WINS | Seasonal AR | 0.077 | 0.0170 | 0.0163 | 0.0178 | 0.0134 |
| Recreational books | SEASONAL AR WINS | Seasonal AR | 0.055 | 0.0224 | 0.0212 | 0.0230 | 0.0176 |
| Fresh biscuits, rolls, muffins | SEASONAL AR WINS | Seasonal AR | 0.117 | 0.0144 | 0.0131 | 0.0147 | 0.0121 |
| Other meats | SEASONAL AR WINS | Seasonal AR | 0.192 | 0.0095 | 0.0092 | 0.0100 | 0.0081 |
| Full service meals and snacks | TIE | HRNN | 2.329 | 0.0018 | 0.0017 | 0.0018 | 0.0019 |
| Garbage and trash collection | SEASONAL AR WINS | Seasonal AR | 0.356 | 0.0037 | 0.0035 | 0.0039 | 0.0029 |
| Ice cream and related products | SEASONAL AR WINS | Seasonal AR | 0.110 | 0.0146 | 0.0136 | 0.0150 | 0.0124 |
| Breakfast cereal | SEASONAL AR WINS | Seasonal AR | 0.132 | 0.0128 | 0.0122 | 0.0133 | 0.0110 |
| Nonfrozen noncarbonated juices and drinks | SEASONAL AR WINS | Seasonal AR | 0.339 | 0.0074 | 0.0073 | 0.0076 | 0.0067 |
| Boys' and girls' footwear | SEASONAL AR WINS | Seasonal AR | 0.125 | 0.0129 | 0.0126 | 0.0137 | 0.0110 |
| Uncooked beef steaks | SEASONAL AR WINS | Seasonal AR | 0.236 | 0.0135 | 0.0129 | 0.0139 | 0.0126 |
| Purchase, subscription, and rental of video | SEASONAL AR WINS | Seasonal AR | 0.181 | 0.0126 | 0.0122 | 0.0131 | 0.0113 |
| Other fats and oils including peanut butter | SEASONAL AR WINS | Seasonal AR | 0.105 | 0.0111 | 0.0108 | 0.0118 | 0.0090 |
| Snacks | TIE | Seasonal AR | 0.363 | 0.0077 | 0.0072 | 0.0082 | 0.0071 |
| Televisions | SEASONAL AR WINS | Seasonal AR | 0.103 | 0.0127 | 0.0131 | 0.0134 | 0.0106 |
| Bacon, breakfast sausage, and related products | SEASONAL AR WINS | Seasonal AR | 0.131 | 0.0117 | 0.0115 | 0.0123 | 0.0101 |
| Other bakery products | SEASONAL AR WINS | Seasonal AR | 0.215 | 0.0078 | 0.0075 | 0.0082 | 0.0068 |
| Infants' and toddlers' apparel | SEASONAL AR WINS | Seasonal AR | 0.099 | 0.0144 | 0.0153 | 0.0152 | 0.0124 |
| Cakes, cupcakes, and cookies | SEASONAL AR WINS | Seasonal AR | 0.207 | 0.0081 | 0.0077 | 0.0086 | 0.0071 |
| Rent of primary residence | TIE | I-GRU | 7.679 | 0.0008 | 0.0009 | 0.0008 | 0.0013 |
| Coffee | SEASONAL AR WINS | Seasonal AR | 0.227 | 0.0102 | 0.0103 | 0.0107 | 0.0094 |
| Other uncooked poultry including turkey | SEASONAL AR WINS | Seasonal AR | 0.077 | 0.0144 | 0.0138 | 0.0148 | 0.0121 |
| Potatoes | SEASONAL AR WINS | Seasonal AR | 0.066 | 0.0159 | 0.0173 | 0.0172 | 0.0132 |
| Motor vehicle maintenance and repair | TIE | Seasonal AR | 1.034 | 0.0056 | 0.0060 | 0.0058 | 0.0055 |
| Bread | SEASONAL AR WINS | Seasonal AR | 0.171 | 0.0079 | 0.0072 | 0.0081 | 0.0069 |
| Other beverage materials including tea | SEASONAL AR WINS | Seasonal AR | 0.096 | 0.0119 | 0.0111 | 0.0122 | 0.0101 |
| Other processed fruits and vegetables including dried | SEASONAL AR WINS | Seasonal AR | 0.080 | 0.0103 | 0.0105 | 0.0108 | 0.0082 |
| Leased cars and trucks | SEASONAL AR WINS | Seasonal AR | 0.383 | 0.0070 | 0.0072 | 0.0072 | 0.0066 |
| Canned fruits and vegetables | SEASONAL AR WINS | Seasonal AR | 0.101 | 0.0107 | 0.0106 | 0.0112 | 0.0091 |
| Limited service meals and snacks | TIE | HRNN | 2.634 | 0.0012 | 0.0012 | 0.0012 | 0.0015 |
| Pork chops | SEASONAL AR WINS | Seasonal AR | 0.045 | 0.0201 | 0.0188 | 0.0208 | 0.0167 |
| Other pork including roasts, steaks, and ribs | SEASONAL AR WINS | Seasonal AR | 0.094 | 0.0174 | 0.0165 | 0.0179 | 0.0158 |
| Soups | SEASONAL AR WINS | Seasonal AR | 0.088 | 0.0126 | 0.0124 | 0.0129 | 0.0109 |
| Flour and prepared flour mixes | SEASONAL AR WINS | Seasonal AR | 0.038 | 0.0142 | 0.0146 | 0.0155 | 0.0103 |
| Audio equipment | SEASONAL AR WINS | Seasonal AR | 0.045 | 0.0176 | 0.0172 | 0.0182 | 0.0144 |

## Adoption candidates

- SEHE01 Fuel oil: HRNN beats production proxy in window C by 0.40 pp m/m; window B gap 0.26 pp.
- SEFV03 Food at employee sites and schools: HRNN beats production proxy in window C by 0.63 pp m/m; window B gap 0.40 pp.
- SETA02 Used cars and trucks: HRNN beats production proxy in window C by 0.01 pp m/m; window B gap 0.03 pp.
- SEFV01 Full service meals and snacks: HRNN beats production proxy in window C by 0.01 pp m/m; window B gap 0.01 pp.
- SEFV02 Limited service meals and snacks: HRNN beats production proxy in window C by 0.01 pp m/m; window B gap 0.00 pp.
- SEMC Professional services: HRNN beats production proxy in window C by 0.00 pp m/m; window B gap 0.01 pp.
- SERB01 Pets and pet products: HRNN beats production proxy in window C by 0.02 pp m/m; window B gap 0.01 pp.
- SEFC02 Uncooked beef roasts: HRNN beats production proxy in window C by 0.07 pp m/m; window B gap 0.07 pp.
- SERA06 Recorded music and music subscriptions: HRNN beats production proxy in window C by 0.03 pp m/m; window B gap 0.04 pp.
- SEFH Eggs: HRNN beats production proxy in window C by 0.03 pp m/m; window B gap 0.03 pp.
- SEFK03 Citrus fruits: HRNN beats production proxy in window C by 0.03 pp m/m; window B gap 0.00 pp.
- SEFW01 Beer, ale, and other malt beverages at home: HRNN beats production proxy in window C by 0.02 pp m/m; window B gap 0.02 pp.

## Honest notes

- Production component MAE in this first artifact is a tier-style endogenous proxy, because the existing production backtest artifact stores headline rows but not a full per-component historical forecast panel.
- SETB01 gasoline uses the same EIA weekly regular gasoline calendar-month measurement in HRNN, I-GRU, Seasonal AR, Production Tier 1 fallback, and Production Tier 3 fallback whenever the monthly EIA comparison is available.
- Aggregate-node challenger forecasts can look better than bottom-up rows because they forecast published aggregates directly; bottom-up leaf aggregation is the apples-to-apples view.
- Window A undercredits production external feeds that did not have current local cached histories before modern feed availability.
- The current BLS hierarchy is applied across history; historical parent changes are documented rather than reconstructed.
