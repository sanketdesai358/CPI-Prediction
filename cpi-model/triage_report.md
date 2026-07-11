# CPI Model Triage Report

Generated from the validated registry plus the current BLS history cache. `model_weight` is the BLS current relative-importance weight for the selected non-overlapping forecast universe; parents and overlapping aggregates are excluded from the contribution table.

| Code | Component | Tier | Model | BLS RI | Model weight | sigma | rho | seasonal |
|---|---|---:|---|---:|---:|---:|---:|---:|
| SAF111 | Cereals and bakery products | 1 | food_commodity_complex_factor | 1.016 | 0.000 | 0.0061 | 0.234 | 0.097 |
| SAF112 | Meats, poultry, fish, and eggs | 1 | food_commodity_complex_factor | 1.943 | 0.000 | 0.0094 | 0.427 | 0.068 |
| SAF113 | Fruits and vegetables | 1 | food_commodity_complex_factor | 1.287 | 0.000 | 0.0083 | 0.090 | 0.365 |
| SAF114 | Nonalcoholic beverages and beverage materials | 1 | food_commodity_complex_factor | 0.993 | 0.000 | 0.0074 | 0.109 | 0.381 |
| SAF115 | Other food at home | 1 | food_commodity_complex_factor | 2.217 | 0.000 | 0.0055 | 0.386 | 0.154 |
| SEFA02 | Breakfast cereal | 1 | food_commodity_complex_factor | 0.132 | 0.132 | 0.0119 | -0.176 | 0.156 |
| SEFA03 | Rice, pasta, cornmeal | 1 | food_commodity_complex_factor | 0.137 | 0.137 | 0.0098 | -0.040 | 0.119 |
| SEFC01 | Uncooked ground beef | 1 | food_commodity_complex_factor | 0.235 | 0.235 | 0.0170 | 0.315 | 0.131 |
| SEFC02 | Uncooked beef roasts | 1 | food_commodity_complex_factor | 0.086 | 0.086 | 0.0282 | 0.208 | 0.210 |
| SEFC03 | Uncooked beef steaks | 1 | food_commodity_complex_factor | 0.236 | 0.236 | 0.0215 | 0.318 | 0.156 |
| SEFC04 | Uncooked other beef and veal | 1 | food_commodity_complex_factor | 0.073 | 0.073 | 0.0179 | 0.239 | 0.149 |
| SEFD01 | Bacon, breakfast sausage, and related products | 1 | food_commodity_complex_factor | 0.131 | 0.131 | 0.0152 | 0.106 | 0.358 |
| SEFD02 | Ham | 1 | food_commodity_complex_factor | 0.067 | 0.067 | 0.0277 | -0.103 | 0.499 |
| SEFD03 | Pork chops | 1 | food_commodity_complex_factor | 0.045 | 0.045 | 0.0235 | -0.131 | 0.154 |
| SEFD04 | Other pork including roasts, steaks, and ribs | 1 | food_commodity_complex_factor | 0.094 | 0.094 | 0.0215 | -0.119 | 0.151 |
| SEFF01 | Chicken | 1 | food_commodity_complex_factor | 0.281 | 0.281 | 0.0105 | 0.221 | 0.192 |
| SEFF02 | Other uncooked poultry including turkey | 1 | food_commodity_complex_factor | 0.077 | 0.077 | 0.0171 | 0.010 | 0.334 |
| SEFH | Eggs | 1 | food_commodity_complex_factor | 0.113 | 0.113 | 0.0521 | 0.308 | 0.217 |
| SEFJ | Dairy and related products | 1 | food_commodity_complex_factor | 0.732 | 0.000 | 0.0064 | 0.324 | 0.119 |
| SEFJ01 | Milk | 1 | food_commodity_complex_factor | 0.191 | 0.191 | 0.0102 | 0.230 | 0.113 |
| SEFJ02 | Cheese and related products | 1 | food_commodity_complex_factor | 0.243 | 0.243 | 0.0086 | -0.063 | 0.092 |
| SEFJ03 | Ice cream and related products | 1 | food_commodity_complex_factor | 0.110 | 0.110 | 0.0132 | -0.051 | 0.302 |
| SEFJ04 | Other dairy and related products | 1 | food_commodity_complex_factor | 0.189 | 0.189 | 0.0094 | 0.146 | 0.264 |
| SEFP01 | Coffee | 1 | food_commodity_complex_factor | 0.227 | 0.227 | 0.0120 | 0.052 | 0.216 |
| SEFS01 | Butter and margarine | 1 | food_commodity_complex_factor | 0.062 | 0.062 | 0.0179 | 0.063 | 0.371 |
| SEHA | Rent of primary residence | 1 | shelter_tier1_cpi_fallback | 7.679 | 7.679 | 0.0016 | 0.850 | 0.084 |
| SEHC | Owners' equivalent rent of residences | 1 | oer_tier1_cpi_fallback | 25.700 | 25.700 | 0.0014 | 0.841 | 0.056 |
| SEHC01 | Owners' equivalent rent of primary residence | 1 | oer_tier1_cpi_fallback | 24.742 | 0.000 | 0.0014 | 0.840 | 0.055 |
| SEHE01 | Fuel oil | 1 | measurement_pass_through_fuel_oil | 0.117 | 0.117 | 0.0639 | 0.377 | 0.082 |
| SEHF01 | Electricity | 1 | tariff_event_electricity | 2.506 | 2.506 | 0.0141 | 0.290 | 0.728 |
| SEHF02 | Utility (piped) gas service | 1 | distributed_lag_utility_gas | 0.734 | 0.734 | 0.0246 | 0.254 | 0.142 |
| SETA01 | New vehicles | 1 | new_vehicle_transaction_proxy | 3.735 | 3.735 | 0.0044 | 0.705 | 0.093 |
| SETA02 | Used cars and trucks | 1 | used_vehicle_lag_kernel | 2.628 | 2.628 | 0.0214 | 0.518 | 0.218 |
| SETA04 | Car and truck rental | 1 | rental_rate_scrape_proxy | 0.140 | 0.140 | 0.0611 | 0.365 | 0.550 |
| SETB01 | Gasoline (all types) | 1 | measurement_pass_through_gasoline | 4.250 | 4.250 | 0.0578 | 0.395 | 0.235 |
| SETG01 | Airline fares | 1 | airfare_fare_mix_proxy | 1.107 | 1.107 | 0.0530 | 0.472 | 0.485 |
| SEEB01 | College tuition and fees | 2 | tuition_aug_sep_event | 1.308 | 0.000 | 0.0037 | 0.492 | 0.756 |
| SEED03 | Wireless telephone services | 2 | wireless_plan_launch_event | 1.328 | 0.000 | 0.0091 | 0.228 | 0.080 |
| SEHG | Water and sewer and trash collection services | 2 | municipal_fee_calendar_step | 1.133 | 0.000 | 0.0025 | 0.088 | 0.371 |
| SEME | Health insurance | 2 | health_insurance_retained_earnings_step | 0.826 | 0.826 | 0.0156 | 0.843 | 0.009 |
| SETE | Motor vehicle insurance | 2 | insurance_filing_momentum | 2.617 | 2.617 | 0.0163 | 0.347 | 0.116 |
| SA0 | All items | 3 | seasonal_ar_partial_pool | 100.000 | 0.000 | 0.0034 | 0.553 | 0.341 |
| SA0E | Energy | 3 | seasonal_ar_partial_pool | 7.791 | 0.000 | 0.0310 | 0.407 | 0.244 |
| SA0L1 | All items less food | 3 | seasonal_ar_partial_pool | 86.553 | 0.000 | 0.0038 | 0.522 | 0.331 |
| SA0L1E | All items less food and energy | 3 | seasonal_ar_partial_pool | 78.762 | 0.000 | 0.0022 | 0.545 | 0.341 |
| SA0L2 | All items less shelter | 3 | seasonal_ar_partial_pool | 64.851 | 0.000 | 0.0048 | 0.522 | 0.336 |
| SA0L5 | All items less medical care | 3 | seasonal_ar_partial_pool | 91.771 | 0.000 | 0.0037 | 0.559 | 0.325 |
| SA0LE | All items less energy | 3 | seasonal_ar_partial_pool | 92.209 | 0.000 | 0.0021 | 0.599 | 0.341 |
| SA311 | Apparel less footwear | 3 | seasonal_ar_partial_pool | 1.866 | 0.000 | 0.0225 | 0.325 | 0.822 |
| SAA | Apparel | 3 | seasonal_ar_partial_pool | 2.458 | 0.000 | 0.0197 | 0.340 | 0.821 |
| SAA1 | Men's and boys' apparel | 3 | sarima_partial_pool | 0.609 | 0.000 | 0.0217 | 0.164 | 0.731 |
| SAA2 | Women's and girls' apparel | 3 | seasonal_ar_partial_pool | 0.976 | 0.000 | 0.0294 | 0.339 | 0.827 |
| SAC | Commodities | 3 | seasonal_ar_partial_pool | 36.735 | 0.000 | 0.0072 | 0.510 | 0.325 |
| SACE | Energy commodities | 3 | seasonal_ar_partial_pool | 4.550 | 0.000 | 0.0565 | 0.397 | 0.222 |
| SACL1 | Commodities less food | 3 | seasonal_ar_partial_pool | 23.288 | 0.000 | 0.0109 | 0.487 | 0.307 |
| SACL11 | Commodities less food and beverages | 3 | seasonal_ar_partial_pool | 22.469 | 0.000 | 0.0113 | 0.490 | 0.305 |
| SACL1E | Commodities less food and energy commodities | 3 | seasonal_ar_partial_pool | 18.738 | 0.000 | 0.0052 | 0.525 | 0.344 |
| SAD | Durables | 3 | seasonal_ar_partial_pool | 10.457 | 0.000 | 0.0071 | 0.641 | 0.140 |
| SAE | Education and communication | 3 | seasonal_ar_partial_pool | 5.701 | 0.000 | 0.0031 | 0.209 | 0.258 |
| SAE1 | Education | 3 | seasonal_ar_partial_pool | 2.524 | 0.000 | 0.0030 | 0.476 | 0.800 |
| SAE2 | Communication | 3 | ets_partial_pool | 3.177 | 3.177 | 0.0049 | 0.181 | 0.098 |
| SAE21 | Information and information processing | 3 | ets_partial_pool | 3.111 | 0.000 | 0.0050 | 0.185 | 0.096 |
| SAF | Food and beverages | 3 | seasonal_ar_partial_pool | 14.268 | 0.000 | 0.0031 | 0.582 | 0.162 |
| SAF1 | Food | 3 | seasonal_ar_partial_pool | 13.447 | 0.000 | 0.0033 | 0.579 | 0.158 |
| SAF11 | Food at home | 3 | seasonal_ar_partial_pool | 8.187 | 0.000 | 0.0049 | 0.468 | 0.184 |
| SAF1121 | Meats, poultry, and fish | 3 | seasonal_ar_partial_pool | 1.830 | 0.000 | 0.0090 | 0.470 | 0.203 |
| SAF11211 | Meats | 3 | seasonal_ar_partial_pool | 1.158 | 0.000 | 0.0117 | 0.396 | 0.164 |
| SAF1131 | Fresh fruits and vegetables | 3 | sarima_partial_pool | 1.024 | 0.000 | 0.0098 | 0.095 | 0.341 |
| SAF116 | Alcoholic beverages | 3 | sarima_partial_pool | 0.819 | 0.000 | 0.0024 | 0.182 | 0.243 |
| SAG | Other goods and services | 3 | sarima_partial_pool | 2.892 | 2.892 | 0.0031 | 0.048 | 0.187 |
| SAG1 | Personal care | 3 | sarima_partial_pool | 2.444 | 0.000 | 0.0034 | 0.096 | 0.185 |
| SAH | Housing | 3 | seasonal_ar_partial_pool | 43.896 | 0.000 | 0.0021 | 0.565 | 0.338 |
| SAH1 | Shelter | 3 | seasonal_ar_partial_pool | 35.149 | 0.000 | 0.0016 | 0.683 | 0.098 |
| SAH2 | Fuels and utilities | 3 | seasonal_ar_partial_pool | 4.546 | 0.000 | 0.0101 | 0.302 | 0.504 |
| SAH21 | Household energy | 3 | seasonal_ar_partial_pool | 3.413 | 0.000 | 0.0130 | 0.308 | 0.509 |
| SAH3 | Household furnishings and operations | 3 | seasonal_ar_partial_pool | 4.202 | 4.202 | 0.0046 | 0.335 | 0.277 |
| SAM | Medical care | 3 | seasonal_ar_partial_pool | 8.229 | 0.000 | 0.0028 | 0.341 | 0.189 |
| SAM1 | Medical care commodities | 3 | ets_partial_pool | 1.409 | 0.000 | 0.0050 | 0.137 | 0.111 |
| SAM2 | Medical care services | 3 | seasonal_ar_partial_pool | 6.821 | 0.000 | 0.0032 | 0.378 | 0.163 |
| SAN | Nondurables | 3 | seasonal_ar_partial_pool | 26.278 | 0.000 | 0.0091 | 0.432 | 0.328 |
| SAN1D | Domestically produced farm food | 3 | seasonal_ar_partial_pool | 6.823 | 0.000 | 0.0050 | 0.490 | 0.154 |
| SANL1 | Nondurables less food | 3 | seasonal_ar_partial_pool | 12.831 | 0.000 | 0.0182 | 0.408 | 0.305 |
| SANL11 | Nondurables less food and beverages | 3 | seasonal_ar_partial_pool | 12.012 | 0.000 | 0.0196 | 0.410 | 0.302 |
| SANL113 | Nondurables less food, beverages, and apparel | 3 | seasonal_ar_partial_pool | 9.554 | 0.000 | 0.0231 | 0.400 | 0.235 |
| SANL13 | Nondurables less food and apparel | 3 | seasonal_ar_partial_pool | 10.375 | 0.000 | 0.0211 | 0.397 | 0.237 |
| SAR | Recreation | 3 | seasonal_ar_partial_pool | 5.031 | 0.000 | 0.0036 | 0.219 | 0.241 |
| SAS | Services | 3 | seasonal_ar_partial_pool | 63.265 | 0.000 | 0.0020 | 0.562 | 0.250 |
| SAS24 | Utilities and public transportation | 3 | seasonal_ar_partial_pool | 8.107 | 0.000 | 0.0069 | 0.398 | 0.403 |
| SAS2RS | Rent of shelter | 3 | seasonal_ar_partial_pool | 34.862 | 0.000 | 0.0016 | 0.687 | 0.098 |
| SAS367 | Other services | 3 | sarima_partial_pool | 9.660 | 0.000 | 0.0022 | 0.180 | 0.137 |
| SAS4 | Transportation services | 3 | seasonal_ar_partial_pool | 6.378 | 0.000 | 0.0103 | 0.452 | 0.182 |
| SASL2RS | Services less rent of shelter | 3 | seasonal_ar_partial_pool | 28.402 | 0.000 | 0.0030 | 0.368 | 0.300 |
| SASL5 | Services less medical care services | 3 | seasonal_ar_partial_pool | 56.443 | 0.000 | 0.0022 | 0.601 | 0.213 |
| SASLE | Services less energy services | 3 | seasonal_ar_partial_pool | 60.025 | 0.000 | 0.0018 | 0.601 | 0.185 |
| SAT | Transportation | 3 | seasonal_ar_partial_pool | 17.526 | 0.000 | 0.0157 | 0.514 | 0.254 |
| SAT1 | Private transportation | 3 | seasonal_ar_partial_pool | 15.834 | 0.000 | 0.0156 | 0.483 | 0.240 |
| SEAA | Men's apparel | 3 | sarima_partial_pool | 0.489 | 0.000 | 0.0229 | 0.130 | 0.728 |
| SEAA02 | Men's underwear, nightwear, swimwear and accessories | 3 | sarima_partial_pool | 0.133 | 0.133 | 0.0195 | 0.052 | 0.387 |
| SEAA03 | Men's shirts and sweaters | 3 | sarima_partial_pool | 0.131 | 0.131 | 0.0338 | 0.167 | 0.643 |
| SEAA04 | Men's pants and shorts | 3 | sarima_partial_pool | 0.121 | 0.121 | 0.0298 | -0.036 | 0.628 |
| SEAB | Boys' apparel | 3 | sarima_partial_pool | 0.120 | 0.120 | 0.0275 | 0.168 | 0.381 |
| SEAC | Women's apparel | 3 | seasonal_ar_partial_pool | 0.827 | 0.000 | 0.0297 | 0.340 | 0.815 |
| SEAC02 | Women's dresses | 3 | seasonal_ar_partial_pool | 0.111 | 0.111 | 0.0576 | 0.282 | 0.809 |
| SEAC03 | Women's suits and separates | 3 | seasonal_ar_partial_pool | 0.389 | 0.389 | 0.0361 | 0.281 | 0.765 |
| SEAC04 | Women's underwear, nightwear, swimwear and accessories | 3 | sarima_partial_pool | 0.244 | 0.244 | 0.0189 | 0.120 | 0.397 |
| SEAD | Girls' apparel | 3 | sarima_partial_pool | 0.150 | 0.150 | 0.0359 | 0.200 | 0.644 |
| SEAE | Footwear | 3 | seasonal_ar_partial_pool | 0.592 | 0.000 | 0.0124 | 0.321 | 0.579 |
| SEAE01 | Men's footwear | 3 | sarima_partial_pool | 0.191 | 0.191 | 0.0135 | 0.048 | 0.426 |
| SEAE02 | Boys' and girls' footwear | 3 | sarima_partial_pool | 0.125 | 0.125 | 0.0178 | 0.166 | 0.265 |
| SEAE03 | Women's footwear | 3 | seasonal_ar_partial_pool | 0.276 | 0.276 | 0.0162 | 0.289 | 0.561 |
| SEAG | Jewelry and watches | 3 | sarima_partial_pool | 0.181 | 0.000 | 0.0283 | -0.145 | 0.521 |
| SEAG02 | Jewelry | 3 | sarima_partial_pool | 0.146 | 0.146 | 0.0341 | -0.138 | 0.529 |
| SEEB | Tuition, other school fees, and childcare | 3 | seasonal_ar_partial_pool | 2.487 | 2.487 | 0.0031 | 0.495 | 0.819 |
| SEEB02 | Elementary and high school tuition and fees | 3 | seasonal_ar_partial_pool | 0.396 | 0.000 | 0.0043 | 0.541 | 0.594 |
| SEEB03 | Day care and preschool | 3 | sarima_partial_pool | 0.680 | 0.000 | 0.0042 | 0.061 | 0.456 |
| SEED | Telephone services | 3 | seasonal_ar_partial_pool | 1.451 | 0.000 | 0.0070 | 0.225 | 0.084 |
| SEED04 | Residential telephone services | 3 | sarima_partial_pool | 0.123 | 0.000 | 0.0065 | 0.120 | 0.244 |
| SEEE | Information technology, hardware and services | 3 | sarima_partial_pool | 1.659 | 0.000 | 0.0052 | 0.114 | 0.149 |
| SEEE01 | Computers, peripherals, and smart home assistants | 3 | sarima_partial_pool | 0.300 | 0.000 | 0.0124 | 0.040 | 0.150 |
| SEEE03 | Internet services and electronic information providers | 3 | seasonal_ar_partial_pool | 0.909 | 0.000 | 0.0064 | 0.210 | 0.145 |
| SEEE04 | Telephone hardware, calculators, and other consumer information items | 3 | seasonal_ar_partial_pool | 0.410 | 0.000 | 0.0133 | 0.225 | 0.167 |
| SEFA | Cereals and cereal products | 3 | ets_partial_pool | 0.307 | 0.000 | 0.0085 | 0.078 | 0.114 |
| SEFB | Bakery products | 3 | ets_partial_pool | 0.710 | 0.000 | 0.0064 | 0.102 | 0.088 |
| SEFB01 | Bread | 3 | ets_partial_pool | 0.171 | 0.171 | 0.0086 | -0.134 | 0.056 |
| SEFB02 | Fresh biscuits, rolls, muffins | 3 | seasonal_ar_partial_pool | 0.117 | 0.117 | 0.0125 | -0.315 | 0.072 |
| SEFB03 | Cakes, cupcakes, and cookies | 3 | sarima_partial_pool | 0.207 | 0.207 | 0.0089 | -0.141 | 0.126 |
| SEFB04 | Other bakery products | 3 | sarima_partial_pool | 0.215 | 0.215 | 0.0103 | -0.088 | 0.322 |
| SEFC | Beef and veal | 3 | seasonal_ar_partial_pool | 0.628 | 0.000 | 0.0183 | 0.402 | 0.162 |
| SEFD | Pork | 3 | seasonal_ar_partial_pool | 0.337 | 0.000 | 0.0129 | 0.207 | 0.385 |
| SEFE | Other meats | 3 | sarima_partial_pool | 0.192 | 0.192 | 0.0107 | -0.004 | 0.210 |
| SEFF | Poultry | 3 | seasonal_ar_partial_pool | 0.357 | 0.000 | 0.0094 | 0.287 | 0.191 |
| SEFG | Fish and seafood | 3 | sarima_partial_pool | 0.316 | 0.000 | 0.0090 | -0.067 | 0.294 |
| SEFG01 | Fresh fish and seafood | 3 | seasonal_ar_partial_pool | 0.169 | 0.169 | 0.0113 | -0.252 | 0.247 |
| SEFG02 | Processed fish and seafood | 3 | sarima_partial_pool | 0.147 | 0.147 | 0.0121 | -0.069 | 0.406 |
| SEFK | Fresh fruits | 3 | sarima_partial_pool | 0.528 | 0.000 | 0.0128 | 0.025 | 0.462 |
| SEFK04 | Other fresh fruits | 3 | seasonal_ar_partial_pool | 0.315 | 0.315 | 0.0297 | 0.278 | 0.592 |
| SEFL | Fresh vegetables | 3 | seasonal_ar_partial_pool | 0.496 | 0.000 | 0.0127 | 0.208 | 0.182 |
| SEFL04 | Other fresh vegetables | 3 | sarima_partial_pool | 0.309 | 0.309 | 0.0117 | 0.139 | 0.210 |
| SEFM | Processed fruits and vegetables | 3 | sarima_partial_pool | 0.264 | 0.000 | 0.0100 | 0.163 | 0.444 |
| SEFM01 | Canned fruits and vegetables | 3 | sarima_partial_pool | 0.101 | 0.101 | 0.0137 | 0.092 | 0.436 |
| SEFN | Juices and nonalcoholic drinks | 3 | sarima_partial_pool | 0.670 | 0.000 | 0.0089 | 0.050 | 0.388 |
| SEFN01 | Carbonated drinks | 3 | sarima_partial_pool | 0.326 | 0.326 | 0.0138 | -0.043 | 0.490 |
| SEFN03 | Nonfrozen noncarbonated juices and drinks | 3 | sarima_partial_pool | 0.339 | 0.339 | 0.0080 | 0.031 | 0.178 |
| SEFP | Beverage materials including coffee and tea | 3 | sarima_partial_pool | 0.323 | 0.000 | 0.0087 | 0.036 | 0.214 |
| SEFR | Sugar and sweets | 3 | sarima_partial_pool | 0.325 | 0.000 | 0.0077 | 0.001 | 0.232 |
| SEFR02 | Candy and chewing gum | 3 | sarima_partial_pool | 0.238 | 0.238 | 0.0091 | -0.034 | 0.160 |
| SEFS | Fats and oils | 3 | sarima_partial_pool | 0.215 | 0.000 | 0.0109 | 0.090 | 0.369 |
| SEFS03 | Other fats and oils including peanut butter | 3 | sarima_partial_pool | 0.105 | 0.105 | 0.0119 | -0.045 | 0.248 |
| SEFT | Other foods | 3 | seasonal_ar_partial_pool | 1.676 | 0.000 | 0.0061 | 0.278 | 0.211 |
| SEFT02 | Frozen and freeze dried prepared foods | 3 | sarima_partial_pool | 0.290 | 0.290 | 0.0098 | -0.050 | 0.275 |
| SEFT03 | Snacks | 3 | sarima_partial_pool | 0.363 | 0.363 | 0.0096 | -0.034 | 0.201 |
| SEFT04 | Spices, seasonings, condiments, sauces | 3 | sarima_partial_pool | 0.318 | 0.318 | 0.0102 | 0.022 | 0.519 |
| SEFT06 | Other miscellaneous foods | 3 | sarima_partial_pool | 0.567 | 0.567 | 0.0088 | -0.097 | 0.356 |
| SEFV | Food away from home | 3 | seasonal_ar_partial_pool | 5.260 | 0.000 | 0.0020 | 0.646 | 0.063 |
| SEFV01 | Full service meals and snacks | 3 | seasonal_ar_partial_pool | 2.329 | 2.329 | 0.0023 | 0.464 | 0.072 |
| SEFV02 | Limited service meals and snacks | 3 | seasonal_ar_partial_pool | 2.634 | 2.634 | 0.0022 | 0.566 | 0.087 |
| SEFV05 | Other food away from home | 3 | sarima_partial_pool | 0.181 | 0.181 | 0.0047 | -0.109 | 0.123 |
| SEFW | Alcoholic beverages at home | 3 | sarima_partial_pool | 0.385 | 0.000 | 0.0035 | 0.142 | 0.336 |
| SEFW01 | Beer, ale, and other malt beverages at home | 3 | sarima_partial_pool | 0.133 | 0.133 | 0.0049 | 0.152 | 0.170 |
| SEFW03 | Wine at home | 3 | sarima_partial_pool | 0.166 | 0.166 | 0.0051 | 0.030 | 0.393 |
| SEFX | Alcoholic beverages away from home | 3 | ets_partial_pool | 0.434 | 0.434 | 0.0031 | 0.035 | 0.111 |
| SEGA | Tobacco and smoking products | 3 | ets_partial_pool | 0.447 | 0.000 | 0.0056 | -0.111 | 0.093 |
| SEGA01 | Cigarettes | 3 | ets_partial_pool | 0.327 | 0.000 | 0.0059 | -0.093 | 0.081 |
| SEGA02 | Tobacco products other than cigarettes | 3 | seasonal_ar_partial_pool | 0.115 | 0.000 | 0.0085 | -0.414 | 0.113 |
| SEGB | Personal care products | 3 | sarima_partial_pool | 0.667 | 0.000 | 0.0045 | 0.198 | 0.288 |
| SEGB01 | Hair, dental, shaving, and miscellaneous personal care products | 3 | sarima_partial_pool | 0.318 | 0.000 | 0.0054 | 0.084 | 0.203 |
| SEGB02 | Cosmetics, perfume, bath, nail preparations and implements | 3 | sarima_partial_pool | 0.339 | 0.000 | 0.0068 | -0.001 | 0.228 |
| SEGC | Personal care services | 3 | sarima_partial_pool | 0.656 | 0.000 | 0.0039 | 0.115 | 0.127 |
| SEGC01 | Haircuts and other personal care services | 3 | sarima_partial_pool | 0.656 | 0.000 | 0.0039 | 0.115 | 0.127 |
| SEGD | Miscellaneous personal services | 3 | ets_partial_pool | 0.938 | 0.000 | 0.0065 | 0.007 | 0.091 |
| SEGD02 | Funeral expenses | 3 | ets_partial_pool | 0.164 | 0.000 | 0.0046 | -0.184 | 0.090 |
| SEGD03 | Laundry and dry cleaning services | 3 | ets_partial_pool | 0.129 | 0.000 | 0.0039 | 0.159 | 0.064 |
| SEGD05 | Financial services | 3 | seasonal_ar_partial_pool | 0.242 | 0.000 | 0.0208 | 0.306 | 0.180 |
| SEGE | Miscellaneous personal goods | 3 | sarima_partial_pool | 0.183 | 0.000 | 0.0150 | 0.052 | 0.302 |
| SEHB | Lodging away from home | 3 | seasonal_ar_partial_pool | 1.483 | 1.483 | 0.0343 | 0.465 | 0.609 |
| SEHB02 | Other lodging away from home including hotels and motels | 3 | seasonal_ar_partial_pool | 1.269 | 0.000 | 0.0399 | 0.470 | 0.618 |
| SEHD | Tenants' and household insurance | 3 | ets_partial_pool | 0.286 | 0.286 | 0.0037 | 0.167 | 0.040 |
| SEHE | Fuel oil and other fuels | 3 | seasonal_ar_partial_pool | 0.173 | 0.000 | 0.0441 | 0.406 | 0.124 |
| SEHF | Energy services | 3 | seasonal_ar_partial_pool | 3.240 | 0.000 | 0.0135 | 0.305 | 0.558 |
| SEHG01 | Water and sewerage maintenance | 3 | sarima_partial_pool | 0.777 | 0.777 | 0.0027 | 0.060 | 0.481 |
| SEHG02 | Garbage and trash collection | 3 | sarima_partial_pool | 0.356 | 0.356 | 0.0049 | 0.039 | 0.127 |
| SEHH | Window and floor coverings and other linens | 3 | sarima_partial_pool | 0.232 | 0.000 | 0.0164 | 0.034 | 0.403 |
| SEHH03 | Other linens | 3 | sarima_partial_pool | 0.121 | 0.000 | 0.0253 | -0.031 | 0.423 |
| SEHJ | Furniture and bedding | 3 | ets_partial_pool | 0.848 | 0.000 | 0.0086 | 0.189 | 0.100 |
| SEHJ01 | Bedroom furniture | 3 | ets_partial_pool | 0.291 | 0.000 | 0.0101 | 0.077 | 0.069 |
| SEHJ02 | Living room, kitchen, and dining room furniture | 3 | ets_partial_pool | 0.423 | 0.000 | 0.0120 | 0.146 | 0.074 |
| SEHJ03 | Other furniture | 3 | sarima_partial_pool | 0.128 | 0.000 | 0.0158 | 0.144 | 0.191 |
| SEHK | Appliances | 3 | sarima_partial_pool | 0.197 | 0.000 | 0.0130 | 0.010 | 0.431 |
| SEHK02 | Other appliances | 3 | sarima_partial_pool | 0.129 | 0.000 | 0.0149 | -0.072 | 0.406 |
| SEHL | Other household equipment and furnishings | 3 | seasonal_ar_partial_pool | 0.544 | 0.000 | 0.0110 | 0.258 | 0.342 |
| SEHL01 | Clocks, lamps, and decorator items | 3 | sarima_partial_pool | 0.311 | 0.000 | 0.0152 | 0.096 | 0.152 |
| SEHL02 | Indoor plants and flowers | 3 | sarima_partial_pool | 0.116 | 0.000 | 0.0177 | -0.077 | 0.650 |
| SEHM | Tools, hardware, outdoor equipment and supplies | 3 | seasonal_ar_partial_pool | 0.670 | 0.000 | 0.0069 | 0.312 | 0.101 |
| SEHM01 | Tools, hardware and supplies | 3 | seasonal_ar_partial_pool | 0.208 | 0.000 | 0.0081 | 0.258 | 0.228 |
| SEHM02 | Outdoor equipment and supplies | 3 | ets_partial_pool | 0.287 | 0.000 | 0.0097 | 0.197 | 0.098 |
| SEHN | Housekeeping supplies | 3 | seasonal_ar_partial_pool | 0.826 | 0.000 | 0.0057 | 0.225 | 0.105 |
| SEHN01 | Household cleaning products | 3 | seasonal_ar_partial_pool | 0.298 | 0.000 | 0.0062 | 0.218 | 0.079 |
| SEHN02 | Household paper products | 3 | ets_partial_pool | 0.172 | 0.000 | 0.0101 | 0.053 | 0.101 |
| SEHN03 | Miscellaneous household products | 3 | sarima_partial_pool | 0.356 | 0.000 | 0.0088 | 0.060 | 0.133 |
| SEMC | Professional services | 3 | seasonal_ar_partial_pool | 3.399 | 3.399 | 0.0027 | 0.224 | 0.157 |
| SEMC01 | Physicians' services | 3 | seasonal_ar_partial_pool | 1.658 | 0.000 | 0.0039 | 0.220 | 0.086 |
| SEMC02 | Dental services | 3 | sarima_partial_pool | 0.914 | 0.000 | 0.0051 | 0.090 | 0.129 |
| SEMC03 | Eyeglasses and eye care | 3 | ets_partial_pool | 0.315 | 0.000 | 0.0057 | -0.094 | 0.093 |
| SEMD | Hospital and related services | 3 | sarima_partial_pool | 2.595 | 2.595 | 0.0047 | -0.053 | 0.278 |
| SEMD01 | Hospital services | 3 | sarima_partial_pool | 2.145 | 0.000 | 0.0051 | -0.083 | 0.243 |
| SEMD02 | Nursing homes and adult day services | 3 | sarima_partial_pool | 0.221 | 0.000 | 0.0045 | 0.102 | 0.380 |
| SEMF | Medicinal drugs | 3 | ets_partial_pool | 1.277 | 0.000 | 0.0052 | 0.116 | 0.107 |
| SEMF01 | Prescription drugs | 3 | sarima_partial_pool | 0.917 | 0.917 | 0.0067 | 0.064 | 0.143 |
| SEMF02 | Nonprescription drugs | 3 | sarima_partial_pool | 0.360 | 0.360 | 0.0069 | 0.174 | 0.205 |
| SEMG | Medical equipment and supplies | 3 | sarima_partial_pool | 0.132 | 0.132 | 0.0102 | 0.137 | 0.146 |
| SERA | Video and audio | 3 | seasonal_ar_partial_pool | 1.027 | 0.000 | 0.0054 | 0.337 | 0.288 |
| SERA01 | Televisions | 3 | seasonal_ar_partial_pool | 0.103 | 0.103 | 0.0163 | 0.354 | 0.332 |
| SERA02 | Cable, satellite, and live streaming television service | 3 | seasonal_ar_partial_pool | 0.591 | 0.591 | 0.0061 | 0.333 | 0.267 |
| SERA04 | Purchase, subscription, and rental of video | 3 | sarima_partial_pool | 0.181 | 0.181 | 0.0175 | 0.082 | 0.158 |
| SERB | Pets, pet products and services | 3 | seasonal_ar_partial_pool | 1.137 | 0.000 | 0.0045 | 0.365 | 0.128 |
| SERB01 | Pets and pet products | 3 | seasonal_ar_partial_pool | 0.597 | 0.597 | 0.0056 | 0.298 | 0.041 |
| SERB02 | Pet services including veterinary | 3 | sarima_partial_pool | 0.540 | 0.540 | 0.0054 | 0.138 | 0.179 |
| SERC | Sporting goods | 3 | ets_partial_pool | 0.520 | 0.520 | 0.0089 | -0.035 | 0.081 |
| SERC01 | Sports vehicles including bicycles | 3 | ets_partial_pool | 0.277 | 0.000 | 0.0137 | -0.043 | 0.072 |
| SERC02 | Sports equipment | 3 | ets_partial_pool | 0.232 | 0.000 | 0.0079 | 0.146 | 0.101 |
| SERE | Other recreational goods | 3 | seasonal_ar_partial_pool | 0.381 | 0.381 | 0.0089 | 0.248 | 0.344 |
| SERE01 | Toys | 3 | seasonal_ar_partial_pool | 0.295 | 0.000 | 0.0105 | 0.220 | 0.370 |
| SERF | Other recreation services | 3 | ets_partial_pool | 1.791 | 1.791 | 0.0072 | 0.089 | 0.058 |
| SERF01 | Club membership for shopping clubs, fraternal, or other organizations, or participant sports fees | 3 | ets_partial_pool | 0.740 | 0.000 | 0.0087 | 0.127 | 0.085 |
| SERF02 | Admissions | 3 | ets_partial_pool | 0.690 | 0.000 | 0.0134 | 0.109 | 0.052 |
| SERF03 | Fees for lessons or instructions | 3 | ets_partial_pool | 0.155 | 0.000 | 0.0088 | -0.034 | 0.086 |
| SERG | Recreational reading materials | 3 | seasonal_ar_partial_pool | 0.109 | 0.000 | 0.0124 | -0.378 | 0.046 |
| SETA | New and used motor vehicles | 3 | seasonal_ar_partial_pool | 6.959 | 0.000 | 0.0101 | 0.570 | 0.189 |
| SETA03 | Leased cars and trucks | 3 | sarima_partial_pool | 0.383 | 0.383 | 0.0079 | 0.069 | 0.134 |
| SETB | Motor fuel | 3 | seasonal_ar_partial_pool | 4.378 | 0.000 | 0.0579 | 0.396 | 0.233 |
| SETB02 | Other motor fuels | 3 | seasonal_ar_partial_pool | 0.128 | 0.128 | 0.0511 | 0.515 | 0.119 |
| SETC | Motor vehicle parts and equipment | 3 | seasonal_ar_partial_pool | 0.336 | 0.000 | 0.0056 | 0.299 | 0.086 |
| SETC01 | Tires | 3 | sarima_partial_pool | 0.282 | 0.282 | 0.0070 | 0.184 | 0.137 |
| SETD | Motor vehicle maintenance and repair | 3 | seasonal_ar_partial_pool | 1.034 | 1.034 | 0.0053 | 0.228 | 0.115 |
| SETD02 | Motor vehicle maintenance and servicing | 3 | ets_partial_pool | 0.513 | 0.000 | 0.0046 | 0.055 | 0.039 |
| SETD03 | Motor vehicle repair | 3 | sarima_partial_pool | 0.395 | 0.000 | 0.0108 | 0.150 | 0.128 |
| SETF | Motor vehicle fees | 3 | seasonal_ar_partial_pool | 0.511 | 0.511 | 0.0064 | -0.247 | 0.334 |
| SETF01 | State motor vehicle registration and license fees | 3 | sarima_partial_pool | 0.295 | 0.000 | 0.0041 | -0.076 | 0.331 |
| SETF03 | Parking and other fees | 3 | seasonal_ar_partial_pool | 0.195 | 0.000 | 0.0119 | -0.257 | 0.258 |
| SETG | Public transportation | 3 | seasonal_ar_partial_pool | 1.693 | 0.000 | 0.0342 | 0.508 | 0.473 |
| SETG02 | Other intercity transportation | 3 | sarima_partial_pool | 0.232 | 0.232 | 0.0162 | 0.023 | 0.312 |
| SETG03 | Intracity transportation | 3 | seasonal_ar_partial_pool | 0.348 | 0.348 | 0.0134 | -0.368 | 0.124 |
| AA0 | All items - old base | 4 | parent_inherit | 0.000 | 0.000 | 0.0034 | 0.553 | 0.341 |
| AA0R | Purchasing power of the consumer dollar - old base | 4 | parent_inherit | 0.000 | 0.000 | 0.0045 | 0.104 | 0.240 |
| SA0L12 | All items less food and shelter | 4 | parent_inherit | 0.000 | 0.000 | 0.0058 | 0.494 | 0.322 |
| SA0L12E | All items less food, shelter, and energy | 4 | parent_inherit | 0.000 | 0.000 | 0.0032 | 0.460 | 0.368 |
| SA0L12E4 | All items less food, shelter, energy, and used cars and trucks | 4 | parent_inherit | 0.000 | 0.000 | 0.0029 | 0.384 | 0.515 |
| SA0R | Purchasing power of the consumer dollar | 4 | parent_inherit | 0.000 | 0.000 | 0.0036 | 0.442 | 0.337 |
| SACL1E4 | Commodities less food, energy, and used cars and trucks | 4 | parent_inherit | 0.000 | 0.000 | 0.0046 | 0.413 | 0.643 |
| SAEC | Education and communication commodities | 4 | parent_inherit | 0.000 | 0.000 | 0.0081 | 0.031 | 0.143 |
| SAES | Education and communication services | 4 | parent_inherit | 0.000 | 0.000 | 0.0032 | 0.243 | 0.258 |
| SAGC | Other goods | 4 | parent_inherit | 0.000 | 0.000 | 0.0040 | -0.007 | 0.294 |
| SAGS | Other personal services | 4 | parent_inherit | 0.000 | 0.000 | 0.0042 | -0.019 | 0.066 |
| SAH31 | Household furnishings and supplies | 4 | parent_inherit | 0.000 | 0.000 | 0.0051 | 0.457 | 0.321 |
| SARC | Recreation commodities | 4 | parent_inherit | 0.000 | 0.000 | 0.0048 | 0.236 | 0.262 |
| SARS | Recreation services | 4 | parent_inherit | 0.000 | 0.000 | 0.0046 | 0.192 | 0.168 |
| SATCLTB | Transportation commodities less motor fuel | 4 | parent_inherit | 0.000 | 0.000 | 0.0098 | 0.585 | 0.162 |
| SEAA01 | Men's suits, sport coats, and outerwear | 4 | parent_inherit | 0.099 | 0.099 | 0.0375 | 0.091 | 0.522 |
| SEAC01 | Women's outerwear | 4 | parent_inherit | 0.067 | 0.067 | 0.0445 | 0.242 | 0.615 |
| SEAF | Infants' and toddlers' apparel | 4 | parent_inherit | 0.099 | 0.099 | 0.0209 | 0.083 | 0.350 |
| SEAG01 | Watches | 4 | parent_inherit | 0.035 | 0.035 | 0.0253 | -0.218 | 0.183 |
| SEEA | Educational books and supplies | 4 | parent_inherit | 0.037 | 0.037 | 0.0109 | -0.184 | 0.093 |
| SEEB04 | Technical and vocational school tuition and fixed fees | 4 | parent_inherit | 0.000 | 0.000 | 0.0036 | -0.123 | 0.172 |
| SEEC | Postage and delivery services | 4 | parent_inherit | 0.067 | 0.000 | 0.0102 | 0.211 | 0.261 |
| SEEC01 | Postage | 4 | parent_inherit | 0.061 | 0.000 | 0.0117 | 0.135 | 0.288 |
| SEEC02 | Delivery services | 4 | parent_inherit | 0.005 | 0.000 | 0.0143 | 0.083 | 0.500 |
| SEEE02 | Computer software and accessories | 4 | parent_inherit | 0.031 | 0.000 | 0.0214 | 0.069 | 0.056 |
| SEEEC | Information technology commodities | 4 | parent_inherit | 0.000 | 0.000 | 0.0093 | 0.073 | 0.179 |
| SEFA01 | Flour and prepared flour mixes | 4 | parent_inherit | 0.038 | 0.038 | 0.0193 | 0.082 | 0.635 |
| SEFK01 | Apples | 4 | parent_inherit | 0.077 | 0.077 | 0.0227 | 0.198 | 0.446 |
| SEFK02 | Bananas | 4 | parent_inherit | 0.057 | 0.057 | 0.0103 | -0.127 | 0.045 |
| SEFK03 | Citrus fruits | 4 | parent_inherit | 0.079 | 0.079 | 0.0280 | 0.375 | 0.490 |
| SEFL01 | Potatoes | 4 | parent_inherit | 0.066 | 0.066 | 0.0288 | 0.110 | 0.734 |
| SEFL02 | Lettuce | 4 | parent_inherit | 0.047 | 0.047 | 0.0404 | -0.012 | 0.222 |
| SEFL03 | Tomatoes | 4 | parent_inherit | 0.073 | 0.073 | 0.0363 | 0.202 | 0.268 |
| SEFM02 | Frozen fruits and vegetables | 4 | parent_inherit | 0.083 | 0.083 | 0.0113 | 0.051 | 0.217 |
| SEFM03 | Other processed fruits and vegetables including dried | 4 | parent_inherit | 0.080 | 0.080 | 0.0115 | -0.174 | 0.273 |
| SEFN02 | Frozen noncarbonated juices and drinks | 4 | parent_inherit | 0.004 | 0.004 | 0.0185 | -0.026 | 0.083 |
| SEFP02 | Other beverage materials including tea | 4 | parent_inherit | 0.096 | 0.096 | 0.0111 | -0.282 | 0.227 |
| SEFR01 | Sugar and sugar substitutes | 4 | parent_inherit | 0.032 | 0.032 | 0.0149 | 0.017 | 0.565 |
| SEFR03 | Other sweets | 4 | parent_inherit | 0.055 | 0.055 | 0.0110 | -0.142 | 0.146 |
| SEFS02 | Salad dressing | 4 | parent_inherit | 0.048 | 0.048 | 0.0150 | -0.169 | 0.303 |
| SEFT01 | Soups | 4 | parent_inherit | 0.088 | 0.088 | 0.0168 | 0.327 | 0.540 |
| SEFT05 | Baby food and formula | 4 | parent_inherit | 0.051 | 0.051 | 0.0107 | -0.070 | 0.143 |
| SEFV03 | Food at employee sites and schools | 4 | parent_inherit | 0.063 | 0.063 | 0.0563 | 0.362 | 0.081 |
| SEFV04 | Food from vending machines and mobile vendors | 4 | parent_inherit | 0.053 | 0.053 | 0.0075 | 0.089 | 0.103 |
| SEFW02 | Distilled spirits at home | 4 | parent_inherit | 0.087 | 0.087 | 0.0050 | 0.080 | 0.246 |
| SEGD01 | Legal services | 4 | parent_inherit | 0.000 | 0.000 | 0.0065 | 0.096 | 0.139 |
| SEGD04 | Apparel services other than laundry and dry cleaning | 4 | parent_inherit | 0.029 | 0.000 | 0.0101 | -0.012 | 0.077 |
| SEHB01 | Lodging while at school | 4 | parent_inherit | 0.000 | 0.000 | 0.0037 | 0.545 | 0.819 |
| SEHE02 | Propane, kerosene, and firewood | 4 | parent_inherit | 0.057 | 0.057 | 0.0223 | 0.491 | 0.466 |
| SEHH01 | Floor coverings | 4 | parent_inherit | 0.068 | 0.000 | 0.0127 | 0.018 | 0.071 |
| SEHH02 | Window coverings | 4 | parent_inherit | 0.044 | 0.000 | 0.0270 | -0.181 | 0.182 |
| SEHK01 | Major appliances | 4 | parent_inherit | 0.065 | 0.000 | 0.0183 | 0.085 | 0.297 |
| SEHL03 | Dishes and flatware | 4 | parent_inherit | 0.045 | 0.000 | 0.0250 | 0.030 | 0.207 |
| SEHL04 | Nonelectric cookware and tableware | 4 | parent_inherit | 0.070 | 0.000 | 0.0165 | 0.185 | 0.275 |
| SEHP | Household operations | 4 | parent_inherit | 0.000 | 0.000 | 0.0072 | -0.122 | 0.126 |
| SEHP01 | Domestic services | 4 | parent_inherit | 0.000 | 0.000 | 0.0139 | -0.265 | 0.087 |
| SEHP02 | Gardening and lawncare services | 4 | parent_inherit | 0.000 | 0.000 | 0.0124 | -0.003 | 0.205 |
| SEHP03 | Moving, storage, freight expense | 4 | parent_inherit | 0.077 | 0.000 | 0.0240 | 0.091 | 0.116 |
| SEHP04 | Repair of household items | 4 | parent_inherit | 0.000 | 0.000 | 0.0129 | -0.134 | 0.182 |
| SEMC04 | Services by other medical professionals | 4 | parent_inherit | 0.000 | 0.000 | 0.0046 | -0.090 | 0.145 |
| SEMD03 | Home health care | 4 | parent_inherit | 0.000 | 0.000 | 0.0121 | -0.014 | 0.139 |
| SERA03 | Other video equipment | 4 | parent_inherit | 0.018 | 0.018 | 0.0181 | 0.109 | 0.417 |
| SERA05 | Audio equipment | 4 | parent_inherit | 0.045 | 0.045 | 0.0192 | 0.034 | 0.243 |
| SERA06 | Recorded music and music subscriptions | 4 | parent_inherit | 0.083 | 0.083 | 0.0125 | 0.181 | 0.097 |
| SERAC | Video and audio products | 4 | parent_inherit | 0.000 | 0.000 | 0.0104 | 0.295 | 0.418 |
| SERAS | Video and audio services | 4 | parent_inherit | 0.000 | 0.000 | 0.0063 | 0.298 | 0.238 |
| SERD | Photography | 4 | parent_inherit | 0.063 | 0.000 | 0.0097 | 0.078 | 0.276 |
| SERD01 | Photographic equipment and supplies | 4 | parent_inherit | 0.026 | 0.026 | 0.0170 | 0.166 | 0.292 |
| SERD02 | Photographers and photo processing | 4 | parent_inherit | 0.036 | 0.036 | 0.0100 | -0.045 | 0.109 |
| SERE02 | Sewing machines, fabric and supplies | 4 | parent_inherit | 0.029 | 0.000 | 0.0318 | 0.049 | 0.063 |
| SERE03 | Music instruments and accessories | 4 | parent_inherit | 0.042 | 0.000 | 0.0108 | -0.050 | 0.120 |
| SERG01 | Newspapers and magazines | 4 | parent_inherit | 0.054 | 0.054 | 0.0200 | -0.466 | 0.077 |
| SERG02 | Recreational books | 4 | parent_inherit | 0.055 | 0.055 | 0.0170 | -0.369 | 0.086 |
| SETC02 | Vehicle accessories other than tires | 4 | parent_inherit | 0.054 | 0.054 | 0.0085 | -0.123 | 0.037 |
| SETD01 | Motor vehicle body work | 4 | parent_inherit | 0.000 | 0.000 | 0.0064 | 0.150 | 0.073 |
| SS01031 | Rice | 4 | parent_inherit | 0.000 | 0.000 | 0.0112 | -0.214 | 0.098 |
| SS02011 | White bread | 4 | parent_inherit | 0.000 | 0.000 | 0.0098 | -0.166 | 0.060 |
| SS02021 | Bread other than white | 4 | parent_inherit | 0.000 | 0.000 | 0.0102 | -0.214 | 0.088 |
| SS02041 | Fresh cakes and cupcakes | 4 | parent_inherit | 0.000 | 0.000 | 0.0121 | -0.260 | 0.183 |
| SS02042 | Cookies | 4 | parent_inherit | 0.000 | 0.000 | 0.0138 | -0.247 | 0.112 |
| SS02063 | Fresh sweetrolls, coffeecakes, doughnuts | 4 | parent_inherit | 0.000 | 0.000 | 0.0145 | -0.304 | 0.064 |
| SS0206A | Crackers, bread, and cracker products | 4 | parent_inherit | 0.000 | 0.000 | 0.0158 | -0.143 | 0.356 |
| SS0206B | Frozen and refrigerated bakery products, pies, tarts, turnovers | 4 | parent_inherit | 0.000 | 0.000 | 0.0137 | -0.188 | 0.278 |
| SS04011 | Bacon and related products | 4 | parent_inherit | 0.000 | 0.000 | 0.0203 | 0.217 | 0.236 |
| SS04012 | Breakfast sausage and related products | 4 | parent_inherit | 0.000 | 0.000 | 0.0172 | -0.154 | 0.481 |
| SS04031 | Ham, excluding canned | 4 | parent_inherit | 0.000 | 0.000 | 0.0298 | -0.109 | 0.497 |
| SS05011 | Frankfurters | 4 | parent_inherit | 0.000 | 0.000 | 0.0285 | -0.204 | 0.294 |
| SS05014 | Lamb and organ meats | 4 | parent_inherit | 0.000 | 0.000 | 0.0187 | -0.369 | 0.308 |
| SS05015 | Lamb and mutton | 4 | parent_inherit | 0.000 | 0.000 | 0.0218 | -0.362 | 0.000 |
| SS0501A | Lunchmeats | 4 | parent_inherit | 0.000 | 0.000 | 0.0111 | -0.043 | 0.157 |
| SS06011 | Fresh whole chicken | 4 | parent_inherit | 0.000 | 0.000 | 0.0155 | -0.104 | 0.132 |
| SS06021 | Fresh and frozen chicken parts | 4 | parent_inherit | 0.000 | 0.000 | 0.0111 | 0.177 | 0.166 |
| SS07011 | Shelf stable fish and seafood | 4 | parent_inherit | 0.000 | 0.000 | 0.0151 | -0.209 | 0.247 |
| SS07021 | Frozen fish and seafood | 4 | parent_inherit | 0.000 | 0.000 | 0.0160 | -0.177 | 0.365 |
| SS09011 | Fresh whole milk | 4 | parent_inherit | 0.000 | 0.000 | 0.0116 | 0.231 | 0.096 |
| SS09021 | Fresh milk other than whole | 4 | parent_inherit | 0.000 | 0.000 | 0.0105 | 0.108 | 0.112 |
| SS10011 | Butter | 4 | parent_inherit | 0.000 | 0.000 | 0.0229 | -0.099 | 0.434 |
| SS11031 | Oranges, including tangerines | 4 | parent_inherit | 0.000 | 0.000 | 0.0368 | 0.329 | 0.588 |
| SS13031 | Canned fruits | 4 | parent_inherit | 0.000 | 0.000 | 0.0132 | -0.102 | 0.238 |
| SS14011 | Frozen vegetables | 4 | parent_inherit | 0.000 | 0.000 | 0.0134 | 0.027 | 0.263 |
| SS14021 | Canned vegetables | 4 | parent_inherit | 0.000 | 0.000 | 0.0161 | 0.098 | 0.446 |
| SS14022 | Dried beans, peas, and lentils | 4 | parent_inherit | 0.000 | 0.000 | 0.0142 | -0.155 | 0.135 |
| SS16011 | Margarine | 4 | parent_inherit | 0.000 | 0.000 | 0.0197 | 0.013 | 0.205 |
| SS16014 | Peanut butter | 4 | parent_inherit | 0.000 | 0.000 | 0.0206 | -0.305 | 0.209 |
| SS17031 | Roasted coffee | 4 | parent_inherit | 0.000 | 0.000 | 0.0124 | 0.040 | 0.220 |
| SS17032 | Instant coffee | 4 | parent_inherit | 0.000 | 0.000 | 0.0177 | -0.242 | 0.144 |
| SS18041 | Salt and other seasonings and spices | 4 | parent_inherit | 0.000 | 0.000 | 0.0147 | -0.022 | 0.410 |
| SS18042 | Olives, pickles, relishes | 4 | parent_inherit | 0.000 | 0.000 | 0.0204 | -0.258 | 0.173 |
| SS18043 | Sauces and gravies | 4 | parent_inherit | 0.000 | 0.000 | 0.0112 | -0.008 | 0.308 |
| SS1804B | Other condiments | 4 | parent_inherit | 0.000 | 0.000 | 0.0290 | -0.169 | 0.317 |
| SS18064 | Prepared salads | 4 | parent_inherit | 0.000 | 0.000 | 0.0137 | -0.111 | 0.228 |
| SS20021 | Whiskey at home | 4 | parent_inherit | 0.000 | 0.000 | 0.0082 | 0.012 | 0.226 |
| SS20022 | Distilled spirits, excluding whiskey, at home | 4 | parent_inherit | 0.000 | 0.000 | 0.0052 | 0.072 | 0.160 |
| SS20051 | Beer, ale, and other malt beverages away from home | 4 | parent_inherit | 0.000 | 0.000 | 0.0042 | -0.067 | 0.040 |
| SS20052 | Wine away from home | 4 | parent_inherit | 0.000 | 0.000 | 0.0034 | 0.060 | 0.114 |
| SS20053 | Distilled spirits away from home | 4 | parent_inherit | 0.000 | 0.000 | 0.0048 | 0.137 | 0.113 |
| SS27051 | Land-line interstate toll calls | 4 | parent_inherit | 0.000 | 0.000 | 0.0000 | 0.000 | 0.000 |
| SS27061 | Land-line intrastate toll calls | 4 | parent_inherit | 0.000 | 0.000 | 0.0000 | 0.000 | 0.000 |
| SS30021 | Laundry equipment | 4 | parent_inherit | 0.000 | 0.000 | 0.0290 | 0.131 | 0.160 |
| SS31022 | Video discs and other media | 4 | parent_inherit | 0.000 | 0.000 | 0.0294 | 0.105 | 0.168 |
| SS31023 | Video game hardware, software and accessories | 4 | parent_inherit | 0.000 | 0.000 | 0.0000 | 0.000 | 0.000 |
| SS33032 | Stationery, stationery supplies, gift wrap | 4 | parent_inherit | 0.000 | 0.000 | 0.0179 | 0.371 | 0.549 |
| SS45011 | New cars | 4 | parent_inherit | 0.000 | 0.000 | 0.0049 | 0.638 | 0.100 |
| SS4501A | New cars and trucks | 4 | parent_inherit | 0.000 | 0.000 | 0.0052 | 0.719 | 0.182 |
| SS45021 | New trucks | 4 | parent_inherit | 0.000 | 0.000 | 0.0043 | 0.696 | 0.082 |
| SS45031 | New motorcycles | 4 | parent_inherit | 0.000 | 0.000 | 0.0000 | 0.000 | 0.000 |
| SS47014 | Gasoline, unleaded regular | 4 | parent_inherit | 0.000 | 0.000 | 0.0598 | 0.392 | 0.233 |
| SS47015 | Gasoline, unleaded midgrade | 4 | parent_inherit | 0.000 | 0.000 | 0.0513 | 0.403 | 0.249 |
| SS47016 | Gasoline, unleaded premium | 4 | parent_inherit | 0.000 | 0.000 | 0.0470 | 0.416 | 0.249 |
| SS47021 | Motor oil, coolant, and fluids | 4 | parent_inherit | 0.000 | 0.000 | 0.0186 | -0.313 | 0.080 |
| SS48021 | Vehicle parts and equipment other than tires | 4 | parent_inherit | 0.000 | 0.000 | 0.0104 | -0.290 | 0.088 |
| SS52051 | Parking fees and tolls | 4 | parent_inherit | 0.000 | 0.000 | 0.0063 | -0.144 | 0.273 |
| SS53021 | Intercity bus fare | 4 | parent_inherit | 0.000 | 0.000 | 0.0491 | -0.107 | 0.410 |
| SS53022 | Intercity train fare | 4 | parent_inherit | 0.000 | 0.000 | 0.0224 | -0.096 | 0.707 |
| SS53023 | Ship fare | 4 | parent_inherit | 0.000 | 0.000 | 0.0136 | 0.184 | 0.118 |
| SS53031 | Intracity mass transit | 4 | parent_inherit | 0.000 | 0.000 | 0.0185 | -0.583 | 0.108 |
| SS5702 | Inpatient hospital services | 4 | parent_inherit | 0.000 | 0.000 | 0.0054 | -0.085 | 0.235 |
| SS5703 | Outpatient hospital services | 4 | parent_inherit | 0.000 | 0.000 | 0.0055 | -0.070 | 0.208 |
| SS61011 | Toys, games, hobbies and playground equipment | 4 | parent_inherit | 0.000 | 0.000 | 0.0117 | 0.153 | 0.306 |
| SS61021 | Film and photographic supplies | 4 | parent_inherit | 0.000 | 0.000 | 0.0105 | 0.081 | 0.000 |
| SS61023 | Photographic equipment | 4 | parent_inherit | 0.000 | 0.000 | 0.0180 | 0.165 | 0.304 |
| SS61031 | Pet food and treats | 4 | parent_inherit | 0.000 | 0.000 | 0.0060 | 0.437 | 0.037 |
| SS61032 | Purchase of pets, pet supplies, accessories | 4 | parent_inherit | 0.000 | 0.000 | 0.0085 | 0.041 | 0.050 |
| SS62011 | Automobile service clubs | 4 | parent_inherit | 0.000 | 0.000 | 0.0258 | -0.027 | 0.289 |
| SS62031 | Admission to movies, theaters, and concerts | 4 | parent_inherit | 0.000 | 0.000 | 0.0080 | -0.201 | 0.138 |
| SS62032 | Admission to sporting events | 4 | parent_inherit | 0.000 | 0.000 | 0.0389 | 0.142 | 0.128 |
| SS62051 | Photographer fees | 4 | parent_inherit | 0.000 | 0.000 | 0.0095 | -0.000 | 0.203 |
| SS62052 | Photo Processing | 4 | parent_inherit | 0.000 | 0.000 | 0.0148 | 0.011 | 0.229 |
| SS62053 | Pet services | 4 | parent_inherit | 0.000 | 0.000 | 0.0078 | 0.081 | 0.075 |
| SS62054 | Veterinarian services | 4 | parent_inherit | 0.000 | 0.000 | 0.0067 | 0.172 | 0.137 |
| SS62055 | Subscription and rental of video and video games | 4 | parent_inherit | 0.000 | 0.000 | 0.0221 | 0.038 | 0.088 |
| SS68021 | Checking account and other bank services | 4 | parent_inherit | 0.000 | 0.000 | 0.0206 | -0.316 | 0.123 |
| SS68023 | Tax return preparation and other accounting fees | 4 | parent_inherit | 0.000 | 0.000 | 0.0293 | 0.351 | 0.157 |
| SSEA011 | College textbooks | 4 | parent_inherit | 0.000 | 0.000 | 0.0130 | -0.223 | 0.060 |
| SSEE041 | Smartphones | 4 | parent_inherit | 0.000 | 0.000 | 0.0165 | 0.247 | 0.324 |
| SSFV031A | Food at elementary and secondary schools | 4 | parent_inherit | 0.000 | 0.000 | 0.0338 | 0.489 | 0.048 |
| SSGE013 | Infants' equipment | 4 | parent_inherit | 0.000 | 0.000 | 0.0261 | -0.158 | 0.158 |
| SSHJ031 | Infants' furniture | 4 | parent_inherit | 0.000 | 0.000 | 0.0270 | -0.043 | 0.555 |
