# We start by loading the libraries that we will use in this analysis.
import pickle
import pandas as pd

def main():
    # Load the prepared data
    financial_data = load_data()

    # Calculate EM1
    country_em1, summary_stats_em1 = calculate_em1(financial_data)

    # Calculate EM2
    country_em2, summary_stats_em2 = calculate_em2(financial_data)

    # Save and print results
    save_results(country_em1, summary_stats_em1, country_em2, summary_stats_em2)

def load_data():
    """
    Load the prepared financial data from the previous step.
    """
    df = pd.read_csv('data/generated/financial_data_prepared.csv')
    return df

def calculate_em1(df):
    """
    Calculate EM1 for each firm and then take the country-level median.
    This function combines all necessary steps into one.
    """
    # Step 1: Calculate Accruals
    # Group by unique firm (item6105) and calculate diffs within each firm
    # If a firm does not report information on taxes payable or short-term debt,
    # then the change in both variables is assumed to be zero (per paper).
    df['delta_CA'] = df.groupby('item6105')['item2201'].diff()  # Change in total current assets
    df['delta_Cash'] = df.groupby('item6105')['item2003'].diff()  # Change in cash and cash equivalents
    df['delta_CL'] = df.groupby('item6105')['item3101'].diff()  # Change in total current liabilities
    df['delta_STD'] = df.groupby('item6105')['item3051'].diff().fillna(0)  # Apply fillna only for STD
    df['delta_TP'] = df.groupby('item6105')['item3063'].diff().fillna(0)  # Apply fillna only for TP
    df['Dep'] = df['item1151']  # Depreciation and amortization expense

    df['Accruals'] = (df['delta_CA'] - df['delta_Cash']) - (df['delta_CL'] - df['delta_STD'] - df['delta_TP']) - df['Dep']

    # Step 2: Calculate Operating Cash Flow (CFO) by subtracting accruals from operating income.
    df['CFO'] = df['item1250'] - df['Accruals']

    # Step 3: Calculate the standard deviations for Operating Income and CFO for each firm
    df['std_operating_income'] = df.groupby('item6105')['item1250'].transform('std')
    df['std_cfo'] = df.groupby('item6105')['CFO'].transform('std')

    # Step 4: Retrieve Lagged Total Assets
    # For scaling, identify the total assets from the prior year (making use of year 0 as well. Otherwise would have dropped it in accruals step)
    df['lagged_total_assets'] = df.groupby('item6105')['item2999'].shift(1)

    # Step 5: Scale the standard deviations individually by lagged total assets
    df['scaled_std_operating_income'] = df['std_operating_income'] / df['lagged_total_assets']
    df['scaled_std_cfo'] = df['std_cfo'] / df['lagged_total_assets']

    # Step 6: Calculate EM1 as the ratio of the scaled standard deviations
    df['EM1'] = df['scaled_std_operating_income'] / df['scaled_std_cfo']

    # Drop rows where EM1 is NaN
    ## df = df.dropna(subset=['EM1'])

    # Step 7: Group by country (item6026) and calculate the median of EM1 for each country
    country_em1 = df.groupby('item6026')['EM1'].median().reset_index()
    # Round the EM1 results to three decimal places
    country_em1['EM1'] = country_em1['EM1'].round(3)

    # Step 8: Calculate summary statistics (mean, median, std, min, max) for EM1 across countries
    summary_stats_em1 = country_em1['EM1'].agg(['mean', 'median', 'std', 'min', 'max']).round(3)

    return country_em1, summary_stats_em1

def calculate_em2(df):
    """
    Calculate EM2, which is the Spearman correlation between the change in Accruals and CFO,
    both scaled by lagged total assets.
    """
    # Step 1: Calculate the change in Accruals and CFO
    df['delta_Accruals'] = df.groupby('item6105')['Accruals'].diff()
    df['delta_CFO'] = df.groupby('item6105')['CFO'].diff()

    # Step 2: Scale by lagged total assets
    df['scaled_delta_Accruals'] = df['delta_Accruals'] / df['lagged_total_assets']
    df['scaled_delta_CFO'] = df['delta_CFO'] / df['lagged_total_assets']

    # Step 3: Calculate EM2 as the Spearman correlation between scaled changes
    country_em2 = df.groupby('item6026').apply(
        lambda x: x[['scaled_delta_Accruals', 'scaled_delta_CFO']].corr(method='spearman').iloc[0, 1]
    ).reset_index()
    country_em2.columns = ['item6026', 'EM2']
    # Round the EM2 results to three decimal places
    country_em2['EM2'] = country_em2['EM2'].round(3)

    # Step 4: Calculate summary statistics (mean, median, std, min, max) for EM2 across countries
    summary_stats_em2 = country_em2['EM2'].agg(['mean', 'median', 'std', 'min', 'max']).round(3)

    return country_em2, summary_stats_em2

def save_results(country_em1, summary_stats_em1, country_em2, summary_stats_em2):
    """
    Save the EM1 and EM2 results to a pickle file and print them.
    """
    with open('output/em_results.pickle', 'wb') as f:
        pickle.dump({
            'country_em1': country_em1,
            'summary_stats_em1': summary_stats_em1,
            'country_em2': country_em2,
            'summary_stats_em2': summary_stats_em2
        }, f)

    print("EM1 Country-Level Results:")
    print(country_em1)
    print("\nEM1 Summary Statistics:")
    print(summary_stats_em1)

    print("\nEM2 Country-Level Results:")
    print(country_em2)
    print("\nEM2 Summary Statistics:")
    print(summary_stats_em2)

if __name__ == "__main__":
    main()