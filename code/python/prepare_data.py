# --- Header -------------------------------------------------------------------
# Prepares the data for analysis
#
# (C) Your Project -  See LICENSE file for details
# ------------------------------------------------------------------------------

from itertools import product
import numpy as np
import pandas as pd

from utils import read_config, setup_logging

log = setup_logging()

def main():
    log.info("Preparing data for analysis ...")
    cfg = read_config('config/prepare_data_cfg.yaml')

    # Load the pulled data
    data = pd.read_csv(cfg['worldscope_sample_save_path'])
    log.info(f"Loaded data with {data.shape[0]} rows and {data.shape[1]} columns.")
    log.info(f"Data columns: {data.columns.tolist()}")

    # Filter countries with at least 300 firm-year observations for the required variables
    required_vars = ['item2999', 'item1001', 'item7250', 'item1250']

    # Filter out rows with missing values in the required variables
    data_filtered = data.dropna(subset=required_vars)
    log.info(f"Data after filtering missing values in required variables has {data_filtered.shape[0]} rows.")

    # Count firm-year observations per country
    country_counts = data_filtered['item6026'].value_counts()
    log.info(f"Country counts:\n{country_counts}")

    # Filter countries with at least 300 observations
    sufficient_data_countries = country_counts[country_counts >= 300].index.tolist()
    data_filtered = data_filtered[data_filtered['item6026'].isin(sufficient_data_countries)]
    log.info(f"Data after filtering countries with at least 300 observations has {data_filtered.shape[0]} rows.")

    # Ensure each firm has data for at least three consecutive years for the required variables
    def has_consecutive_years(df, min_years=3):
        years = sorted(df['year_'].unique())
        return any([all([(years[i + j] - years[i]) == j for j in range(min_years)]) for i in range(len(years) - min_years + 1)])

    # Group by firm and filter for consecutive years
    firm_groups = data_filtered.groupby('item6105')
    log.info(f"Firm groups: {len(firm_groups)}")

    def filter_consecutive_years(group):
        if 'year_' not in group.columns:
            log.error("Column 'year_' not found in group")
            return pd.DataFrame()
        return group if has_consecutive_years(group) else pd.DataFrame()

    consecutive_firm_data = firm_groups.apply(filter_consecutive_years, include_groups=False)
    consecutive_firm_data.reset_index(drop=True, inplace=True)
    log.info(f"Data after filtering for firms with at least three consecutive years has {consecutive_firm_data.shape[0]} rows.")

    if consecutive_firm_data.empty:
        log.warning("No data found with three consecutive years. Please check the data and the required variables.")

    # Save the prepared data
    consecutive_firm_data.to_csv(cfg['prepared_data_save_path'], index=False)
    log.info(f"Prepared data saved to {cfg['prepared_data_save_path']}")

    log.info("Preparing data for analysis ... Done!")

if __name__ == '__main__':
    main()