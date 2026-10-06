# HRNN Challenger Comparison

Research comparison only. Not used in production forecasts.

Generated: 2026-10-06T18:15:28+00:00

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
| Electricity | SEASONAL AR WINS | Seasonal AR | 2.530 | 0.0107 | 0.0110 | 0.0118 | 0.0077 |
| Airline fares | SEASONAL AR WINS | Seasonal AR | 1.040 | 0.0369 | 0.0381 | 0.0396 | 0.0334 |
| Lodging away from home | SEASONAL AR WINS | Seasonal AR | 1.405 | 0.0224 | 0.0221 | 0.0221 | 0.0198 |
| Women's suits and separates | SEASONAL AR WINS | Seasonal AR | 0.384 | 0.0223 | 0.0248 | 0.0255 | 0.0143 |
| Household furnishings and operations | SEASONAL AR WINS | Seasonal AR | 4.228 | 0.0038 | 0.0039 | 0.0041 | 0.0032 |
| Hospital and related services | SEASONAL AR WINS | Seasonal AR | 2.611 | 0.0044 | 0.0044 | 0.0046 | 0.0036 |
| Car and truck rental | SEASONAL AR WINS | Seasonal AR | 0.153 | 0.0385 | 0.0388 | 0.0398 | 0.0278 |
| Women's dresses | SEASONAL AR WINS | Seasonal AR | 0.112 | 0.0367 | 0.0397 | 0.0413 | 0.0234 |
| Other fresh fruits | SEASONAL AR WINS | Seasonal AR | 0.308 | 0.0161 | 0.0164 | 0.0173 | 0.0120 |
| Jewelry | SEASONAL AR WINS | Seasonal AR | 0.142 | 0.0336 | 0.0349 | 0.0362 | 0.0246 |
| Girls' apparel | SEASONAL AR WINS | Seasonal AR | 0.149 | 0.0285 | 0.0307 | 0.0314 | 0.0207 |
| Tuition, other school fees, and childcare | SEASONAL AR WINS | Seasonal AR | 2.542 | 0.0020 | 0.0022 | 0.0021 | 0.0016 |
| Prescription drugs | SEASONAL AR WINS | Seasonal AR | 0.909 | 0.0055 | 0.0054 | 0.0058 | 0.0044 |
| Communication | SEASONAL AR WINS | Seasonal AR | 3.227 | 0.0041 | 0.0044 | 0.0043 | 0.0038 |
| Men's shirts and sweaters | SEASONAL AR WINS | Seasonal AR | 0.133 | 0.0231 | 0.0251 | 0.0260 | 0.0167 |
| Spices, seasonings, condiments, sauces | SEASONAL AR WINS | Seasonal AR | 0.323 | 0.0087 | 0.0086 | 0.0094 | 0.0063 |
| Carbonated drinks | SEASONAL AR WINS | Seasonal AR | 0.330 | 0.0109 | 0.0107 | 0.0114 | 0.0086 |
| Other goods and services | TIE | Seasonal AR | 2.900 | 0.0031 | 0.0030 | 0.0033 | 0.0029 |
| Sporting goods | SEASONAL AR WINS | Seasonal AR | 0.535 | 0.0072 | 0.0070 | 0.0075 | 0.0060 |
| Motor vehicle fees | SEASONAL AR WINS | Seasonal AR | 0.500 | 0.0066 | 0.0070 | 0.0069 | 0.0053 |
| Women's footwear | SEASONAL AR WINS | Seasonal AR | 0.275 | 0.0104 | 0.0113 | 0.0116 | 0.0080 |
| Men's pants and shorts | SEASONAL AR WINS | Seasonal AR | 0.118 | 0.0203 | 0.0202 | 0.0214 | 0.0150 |
| Other recreation services | TIE | Seasonal AR | 1.781 | 0.0054 | 0.0052 | 0.0056 | 0.0051 |
| Health insurance | I-GRU WINS | I-GRU | 0.817 | 0.0084 | 0.0106 | 0.0077 | 0.0137 |
| Women's underwear, nightwear, swimwear and accessories | SEASONAL AR WINS | Seasonal AR | 0.239 | 0.0144 | 0.0144 | 0.0152 | 0.0123 |
| Men's suits, sport coats, and outerwear | SEASONAL AR WINS | Seasonal AR | 0.099 | 0.0251 | 0.0248 | 0.0262 | 0.0200 |
| Women's outerwear | SEASONAL AR WINS | Seasonal AR | 0.069 | 0.0305 | 0.0314 | 0.0324 | 0.0233 |
| Used cars and trucks | TIE | HRNN | 2.688 | 0.0106 | 0.0104 | 0.0111 | 0.0119 |
| Frozen and freeze dried prepared foods | SEASONAL AR WINS | Seasonal AR | 0.291 | 0.0100 | 0.0097 | 0.0104 | 0.0084 |
| Intracity transportation | SEASONAL AR WINS | Seasonal AR | 0.360 | 0.0087 | 0.0091 | 0.0090 | 0.0075 |
| Fuel oil | HRNN WINS | HRNN | 0.116 | 0.0563 | 0.0529 | 0.0547 | 0.0556 |
| Fresh fish and seafood | SEASONAL AR WINS | Seasonal AR | 0.168 | 0.0097 | 0.0095 | 0.0103 | 0.0074 |
| Men's footwear | SEASONAL AR WINS | Seasonal AR | 0.197 | 0.0109 | 0.0116 | 0.0118 | 0.0090 |
| Food at employee sites and schools | HRNN WINS | HRNN | 0.065 | 0.0259 | 0.0200 | 0.0218 | 0.0238 |
| Boys' apparel | SEASONAL AR WINS | Seasonal AR | 0.120 | 0.0179 | 0.0182 | 0.0189 | 0.0148 |
| Processed fish and seafood | SEASONAL AR WINS | Seasonal AR | 0.150 | 0.0106 | 0.0101 | 0.0113 | 0.0082 |
| Ham | SEASONAL AR WINS | Seasonal AR | 0.066 | 0.0206 | 0.0209 | 0.0223 | 0.0151 |
| Water and sewerage maintenance | SEASONAL AR WINS | Seasonal AR | 0.784 | 0.0024 | 0.0025 | 0.0026 | 0.0020 |
| Other recreational goods | SEASONAL AR WINS | Seasonal AR | 0.384 | 0.0077 | 0.0076 | 0.0080 | 0.0069 |
| Owners' equivalent rent of residences | TIE | I-GRU | 25.903 | 0.0008 | 0.0008 | 0.0007 | 0.0012 |
| Other meats | SEASONAL AR WINS | Seasonal AR | 0.195 | 0.0099 | 0.0095 | 0.0103 | 0.0083 |
| Professional services | TIE | Seasonal AR | 3.405 | 0.0023 | 0.0023 | 0.0024 | 0.0023 |
| Nonfrozen noncarbonated juices and drinks | SEASONAL AR WINS | Seasonal AR | 0.334 | 0.0081 | 0.0080 | 0.0083 | 0.0072 |
| Fresh biscuits, rolls, muffins | SEASONAL AR WINS | Seasonal AR | 0.117 | 0.0144 | 0.0130 | 0.0147 | 0.0119 |
| Newspapers and magazines | SEASONAL AR WINS | Seasonal AR | 0.057 | 0.0270 | 0.0248 | 0.0279 | 0.0219 |
| Pet services including veterinary | SEASONAL AR WINS | Seasonal AR | 0.542 | 0.0058 | 0.0056 | 0.0059 | 0.0053 |
| Cheese and related products | SEASONAL AR WINS | Seasonal AR | 0.249 | 0.0090 | 0.0083 | 0.0091 | 0.0079 |
| Other miscellaneous foods | TIE | Seasonal AR | 0.560 | 0.0071 | 0.0067 | 0.0074 | 0.0067 |
| Recreational books | SEASONAL AR WINS | Seasonal AR | 0.058 | 0.0228 | 0.0216 | 0.0234 | 0.0184 |
| Men's underwear, nightwear, swimwear and accessories | SEASONAL AR WINS | Seasonal AR | 0.133 | 0.0125 | 0.0120 | 0.0130 | 0.0105 |
| Apples | SEASONAL AR WINS | Seasonal AR | 0.080 | 0.0169 | 0.0163 | 0.0175 | 0.0138 |
| Snacks | SEASONAL AR WINS | Seasonal AR | 0.366 | 0.0076 | 0.0072 | 0.0081 | 0.0070 |
| Full service meals and snacks | TIE | HRNN | 2.354 | 0.0018 | 0.0016 | 0.0018 | 0.0018 |
| Garbage and trash collection | SEASONAL AR WINS | Seasonal AR | 0.363 | 0.0037 | 0.0035 | 0.0039 | 0.0030 |
| Breakfast cereal | SEASONAL AR WINS | Seasonal AR | 0.132 | 0.0128 | 0.0122 | 0.0132 | 0.0110 |
| Other fats and oils including peanut butter | SEASONAL AR WINS | Seasonal AR | 0.107 | 0.0110 | 0.0107 | 0.0116 | 0.0089 |
| Uncooked beef steaks | SEASONAL AR WINS | Seasonal AR | 0.236 | 0.0135 | 0.0129 | 0.0140 | 0.0126 |
| Ice cream and related products | SEASONAL AR WINS | Seasonal AR | 0.108 | 0.0141 | 0.0131 | 0.0144 | 0.0120 |
| Motor vehicle maintenance and repair | SEASONAL AR WINS | Seasonal AR | 1.063 | 0.0055 | 0.0058 | 0.0057 | 0.0053 |
| Other bakery products | SEASONAL AR WINS | Seasonal AR | 0.217 | 0.0080 | 0.0077 | 0.0084 | 0.0070 |
| Leased cars and trucks | SEASONAL AR WINS | Seasonal AR | 0.383 | 0.0065 | 0.0068 | 0.0067 | 0.0059 |
| Cakes, cupcakes, and cookies | SEASONAL AR WINS | Seasonal AR | 0.208 | 0.0083 | 0.0079 | 0.0088 | 0.0073 |
| Bacon, breakfast sausage, and related products | SEASONAL AR WINS | Seasonal AR | 0.130 | 0.0115 | 0.0113 | 0.0121 | 0.0099 |
| Infants' and toddlers' apparel | SEASONAL AR WINS | Seasonal AR | 0.096 | 0.0144 | 0.0152 | 0.0152 | 0.0123 |
| Rent of primary residence | TIE | I-GRU | 7.728 | 0.0008 | 0.0009 | 0.0008 | 0.0013 |
| Other intercity transportation | SEASONAL AR WINS | Seasonal AR | 0.224 | 0.0156 | 0.0157 | 0.0162 | 0.0147 |
| Other beverage materials including tea | SEASONAL AR WINS | Seasonal AR | 0.096 | 0.0123 | 0.0115 | 0.0126 | 0.0103 |
| Televisions | SEASONAL AR WINS | Seasonal AR | 0.108 | 0.0127 | 0.0131 | 0.0134 | 0.0110 |
| Limited service meals and snacks | TIE | HRNN | 2.647 | 0.0013 | 0.0012 | 0.0013 | 0.0015 |
| Other uncooked poultry including turkey | SEASONAL AR WINS | Seasonal AR | 0.077 | 0.0142 | 0.0135 | 0.0146 | 0.0118 |
| Bread | SEASONAL AR WINS | Seasonal AR | 0.172 | 0.0077 | 0.0070 | 0.0079 | 0.0066 |
| Other fresh vegetables | SEASONAL AR WINS | Seasonal AR | 0.303 | 0.0089 | 0.0090 | 0.0093 | 0.0084 |
| Coffee | SEASONAL AR WINS | Seasonal AR | 0.222 | 0.0106 | 0.0107 | 0.0110 | 0.0098 |
| Boys' and girls' footwear | SEASONAL AR WINS | Seasonal AR | 0.121 | 0.0130 | 0.0127 | 0.0137 | 0.0116 |
| Other processed fruits and vegetables including dried | SEASONAL AR WINS | Seasonal AR | 0.080 | 0.0103 | 0.0105 | 0.0108 | 0.0081 |
| Canned fruits and vegetables | SEASONAL AR WINS | Seasonal AR | 0.101 | 0.0106 | 0.0104 | 0.0110 | 0.0089 |
| Potatoes | SEASONAL AR WINS | Seasonal AR | 0.071 | 0.0154 | 0.0169 | 0.0167 | 0.0131 |
| Purchase, subscription, and rental of video | SEASONAL AR WINS | Seasonal AR | 0.186 | 0.0123 | 0.0119 | 0.0129 | 0.0114 |
| Other pork including roasts, steaks, and ribs | SEASONAL AR WINS | Seasonal AR | 0.095 | 0.0176 | 0.0166 | 0.0180 | 0.0159 |
| Salad dressing | SEASONAL AR WINS | Seasonal AR | 0.051 | 0.0165 | 0.0159 | 0.0171 | 0.0134 |

## Adoption candidates

- SETA02 Used cars and trucks: HRNN beats production proxy in window C by 0.02 pp m/m; window B gap 0.03 pp.
- SEHE01 Fuel oil: HRNN beats production proxy in window C by 0.34 pp m/m; window B gap 0.22 pp.
- SEFV03 Food at employee sites and schools: HRNN beats production proxy in window C by 0.59 pp m/m; window B gap 0.37 pp.
- SEFV01 Full service meals and snacks: HRNN beats production proxy in window C by 0.01 pp m/m; window B gap 0.01 pp.
- SEFV02 Limited service meals and snacks: HRNN beats production proxy in window C by 0.01 pp m/m; window B gap 0.00 pp.
- SERB01 Pets and pet products: HRNN beats production proxy in window C by 0.02 pp m/m; window B gap 0.01 pp.
- SEFC02 Uncooked beef roasts: HRNN beats production proxy in window C by 0.09 pp m/m; window B gap 0.08 pp.
- SEFH Eggs: HRNN beats production proxy in window C by 0.06 pp m/m; window B gap 0.05 pp.
- SEFK03 Citrus fruits: HRNN beats production proxy in window C by 0.04 pp m/m; window B gap 0.01 pp.
- SEMG Medical equipment and supplies: HRNN beats production proxy in window C by 0.02 pp m/m; window B gap 0.01 pp.
- SEFW01 Beer, ale, and other malt beverages at home: HRNN beats production proxy in window C by 0.02 pp m/m; window B gap 0.02 pp.
- SERA06 Recorded music and music subscriptions: HRNN beats production proxy in window C by 0.03 pp m/m; window B gap 0.04 pp.

## Honest notes

- Production component MAE in this first artifact is a tier-style endogenous proxy, because the existing production backtest artifact stores headline rows but not a full per-component historical forecast panel.
- SETB01 gasoline uses the same EIA weekly regular gasoline calendar-month measurement in HRNN, I-GRU, Seasonal AR, Production Tier 1 fallback, and Production Tier 3 fallback whenever the monthly EIA comparison is available.
- Aggregate-node challenger forecasts can look better than bottom-up rows because they forecast published aggregates directly; bottom-up leaf aggregation is the apples-to-apples view.
- Window A undercredits production external feeds that did not have current local cached histories before modern feed availability.
- The current BLS hierarchy is applied across history; historical parent changes are documented rather than reconstructed.
