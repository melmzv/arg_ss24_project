# --- Header -------------------------------------------------------------------
# Prepare the pulled data for further analysis as per the requirements by Leuz et al.
#
# (C) Melisa Mazaeva -  See LICENSE file for details
# ------------------------------------------------------------------------------

import pandas as pd
from utils import read_config, setup_logging

log = setup_logging()

def main():
    log.info("Preparing data for analysis ...")
    cfg = read_config('config/prepare_data_cfg.yaml')

    # Load the pulled data
    wrds_data = pd.read_csv(cfg['worldscope_sample_save_path'])

    # Check for duplicate firm-year observations
    dup_obs = wrds_data[wrds_data.duplicated(subset=['item6105', 'year_'], keep=False)]
    if not dup_obs.empty:
        log.warning(f"Found {dup_obs.shape[0]} duplicate firm-year observations. Removing duplicates.")
        wrds_data = wrds_data.drop_duplicates(subset=['item6105', 'year_'], keep='first')

    # Filter countries with at least 300 firm-year observations for key accounting variables
    filtered_countries_data = filter_countries(wrds_data)

    # Filter firms with at least three consecutive years of income statement and balance sheet information
    filtered_firms_data = filter_firms(filtered_countries_data)

    # Save the filtered dataset
    filtered_firms_data.to_csv(cfg['prepared_data_save_path'], index=False)

    log.info("Preparing data for analysis ... Done!")

def filter_countries(df):
    key_vars = ['item2999', 'item1001', 'item1250', 'item1651']  # Total Assets, Net Sales, Operating Income, Net Income
    grouped = df.groupby('item6026')
    country_filter = grouped.filter(lambda x: all(x[key_vars].count() >= 300))
    eliminated_countries = set(df['item6026'].unique()) - set(country_filter['item6026'].unique())
    return country_filter, list(eliminated_countries)

def filter_firms(df):
    key_vars = ['item2999', 'item1001', 'item1250', 'item1651']
    df = df.dropna(subset=key_vars)
    
    def has_three_consecutive_years(group):
        group = group.sort_values('year_')
        consecutive_years = (group['year_'].diff() == 1).astype(int).rolling(window=3).sum()
        return (consecutive_years >= 2).any()

    firm_filter = df.groupby('item6105').filter(has_three_consecutive_years)
    return firm_filter

if __name__ == "__main__":
    main()