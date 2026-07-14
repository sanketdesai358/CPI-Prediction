# CPI Model Triage Report

Generated from the validated registry plus the current BLS history cache. `model_weight` is the BLS current relative-importance weight for the selected non-overlapping forecast universe; parents and overlapping aggregates are excluded from the contribution table.

| Code | Component | Tier | Model | BLS RI | Model weight | sigma | rho | seasonal |
|---|---|---:|---|---:|---:|---:|---:|---:|
| SAF111 | Cereals and bakery products | 1 | food_commodity_complex_factor | 1.023 | 0.000 | 0.0061 | 0.236 | 0.097 |
| SAF112 | Meats, poultry, fish, and eggs | 1 | food_commodity_complex_factor | 1.959 | 0.000 | 0.0094 | 0.427 | 0.069 |
| SAF113 | Fruits and vegetables | 1 | food_commodity_complex_factor | 1.283 | 0.000 | 0.0083 | 0.094 | 0.371 |
| SAF114 | Nonalcoholic beverages and beverage materials | 1 | food_commodity_complex_factor | 0.981 | 0.000 | 0.0076 | 0.113 | 0.374 |
| SAF115 | Other food at home | 1 | food_commodity_complex_factor | 2.242 | 0.000 | 0.0055 | 0.382 | 0.157 |
| SEFA02 | Breakfast cereal | 1 | food_commodity_complex_factor | 0.133 | 0.133 | 0.0119 | -0.179 | 0.157 |
| SEFA03 | Rice, pasta, cornmeal | 1 | food_commodity_complex_factor | 0.140 | 0.140 | 0.0098 | -0.054 | 0.124 |
| SEFC01 | Uncooked ground beef | 1 | food_commodity_complex_factor | 0.240 | 0.240 | 0.0170 | 0.305 | 0.135 |
| SEFC02 | Uncooked beef roasts | 1 | food_commodity_complex_factor | 0.087 | 0.087 | 0.0282 | 0.205 | 0.211 |
| SEFC03 | Uncooked beef steaks | 1 | food_commodity_complex_factor | 0.239 | 0.239 | 0.0215 | 0.315 | 0.155 |
| SEFC04 | Uncooked other beef and veal | 1 | food_commodity_complex_factor | 0.075 | 0.075 | 0.0179 | 0.236 | 0.153 |
| SEFD01 | Bacon, breakfast sausage, and related products | 1 | food_commodity_complex_factor | 0.130 | 0.130 | 0.0153 | 0.101 | 0.350 |
| SEFD02 | Ham | 1 | food_commodity_complex_factor | 0.067 | 0.067 | 0.0277 | -0.100 | 0.498 |
| SEFD03 | Pork chops | 1 | food_commodity_complex_factor | 0.046 | 0.046 | 0.0234 | -0.120 | 0.155 |
| SEFD04 | Other pork including roasts, steaks, and ribs | 1 | food_commodity_complex_factor | 0.095 | 0.095 | 0.0215 | -0.120 | 0.149 |
| SEFF01 | Chicken | 1 | food_commodity_complex_factor | 0.280 | 0.280 | 0.0105 | 0.215 | 0.188 |
| SEFF02 | Other uncooked poultry including turkey | 1 | food_commodity_complex_factor | 0.076 | 0.076 | 0.0171 | 0.002 | 0.331 |
| SEFH | Eggs | 1 | food_commodity_complex_factor | 0.112 | 0.112 | 0.0520 | 0.305 | 0.214 |
| SEFJ | Dairy and related products | 1 | food_commodity_complex_factor | 0.743 | 0.000 | 0.0065 | 0.312 | 0.105 |
| SEFJ01 | Milk | 1 | food_commodity_complex_factor | 0.195 | 0.195 | 0.0103 | 0.264 | 0.098 |
| SEFJ02 | Cheese and related products | 1 | food_commodity_complex_factor | 0.250 | 0.250 | 0.0089 | -0.128 | 0.084 |
| SEFJ03 | Ice cream and related products | 1 | food_commodity_complex_factor | 0.109 | 0.109 | 0.0132 | -0.030 | 0.298 |
| SEFJ04 | Other dairy and related products | 1 | food_commodity_complex_factor | 0.189 | 0.189 | 0.0095 | 0.144 | 0.272 |
| SEFP01 | Coffee | 1 | food_commodity_complex_factor | 0.224 | 0.224 | 0.0121 | 0.049 | 0.213 |
| SEFS01 | Butter and margarine | 1 | food_commodity_complex_factor | 0.062 | 0.062 | 0.0179 | 0.064 | 0.372 |
| SEHA | Rent of primary residence | 1 | shelter_tier1_cpi_fallback | 7.716 | 7.716 | 0.0016 | 0.846 | 0.085 |
| SEHB | Lodging away from home | 1 | costar_adr_pass_through | 1.451 | 1.451 | 0.0343 | 0.470 | 0.610 |
| SEHC | Owners' equivalent rent of residences | 1 | oer_tier1_cpi_fallback | 25.849 | 25.849 | 0.0014 | 0.840 | 0.055 |
| SEHC01 | Owners' equivalent rent of primary residence | 1 | oer_tier1_cpi_fallback | 24.886 | 0.000 | 0.0014 | 0.840 | 0.055 |
| SEHE01 | Fuel oil | 1 | measurement_pass_through_fuel_oil | 0.106 | 0.106 | 0.0644 | 0.370 | 0.083 |
| SEHF01 | Electricity | 1 | tariff_event_electricity | 2.552 | 2.552 | 0.0141 | 0.292 | 0.721 |
| SEHF02 | Utility (piped) gas service | 1 | distributed_lag_utility_gas | 0.748 | 0.748 | 0.0246 | 0.253 | 0.142 |
| SETA01 | New vehicles | 1 | new_vehicle_transaction_proxy | 3.752 | 3.752 | 0.0044 | 0.702 | 0.094 |
| SETA02 | Used cars and trucks | 1 | used_vehicle_lag_kernel | 2.679 | 2.679 | 0.0215 | 0.520 | 0.221 |
| SETA04 | Car and truck rental | 1 | rental_rate_scrape_proxy | 0.157 | 0.157 | 0.0613 | 0.355 | 0.554 |
| SETB01 | Gasoline (all types) | 1 | measurement_pass_through_gasoline | 3.852 | 3.852 | 0.0585 | 0.369 | 0.226 |
| SETB02 | Other motor fuels | 1 | measurement_pass_through_diesel | 0.119 | 0.119 | 0.0515 | 0.508 | 0.118 |
| SETG01 | Airline fares | 1 | airfare_fare_mix_proxy | 1.091 | 1.091 | 0.0525 | 0.456 | 0.476 |
| SEEB01 | College tuition and fees | 2 | tuition_aug_sep_event | 1.313 | 0.000 | 0.0036 | 0.493 | 0.757 |
| SEED03 | Wireless telephone services | 2 | wireless_plan_launch_event | 1.289 | 0.000 | 0.0095 | 0.143 | 0.086 |
| SEHG | Water and sewer and trash collection services | 2 | municipal_fee_calendar_step | 1.140 | 0.000 | 0.0025 | 0.080 | 0.371 |
| SEME | Health insurance | 2 | health_insurance_retained_earnings_step | 0.825 | 0.825 | 0.0156 | 0.843 | 0.009 |
| SETE | Motor vehicle insurance | 2 | insurance_filing_momentum | 2.569 | 2.569 | 0.0165 | 0.359 | 0.109 |
| SA0 | All items | 3 | seasonal_ar_partial_pool | 100.000 | 0.000 | 0.0034 | 0.525 | 0.320 |
| SA0E | Energy | 3 | seasonal_ar_partial_pool | 7.432 | 0.000 | 0.0313 | 0.379 | 0.225 |
| SA0L1 | All items less food | 3 | seasonal_ar_partial_pool | 86.478 | 0.000 | 0.0038 | 0.493 | 0.309 |
| SA0L1E | All items less food and energy | 3 | seasonal_ar_partial_pool | 79.046 | 0.000 | 0.0022 | 0.537 | 0.334 |
| SA0L2 | All items less shelter | 3 | seasonal_ar_partial_pool | 64.696 | 0.000 | 0.0048 | 0.495 | 0.316 |
| SA0L5 | All items less medical care | 3 | seasonal_ar_partial_pool | 91.749 | 0.000 | 0.0037 | 0.533 | 0.306 |
| SA0LE | All items less energy | 3 | seasonal_ar_partial_pool | 92.568 | 0.000 | 0.0021 | 0.593 | 0.335 |
| SA311 | Apparel less footwear | 3 | seasonal_ar_partial_pool | 1.846 | 0.000 | 0.0225 | 0.334 | 0.822 |
| SAA | Apparel | 3 | seasonal_ar_partial_pool | 2.438 | 0.000 | 0.0197 | 0.349 | 0.821 |
| SAA1 | Men's and boys' apparel | 3 | sarima_partial_pool | 0.604 | 0.000 | 0.0216 | 0.164 | 0.732 |
| SAA2 | Women's and girls' apparel | 3 | seasonal_ar_partial_pool | 0.969 | 0.000 | 0.0292 | 0.351 | 0.826 |
| SAC | Commodities | 3 | seasonal_ar_partial_pool | 36.483 | 0.000 | 0.0072 | 0.485 | 0.314 |
| SACE | Energy commodities | 3 | seasonal_ar_partial_pool | 4.131 | 0.000 | 0.0572 | 0.371 | 0.213 |
| SACL1 | Commodities less food | 3 | seasonal_ar_partial_pool | 22.961 | 0.000 | 0.0110 | 0.460 | 0.295 |
| SACL11 | Commodities less food and beverages | 3 | seasonal_ar_partial_pool | 22.139 | 0.000 | 0.0114 | 0.462 | 0.294 |
| SACL1E | Commodities less food and energy commodities | 3 | seasonal_ar_partial_pool | 18.830 | 0.000 | 0.0052 | 0.527 | 0.342 |
| SAD | Durables | 3 | seasonal_ar_partial_pool | 10.542 | 0.000 | 0.0071 | 0.640 | 0.143 |
| SAE | Education and communication | 3 | sarima_partial_pool | 5.677 | 0.000 | 0.0032 | 0.156 | 0.251 |
| SAE1 | Education | 3 | seasonal_ar_partial_pool | 2.537 | 0.000 | 0.0030 | 0.475 | 0.801 |
| SAE2 | Communication | 3 | ets_partial_pool | 3.140 | 3.140 | 0.0050 | 0.110 | 0.103 |
| SAE21 | Information and information processing | 3 | ets_partial_pool | 3.075 | 0.000 | 0.0052 | 0.120 | 0.099 |
| SAF | Food and beverages | 3 | seasonal_ar_partial_pool | 14.345 | 0.000 | 0.0031 | 0.582 | 0.162 |
| SAF1 | Food | 3 | seasonal_ar_partial_pool | 13.522 | 0.000 | 0.0033 | 0.580 | 0.158 |
| SAF11 | Food at home | 3 | seasonal_ar_partial_pool | 8.231 | 0.000 | 0.0049 | 0.468 | 0.184 |
| SAF1121 | Meats, poultry, and fish | 3 | seasonal_ar_partial_pool | 1.847 | 0.000 | 0.0090 | 0.468 | 0.203 |
| SAF11211 | Meats | 3 | seasonal_ar_partial_pool | 1.174 | 0.000 | 0.0117 | 0.389 | 0.167 |
| SAF1131 | Fresh fruits and vegetables | 3 | sarima_partial_pool | 1.017 | 0.000 | 0.0098 | 0.101 | 0.351 |
| SAF116 | Alcoholic beverages | 3 | sarima_partial_pool | 0.823 | 0.000 | 0.0024 | 0.183 | 0.242 |
| SAG | Other goods and services | 3 | sarima_partial_pool | 2.906 | 2.906 | 0.0031 | 0.038 | 0.188 |
| SAG1 | Personal care | 3 | sarima_partial_pool | 2.460 | 0.000 | 0.0034 | 0.091 | 0.186 |
| SAH | Housing | 3 | seasonal_ar_partial_pool | 44.149 | 0.000 | 0.0021 | 0.564 | 0.323 |
| SAH1 | Shelter | 3 | seasonal_ar_partial_pool | 35.304 | 0.000 | 0.0016 | 0.678 | 0.095 |
| SAH2 | Fuels and utilities | 3 | seasonal_ar_partial_pool | 4.601 | 0.000 | 0.0101 | 0.301 | 0.495 |
| SAH21 | Household energy | 3 | seasonal_ar_partial_pool | 3.461 | 0.000 | 0.0130 | 0.307 | 0.501 |
| SAH3 | Household furnishings and operations | 3 | seasonal_ar_partial_pool | 4.244 | 4.244 | 0.0046 | 0.302 | 0.277 |
| SAM | Medical care | 3 | seasonal_ar_partial_pool | 8.251 | 0.000 | 0.0028 | 0.336 | 0.189 |
| SAM1 | Medical care commodities | 3 | ets_partial_pool | 1.412 | 0.000 | 0.0050 | 0.142 | 0.110 |
| SAM2 | Medical care services | 3 | seasonal_ar_partial_pool | 6.840 | 0.000 | 0.0032 | 0.368 | 0.164 |
| SAN | Nondurables | 3 | seasonal_ar_partial_pool | 25.941 | 0.000 | 0.0093 | 0.403 | 0.318 |
| SAN1D | Domestically produced farm food | 3 | seasonal_ar_partial_pool | 6.876 | 0.000 | 0.0050 | 0.488 | 0.153 |
| SANL1 | Nondurables less food | 3 | seasonal_ar_partial_pool | 12.419 | 0.000 | 0.0185 | 0.377 | 0.295 |
| SANL11 | Nondurables less food and beverages | 3 | seasonal_ar_partial_pool | 11.597 | 0.000 | 0.0199 | 0.379 | 0.293 |
| SANL113 | Nondurables less food, beverages, and apparel | 3 | seasonal_ar_partial_pool | 9.159 | 0.000 | 0.0235 | 0.368 | 0.225 |
| SANL13 | Nondurables less food and apparel | 3 | seasonal_ar_partial_pool | 9.983 | 0.000 | 0.0214 | 0.365 | 0.227 |
| SAR | Recreation | 3 | seasonal_ar_partial_pool | 5.070 | 0.000 | 0.0036 | 0.217 | 0.234 |
| SAS | Services | 3 | seasonal_ar_partial_pool | 63.517 | 0.000 | 0.0020 | 0.548 | 0.229 |
| SAS24 | Utilities and public transportation | 3 | seasonal_ar_partial_pool | 8.131 | 0.000 | 0.0069 | 0.382 | 0.383 |
| SAS2RS | Rent of shelter | 3 | seasonal_ar_partial_pool | 35.016 | 0.000 | 0.0017 | 0.683 | 0.096 |
| SAS367 | Other services | 3 | sarima_partial_pool | 9.666 | 0.000 | 0.0022 | 0.126 | 0.145 |
| SAS4 | Transportation services | 3 | seasonal_ar_partial_pool | 6.352 | 0.000 | 0.0103 | 0.446 | 0.174 |
| SASL2RS | Services less rent of shelter | 3 | seasonal_ar_partial_pool | 28.501 | 0.000 | 0.0030 | 0.354 | 0.277 |
| SASL5 | Services less medical care services | 3 | seasonal_ar_partial_pool | 56.677 | 0.000 | 0.0022 | 0.591 | 0.193 |
| SASLE | Services less energy services | 3 | seasonal_ar_partial_pool | 60.217 | 0.000 | 0.0018 | 0.582 | 0.179 |
| SAT | Transportation | 3 | seasonal_ar_partial_pool | 17.164 | 0.000 | 0.0158 | 0.487 | 0.240 |
| SAT1 | Private transportation | 3 | seasonal_ar_partial_pool | 15.482 | 0.000 | 0.0158 | 0.459 | 0.224 |
| SEAA | Men's apparel | 3 | sarima_partial_pool | 0.485 | 0.000 | 0.0228 | 0.132 | 0.728 |
| SEAA02 | Men's underwear, nightwear, swimwear and accessories | 3 | sarima_partial_pool | 0.134 | 0.134 | 0.0194 | 0.052 | 0.382 |
| SEAA03 | Men's shirts and sweaters | 3 | sarima_partial_pool | 0.128 | 0.128 | 0.0337 | 0.176 | 0.646 |
| SEAA04 | Men's pants and shorts | 3 | sarima_partial_pool | 0.120 | 0.120 | 0.0298 | -0.040 | 0.628 |
| SEAB | Boys' apparel | 3 | sarima_partial_pool | 0.119 | 0.119 | 0.0273 | 0.163 | 0.378 |
| SEAC | Women's apparel | 3 | seasonal_ar_partial_pool | 0.821 | 0.000 | 0.0295 | 0.352 | 0.813 |
| SEAC02 | Women's dresses | 3 | seasonal_ar_partial_pool | 0.110 | 0.110 | 0.0572 | 0.303 | 0.808 |
| SEAC03 | Women's suits and separates | 3 | seasonal_ar_partial_pool | 0.385 | 0.385 | 0.0359 | 0.290 | 0.763 |
| SEAC04 | Women's underwear, nightwear, swimwear and accessories | 3 | sarima_partial_pool | 0.245 | 0.245 | 0.0189 | 0.118 | 0.395 |
| SEAD | Girls' apparel | 3 | seasonal_ar_partial_pool | 0.148 | 0.148 | 0.0359 | 0.206 | 0.645 |
| SEAE | Footwear | 3 | seasonal_ar_partial_pool | 0.591 | 0.000 | 0.0124 | 0.323 | 0.580 |
| SEAE01 | Men's footwear | 3 | sarima_partial_pool | 0.192 | 0.192 | 0.0135 | 0.047 | 0.426 |
| SEAE02 | Boys' and girls' footwear | 3 | sarima_partial_pool | 0.126 | 0.126 | 0.0178 | 0.168 | 0.259 |
| SEAE03 | Women's footwear | 3 | seasonal_ar_partial_pool | 0.272 | 0.272 | 0.0162 | 0.287 | 0.564 |
| SEAG | Jewelry and watches | 3 | sarima_partial_pool | 0.175 | 0.000 | 0.0285 | -0.149 | 0.507 |
| SEAG02 | Jewelry | 3 | sarima_partial_pool | 0.140 | 0.140 | 0.0343 | -0.143 | 0.514 |
| SEEB | Tuition, other school fees, and childcare | 3 | seasonal_ar_partial_pool | 2.499 | 2.499 | 0.0031 | 0.496 | 0.820 |
| SEEB02 | Elementary and high school tuition and fees | 3 | seasonal_ar_partial_pool | 0.400 | 0.000 | 0.0043 | 0.536 | 0.593 |
| SEEB03 | Day care and preschool | 3 | sarima_partial_pool | 0.683 | 0.000 | 0.0042 | 0.064 | 0.457 |
| SEED | Telephone services | 3 | ets_partial_pool | 1.413 | 0.000 | 0.0075 | 0.114 | 0.095 |
| SEED04 | Residential telephone services | 3 | sarima_partial_pool | 0.124 | 0.000 | 0.0065 | 0.114 | 0.241 |
| SEEE | Information technology, hardware and services | 3 | sarima_partial_pool | 1.661 | 0.000 | 0.0051 | 0.086 | 0.148 |
| SEEE01 | Computers, peripherals, and smart home assistants | 3 | sarima_partial_pool | 0.298 | 0.000 | 0.0124 | 0.036 | 0.150 |
| SEEE03 | Internet services and electronic information providers | 3 | sarima_partial_pool | 0.914 | 0.000 | 0.0063 | 0.182 | 0.134 |
| SEEE04 | Telephone hardware, calculators, and other consumer information items | 3 | seasonal_ar_partial_pool | 0.407 | 0.000 | 0.0132 | 0.234 | 0.160 |
| SEFA | Cereals and cereal products | 3 | ets_partial_pool | 0.311 | 0.000 | 0.0085 | 0.073 | 0.118 |
| SEFB | Bakery products | 3 | ets_partial_pool | 0.713 | 0.000 | 0.0064 | 0.105 | 0.088 |
| SEFB01 | Bread | 3 | ets_partial_pool | 0.173 | 0.173 | 0.0086 | -0.139 | 0.056 |
| SEFB02 | Fresh biscuits, rolls, muffins | 3 | seasonal_ar_partial_pool | 0.116 | 0.116 | 0.0125 | -0.328 | 0.080 |
| SEFB03 | Cakes, cupcakes, and cookies | 3 | sarima_partial_pool | 0.206 | 0.206 | 0.0089 | -0.135 | 0.123 |
| SEFB04 | Other bakery products | 3 | sarima_partial_pool | 0.219 | 0.219 | 0.0103 | -0.077 | 0.322 |
| SEFC | Beef and veal | 3 | seasonal_ar_partial_pool | 0.640 | 0.000 | 0.0184 | 0.396 | 0.163 |
| SEFD | Pork | 3 | seasonal_ar_partial_pool | 0.338 | 0.000 | 0.0129 | 0.205 | 0.380 |
| SEFE | Other meats | 3 | sarima_partial_pool | 0.195 | 0.195 | 0.0108 | -0.026 | 0.202 |
| SEFF | Poultry | 3 | seasonal_ar_partial_pool | 0.357 | 0.000 | 0.0094 | 0.275 | 0.186 |
| SEFG | Fish and seafood | 3 | sarima_partial_pool | 0.317 | 0.000 | 0.0090 | -0.065 | 0.292 |
| SEFG01 | Fresh fish and seafood | 3 | seasonal_ar_partial_pool | 0.169 | 0.169 | 0.0112 | -0.240 | 0.235 |
| SEFG02 | Processed fish and seafood | 3 | sarima_partial_pool | 0.148 | 0.148 | 0.0121 | -0.064 | 0.408 |
| SEFK | Fresh fruits | 3 | sarima_partial_pool | 0.525 | 0.000 | 0.0128 | 0.029 | 0.462 |
| SEFK04 | Other fresh fruits | 3 | seasonal_ar_partial_pool | 0.307 | 0.307 | 0.0296 | 0.292 | 0.589 |
| SEFL | Fresh vegetables | 3 | seasonal_ar_partial_pool | 0.492 | 0.000 | 0.0127 | 0.208 | 0.189 |
| SEFL04 | Other fresh vegetables | 3 | sarima_partial_pool | 0.305 | 0.305 | 0.0116 | 0.161 | 0.223 |
| SEFM | Processed fruits and vegetables | 3 | sarima_partial_pool | 0.267 | 0.000 | 0.0100 | 0.165 | 0.444 |
| SEFM01 | Canned fruits and vegetables | 3 | sarima_partial_pool | 0.102 | 0.102 | 0.0137 | 0.095 | 0.436 |
| SEFN | Juices and nonalcoholic drinks | 3 | sarima_partial_pool | 0.664 | 0.000 | 0.0090 | 0.063 | 0.384 |
| SEFN01 | Carbonated drinks | 3 | sarima_partial_pool | 0.324 | 0.324 | 0.0138 | -0.038 | 0.492 |
| SEFN03 | Nonfrozen noncarbonated juices and drinks | 3 | sarima_partial_pool | 0.334 | 0.334 | 0.0082 | 0.044 | 0.178 |
| SEFP | Beverage materials including coffee and tea | 3 | sarima_partial_pool | 0.318 | 0.000 | 0.0089 | 0.014 | 0.211 |
| SEFR | Sugar and sweets | 3 | sarima_partial_pool | 0.330 | 0.000 | 0.0077 | 0.010 | 0.236 |
| SEFR02 | Candy and chewing gum | 3 | sarima_partial_pool | 0.243 | 0.243 | 0.0092 | -0.018 | 0.167 |
| SEFS | Fats and oils | 3 | sarima_partial_pool | 0.219 | 0.000 | 0.0109 | 0.072 | 0.368 |
| SEFS03 | Other fats and oils including peanut butter | 3 | sarima_partial_pool | 0.107 | 0.107 | 0.0119 | -0.054 | 0.248 |
| SEFT | Other foods | 3 | seasonal_ar_partial_pool | 1.693 | 0.000 | 0.0061 | 0.277 | 0.212 |
| SEFT02 | Frozen and freeze dried prepared foods | 3 | sarima_partial_pool | 0.296 | 0.296 | 0.0100 | -0.061 | 0.276 |
| SEFT03 | Snacks | 3 | sarima_partial_pool | 0.365 | 0.365 | 0.0096 | -0.033 | 0.201 |
| SEFT04 | Spices, seasonings, condiments, sauces | 3 | sarima_partial_pool | 0.320 | 0.320 | 0.0102 | 0.021 | 0.519 |
| SEFT06 | Other miscellaneous foods | 3 | sarima_partial_pool | 0.571 | 0.571 | 0.0088 | -0.095 | 0.356 |
| SEFV | Food away from home | 3 | seasonal_ar_partial_pool | 5.291 | 0.000 | 0.0020 | 0.646 | 0.058 |
| SEFV01 | Full service meals and snacks | 3 | seasonal_ar_partial_pool | 2.347 | 2.347 | 0.0023 | 0.463 | 0.072 |
| SEFV02 | Limited service meals and snacks | 3 | seasonal_ar_partial_pool | 2.645 | 2.645 | 0.0022 | 0.563 | 0.093 |
| SEFV05 | Other food away from home | 3 | ets_partial_pool | 0.183 | 0.183 | 0.0047 | -0.116 | 0.117 |
| SEFW | Alcoholic beverages at home | 3 | sarima_partial_pool | 0.386 | 0.000 | 0.0035 | 0.145 | 0.337 |
| SEFW01 | Beer, ale, and other malt beverages at home | 3 | sarima_partial_pool | 0.134 | 0.134 | 0.0049 | 0.149 | 0.168 |
| SEFW03 | Wine at home | 3 | sarima_partial_pool | 0.165 | 0.165 | 0.0051 | 0.032 | 0.393 |
| SEFX | Alcoholic beverages away from home | 3 | ets_partial_pool | 0.437 | 0.437 | 0.0031 | 0.032 | 0.107 |
| SEGA | Tobacco and smoking products | 3 | ets_partial_pool | 0.445 | 0.000 | 0.0057 | -0.123 | 0.095 |
| SEGA01 | Cigarettes | 3 | ets_partial_pool | 0.327 | 0.000 | 0.0060 | -0.106 | 0.084 |
| SEGA02 | Tobacco products other than cigarettes | 3 | seasonal_ar_partial_pool | 0.114 | 0.000 | 0.0086 | -0.409 | 0.114 |
| SEGB | Personal care products | 3 | sarima_partial_pool | 0.670 | 0.000 | 0.0045 | 0.193 | 0.292 |
| SEGB01 | Hair, dental, shaving, and miscellaneous personal care products | 3 | sarima_partial_pool | 0.320 | 0.000 | 0.0054 | 0.081 | 0.205 |
| SEGB02 | Cosmetics, perfume, bath, nail preparations and implements | 3 | sarima_partial_pool | 0.340 | 0.000 | 0.0068 | -0.001 | 0.229 |
| SEGC | Personal care services | 3 | sarima_partial_pool | 0.667 | 0.000 | 0.0040 | 0.117 | 0.142 |
| SEGC01 | Haircuts and other personal care services | 3 | sarima_partial_pool | 0.667 | 0.000 | 0.0040 | 0.117 | 0.142 |
| SEGD | Miscellaneous personal services | 3 | ets_partial_pool | 0.941 | 0.000 | 0.0065 | -0.007 | 0.090 |
| SEGD02 | Funeral expenses | 3 | ets_partial_pool | 0.164 | 0.000 | 0.0046 | -0.158 | 0.093 |
| SEGD03 | Laundry and dry cleaning services | 3 | ets_partial_pool | 0.130 | 0.000 | 0.0039 | 0.151 | 0.064 |
| SEGD05 | Financial services | 3 | seasonal_ar_partial_pool | 0.241 | 0.000 | 0.0208 | 0.271 | 0.181 |
| SEGE | Miscellaneous personal goods | 3 | sarima_partial_pool | 0.181 | 0.000 | 0.0150 | 0.055 | 0.302 |
| SEHB02 | Other lodging away from home including hotels and motels | 3 | seasonal_ar_partial_pool | 1.236 | 0.000 | 0.0399 | 0.477 | 0.620 |
| SEHD | Tenants' and household insurance | 3 | ets_partial_pool | 0.288 | 0.288 | 0.0037 | 0.169 | 0.040 |
| SEHE | Fuel oil and other fuels | 3 | seasonal_ar_partial_pool | 0.162 | 0.000 | 0.0445 | 0.398 | 0.125 |
| SEHF | Energy services | 3 | seasonal_ar_partial_pool | 3.300 | 0.000 | 0.0135 | 0.305 | 0.555 |
| SEHG01 | Water and sewerage maintenance | 3 | sarima_partial_pool | 0.783 | 0.783 | 0.0027 | 0.041 | 0.481 |
| SEHG02 | Garbage and trash collection | 3 | sarima_partial_pool | 0.358 | 0.358 | 0.0049 | 0.040 | 0.129 |
| SEHH | Window and floor coverings and other linens | 3 | sarima_partial_pool | 0.233 | 0.000 | 0.0164 | 0.031 | 0.402 |
| SEHH03 | Other linens | 3 | sarima_partial_pool | 0.121 | 0.000 | 0.0253 | -0.032 | 0.421 |
| SEHJ | Furniture and bedding | 3 | ets_partial_pool | 0.855 | 0.000 | 0.0086 | 0.177 | 0.097 |
| SEHJ01 | Bedroom furniture | 3 | ets_partial_pool | 0.291 | 0.000 | 0.0100 | 0.076 | 0.073 |
| SEHJ02 | Living room, kitchen, and dining room furniture | 3 | ets_partial_pool | 0.431 | 0.000 | 0.0120 | 0.139 | 0.074 |
| SEHJ03 | Other furniture | 3 | sarima_partial_pool | 0.128 | 0.000 | 0.0158 | 0.145 | 0.198 |
| SEHK | Appliances | 3 | sarima_partial_pool | 0.196 | 0.000 | 0.0129 | 0.005 | 0.426 |
| SEHK02 | Other appliances | 3 | sarima_partial_pool | 0.128 | 0.000 | 0.0149 | -0.073 | 0.401 |
| SEHL | Other household equipment and furnishings | 3 | seasonal_ar_partial_pool | 0.544 | 0.000 | 0.0110 | 0.258 | 0.342 |
| SEHL01 | Clocks, lamps, and decorator items | 3 | sarima_partial_pool | 0.308 | 0.000 | 0.0153 | 0.104 | 0.155 |
| SEHL02 | Indoor plants and flowers | 3 | sarima_partial_pool | 0.118 | 0.000 | 0.0176 | -0.081 | 0.646 |
| SEHM | Tools, hardware, outdoor equipment and supplies | 3 | seasonal_ar_partial_pool | 0.669 | 0.000 | 0.0069 | 0.313 | 0.101 |
| SEHM01 | Tools, hardware and supplies | 3 | seasonal_ar_partial_pool | 0.210 | 0.000 | 0.0081 | 0.253 | 0.225 |
| SEHM02 | Outdoor equipment and supplies | 3 | seasonal_ar_partial_pool | 0.283 | 0.000 | 0.0098 | 0.206 | 0.101 |
| SEHN | Housekeeping supplies | 3 | seasonal_ar_partial_pool | 0.831 | 0.000 | 0.0057 | 0.224 | 0.109 |
| SEHN01 | Household cleaning products | 3 | seasonal_ar_partial_pool | 0.302 | 0.000 | 0.0063 | 0.229 | 0.080 |
| SEHN02 | Household paper products | 3 | ets_partial_pool | 0.170 | 0.000 | 0.0101 | 0.058 | 0.099 |
| SEHN03 | Miscellaneous household products | 3 | sarima_partial_pool | 0.359 | 0.000 | 0.0088 | 0.060 | 0.136 |
| SEMC | Professional services | 3 | seasonal_ar_partial_pool | 3.407 | 3.407 | 0.0027 | 0.212 | 0.154 |
| SEMC01 | Physicians' services | 3 | seasonal_ar_partial_pool | 1.660 | 0.000 | 0.0039 | 0.226 | 0.084 |
| SEMC02 | Dental services | 3 | sarima_partial_pool | 0.917 | 0.000 | 0.0051 | 0.073 | 0.126 |
| SEMC03 | Eyeglasses and eye care | 3 | ets_partial_pool | 0.316 | 0.000 | 0.0057 | -0.102 | 0.089 |
| SEMD | Hospital and related services | 3 | sarima_partial_pool | 2.607 | 2.607 | 0.0047 | -0.063 | 0.277 |
| SEMD01 | Hospital services | 3 | sarima_partial_pool | 2.156 | 0.000 | 0.0051 | -0.093 | 0.242 |
| SEMD02 | Nursing homes and adult day services | 3 | sarima_partial_pool | 0.222 | 0.000 | 0.0045 | 0.101 | 0.382 |
| SEMF | Medicinal drugs | 3 | ets_partial_pool | 1.281 | 0.000 | 0.0052 | 0.118 | 0.106 |
| SEMF01 | Prescription drugs | 3 | sarima_partial_pool | 0.920 | 0.920 | 0.0067 | 0.067 | 0.143 |
| SEMF02 | Nonprescription drugs | 3 | sarima_partial_pool | 0.362 | 0.362 | 0.0069 | 0.176 | 0.202 |
| SEMG | Medical equipment and supplies | 3 | sarima_partial_pool | 0.130 | 0.130 | 0.0103 | 0.136 | 0.142 |
| SERA | Video and audio | 3 | seasonal_ar_partial_pool | 1.036 | 0.000 | 0.0054 | 0.329 | 0.285 |
| SERA01 | Televisions | 3 | seasonal_ar_partial_pool | 0.104 | 0.104 | 0.0164 | 0.352 | 0.344 |
| SERA02 | Cable, satellite, and live streaming television service | 3 | seasonal_ar_partial_pool | 0.596 | 0.596 | 0.0061 | 0.330 | 0.263 |
| SERA04 | Purchase, subscription, and rental of video | 3 | sarima_partial_pool | 0.181 | 0.181 | 0.0175 | 0.081 | 0.158 |
| SERB | Pets, pet products and services | 3 | seasonal_ar_partial_pool | 1.143 | 0.000 | 0.0044 | 0.366 | 0.131 |
| SERB01 | Pets and pet products | 3 | seasonal_ar_partial_pool | 0.600 | 0.600 | 0.0055 | 0.294 | 0.042 |
| SERB02 | Pet services including veterinary | 3 | sarima_partial_pool | 0.543 | 0.543 | 0.0054 | 0.138 | 0.180 |
| SERC | Sporting goods | 3 | ets_partial_pool | 0.530 | 0.530 | 0.0089 | -0.023 | 0.080 |
| SERC01 | Sports vehicles including bicycles | 3 | ets_partial_pool | 0.285 | 0.000 | 0.0139 | -0.035 | 0.074 |
| SERC02 | Sports equipment | 3 | ets_partial_pool | 0.234 | 0.000 | 0.0079 | 0.153 | 0.104 |
| SERE | Other recreational goods | 3 | seasonal_ar_partial_pool | 0.391 | 0.391 | 0.0092 | 0.249 | 0.320 |
| SERE01 | Toys | 3 | seasonal_ar_partial_pool | 0.305 | 0.000 | 0.0109 | 0.222 | 0.339 |
| SERF | Other recreation services | 3 | ets_partial_pool | 1.798 | 1.798 | 0.0072 | 0.088 | 0.059 |
| SERF01 | Club membership for shopping clubs, fraternal, or other organizations, or participant sports fees | 3 | ets_partial_pool | 0.740 | 0.000 | 0.0087 | 0.129 | 0.091 |
| SERF02 | Admissions | 3 | ets_partial_pool | 0.696 | 0.000 | 0.0134 | 0.110 | 0.053 |
| SERF03 | Fees for lessons or instructions | 3 | ets_partial_pool | 0.155 | 0.000 | 0.0088 | -0.034 | 0.085 |
| SERG | Recreational reading materials | 3 | seasonal_ar_partial_pool | 0.110 | 0.000 | 0.0124 | -0.378 | 0.046 |
| SETA | New and used motor vehicles | 3 | seasonal_ar_partial_pool | 7.045 | 0.000 | 0.0101 | 0.570 | 0.194 |
| SETA03 | Leased cars and trucks | 3 | sarima_partial_pool | 0.384 | 0.384 | 0.0079 | 0.070 | 0.134 |
| SETB | Motor fuel | 3 | seasonal_ar_partial_pool | 3.971 | 0.000 | 0.0586 | 0.370 | 0.224 |
| SETC | Motor vehicle parts and equipment | 3 | seasonal_ar_partial_pool | 0.338 | 0.000 | 0.0056 | 0.294 | 0.085 |
| SETC01 | Tires | 3 | sarima_partial_pool | 0.283 | 0.283 | 0.0070 | 0.184 | 0.137 |
| SETD | Motor vehicle maintenance and repair | 3 | seasonal_ar_partial_pool | 1.048 | 1.048 | 0.0054 | 0.230 | 0.117 |
| SETD02 | Motor vehicle maintenance and servicing | 3 | ets_partial_pool | 0.519 | 0.000 | 0.0045 | 0.050 | 0.044 |
| SETD03 | Motor vehicle repair | 3 | sarima_partial_pool | 0.404 | 0.000 | 0.0109 | 0.153 | 0.128 |
| SETF | Motor vehicle fees | 3 | seasonal_ar_partial_pool | 0.510 | 0.510 | 0.0064 | -0.250 | 0.335 |
| SETF01 | State motor vehicle registration and license fees | 3 | sarima_partial_pool | 0.296 | 0.000 | 0.0037 | -0.081 | 0.328 |
| SETF03 | Parking and other fees | 3 | seasonal_ar_partial_pool | 0.194 | 0.000 | 0.0120 | -0.258 | 0.261 |
| SETG | Public transportation | 3 | seasonal_ar_partial_pool | 1.683 | 0.000 | 0.0339 | 0.495 | 0.464 |
| SETG02 | Other intercity transportation | 3 | sarima_partial_pool | 0.232 | 0.232 | 0.0160 | 0.020 | 0.312 |
| SETG03 | Intracity transportation | 3 | seasonal_ar_partial_pool | 0.354 | 0.354 | 0.0134 | -0.377 | 0.122 |
| AA0 | All items - old base | 4 | parent_inherit | 0.000 | 0.000 | 0.0034 | 0.525 | 0.320 |
| AA0R | Purchasing power of the consumer dollar - old base | 4 | parent_inherit | 0.000 | 0.000 | 0.0045 | 0.104 | 0.231 |
| SA0L12 | All items less food and shelter | 4 | parent_inherit | 0.000 | 0.000 | 0.0059 | 0.465 | 0.301 |
| SA0L12E | All items less food, shelter, and energy | 4 | parent_inherit | 0.000 | 0.000 | 0.0031 | 0.456 | 0.362 |
| SA0L12E4 | All items less food, shelter, energy, and used cars and trucks | 4 | parent_inherit | 0.000 | 0.000 | 0.0029 | 0.379 | 0.511 |
| SA0R | Purchasing power of the consumer dollar | 4 | parent_inherit | 0.000 | 0.000 | 0.0037 | 0.417 | 0.321 |
| SACL1E4 | Commodities less food, energy, and used cars and trucks | 4 | parent_inherit | 0.000 | 0.000 | 0.0046 | 0.417 | 0.642 |
| SAEC | Education and communication commodities | 4 | parent_inherit | 0.000 | 0.000 | 0.0081 | 0.030 | 0.142 |
| SAES | Education and communication services | 4 | parent_inherit | 0.000 | 0.000 | 0.0033 | 0.183 | 0.254 |
| SAGC | Other goods | 4 | parent_inherit | 0.000 | 0.000 | 0.0040 | -0.002 | 0.298 |
| SAGS | Other personal services | 4 | parent_inherit | 0.000 | 0.000 | 0.0042 | -0.012 | 0.069 |
| SAH31 | Household furnishings and supplies | 4 | parent_inherit | 0.000 | 0.000 | 0.0051 | 0.449 | 0.317 |
| SARC | Recreation commodities | 4 | parent_inherit | 0.000 | 0.000 | 0.0049 | 0.229 | 0.249 |
| SARS | Recreation services | 4 | parent_inherit | 0.000 | 0.000 | 0.0046 | 0.189 | 0.169 |
| SATCLTB | Transportation commodities less motor fuel | 4 | parent_inherit | 0.000 | 0.000 | 0.0099 | 0.585 | 0.164 |
| SEAA01 | Men's suits, sport coats, and outerwear | 4 | parent_inherit | 0.099 | 0.099 | 0.0375 | 0.093 | 0.521 |
| SEAC01 | Women's outerwear | 4 | parent_inherit | 0.065 | 0.065 | 0.0445 | 0.252 | 0.615 |
| SEAF | Infants' and toddlers' apparel | 4 | parent_inherit | 0.097 | 0.097 | 0.0209 | 0.081 | 0.351 |
| SEAG01 | Watches | 4 | parent_inherit | 0.034 | 0.034 | 0.0254 | -0.215 | 0.184 |
| SEEA | Educational books and supplies | 4 | parent_inherit | 0.038 | 0.038 | 0.0109 | -0.192 | 0.088 |
| SEEB04 | Technical and vocational school tuition and fixed fees | 4 | parent_inherit | 0.000 | 0.000 | 0.0036 | -0.123 | 0.172 |
| SEEC | Postage and delivery services | 4 | parent_inherit | 0.067 | 0.000 | 0.0102 | 0.181 | 0.261 |
| SEEC01 | Postage | 4 | parent_inherit | 0.062 | 0.000 | 0.0117 | 0.117 | 0.288 |
| SEEC02 | Delivery services | 4 | parent_inherit | 0.005 | 0.000 | 0.0144 | 0.078 | 0.501 |
| SEEE02 | Computer software and accessories | 4 | parent_inherit | 0.032 | 0.000 | 0.0215 | 0.072 | 0.058 |
| SEEEC | Information technology commodities | 4 | parent_inherit | 0.000 | 0.000 | 0.0093 | 0.072 | 0.180 |
| SEFA01 | Flour and prepared flour mixes | 4 | parent_inherit | 0.038 | 0.038 | 0.0193 | 0.078 | 0.641 |
| SEFK01 | Apples | 4 | parent_inherit | 0.079 | 0.079 | 0.0228 | 0.208 | 0.448 |
| SEFK02 | Bananas | 4 | parent_inherit | 0.058 | 0.058 | 0.0103 | -0.141 | 0.044 |
| SEFK03 | Citrus fruits | 4 | parent_inherit | 0.080 | 0.080 | 0.0278 | 0.368 | 0.490 |
| SEFL01 | Potatoes | 4 | parent_inherit | 0.068 | 0.068 | 0.0288 | 0.121 | 0.731 |
| SEFL02 | Lettuce | 4 | parent_inherit | 0.050 | 0.050 | 0.0406 | 0.024 | 0.207 |
| SEFL03 | Tomatoes | 4 | parent_inherit | 0.068 | 0.068 | 0.0370 | 0.234 | 0.248 |
| SEFM02 | Frozen fruits and vegetables | 4 | parent_inherit | 0.085 | 0.085 | 0.0113 | 0.045 | 0.220 |
| SEFM03 | Other processed fruits and vegetables including dried | 4 | parent_inherit | 0.081 | 0.081 | 0.0115 | -0.175 | 0.273 |
| SEFN02 | Frozen noncarbonated juices and drinks | 4 | parent_inherit | 0.004 | 0.004 | 0.0185 | -0.025 | 0.083 |
| SEFP02 | Other beverage materials including tea | 4 | parent_inherit | 0.094 | 0.094 | 0.0113 | -0.302 | 0.233 |
| SEFR01 | Sugar and sugar substitutes | 4 | parent_inherit | 0.032 | 0.032 | 0.0149 | 0.016 | 0.566 |
| SEFR03 | Other sweets | 4 | parent_inherit | 0.055 | 0.055 | 0.0111 | -0.144 | 0.142 |
| SEFS02 | Salad dressing | 4 | parent_inherit | 0.050 | 0.050 | 0.0152 | -0.214 | 0.284 |
| SEFT01 | Soups | 4 | parent_inherit | 0.089 | 0.089 | 0.0168 | 0.327 | 0.540 |
| SEFT05 | Baby food and formula | 4 | parent_inherit | 0.052 | 0.052 | 0.0107 | -0.056 | 0.144 |
| SEFV03 | Food at employee sites and schools | 4 | parent_inherit | 0.064 | 0.064 | 0.0561 | 0.363 | 0.080 |
| SEFV04 | Food from vending machines and mobile vendors | 4 | parent_inherit | 0.053 | 0.053 | 0.0075 | 0.087 | 0.095 |
| SEFW02 | Distilled spirits at home | 4 | parent_inherit | 0.087 | 0.087 | 0.0050 | 0.079 | 0.244 |
| SEGD01 | Legal services | 4 | parent_inherit | 0.000 | 0.000 | 0.0065 | 0.095 | 0.139 |
| SEGD04 | Apparel services other than laundry and dry cleaning | 4 | parent_inherit | 0.029 | 0.000 | 0.0101 | -0.013 | 0.075 |
| SEHB01 | Lodging while at school | 4 | parent_inherit | 0.000 | 0.000 | 0.0037 | 0.544 | 0.819 |
| SEHE02 | Propane, kerosene, and firewood | 4 | parent_inherit | 0.055 | 0.055 | 0.0223 | 0.489 | 0.467 |
| SEHH01 | Floor coverings | 4 | parent_inherit | 0.068 | 0.000 | 0.0127 | 0.021 | 0.070 |
| SEHH02 | Window coverings | 4 | parent_inherit | 0.045 | 0.000 | 0.0271 | -0.186 | 0.178 |
| SEHK01 | Major appliances | 4 | parent_inherit | 0.065 | 0.000 | 0.0183 | 0.082 | 0.294 |
| SEHL03 | Dishes and flatware | 4 | parent_inherit | 0.045 | 0.000 | 0.0250 | 0.029 | 0.207 |
| SEHL04 | Nonelectric cookware and tableware | 4 | parent_inherit | 0.072 | 0.000 | 0.0166 | 0.186 | 0.274 |
| SEHP | Household operations | 4 | parent_inherit | 0.000 | 0.000 | 0.0073 | -0.122 | 0.131 |
| SEHP01 | Domestic services | 4 | parent_inherit | 0.000 | 0.000 | 0.0140 | -0.266 | 0.088 |
| SEHP02 | Gardening and lawncare services | 4 | parent_inherit | 0.000 | 0.000 | 0.0134 | -0.125 | 0.247 |
| SEHP03 | Moving, storage, freight expense | 4 | parent_inherit | 0.078 | 0.000 | 0.0240 | 0.092 | 0.118 |
| SEHP04 | Repair of household items | 4 | parent_inherit | 0.000 | 0.000 | 0.0129 | -0.140 | 0.180 |
| SEMC04 | Services by other medical professionals | 4 | parent_inherit | 0.000 | 0.000 | 0.0046 | -0.090 | 0.145 |
| SEMD03 | Home health care | 4 | parent_inherit | 0.000 | 0.000 | 0.0121 | -0.014 | 0.139 |
| SERA03 | Other video equipment | 4 | parent_inherit | 0.019 | 0.019 | 0.0188 | 0.110 | 0.347 |
| SERA05 | Audio equipment | 4 | parent_inherit | 0.045 | 0.045 | 0.0192 | 0.034 | 0.243 |
| SERA06 | Recorded music and music subscriptions | 4 | parent_inherit | 0.084 | 0.084 | 0.0125 | 0.182 | 0.097 |
| SERAC | Video and audio products | 4 | parent_inherit | 0.000 | 0.000 | 0.0105 | 0.291 | 0.421 |
| SERAS | Video and audio services | 4 | parent_inherit | 0.000 | 0.000 | 0.0063 | 0.295 | 0.237 |
| SERD | Photography | 4 | parent_inherit | 0.062 | 0.000 | 0.0100 | 0.069 | 0.276 |
| SERD01 | Photographic equipment and supplies | 4 | parent_inherit | 0.025 | 0.025 | 0.0172 | 0.168 | 0.295 |
| SERD02 | Photographers and photo processing | 4 | parent_inherit | 0.035 | 0.035 | 0.0104 | -0.062 | 0.118 |
| SERE02 | Sewing machines, fabric and supplies | 4 | parent_inherit | 0.028 | 0.000 | 0.0318 | 0.053 | 0.064 |
| SERE03 | Music instruments and accessories | 4 | parent_inherit | 0.042 | 0.000 | 0.0107 | -0.042 | 0.115 |
| SERG01 | Newspapers and magazines | 4 | parent_inherit | 0.055 | 0.055 | 0.0201 | -0.454 | 0.075 |
| SERG02 | Recreational books | 4 | parent_inherit | 0.054 | 0.054 | 0.0171 | -0.371 | 0.083 |
| SETC02 | Vehicle accessories other than tires | 4 | parent_inherit | 0.055 | 0.055 | 0.0085 | -0.127 | 0.034 |
| SETD01 | Motor vehicle body work | 4 | parent_inherit | 0.000 | 0.000 | 0.0064 | 0.149 | 0.073 |
| SS01031 | Rice | 4 | parent_inherit | 0.000 | 0.000 | 0.0112 | -0.220 | 0.098 |
| SS02011 | White bread | 4 | parent_inherit | 0.000 | 0.000 | 0.0098 | -0.172 | 0.060 |
| SS02021 | Bread other than white | 4 | parent_inherit | 0.000 | 0.000 | 0.0102 | -0.210 | 0.092 |
| SS02041 | Fresh cakes and cupcakes | 4 | parent_inherit | 0.000 | 0.000 | 0.0121 | -0.249 | 0.169 |
| SS02042 | Cookies | 4 | parent_inherit | 0.000 | 0.000 | 0.0138 | -0.247 | 0.111 |
| SS02063 | Fresh sweetrolls, coffeecakes, doughnuts | 4 | parent_inherit | 0.000 | 0.000 | 0.0146 | -0.318 | 0.066 |
| SS0206A | Crackers, bread, and cracker products | 4 | parent_inherit | 0.000 | 0.000 | 0.0160 | -0.125 | 0.348 |
| SS0206B | Frozen and refrigerated bakery products, pies, tarts, turnovers | 4 | parent_inherit | 0.000 | 0.000 | 0.0137 | -0.180 | 0.281 |
| SS04011 | Bacon and related products | 4 | parent_inherit | 0.000 | 0.000 | 0.0204 | 0.210 | 0.230 |
| SS04012 | Breakfast sausage and related products | 4 | parent_inherit | 0.000 | 0.000 | 0.0172 | -0.152 | 0.480 |
| SS04031 | Ham, excluding canned | 4 | parent_inherit | 0.000 | 0.000 | 0.0298 | -0.106 | 0.496 |
| SS05011 | Frankfurters | 4 | parent_inherit | 0.000 | 0.000 | 0.0292 | -0.238 | 0.290 |
| SS05014 | Lamb and organ meats | 4 | parent_inherit | 0.000 | 0.000 | 0.0183 | -0.392 | 0.280 |
| SS05015 | Lamb and mutton | 4 | parent_inherit | 0.000 | 0.000 | 0.0210 | -0.425 | 0.000 |
| SS0501A | Lunchmeats | 4 | parent_inherit | 0.000 | 0.000 | 0.0111 | -0.046 | 0.151 |
| SS06011 | Fresh whole chicken | 4 | parent_inherit | 0.000 | 0.000 | 0.0154 | -0.108 | 0.131 |
| SS06021 | Fresh and frozen chicken parts | 4 | parent_inherit | 0.000 | 0.000 | 0.0111 | 0.169 | 0.161 |
| SS07011 | Shelf stable fish and seafood | 4 | parent_inherit | 0.000 | 0.000 | 0.0151 | -0.207 | 0.253 |
| SS07021 | Frozen fish and seafood | 4 | parent_inherit | 0.000 | 0.000 | 0.0160 | -0.174 | 0.365 |
| SS09011 | Fresh whole milk | 4 | parent_inherit | 0.000 | 0.000 | 0.0118 | 0.279 | 0.077 |
| SS09021 | Fresh milk other than whole | 4 | parent_inherit | 0.000 | 0.000 | 0.0105 | 0.131 | 0.104 |
| SS10011 | Butter | 4 | parent_inherit | 0.000 | 0.000 | 0.0229 | -0.102 | 0.432 |
| SS11031 | Oranges, including tangerines | 4 | parent_inherit | 0.000 | 0.000 | 0.0364 | 0.320 | 0.587 |
| SS13031 | Canned fruits | 4 | parent_inherit | 0.000 | 0.000 | 0.0133 | -0.100 | 0.234 |
| SS14011 | Frozen vegetables | 4 | parent_inherit | 0.000 | 0.000 | 0.0134 | 0.018 | 0.266 |
| SS14021 | Canned vegetables | 4 | parent_inherit | 0.000 | 0.000 | 0.0161 | 0.099 | 0.447 |
| SS14022 | Dried beans, peas, and lentils | 4 | parent_inherit | 0.000 | 0.000 | 0.0142 | -0.155 | 0.134 |
| SS16011 | Margarine | 4 | parent_inherit | 0.000 | 0.000 | 0.0197 | 0.000 | 0.205 |
| SS16014 | Peanut butter | 4 | parent_inherit | 0.000 | 0.000 | 0.0205 | -0.313 | 0.200 |
| SS17031 | Roasted coffee | 4 | parent_inherit | 0.000 | 0.000 | 0.0125 | 0.031 | 0.217 |
| SS17032 | Instant coffee | 4 | parent_inherit | 0.000 | 0.000 | 0.0178 | -0.243 | 0.137 |
| SS18041 | Salt and other seasonings and spices | 4 | parent_inherit | 0.000 | 0.000 | 0.0148 | -0.024 | 0.407 |
| SS18042 | Olives, pickles, relishes | 4 | parent_inherit | 0.000 | 0.000 | 0.0202 | -0.247 | 0.170 |
| SS18043 | Sauces and gravies | 4 | parent_inherit | 0.000 | 0.000 | 0.0112 | -0.014 | 0.311 |
| SS1804B | Other condiments | 4 | parent_inherit | 0.000 | 0.000 | 0.0291 | -0.178 | 0.313 |
| SS18064 | Prepared salads | 4 | parent_inherit | 0.000 | 0.000 | 0.0137 | -0.107 | 0.226 |
| SS20021 | Whiskey at home | 4 | parent_inherit | 0.000 | 0.000 | 0.0082 | 0.012 | 0.229 |
| SS20022 | Distilled spirits, excluding whiskey, at home | 4 | parent_inherit | 0.000 | 0.000 | 0.0052 | 0.080 | 0.165 |
| SS20051 | Beer, ale, and other malt beverages away from home | 4 | parent_inherit | 0.000 | 0.000 | 0.0042 | -0.068 | 0.040 |
| SS20052 | Wine away from home | 4 | parent_inherit | 0.000 | 0.000 | 0.0034 | 0.063 | 0.121 |
| SS20053 | Distilled spirits away from home | 4 | parent_inherit | 0.000 | 0.000 | 0.0048 | 0.133 | 0.113 |
| SS27051 | Land-line interstate toll calls | 4 | parent_inherit | 0.000 | 0.000 | 0.0000 | 0.000 | 0.000 |
| SS27061 | Land-line intrastate toll calls | 4 | parent_inherit | 0.000 | 0.000 | 0.0000 | 0.000 | 0.000 |
| SS30021 | Laundry equipment | 4 | parent_inherit | 0.000 | 0.000 | 0.0289 | 0.135 | 0.158 |
| SS31022 | Video discs and other media | 4 | parent_inherit | 0.000 | 0.000 | 0.0300 | 0.123 | 0.173 |
| SS31023 | Video game hardware, software and accessories | 4 | parent_inherit | 0.000 | 0.000 | 0.0000 | 0.000 | 0.000 |
| SS33032 | Stationery, stationery supplies, gift wrap | 4 | parent_inherit | 0.000 | 0.000 | 0.0179 | 0.368 | 0.546 |
| SS45011 | New cars | 4 | parent_inherit | 0.000 | 0.000 | 0.0049 | 0.634 | 0.101 |
| SS4501A | New cars and trucks | 4 | parent_inherit | 0.000 | 0.000 | 0.0052 | 0.715 | 0.182 |
| SS45021 | New trucks | 4 | parent_inherit | 0.000 | 0.000 | 0.0043 | 0.693 | 0.082 |
| SS45031 | New motorcycles | 4 | parent_inherit | 0.000 | 0.000 | 0.0000 | 0.000 | 0.000 |
| SS47014 | Gasoline, unleaded regular | 4 | parent_inherit | 0.000 | 0.000 | 0.0605 | 0.365 | 0.224 |
| SS47015 | Gasoline, unleaded midgrade | 4 | parent_inherit | 0.000 | 0.000 | 0.0518 | 0.379 | 0.240 |
| SS47016 | Gasoline, unleaded premium | 4 | parent_inherit | 0.000 | 0.000 | 0.0475 | 0.394 | 0.242 |
| SS47021 | Motor oil, coolant, and fluids | 4 | parent_inherit | 0.000 | 0.000 | 0.0186 | -0.316 | 0.079 |
| SS48021 | Vehicle parts and equipment other than tires | 4 | parent_inherit | 0.000 | 0.000 | 0.0105 | -0.293 | 0.083 |
| SS52051 | Parking fees and tolls | 4 | parent_inherit | 0.000 | 0.000 | 0.0063 | -0.150 | 0.275 |
| SS53021 | Intercity bus fare | 4 | parent_inherit | 0.000 | 0.000 | 0.0491 | -0.107 | 0.410 |
| SS53022 | Intercity train fare | 4 | parent_inherit | 0.000 | 0.000 | 0.0225 | -0.031 | 0.698 |
| SS53023 | Ship fare | 4 | parent_inherit | 0.000 | 0.000 | 0.0132 | 0.181 | 0.125 |
| SS53031 | Intracity mass transit | 4 | parent_inherit | 0.000 | 0.000 | 0.0185 | -0.583 | 0.108 |
| SS5702 | Inpatient hospital services | 4 | parent_inherit | 0.000 | 0.000 | 0.0054 | -0.089 | 0.234 |
| SS5703 | Outpatient hospital services | 4 | parent_inherit | 0.000 | 0.000 | 0.0055 | -0.084 | 0.203 |
| SS61011 | Toys, games, hobbies and playground equipment | 4 | parent_inherit | 0.000 | 0.000 | 0.0123 | 0.149 | 0.272 |
| SS61021 | Film and photographic supplies | 4 | parent_inherit | 0.000 | 0.000 | 0.0108 | 0.072 | 0.000 |
| SS61023 | Photographic equipment | 4 | parent_inherit | 0.000 | 0.000 | 0.0181 | 0.168 | 0.303 |
| SS61031 | Pet food and treats | 4 | parent_inherit | 0.000 | 0.000 | 0.0057 | 0.430 | 0.033 |
| SS61032 | Purchase of pets, pet supplies, accessories | 4 | parent_inherit | 0.000 | 0.000 | 0.0085 | 0.044 | 0.051 |
| SS62011 | Automobile service clubs | 4 | parent_inherit | 0.000 | 0.000 | 0.0262 | -0.027 | 0.290 |
| SS62031 | Admission to movies, theaters, and concerts | 4 | parent_inherit | 0.000 | 0.000 | 0.0081 | -0.188 | 0.130 |
| SS62032 | Admission to sporting events | 4 | parent_inherit | 0.000 | 0.000 | 0.0390 | 0.146 | 0.132 |
| SS62051 | Photographer fees | 4 | parent_inherit | 0.000 | 0.000 | 0.0096 | 0.002 | 0.202 |
| SS62052 | Photo Processing | 4 | parent_inherit | 0.000 | 0.000 | 0.0148 | 0.012 | 0.222 |
| SS62053 | Pet services | 4 | parent_inherit | 0.000 | 0.000 | 0.0078 | 0.079 | 0.075 |
| SS62054 | Veterinarian services | 4 | parent_inherit | 0.000 | 0.000 | 0.0067 | 0.173 | 0.137 |
| SS62055 | Subscription and rental of video and video games | 4 | parent_inherit | 0.000 | 0.000 | 0.0221 | 0.040 | 0.089 |
| SS68021 | Checking account and other bank services | 4 | parent_inherit | 0.000 | 0.000 | 0.0206 | -0.317 | 0.122 |
| SS68023 | Tax return preparation and other accounting fees | 4 | parent_inherit | 0.000 | 0.000 | 0.0293 | 0.303 | 0.158 |
| SSEA011 | College textbooks | 4 | parent_inherit | 0.000 | 0.000 | 0.0130 | -0.219 | 0.056 |
| SSEE041 | Smartphones | 4 | parent_inherit | 0.000 | 0.000 | 0.0164 | 0.249 | 0.325 |
| SSFV031A | Food at elementary and secondary schools | 4 | parent_inherit | 0.000 | 0.000 | 0.0338 | 0.489 | 0.048 |
| SSGE013 | Infants' equipment | 4 | parent_inherit | 0.000 | 0.000 | 0.0263 | -0.157 | 0.158 |
| SSHJ031 | Infants' furniture | 4 | parent_inherit | 0.000 | 0.000 | 0.0270 | -0.043 | 0.555 |
