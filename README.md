## Vision
Seeing this data, the following questions intrigue me:
1. Geo-location of business and how it relates to other fields
2. Revenue, headcount, time_in_business and zip_code should be correlated somehow to each other. What is that relationship?
3. NAICS codes can be used for several things:
    a. build a heirarchy of businesses by NAICS codes (2-digit Sector... 6 digit US industry)
    b. estimate the revenue of each level of heirarchy, verify with US govt reports
4. This data could be used for lead-generation for B2B clients.
    a. If we had additional data on which of these leads actually converted to paying customers, we could find similarities among the businesses to identify other potential clients.
5. Does the phone number of the business match the city, state of its address?
  a. If not, I'd suspect an incorrect record, which could be verified by telephone companies or simply calling the number

## EDA

* The following bad entries are sparsely distributed in all fields: 'None', 'none', 'null', NoneType, '', ' ', 0
  * I replaced them all with -1 so they are easy to identify later. -1 does not conflict with real values for any field.
  * I also ignored 0 as it did not apply to any fields (shed approx 15 records)

* Fill_rate, True_Value_fill_rate and Cardinality are shown as requested
  * All irrelevant data as mentioned above was removed before calculating True_Value_fill_rate and Cardinality
  * See helper_functions.replace_bad_entries and helper_functions.unique_counter for details

* I tried to find relationships between headcount, time_in_business, revenue and Zipcodes(location)
  * There is no linear relationship between just headcount, time_in_business and revenue alone. Location is a key part in untangling these.
  * I explored the connection with location using various plots

* Location: All data is for US businesses. There are about 10 records that belong to Puerto Rico and US Virgin Islands. I ignored them.
  * I mapped the Zipcodes to their corresponding Latitudes/Longitudes using a csv file from here https://www.aggdata.com/node/86
    * Using this data, I filled 209 missing city and state records

  * I plotted the lat/long of each business to see their spatial distribution.
    * A US mainland outline is clearly observable with some outliers in Alaska and Hawaii.
    * There are many more businesses on the Eastern half of the US than the Western half.

  * I added color to the plot which maps to revenue tiers. Shades of pink are high-revenue (Over $100M) and shades of green are mid-range ($2.5M to $100M)
    * The high revenue businesses are exactly co-located with major cities of the US.
      * The following cities have the highest overall count of high-revenue businesses: NYC, Houston, Chicago, San Diego, LA and Dallas
    * Businesses seem to emanate outward from the cities.
    * Revenue tiers also get lower as you move outward from the cities.
    * The northeast megalopolis, also known as the Boston-Washington corridor, is clearly visible at the top of the East coast, marked by a slanted pink line
      * This region accounts for 20% of the United States GDP
      * The Headquarters of 162 of the Fortune 500 companies are located here
      * It is the center of the global hedge fund industry
      * Academically, the region is home to six of the eight Ivy League universities

  * I added headcount to the plot, using size of the points
    * Smaller points means less headcount. Larger means more
    * Once again, the major cities stand out
    * However, notice the spread of pink dots shrink in relation to the green dots, especially in the dense areas
    * This means that businesses in the green range (\$2.5Mto \$100M) typically have more employees than businesses in the pink range (Over \$100M)
      * I suspect the type of industry has a big impact on how many employeed a business has. So it would make a good feature to explore with more time

  * category_code: NAICS code. First 2 digits indicate sector, 3rd is subsector, 4th is industry group, 5th and 6th are specific industries
    * I referenced descriptions of these codes using: https://www.census.gov/eos/www/naics/2017NAICS/2-6%20digit_2017_Codes.xlsx
    * Lots of 3-6 digit codes did not match real NAICS codes but 2-digit codes (sectors) all matched
      * 3-digit: 190,414 did not match, 4-digit: 350,089 did not match, 5-digit: 605,680, 6-digit: 694,956 did not match
