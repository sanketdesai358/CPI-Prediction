# HRNN Challenger Comparison

Research comparison only. Not used in production forecasts.

Generated: 2026-08-28T16:40:05+00:00

## Implementation status

Deterministic HRNN-style challenger artifact. Full PyTorch MAP checkpoint sweep remains a follow-up using this schema.

## Window C headline scoreboard

| Model | Headline NSA MAE | Headline SA MAE | Core NSA MAE | Core SA MAE |
|---|---:|---:|---:|---:|
| Legacy proxy (not full model) | 0.0012 | 0.0011 | 0.0012 | 0.0012 |
| Production Tier 1 fallback | 0.0012 | 0.0012 | 0.0013 | 0.0013 |
| Production Tier 3 fallback | 0.0012 | 0.0011 | 0.0012 | 0.0012 |
| HRNN | 0.0012 | 0.0012 | 0.0015 | 0.0015 |
| I-GRU | 0.0012 | 0.0012 | 0.0013 | 0.0013 |
| Seasonal AR | 0.0011 | 0.0011 | 0.0012 | 0.0012 |

## Component league table

| Component | Verdict | Best model | Weight | Production MAE | HRNN MAE | I-GRU MAE | Seasonal AR MAE |
|---|---|---|---:|---:|---:|---:|---:|
| Electricity | SEASONAL AR WINS | Seasonal AR | 2.551 | 0.0108 | 0.0111 | 0.0119 | 0.0078 |
| Airline fares | SEASONAL AR WINS | Seasonal AR | 1.049 | 0.0373 | 0.0387 | 0.0400 | 0.0337 |
| Lodging away from home | SEASONAL AR WINS | Seasonal AR | 1.402 | 0.0224 | 0.0222 | 0.0220 | 0.0199 |
| Women's suits and separates | SEASONAL AR WINS | Seasonal AR | 0.371 | 0.0219 | 0.0243 | 0.0249 | 0.0141 |
| Household furnishings and operations | SEASONAL AR WINS | Seasonal AR | 4.245 | 0.0038 | 0.0039 | 0.0041 | 0.0032 |
| Hospital and related services | SEASONAL AR WINS | Seasonal AR | 2.618 | 0.0044 | 0.0044 | 0.0046 | 0.0036 |
| Car and truck rental | SEASONAL AR WINS | Seasonal AR | 0.162 | 0.0381 | 0.0384 | 0.0394 | 0.0278 |
| Women's dresses | SEASONAL AR WINS | Seasonal AR | 0.103 | 0.0353 | 0.0382 | 0.0397 | 0.0227 |
| Jewelry | SEASONAL AR WINS | Seasonal AR | 0.145 | 0.0335 | 0.0349 | 0.0361 | 0.0247 |
| Other fresh fruits | SEASONAL AR WINS | Seasonal AR | 0.311 | 0.0163 | 0.0165 | 0.0174 | 0.0122 |
| Communication | SEASONAL AR WINS | Seasonal AR | 3.164 | 0.0038 | 0.0041 | 0.0040 | 0.0035 |
| Girls' apparel | SEASONAL AR WINS | Seasonal AR | 0.143 | 0.0281 | 0.0302 | 0.0309 | 0.0206 |
| Tuition, other school fees, and childcare | SEASONAL AR WINS | Seasonal AR | 2.515 | 0.0019 | 0.0020 | 0.0020 | 0.0015 |
| Prescription drugs | SEASONAL AR WINS | Seasonal AR | 0.913 | 0.0055 | 0.0055 | 0.0059 | 0.0045 |
| Other goods and services | TIE | Seasonal AR | 2.907 | 0.0032 | 0.0030 | 0.0033 | 0.0029 |
| Men's shirts and sweaters | SEASONAL AR WINS | Seasonal AR | 0.125 | 0.0221 | 0.0241 | 0.0250 | 0.0159 |
| Spices, seasonings, condiments, sauces | SEASONAL AR WINS | Seasonal AR | 0.322 | 0.0088 | 0.0087 | 0.0096 | 0.0064 |
| Carbonated drinks | SEASONAL AR WINS | Seasonal AR | 0.325 | 0.0108 | 0.0106 | 0.0113 | 0.0085 |
| Motor vehicle fees | SEASONAL AR WINS | Seasonal AR | 0.505 | 0.0067 | 0.0071 | 0.0070 | 0.0052 |
| Sporting goods | SEASONAL AR WINS | Seasonal AR | 0.531 | 0.0072 | 0.0070 | 0.0075 | 0.0060 |
| Men's pants and shorts | SEASONAL AR WINS | Seasonal AR | 0.120 | 0.0205 | 0.0204 | 0.0217 | 0.0151 |
| Women's footwear | SEASONAL AR WINS | Seasonal AR | 0.272 | 0.0104 | 0.0112 | 0.0116 | 0.0081 |
| Other recreation services | TIE | Seasonal AR | 1.793 | 0.0054 | 0.0052 | 0.0056 | 0.0051 |
| Women's underwear, nightwear, swimwear and accessories | SEASONAL AR WINS | Seasonal AR | 0.243 | 0.0144 | 0.0146 | 0.0152 | 0.0121 |
| Health insurance | I-GRU WINS | I-GRU | 0.824 | 0.0085 | 0.0108 | 0.0078 | 0.0139 |
| Intracity transportation | SEASONAL AR WINS | Seasonal AR | 0.359 | 0.0088 | 0.0091 | 0.0092 | 0.0074 |
| Men's suits, sport coats, and outerwear | SEASONAL AR WINS | Seasonal AR | 0.096 | 0.0249 | 0.0246 | 0.0259 | 0.0199 |
| Women's outerwear | SEASONAL AR WINS | Seasonal AR | 0.066 | 0.0302 | 0.0309 | 0.0321 | 0.0232 |
| Frozen and freeze dried prepared foods | SEASONAL AR WINS | Seasonal AR | 0.296 | 0.0099 | 0.0096 | 0.0104 | 0.0084 |
| Used cars and trucks | TIE | HRNN | 2.698 | 0.0106 | 0.0105 | 0.0112 | 0.0121 |
| Fuel oil | HRNN WINS | HRNN | 0.108 | 0.0563 | 0.0525 | 0.0544 | 0.0554 |
| Fresh fish and seafood | SEASONAL AR WINS | Seasonal AR | 0.170 | 0.0096 | 0.0093 | 0.0102 | 0.0073 |
| Food at employee sites and schools | HRNN WINS | HRNN | 0.064 | 0.0264 | 0.0204 | 0.0222 | 0.0241 |
| Ham | SEASONAL AR WINS | Seasonal AR | 0.068 | 0.0206 | 0.0209 | 0.0223 | 0.0150 |
| Water and sewerage maintenance | SEASONAL AR WINS | Seasonal AR | 0.785 | 0.0024 | 0.0025 | 0.0026 | 0.0020 |
| Men's footwear | SEASONAL AR WINS | Seasonal AR | 0.193 | 0.0109 | 0.0115 | 0.0118 | 0.0089 |
| Boys' apparel | SEASONAL AR WINS | Seasonal AR | 0.119 | 0.0182 | 0.0184 | 0.0192 | 0.0151 |
| Processed fish and seafood | SEASONAL AR WINS | Seasonal AR | 0.148 | 0.0106 | 0.0101 | 0.0113 | 0.0081 |
| Other recreational goods | SEASONAL AR WINS | Seasonal AR | 0.391 | 0.0075 | 0.0074 | 0.0078 | 0.0066 |
| Other meats | SEASONAL AR WINS | Seasonal AR | 0.194 | 0.0098 | 0.0095 | 0.0103 | 0.0082 |
| Fresh biscuits, rolls, muffins | SEASONAL AR WINS | Seasonal AR | 0.116 | 0.0145 | 0.0131 | 0.0149 | 0.0120 |
| Other miscellaneous foods | TIE | Seasonal AR | 0.567 | 0.0071 | 0.0067 | 0.0074 | 0.0066 |
| Newspapers and magazines | SEASONAL AR WINS | Seasonal AR | 0.055 | 0.0269 | 0.0247 | 0.0278 | 0.0217 |
| Pet services including veterinary | SEASONAL AR WINS | Seasonal AR | 0.542 | 0.0058 | 0.0056 | 0.0059 | 0.0053 |
| Recreational books | SEASONAL AR WINS | Seasonal AR | 0.057 | 0.0232 | 0.0219 | 0.0238 | 0.0183 |
| Men's underwear, nightwear, swimwear and accessories | SEASONAL AR WINS | Seasonal AR | 0.134 | 0.0126 | 0.0122 | 0.0133 | 0.0106 |
| Owners' equivalent rent of residences | TIE | I-GRU | 25.918 | 0.0008 | 0.0009 | 0.0008 | 0.0012 |
| Nonfrozen noncarbonated juices and drinks | SEASONAL AR WINS | Seasonal AR | 0.339 | 0.0079 | 0.0078 | 0.0081 | 0.0072 |
| Garbage and trash collection | SEASONAL AR WINS | Seasonal AR | 0.361 | 0.0037 | 0.0035 | 0.0039 | 0.0030 |
| Apples | SEASONAL AR WINS | Seasonal AR | 0.081 | 0.0166 | 0.0161 | 0.0173 | 0.0135 |
| Full service meals and snacks | TIE | HRNN | 2.352 | 0.0018 | 0.0016 | 0.0018 | 0.0018 |
| Cheese and related products | SEASONAL AR WINS | Seasonal AR | 0.248 | 0.0089 | 0.0083 | 0.0091 | 0.0079 |
| Other fats and oils including peanut butter | SEASONAL AR WINS | Seasonal AR | 0.107 | 0.0112 | 0.0109 | 0.0118 | 0.0089 |
| Other intercity transportation | SEASONAL AR WINS | Seasonal AR | 0.227 | 0.0159 | 0.0159 | 0.0165 | 0.0148 |
| Breakfast cereal | SEASONAL AR WINS | Seasonal AR | 0.135 | 0.0126 | 0.0120 | 0.0131 | 0.0109 |
| Snacks | TIE | Seasonal AR | 0.363 | 0.0076 | 0.0071 | 0.0080 | 0.0069 |
| Professional services | TIE | Seasonal AR | 3.422 | 0.0023 | 0.0023 | 0.0024 | 0.0022 |
| Televisions | SEASONAL AR WINS | Seasonal AR | 0.107 | 0.0129 | 0.0133 | 0.0136 | 0.0109 |
| Boys' and girls' footwear | SEASONAL AR WINS | Seasonal AR | 0.124 | 0.0130 | 0.0127 | 0.0138 | 0.0113 |
| Ice cream and related products | SEASONAL AR WINS | Seasonal AR | 0.108 | 0.0142 | 0.0132 | 0.0145 | 0.0122 |
| Bacon, breakfast sausage, and related products | SEASONAL AR WINS | Seasonal AR | 0.131 | 0.0117 | 0.0115 | 0.0123 | 0.0100 |
| Other beverage materials including tea | SEASONAL AR WINS | Seasonal AR | 0.095 | 0.0124 | 0.0116 | 0.0127 | 0.0103 |
| Uncooked beef steaks | SEASONAL AR WINS | Seasonal AR | 0.242 | 0.0133 | 0.0127 | 0.0137 | 0.0125 |
| Other bakery products | SEASONAL AR WINS | Seasonal AR | 0.216 | 0.0080 | 0.0077 | 0.0083 | 0.0070 |
| Purchase, subscription, and rental of video | SEASONAL AR WINS | Seasonal AR | 0.185 | 0.0125 | 0.0121 | 0.0131 | 0.0115 |
| Cakes, cupcakes, and cookies | SEASONAL AR WINS | Seasonal AR | 0.210 | 0.0082 | 0.0078 | 0.0087 | 0.0073 |
| Motor vehicle maintenance and repair | TIE | Seasonal AR | 1.055 | 0.0055 | 0.0058 | 0.0057 | 0.0054 |
| Infants' and toddlers' apparel | SEASONAL AR WINS | Seasonal AR | 0.095 | 0.0144 | 0.0152 | 0.0152 | 0.0125 |
| Other uncooked poultry including turkey | SEASONAL AR WINS | Seasonal AR | 0.077 | 0.0144 | 0.0137 | 0.0149 | 0.0121 |
| Coffee | SEASONAL AR WINS | Seasonal AR | 0.224 | 0.0105 | 0.0106 | 0.0110 | 0.0097 |
| Rent of primary residence | TIE | I-GRU | 7.734 | 0.0008 | 0.0010 | 0.0008 | 0.0013 |
| Other fresh vegetables | SEASONAL AR WINS | Seasonal AR | 0.306 | 0.0089 | 0.0091 | 0.0093 | 0.0083 |
| Bread | SEASONAL AR WINS | Seasonal AR | 0.173 | 0.0078 | 0.0070 | 0.0079 | 0.0067 |
| Potatoes | SEASONAL AR WINS | Seasonal AR | 0.070 | 0.0155 | 0.0170 | 0.0169 | 0.0131 |
| Leased cars and trucks | SEASONAL AR WINS | Seasonal AR | 0.385 | 0.0067 | 0.0070 | 0.0068 | 0.0062 |
| Limited service meals and snacks | TIE | HRNN | 2.655 | 0.0013 | 0.0012 | 0.0012 | 0.0015 |
| Other processed fruits and vegetables including dried | SEASONAL AR WINS | Seasonal AR | 0.082 | 0.0102 | 0.0104 | 0.0106 | 0.0081 |
| Soups | SEASONAL AR WINS | Seasonal AR | 0.089 | 0.0125 | 0.0121 | 0.0127 | 0.0107 |
| Canned fruits and vegetables | SEASONAL AR WINS | Seasonal AR | 0.101 | 0.0107 | 0.0105 | 0.0111 | 0.0091 |
| Tires | SEASONAL AR WINS | Seasonal AR | 0.284 | 0.0057 | 0.0057 | 0.0060 | 0.0051 |

## Adoption candidates

- SETA02 Used cars and trucks: HRNN beats production proxy in window C by 0.02 pp m/m; window B gap 0.03 pp.
- SEHE01 Fuel oil: HRNN beats production proxy in window C by 0.38 pp m/m; window B gap 0.24 pp.
- SEFV03 Food at employee sites and schools: HRNN beats production proxy in window C by 0.60 pp m/m; window B gap 0.38 pp.
- SEFV01 Full service meals and snacks: HRNN beats production proxy in window C by 0.01 pp m/m; window B gap 0.01 pp.
- SEFV02 Limited service meals and snacks: HRNN beats production proxy in window C by 0.01 pp m/m; window B gap 0.00 pp.
- SERB01 Pets and pet products: HRNN beats production proxy in window C by 0.02 pp m/m; window B gap 0.01 pp.
- SEFC02 Uncooked beef roasts: HRNN beats production proxy in window C by 0.08 pp m/m; window B gap 0.08 pp.
- SEFH Eggs: HRNN beats production proxy in window C by 0.06 pp m/m; window B gap 0.04 pp.
- SEFK03 Citrus fruits: HRNN beats production proxy in window C by 0.04 pp m/m; window B gap 0.00 pp.
- SERA06 Recorded music and music subscriptions: HRNN beats production proxy in window C by 0.03 pp m/m; window B gap 0.04 pp.
- SEFW01 Beer, ale, and other malt beverages at home: HRNN beats production proxy in window C by 0.02 pp m/m; window B gap 0.02 pp.
- SEMG Medical equipment and supplies: HRNN beats production proxy in window C by 0.02 pp m/m; window B gap 0.01 pp.

## Honest notes

- Production component MAE in this first artifact is a tier-style endogenous proxy, because the existing production backtest artifact stores headline rows but not a full per-component historical forecast panel.
- SETB01 gasoline uses the same EIA weekly regular gasoline calendar-month measurement in HRNN, I-GRU, Seasonal AR, Production Tier 1 fallback, and Production Tier 3 fallback whenever the monthly EIA comparison is available.
- Aggregate-node challenger forecasts can look better than bottom-up rows because they forecast published aggregates directly; bottom-up leaf aggregation is the apples-to-apples view.
- Window A undercredits production external feeds that did not have current local cached histories before modern feed availability.
- The current BLS hierarchy is applied across history; historical parent changes are documented rather than reconstructed.
