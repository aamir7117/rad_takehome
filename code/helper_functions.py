import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import re

def unique_counter(x):
    '''
    x: pd.Series object
    Returns unique count of the string objects in string. Ignores numeric values including -1.
    Use case, set all undesirable values to -1 prior to calling this function
    '''
    return x[x>-1].str.lower().str.replace(' ','').nunique()

def replace_bad_entries(df, to_replace=['None','null'], repl_with=-1, \
                        fillna_with=-1,**kwargs):
    '''
    df: pandas.DataFrame object
    to_replace: list, array or pd.Series object denoting undesirable values
    repl_with: int, replaces any entries in df that are also in to_replace with this value
    fillna_with: int, replaces any NoneType entries in df with this value
    This function will replace all undesirable values with specified values in place.
    Returns nothing as operations to df are done inplace
    '''
    df.fillna(-1,inplace=True)
    df[df.isin(to_replace)] = -1
    print "All null and irrelevant entries updated to -1"

def numerize_rth(big_df):
    '''
    big_df: pandas.DataFrame object
    Maps the categorical variables to numeric values
    Returns nothing as big_df is modified in place, new columns added: time_n, rev_n, hdcnt_n
    '''
    d_time = {'10+ years':10,'6-10 years':7,'3-5 years':5,'1-2 years':2,-1:-1,
    'Less than a year':-1}
    rev_order = ['Less Than $500,000', '$500,000 to $1 Million',
    '$1 to 2.5 Million', '$2.5 to 5 Million', '$5 to 10 Million',
    '$10 to 20 Million', '$20 to 50 Million', '$50 to 100 Million',
    '$100 to 500 Million', 'Over $500 Million', 'Over $1 Billion']
    d_rev = dict(zip(rev_order+[-1],[0.5,1,2.5,5,10,20,50,100,500,750,1000,-1]))
    d_hdcnt = {'1 to 4':4,'5 to 9':9,'10 to 19':19,'20 to 49':49,'50 to 99':99,
    '100 to 249':249, '250 to 499':499,'500 to 999':999,
    'Over 1,000':1999,-1:-1}
    big_df['time_n'] = big_df.time_in_business.map(d_time)
    big_df['rev_n'] = big_df.revenue.map(d_rev)
    big_df['hdcnt_n'] = big_df.headcount.map(d_hdcnt)


def show_correlations(big_df,cols):
    '''
    big_df: pandas.DataFrame object
    cols: list, array or pd.Series object denoting columns of big_df
    Returns a Dataframe showing linear correlation values between cols
    This function also adds interaction columns to big_df inplace
    For more interactions, add under the Interactions section below
    '''

    # Interactions between hdcnt, time and revenue
    big_df['hdcnt_n * time_n'] = big_df.hdcnt_n * big_df.time_n
    big_df['hdcnt_n * rev_n'] = big_df.hdcnt_n * big_df.rev_n
    big_df['rev_n * time_n'] = big_df.rev_n * big_df.time_n
    big_df['hdcnt_n**2'] = big_df.hdcnt_n**2
    # big_df['rev_n**2'] = big_df.rev_n**2
    # big_df['rev_n**3'] = big_df.rev_n**3

    # Scale values in each column to [0,1]
    cols = cols
    scaler = MinMaxScaler()
    no_miss_rth_df = big_df[cols][(big_df[cols]>-1).sum(axis=1)==len(cols)]
    no_miss_rth_df = pd.DataFrame(no_miss_rth_df)

    return no_miss_rth_df.corr().loc[['time_n','rev_n','hdcnt_n'],cols]

def join_naics_desc(big_df,naics,return_non_match_cnt=True):
    '''
    big_df: pandas.DataFrame object
    naics: pandas.DataFrame object, read from csv at https://www.census.gov/eos/www/naics/2017NAICS/2-6%20digit_2017_Codes.xlsx
    This function breaksout the codes into 2-6 digits and adds their descriptions into big_df
    Returns nothing as big_df is modified in place, new columns added:
    naics_sector, naics_sector_desc
    naics_subsector, naics_subsector_desc
    naics_industry_grp, naics_industry_grp_desc
    naics_industries_5, naics_industries_5_desc
    naics_industries_6, naics_industries_6
    '''

    # Rename columns and grab non-null entries only
    name_d = {'2017 NAICS US   Code':'naics_code','2017 NAICS US Title':'desc'}
    naics = naics[name_d.keys()].rename(columns=name_d)
    naics = naics[naics.naics_code.notnull()]
    naics.set_index('naics_code',inplace=True)
    naics.set_index(naics.index.astype(str),inplace=True)

    # Replace codes like '31-33' to 31, 32, 33 with corresponding desc
    bad_indexes = naics.index[(naics.index.str.find('-')>0)]
    for i in bad_indexes:
        rng = map(int,i.split('-'))
        for new_i in range(rng[0],rng[-1]+1):
            naics.loc[str(new_i)] = naics.loc[i]

    # Add all broken out codes and their corresponding descriptions to big_df
    naics_cols = ['naics_sector','naics_subsector','naics_industry_grp', \
    'naics_industries_5','naics_industries_6']
    regexes = [r'(..)',r'(...)',r'(....)',r'(.....)',r'(......)']

    for i in range(len(naics_cols)):
        col = naics_cols[i]
        big_df[col] = big_df.category_code.str.extract(regexes[i])
        big_df[col+'_desc'] = -1  # initializes column
        mask = big_df[col][big_df[col].notnull()].values
        big_df[col+'_desc'][big_df[col].notnull()] = naics.loc[mask]['desc']

    if return_non_match_cnt==True:
        naics_desc_cols = map(''.join,zip(naics_cols,['_desc']*len(naics_cols)))
        no_match = pd.DataFrame(big_df[naics_desc_cols].isnull().sum())
        return no_match.rename(columns={0:'num_non_matches'})
