# We start by loading the libraries that we will use in this analysis.
import pickle
import pandas as pd

def main():
    # Load the prepared data
    financial_data = load_data()

    # Calculate EM1
    country_em1, summary_stats = calculate_em1(financial_data)

    # Save and print results
    save_results(country_em1, summary_stats)

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
    # Handle NaN values where necessary.
    df['CFO'] = df['item1250'] - df['Accruals']

    # Step 3: Calculate the standard deviations for Operating Income and CFO for each firm (grouped by item1605)
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
    summary_stats = country_em1['EM1'].agg(['mean', 'median', 'std', 'min', 'max']).round(3)

    return country_em1, summary_stats

def save_results(country_em1, summary_stats):
    """
    Save the EM1 results to a pickle file and print them.
    """
    with open('output/em1_results.pickle', 'wb') as f:
        pickle.dump({'country_em1': country_em1, 'summary_stats': summary_stats}, f)
    
    print("EM1 Country-Level Results:")
    print(country_em1)

    print("\nEM1 Summary Statistics:")
    print(summary_stats)

if __name__ == "__main__":
    main()