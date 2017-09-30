import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from collections import defaultdict
import re


class Region(object):
    '''
    This class object defines a region by allowing conditions to define the mask
    that will be used to filter big_df
    '''

    def __init__(self, name, big_df):
        '''
        name: string identifies of class object
        big_df: pandas.DataFrame object
        '''
        self.name = name
        self.masks = defaultdict(list)
        self.masked_items = defaultdict(list)
        self.big_df = big_df

    def add_category(self,col,value_list):
        '''
        col: str, big_df column name
        value: list, list of values that exist in big_df[col]
        This method allows the addition of multiple criteria to define a region
        '''
        for value in value_list:
            self.masked_items[col].append(value)
            mask_lst = self.big_df[col]==value
            if mask_lst.sum() and len(mask_lst)==len(self.big_df):
                self.masks[col].append(mask_lst)

    def get_final_mask(self):
        '''
        This method returns a mask that when applied to big_df will return only
        the records that satisfy all the conditions that have been specified
        for this Region object
        '''
        if len(self.masks):
            all_masks = []
            for col, mask_lst in self.masks.iteritems():
                all_masks.append(np.array(mask_lst).sum(axis=0)>0)
            return np.array(all_masks).sum(axis=0)==len(all_masks)

    def get_df(self):
        return self.big_df[self.get_final_mask()]

    def get_col_counts(self,col):
        '''
        col: str, big_df column name to get value counts of
        This method returns the value_counts of the column specified
        '''
        return self.big_df[self.get_final_mask()][col].value_counts()




def make_USA_divisions(big_df, states_df=True):
    '''
    big_df: pandas.DataFrame object
    This function splits the USA into 9 divisions:
    Pacific, Mountain, West North Central (WNC), WSC, ESC, ENC,
    South Atlantic, Middle Atlantic and New England
    Returns a list of 9 Region class objects
    '''

    all_states = {
    'mountain': ['MT','ID','WY','NV','UT','CO','AZ','NM'],
    'pacific': ['AK','WA','OR','CA'],
    'westnorthcentral': ['IA','KS','MN','MO','NE','ND','SD'],
    'westsouthcentral': ['OK','TX','AK','LA'],
    'eastnorthcentral': ['WI','MI','IL','IN','OH'],
    'eastsouthcentral': ['KY','TN','AL','MS'],
    'southatlantic': ['WV','MD','DE','VA','NC','SC','GA','FL'],
    'middleatlantic': ['PA','NJ','NY'],
    'newengland': ['ME','VT','NH','MA','RI','CT']
    }

    all_divisions = []

    for name, states in all_states.iteritems():
        r = Region(str(name),big_df)
        r.add_category('state',states)
        all_divisions.append(r)

    if states_df==True:
        states = pd.DataFrame(all_states.values(),index=all_states.keys())
        return all_divisions, states
    else:
        return all_divisions


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
    Returns nothing as big_df is modified in place, new columns added:
    time_n, rev_n, hdcnt_n
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

def common_industries(big_df,division, col):
    '''
    division: class Region object
    col: str, name of column. For example: naics_industries_5_desc
    This function returns the Percentages more or less common in the specified
    division than in the United States.
    '''
    us = big_df[col]
    d = division.get_df()[col]
    normed_us = (us.value_counts()*1.)/(us.notnull().sum())
    normed_div = ((d.value_counts())*1.)/(d.notnull().sum())
    return (normed_div - normed_us).sort_values(ascending=False)
