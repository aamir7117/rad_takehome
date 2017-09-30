This README is meant to be accompanies by file, 'code/Aamir_radius_takehome.ipynb'

## Vision
The following questions intrigued me about this dataset:
* Geo-location of businesses and how it relates to other fields
* Revenue, headcount, time_in_business and zip_code should be correlated somehow to each other. What is that relationship?
* NAICS codes can be used for several things:
      * analyze regional distribution by NAICS codes (2-digit Sector... 6 digit US industry)
      * estimate the revenue of each level of heirarchy, verify with US govt reports
* This data could be used for lead-generation for B2B clients.
      * If we knew which records were successful customers, we could find similarities among the businesses to identify other potential clients.
* Does the phone number of the business match the city, state of its address?
      * If not, I'd suspect an incorrect record, which could be verified by telephone companies or simply calling the number
      * About half the records are blank for this field

## EDA

* The following bad entries are sparsely distributed in all fields: 'None', 'none', 'null', NoneType, '', ' ', 0
      * I replaced them all with -1 so they can be easily identified later. The value of -1 did not conflict with any real values
      * I also ignored 0 as it did not apply to any fields (shed approx 15 records)

* Fill_rate, True_Value_fill_rate and Cardinality are shown as requested
      * All irrelevant data was removed before calculating True_Value_fill_rate and Cardinality
      * See helper.replace_bad_entries and helper.unique_counter for details

* I tried to find relationships between headcount, time_in_business, revenue and Zipcodes(location)
      * Between just headcount, time_in_business and revenue alone, there is no linear relationship. Location is a key part in untangling these.
      * I explored the connection with location using various plots

* Location: All data is for US businesses. There are about 10 records that belong to Puerto Rico and US Virgin Islands. I ignored them.
      * I mapped the Zipcodes to their corresponding Latitudes/Longitudes using a csv file from here https://www.aggdata.com/node/86
      * Using this data, I filled 209 missing city and state records
      * I plotted the lat/long of each business to see their spatial distribution.
      * A US mainland outline is clearly observable with some outliers in Alaska and Hawaii.
      * There are many more businesses on the Eastern half of the US than the Western half.

* Revenue: I added color to the plot which maps to revenue tiers. Shades of pink are high-revenue (Over $100M) and shades of green are mid-range ($2.5M to $100M)
      * The high revenue businesses are exactly co-located with major cities of the US.
      * Businesses seem to emanate outward from the cities.
      * Revenue tiers also get lower as you move outward from the cities.
      * The northeast megalopolis, also known as the Boston-Washington corridor, is clearly visible at the top of the East coast, marked by a slanted pink line
      * This region accounts for 20% of the United States GDP, has 162 out of Fortune 500 companies and is the center of the hedge fund industries

* Headcount: I added headcount to the plot, using size of the points
      * Smaller points means less headcount. Larger means more
      * Once again, the major cities stand out
      * However, notice the spread of pink dots shrink in relation to the green dots, especially in the dense areas
      * This means that businesses in the green range (\$2.5Mto \$100M) typically have more employees than businesses in the pink range (Over \$100M)
      * I suspect the type of industry has a big impact on how many employees a business has. So it would make a good feature to explore with more time

* category_code: NAICS code. First 2 digits indicate sector, 3rd is subsector, 4th is industry group, 5th and 6th are specific industries
      * I referenced the code descriptions using following data from NAICS: https://www.census.gov/eos/www/naics/downloadables/downloadables.html
      * All the 2-digit sectors matched with the offical NAICS codes but lots of 3-6 digit codes did not

* I split the USA into 9 divisions spatially
      * Pacific, Mountain, West North Central (WNC), WSC, ESC, ENC, South Atlantic, Middle Atlantic and New England
      * StatisticalAtlas.com shows NAICS codes analysis for various regions of the US
          * https://statisticalatlas.com/United-States/Overview
      * One of the ways they split geographically is Divisions (Mountain, SouthAtlantic, Pacific..) - Loosely similar to timezones
      * They have approx 140 Million records and they show several plots using the same 20 NAICS sectors as we have


* Different results than StatisticalAtlas
      * StatisticalAtlas has 140 million records. My dataset has only 1 million.
      * See below for overall US percentages per sector. Mine and StatAtlas' are different
          * This is likely due to random sampling to obtain our dataset
