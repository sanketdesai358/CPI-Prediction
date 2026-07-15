# HRNN Challenger Comparison

Research comparison only. Not used in production forecasts.

Generated: 2026-07-15T13:26:27+00:00

## Implementation status

Deterministic HRNN-style challenger artifact. Full PyTorch MAP checkpoint sweep remains a follow-up using this schema.

## Window C headline scoreboard

| Model | Headline NSA MAE | Headline SA MAE | Core NSA MAE | Core SA MAE |
|---|---:|---:|---:|---:|
| Legacy proxy (not full model) | 0.0012 | 0.0011 | 0.0012 | 0.0012 |
| Production Tier 1 fallback | 0.0012 | 0.0012 | 0.0013 | 0.0013 |
| Production Tier 3 fallback | 0.0012 | 0.0011 | 0.0012 | 0.0013 |
| HRNN | 0.0013 | 0.0012 | 0.0015 | 0.0015 |
| I-GRU | 0.0012 | 0.0012 | 0.0013 | 0.0013 |
| Seasonal AR | 0.0011 | 0.0011 | 0.0012 | 0.0012 |

## Component league table

| Component | Verdict | Best model | Weight | Production MAE | HRNN MAE | I-GRU MAE | Seasonal AR MAE |
|---|---|---|---:|---:|---:|---:|---:|
| Electricity | SEASONAL AR WINS | Seasonal AR | 2.552 | 0.0108 | 0.0111 | 0.0118 | 0.0078 |
| Lodging away from home | SEASONAL AR WINS | Seasonal AR | 1.451 | 0.0222 | 0.0221 | 0.0219 | 0.0194 |
| Airline fares | SEASONAL AR WINS | Seasonal AR | 1.091 | 0.0374 | 0.0387 | 0.0401 | 0.0340 |
| Women's suits and separates | SEASONAL AR WINS | Seasonal AR | 0.385 | 0.0217 | 0.0242 | 0.0249 | 0.0140 |
| Household furnishings and operations | SEASONAL AR WINS | Seasonal AR | 4.244 | 0.0038 | 0.0039 | 0.0041 | 0.0032 |
| Hospital and related services | SEASONAL AR WINS | Seasonal AR | 2.607 | 0.0044 | 0.0045 | 0.0046 | 0.0036 |
| Car and truck rental | SEASONAL AR WINS | Seasonal AR | 0.157 | 0.0380 | 0.0390 | 0.0396 | 0.0281 |
| Women's dresses | SEASONAL AR WINS | Seasonal AR | 0.110 | 0.0348 | 0.0379 | 0.0395 | 0.0223 |
| Other fresh fruits | SEASONAL AR WINS | Seasonal AR | 0.307 | 0.0160 | 0.0164 | 0.0172 | 0.0121 |
| Jewelry | SEASONAL AR WINS | Seasonal AR | 0.140 | 0.0333 | 0.0346 | 0.0358 | 0.0248 |
| Girls' apparel | SEASONAL AR WINS | Seasonal AR | 0.148 | 0.0282 | 0.0304 | 0.0312 | 0.0207 |
| Tuition, other school fees, and childcare | SEASONAL AR WINS | Seasonal AR | 2.499 | 0.0018 | 0.0020 | 0.0019 | 0.0015 |
| Prescription drugs | SEASONAL AR WINS | Seasonal AR | 0.920 | 0.0055 | 0.0054 | 0.0058 | 0.0045 |
| Other goods and services | TIE | Seasonal AR | 2.906 | 0.0032 | 0.0031 | 0.0033 | 0.0029 |
| Men's shirts and sweaters | SEASONAL AR WINS | Seasonal AR | 0.128 | 0.0224 | 0.0243 | 0.0254 | 0.0158 |
| Spices, seasonings, condiments, sauces | SEASONAL AR WINS | Seasonal AR | 0.320 | 0.0090 | 0.0088 | 0.0097 | 0.0065 |
| Motor vehicle fees | SEASONAL AR WINS | Seasonal AR | 0.510 | 0.0066 | 0.0071 | 0.0070 | 0.0050 |
| Carbonated drinks | SEASONAL AR WINS | Seasonal AR | 0.324 | 0.0109 | 0.0107 | 0.0114 | 0.0087 |
| Communication | SEASONAL AR WINS | Seasonal AR | 3.140 | 0.0037 | 0.0040 | 0.0038 | 0.0034 |
| Men's pants and shorts | SEASONAL AR WINS | Seasonal AR | 0.120 | 0.0208 | 0.0207 | 0.0220 | 0.0154 |
| Other recreation services | TIE | Seasonal AR | 1.798 | 0.0055 | 0.0052 | 0.0057 | 0.0051 |
| Women's footwear | SEASONAL AR WINS | Seasonal AR | 0.272 | 0.0105 | 0.0113 | 0.0117 | 0.0082 |
| Sporting goods | SEASONAL AR WINS | Seasonal AR | 0.530 | 0.0072 | 0.0070 | 0.0075 | 0.0061 |
| Women's underwear, nightwear, swimwear and accessories | SEASONAL AR WINS | Seasonal AR | 0.245 | 0.0145 | 0.0148 | 0.0154 | 0.0121 |
| Intracity transportation | SEASONAL AR WINS | Seasonal AR | 0.354 | 0.0090 | 0.0092 | 0.0093 | 0.0074 |
| Health insurance | I-GRU WINS | I-GRU | 0.825 | 0.0086 | 0.0110 | 0.0079 | 0.0142 |
| Men's suits, sport coats, and outerwear | SEASONAL AR WINS | Seasonal AR | 0.099 | 0.0248 | 0.0246 | 0.0259 | 0.0199 |
| Women's outerwear | SEASONAL AR WINS | Seasonal AR | 0.065 | 0.0304 | 0.0311 | 0.0322 | 0.0232 |
| Frozen and freeze dried prepared foods | SEASONAL AR WINS | Seasonal AR | 0.296 | 0.0099 | 0.0096 | 0.0103 | 0.0084 |
| Fuel oil | HRNN WINS | HRNN | 0.106 | 0.0567 | 0.0527 | 0.0544 | 0.0563 |
| Fresh fish and seafood | SEASONAL AR WINS | Seasonal AR | 0.169 | 0.0096 | 0.0093 | 0.0102 | 0.0072 |
| Water and sewerage maintenance | SEASONAL AR WINS | Seasonal AR | 0.783 | 0.0025 | 0.0025 | 0.0026 | 0.0019 |
| Food at employee sites and schools | HRNN WINS | HRNN | 0.064 | 0.0268 | 0.0207 | 0.0226 | 0.0245 |
| Ham | SEASONAL AR WINS | Seasonal AR | 0.067 | 0.0209 | 0.0212 | 0.0227 | 0.0152 |
| Men's footwear | SEASONAL AR WINS | Seasonal AR | 0.192 | 0.0110 | 0.0116 | 0.0119 | 0.0090 |
| Boys' apparel | SEASONAL AR WINS | Seasonal AR | 0.119 | 0.0184 | 0.0186 | 0.0194 | 0.0153 |
| Processed fish and seafood | SEASONAL AR WINS | Seasonal AR | 0.148 | 0.0106 | 0.0101 | 0.0113 | 0.0082 |
| Used cars and trucks | TIE | HRNN | 2.679 | 0.0108 | 0.0107 | 0.0113 | 0.0122 |
| Other meats | SEASONAL AR WINS | Seasonal AR | 0.195 | 0.0099 | 0.0095 | 0.0103 | 0.0083 |
| Pet services including veterinary | SEASONAL AR WINS | Seasonal AR | 0.543 | 0.0059 | 0.0057 | 0.0059 | 0.0053 |
| Other miscellaneous foods | TIE | Seasonal AR | 0.571 | 0.0071 | 0.0066 | 0.0073 | 0.0065 |
| Fresh biscuits, rolls, muffins | SEASONAL AR WINS | Seasonal AR | 0.116 | 0.0148 | 0.0134 | 0.0151 | 0.0122 |
| Owners' equivalent rent of residences | TIE | I-GRU | 25.849 | 0.0008 | 0.0009 | 0.0008 | 0.0012 |
| Newspapers and magazines | SEASONAL AR WINS | Seasonal AR | 0.055 | 0.0270 | 0.0249 | 0.0279 | 0.0219 |
| Men's underwear, nightwear, swimwear and accessories | SEASONAL AR WINS | Seasonal AR | 0.134 | 0.0127 | 0.0124 | 0.0134 | 0.0107 |
| Other recreational goods | SEASONAL AR WINS | Seasonal AR | 0.391 | 0.0074 | 0.0074 | 0.0077 | 0.0067 |
| Recreational books | SEASONAL AR WINS | Seasonal AR | 0.054 | 0.0224 | 0.0213 | 0.0230 | 0.0176 |
| Apples | SEASONAL AR WINS | Seasonal AR | 0.079 | 0.0168 | 0.0162 | 0.0175 | 0.0135 |
| Other intercity transportation | SEASONAL AR WINS | Seasonal AR | 0.232 | 0.0158 | 0.0159 | 0.0165 | 0.0147 |
| Garbage and trash collection | SEASONAL AR WINS | Seasonal AR | 0.358 | 0.0036 | 0.0035 | 0.0038 | 0.0029 |
| Breakfast cereal | SEASONAL AR WINS | Seasonal AR | 0.133 | 0.0127 | 0.0121 | 0.0132 | 0.0109 |
| Other fats and oils including peanut butter | SEASONAL AR WINS | Seasonal AR | 0.107 | 0.0113 | 0.0110 | 0.0120 | 0.0091 |
| Full service meals and snacks | TIE | HRNN | 2.347 | 0.0018 | 0.0017 | 0.0018 | 0.0018 |
| Televisions | SEASONAL AR WINS | Seasonal AR | 0.104 | 0.0128 | 0.0132 | 0.0136 | 0.0106 |
| Uncooked beef steaks | SEASONAL AR WINS | Seasonal AR | 0.239 | 0.0134 | 0.0129 | 0.0139 | 0.0125 |
| Snacks | TIE | Seasonal AR | 0.365 | 0.0076 | 0.0071 | 0.0081 | 0.0070 |
| Ice cream and related products | SEASONAL AR WINS | Seasonal AR | 0.109 | 0.0144 | 0.0134 | 0.0147 | 0.0124 |
| Boys' and girls' footwear | SEASONAL AR WINS | Seasonal AR | 0.126 | 0.0128 | 0.0125 | 0.0136 | 0.0111 |
| Nonfrozen noncarbonated juices and drinks | SEASONAL AR WINS | Seasonal AR | 0.334 | 0.0077 | 0.0076 | 0.0078 | 0.0070 |
| Motor vehicle insurance | TIE | I-GRU | 2.569 | 0.0056 | 0.0069 | 0.0055 | 0.0077 |
| Infants' and toddlers' apparel | SEASONAL AR WINS | Seasonal AR | 0.097 | 0.0145 | 0.0154 | 0.0153 | 0.0125 |
| Bacon, breakfast sausage, and related products | SEASONAL AR WINS | Seasonal AR | 0.130 | 0.0117 | 0.0115 | 0.0123 | 0.0102 |
| Cheese and related products | TIE | Seasonal AR | 0.250 | 0.0087 | 0.0080 | 0.0088 | 0.0079 |
| Purchase, subscription, and rental of video | SEASONAL AR WINS | Seasonal AR | 0.181 | 0.0124 | 0.0120 | 0.0130 | 0.0113 |
| Other uncooked poultry including turkey | SEASONAL AR WINS | Seasonal AR | 0.076 | 0.0147 | 0.0139 | 0.0151 | 0.0122 |
| Other bakery products | SEASONAL AR WINS | Seasonal AR | 0.219 | 0.0077 | 0.0075 | 0.0081 | 0.0069 |
| Bread | SEASONAL AR WINS | Seasonal AR | 0.173 | 0.0079 | 0.0072 | 0.0081 | 0.0068 |
| Rent of primary residence | TIE | I-GRU | 7.716 | 0.0008 | 0.0010 | 0.0008 | 0.0013 |
| Other beverage materials including tea | SEASONAL AR WINS | Seasonal AR | 0.094 | 0.0123 | 0.0115 | 0.0125 | 0.0104 |
| Cakes, cupcakes, and cookies | SEASONAL AR WINS | Seasonal AR | 0.206 | 0.0080 | 0.0077 | 0.0085 | 0.0072 |
| Limited service meals and snacks | TIE | HRNN | 2.645 | 0.0012 | 0.0012 | 0.0012 | 0.0015 |
| Coffee | SEASONAL AR WINS | Seasonal AR | 0.224 | 0.0106 | 0.0107 | 0.0110 | 0.0098 |
| Other processed fruits and vegetables including dried | SEASONAL AR WINS | Seasonal AR | 0.081 | 0.0102 | 0.0104 | 0.0107 | 0.0081 |
| Motor vehicle maintenance and repair | TIE | Seasonal AR | 1.048 | 0.0056 | 0.0059 | 0.0058 | 0.0055 |
| Canned fruits and vegetables | SEASONAL AR WINS | Seasonal AR | 0.102 | 0.0106 | 0.0104 | 0.0111 | 0.0090 |
| Soups | SEASONAL AR WINS | Seasonal AR | 0.089 | 0.0126 | 0.0123 | 0.0128 | 0.0108 |
| Potatoes | SEASONAL AR WINS | Seasonal AR | 0.068 | 0.0157 | 0.0173 | 0.0170 | 0.0133 |
| Other fresh vegetables | SEASONAL AR WINS | Seasonal AR | 0.305 | 0.0090 | 0.0091 | 0.0093 | 0.0085 |
| Tires | SEASONAL AR WINS | Seasonal AR | 0.283 | 0.0058 | 0.0058 | 0.0061 | 0.0052 |
| Other pork including roasts, steaks, and ribs | SEASONAL AR WINS | Seasonal AR | 0.095 | 0.0172 | 0.0162 | 0.0176 | 0.0155 |

## Adoption candidates

- SEHE01 Fuel oil: HRNN beats production proxy in window C by 0.40 pp m/m; window B gap 0.25 pp.
- SEFV03 Food at employee sites and schools: HRNN beats production proxy in window C by 0.61 pp m/m; window B gap 0.38 pp.
- SETA02 Used cars and trucks: HRNN beats production proxy in window C by 0.01 pp m/m; window B gap 0.03 pp.
- SEFV01 Full service meals and snacks: HRNN beats production proxy in window C by 0.01 pp m/m; window B gap 0.01 pp.
- SEFV02 Limited service meals and snacks: HRNN beats production proxy in window C by 0.01 pp m/m; window B gap 0.00 pp.
- SEMC Professional services: HRNN beats production proxy in window C by 0.00 pp m/m; window B gap 0.01 pp.
- SERB01 Pets and pet products: HRNN beats production proxy in window C by 0.02 pp m/m; window B gap 0.01 pp.
- SEFC02 Uncooked beef roasts: HRNN beats production proxy in window C by 0.08 pp m/m; window B gap 0.07 pp.
- SEFH Eggs: HRNN beats production proxy in window C by 0.05 pp m/m; window B gap 0.05 pp.
- SERA06 Recorded music and music subscriptions: HRNN beats production proxy in window C by 0.03 pp m/m; window B gap 0.04 pp.
- SEMG Medical equipment and supplies: HRNN beats production proxy in window C by 0.02 pp m/m; window B gap 0.01 pp.
- SEFK03 Citrus fruits: HRNN beats production proxy in window C by 0.03 pp m/m; window B gap 0.00 pp.

## Honest notes

- Production component MAE in this first artifact is a tier-style endogenous proxy, because the existing production backtest artifact stores headline rows but not a full per-component historical forecast panel.
- SETB01 gasoline uses the same EIA weekly regular gasoline calendar-month measurement in HRNN, I-GRU, Seasonal AR, Production Tier 1 fallback, and Production Tier 3 fallback whenever the monthly EIA comparison is available.
- Aggregate-node challenger forecasts can look better than bottom-up rows because they forecast published aggregates directly; bottom-up leaf aggregation is the apples-to-apples view.
- Window A undercredits production external feeds that did not have current local cached histories before modern feed availability.
- The current BLS hierarchy is applied across history; historical parent changes are documented rather than reconstructed.
