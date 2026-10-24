# HRNN Challenger Comparison

Research comparison only. Not used in production forecasts.

Generated: 2026-10-24T18:38:19+00:00

## Implementation status

Deterministic HRNN-style challenger artifact. Full PyTorch MAP checkpoint sweep remains a follow-up using this schema.

## Window C headline scoreboard

| Model | Headline NSA MAE | Headline SA MAE | Core NSA MAE | Core SA MAE |
|---|---:|---:|---:|---:|
| Legacy proxy (not full model) | 0.0011 | 0.0011 | 0.0012 | 0.0012 |
| Production Tier 1 fallback | 0.0012 | 0.0011 | 0.0013 | 0.0013 |
| Production Tier 3 fallback | 0.0012 | 0.0011 | 0.0012 | 0.0012 |
| HRNN | 0.0012 | 0.0012 | 0.0015 | 0.0015 |
| I-GRU | 0.0012 | 0.0011 | 0.0013 | 0.0013 |
| Seasonal AR | 0.0011 | 0.0011 | 0.0012 | 0.0012 |

## Component league table

| Component | Verdict | Best model | Weight | Production MAE | HRNN MAE | I-GRU MAE | Seasonal AR MAE |
|---|---|---|---:|---:|---:|---:|---:|
| Electricity | SEASONAL AR WINS | Seasonal AR | 2.513 | 0.0106 | 0.0109 | 0.0116 | 0.0077 |
| Airline fares | SEASONAL AR WINS | Seasonal AR | 1.055 | 0.0365 | 0.0379 | 0.0393 | 0.0330 |
| Lodging away from home | SEASONAL AR WINS | Seasonal AR | 1.392 | 0.0220 | 0.0218 | 0.0217 | 0.0196 |
| Women's suits and separates | SEASONAL AR WINS | Seasonal AR | 0.394 | 0.0220 | 0.0246 | 0.0252 | 0.0141 |
| Household furnishings and operations | SEASONAL AR WINS | Seasonal AR | 4.213 | 0.0038 | 0.0038 | 0.0040 | 0.0032 |
| Hospital and related services | SEASONAL AR WINS | Seasonal AR | 2.613 | 0.0044 | 0.0044 | 0.0046 | 0.0036 |
| Car and truck rental | SEASONAL AR WINS | Seasonal AR | 0.153 | 0.0383 | 0.0384 | 0.0395 | 0.0279 |
| Communication | SEASONAL AR WINS | Seasonal AR | 3.200 | 0.0043 | 0.0046 | 0.0045 | 0.0038 |
| Women's dresses | SEASONAL AR WINS | Seasonal AR | 0.112 | 0.0370 | 0.0395 | 0.0414 | 0.0237 |
| Other fresh fruits | SEASONAL AR WINS | Seasonal AR | 0.317 | 0.0164 | 0.0168 | 0.0176 | 0.0121 |
| Jewelry | SEASONAL AR WINS | Seasonal AR | 0.147 | 0.0337 | 0.0350 | 0.0363 | 0.0247 |
| Girls' apparel | SEASONAL AR WINS | Seasonal AR | 0.155 | 0.0281 | 0.0305 | 0.0311 | 0.0204 |
| Prescription drugs | SEASONAL AR WINS | Seasonal AR | 0.893 | 0.0056 | 0.0055 | 0.0059 | 0.0045 |
| Men's shirts and sweaters | SEASONAL AR WINS | Seasonal AR | 0.136 | 0.0229 | 0.0246 | 0.0258 | 0.0165 |
| Tuition, other school fees, and childcare | SEASONAL AR WINS | Seasonal AR | 2.558 | 0.0020 | 0.0022 | 0.0021 | 0.0017 |
| Spices, seasonings, condiments, sauces | SEASONAL AR WINS | Seasonal AR | 0.317 | 0.0088 | 0.0087 | 0.0095 | 0.0064 |
| Other goods and services | TIE | Seasonal AR | 2.894 | 0.0031 | 0.0030 | 0.0032 | 0.0028 |
| Carbonated drinks | SEASONAL AR WINS | Seasonal AR | 0.332 | 0.0107 | 0.0107 | 0.0112 | 0.0086 |
| Sporting goods | SEASONAL AR WINS | Seasonal AR | 0.534 | 0.0071 | 0.0069 | 0.0074 | 0.0059 |
| Women's footwear | SEASONAL AR WINS | Seasonal AR | 0.278 | 0.0103 | 0.0112 | 0.0116 | 0.0080 |
| Men's pants and shorts | SEASONAL AR WINS | Seasonal AR | 0.118 | 0.0201 | 0.0199 | 0.0213 | 0.0147 |
| Motor vehicle fees | SEASONAL AR WINS | Seasonal AR | 0.496 | 0.0065 | 0.0069 | 0.0068 | 0.0053 |
| Other recreation services | TIE | Seasonal AR | 1.780 | 0.0054 | 0.0052 | 0.0056 | 0.0051 |
| Used cars and trucks | HRNN WINS | HRNN | 2.670 | 0.0104 | 0.0102 | 0.0109 | 0.0120 |
| Women's underwear, nightwear, swimwear and accessories | SEASONAL AR WINS | Seasonal AR | 0.238 | 0.0143 | 0.0142 | 0.0151 | 0.0121 |
| Health insurance | I-GRU WINS | I-GRU | 0.811 | 0.0082 | 0.0105 | 0.0076 | 0.0135 |
| Women's outerwear | SEASONAL AR WINS | Seasonal AR | 0.071 | 0.0300 | 0.0309 | 0.0318 | 0.0229 |
| Men's suits, sport coats, and outerwear | SEASONAL AR WINS | Seasonal AR | 0.102 | 0.0251 | 0.0248 | 0.0261 | 0.0201 |
| Frozen and freeze dried prepared foods | SEASONAL AR WINS | Seasonal AR | 0.288 | 0.0099 | 0.0095 | 0.0103 | 0.0083 |
| Intracity transportation | SEASONAL AR WINS | Seasonal AR | 0.366 | 0.0088 | 0.0092 | 0.0091 | 0.0076 |
| Boys' apparel | SEASONAL AR WINS | Seasonal AR | 0.129 | 0.0187 | 0.0191 | 0.0198 | 0.0154 |
| Fresh fish and seafood | SEASONAL AR WINS | Seasonal AR | 0.167 | 0.0096 | 0.0094 | 0.0103 | 0.0073 |
| Other recreational goods | SEASONAL AR WINS | Seasonal AR | 0.396 | 0.0084 | 0.0082 | 0.0087 | 0.0074 |
| Men's footwear | SEASONAL AR WINS | Seasonal AR | 0.198 | 0.0108 | 0.0115 | 0.0117 | 0.0089 |
| Fuel oil | HRNN WINS | HRNN | 0.132 | 0.0569 | 0.0539 | 0.0555 | 0.0567 |
| Food at employee sites and schools | HRNN WINS | HRNN | 0.065 | 0.0256 | 0.0197 | 0.0215 | 0.0238 |
| Ham | SEASONAL AR WINS | Seasonal AR | 0.067 | 0.0206 | 0.0208 | 0.0223 | 0.0150 |
| Processed fish and seafood | SEASONAL AR WINS | Seasonal AR | 0.149 | 0.0105 | 0.0100 | 0.0113 | 0.0080 |
| Nonfrozen noncarbonated juices and drinks | SEASONAL AR WINS | Seasonal AR | 0.337 | 0.0082 | 0.0081 | 0.0085 | 0.0072 |
| Water and sewerage maintenance | SEASONAL AR WINS | Seasonal AR | 0.781 | 0.0024 | 0.0024 | 0.0026 | 0.0020 |
| Other meats | SEASONAL AR WINS | Seasonal AR | 0.195 | 0.0097 | 0.0094 | 0.0102 | 0.0081 |
| Other miscellaneous foods | TIE | Seasonal AR | 0.559 | 0.0072 | 0.0067 | 0.0074 | 0.0066 |
| Fresh biscuits, rolls, muffins | SEASONAL AR WINS | Seasonal AR | 0.116 | 0.0142 | 0.0127 | 0.0145 | 0.0118 |
| Pet services including veterinary | SEASONAL AR WINS | Seasonal AR | 0.536 | 0.0059 | 0.0056 | 0.0059 | 0.0053 |
| Newspapers and magazines | SEASONAL AR WINS | Seasonal AR | 0.059 | 0.0269 | 0.0247 | 0.0277 | 0.0223 |
| Cheese and related products | SEASONAL AR WINS | Seasonal AR | 0.248 | 0.0089 | 0.0082 | 0.0090 | 0.0078 |
| Professional services | TIE | Seasonal AR | 3.389 | 0.0023 | 0.0023 | 0.0024 | 0.0022 |
| Breakfast cereal | SEASONAL AR WINS | Seasonal AR | 0.133 | 0.0128 | 0.0122 | 0.0133 | 0.0109 |
| Full service meals and snacks | TIE | HRNN | 2.347 | 0.0017 | 0.0016 | 0.0018 | 0.0018 |
| Garbage and trash collection | SEASONAL AR WINS | Seasonal AR | 0.362 | 0.0037 | 0.0035 | 0.0039 | 0.0030 |
| Snacks | SEASONAL AR WINS | Seasonal AR | 0.360 | 0.0078 | 0.0073 | 0.0083 | 0.0071 |
| Recreational books | SEASONAL AR WINS | Seasonal AR | 0.058 | 0.0225 | 0.0214 | 0.0231 | 0.0182 |
| Owners' equivalent rent of residences | TIE | I-GRU | 25.853 | 0.0008 | 0.0009 | 0.0007 | 0.0012 |
| Apples | SEASONAL AR WINS | Seasonal AR | 0.078 | 0.0167 | 0.0162 | 0.0174 | 0.0136 |
| Men's underwear, nightwear, swimwear and accessories | SEASONAL AR WINS | Seasonal AR | 0.132 | 0.0122 | 0.0118 | 0.0128 | 0.0105 |
| Other fats and oils including peanut butter | SEASONAL AR WINS | Seasonal AR | 0.108 | 0.0109 | 0.0106 | 0.0115 | 0.0088 |
| Motor vehicle maintenance and repair | SEASONAL AR WINS | Seasonal AR | 1.065 | 0.0054 | 0.0057 | 0.0056 | 0.0052 |
| Bacon, breakfast sausage, and related products | SEASONAL AR WINS | Seasonal AR | 0.131 | 0.0115 | 0.0113 | 0.0121 | 0.0098 |
| Leased cars and trucks | SEASONAL AR WINS | Seasonal AR | 0.382 | 0.0064 | 0.0067 | 0.0065 | 0.0058 |
| Ice cream and related products | SEASONAL AR WINS | Seasonal AR | 0.107 | 0.0140 | 0.0130 | 0.0143 | 0.0120 |
| Infants' and toddlers' apparel | SEASONAL AR WINS | Seasonal AR | 0.098 | 0.0146 | 0.0154 | 0.0154 | 0.0125 |
| Other bakery products | SEASONAL AR WINS | Seasonal AR | 0.217 | 0.0079 | 0.0076 | 0.0082 | 0.0069 |
| Other intercity transportation | SEASONAL AR WINS | Seasonal AR | 0.225 | 0.0156 | 0.0157 | 0.0162 | 0.0147 |
| Other beverage materials including tea | SEASONAL AR WINS | Seasonal AR | 0.094 | 0.0124 | 0.0116 | 0.0127 | 0.0103 |
| Boys' and girls' footwear | SEASONAL AR WINS | Seasonal AR | 0.124 | 0.0134 | 0.0130 | 0.0141 | 0.0118 |
| Cakes, cupcakes, and cookies | SEASONAL AR WINS | Seasonal AR | 0.205 | 0.0082 | 0.0079 | 0.0087 | 0.0073 |
| Televisions | SEASONAL AR WINS | Seasonal AR | 0.106 | 0.0128 | 0.0131 | 0.0135 | 0.0109 |
| Coffee | SEASONAL AR WINS | Seasonal AR | 0.222 | 0.0106 | 0.0106 | 0.0110 | 0.0097 |
| Limited service meals and snacks | TIE | HRNN | 2.637 | 0.0013 | 0.0012 | 0.0013 | 0.0015 |
| Other processed fruits and vegetables including dried | SEASONAL AR WINS | Seasonal AR | 0.081 | 0.0104 | 0.0105 | 0.0109 | 0.0081 |
| Potatoes | SEASONAL AR WINS | Seasonal AR | 0.070 | 0.0156 | 0.0170 | 0.0169 | 0.0131 |
| Uncooked beef steaks | SEASONAL AR WINS | Seasonal AR | 0.233 | 0.0133 | 0.0128 | 0.0137 | 0.0125 |
| Other uncooked poultry including turkey | SEASONAL AR WINS | Seasonal AR | 0.076 | 0.0142 | 0.0135 | 0.0146 | 0.0119 |
| Other pork including roasts, steaks, and ribs | SEASONAL AR WINS | Seasonal AR | 0.092 | 0.0179 | 0.0169 | 0.0184 | 0.0160 |
| Canned fruits and vegetables | SEASONAL AR WINS | Seasonal AR | 0.100 | 0.0104 | 0.0102 | 0.0109 | 0.0087 |
| Bread | SEASONAL AR WINS | Seasonal AR | 0.171 | 0.0076 | 0.0069 | 0.0077 | 0.0066 |
| Purchase, subscription, and rental of video | SEASONAL AR WINS | Seasonal AR | 0.180 | 0.0127 | 0.0123 | 0.0133 | 0.0118 |
| Salad dressing | SEASONAL AR WINS | Seasonal AR | 0.052 | 0.0164 | 0.0157 | 0.0171 | 0.0133 |
| Rent of primary residence | TIE | I-GRU | 7.707 | 0.0008 | 0.0009 | 0.0008 | 0.0012 |
| Soups | SEASONAL AR WINS | Seasonal AR | 0.086 | 0.0124 | 0.0121 | 0.0126 | 0.0105 |

## Adoption candidates

- SETA02 Used cars and trucks: HRNN beats production proxy in window C by 0.02 pp m/m; window B gap 0.03 pp.
- SEHE01 Fuel oil: HRNN beats production proxy in window C by 0.30 pp m/m; window B gap 0.19 pp.
- SEFV03 Food at employee sites and schools: HRNN beats production proxy in window C by 0.59 pp m/m; window B gap 0.37 pp.
- SEFV01 Full service meals and snacks: HRNN beats production proxy in window C by 0.01 pp m/m; window B gap 0.01 pp.
- SEFV02 Limited service meals and snacks: HRNN beats production proxy in window C by 0.01 pp m/m; window B gap 0.00 pp.
- SERB01 Pets and pet products: HRNN beats production proxy in window C by 0.02 pp m/m; window B gap 0.01 pp.
- SEFH Eggs: HRNN beats production proxy in window C by 0.06 pp m/m; window B gap 0.05 pp.
- SEFC02 Uncooked beef roasts: HRNN beats production proxy in window C by 0.09 pp m/m; window B gap 0.07 pp.
- SEFK03 Citrus fruits: HRNN beats production proxy in window C by 0.05 pp m/m; window B gap 0.01 pp.
- SERA06 Recorded music and music subscriptions: HRNN beats production proxy in window C by 0.03 pp m/m; window B gap 0.04 pp.
- SEFW01 Beer, ale, and other malt beverages at home: HRNN beats production proxy in window C by 0.02 pp m/m; window B gap 0.02 pp.
- SEMG Medical equipment and supplies: HRNN beats production proxy in window C by 0.02 pp m/m; window B gap 0.01 pp.

## Honest notes

- Production component MAE in this first artifact is a tier-style endogenous proxy, because the existing production backtest artifact stores headline rows but not a full per-component historical forecast panel.
- SETB01 gasoline uses the same EIA weekly regular gasoline calendar-month measurement in HRNN, I-GRU, Seasonal AR, Production Tier 1 fallback, and Production Tier 3 fallback whenever the monthly EIA comparison is available.
- Aggregate-node challenger forecasts can look better than bottom-up rows because they forecast published aggregates directly; bottom-up leaf aggregation is the apples-to-apples view.
- Window A undercredits production external feeds that did not have current local cached histories before modern feed availability.
- The current BLS hierarchy is applied across history; historical parent changes are documented rather than reconstructed.
