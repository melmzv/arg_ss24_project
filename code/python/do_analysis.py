# We start by loading the libraries that we will use in this analysis.
import pickle
import pandas as pd

def main():
    # Load prepared data
    financial_data = load_data()

    # Calculate accruals
    financial_data = calculate_accruals(financial_data)

    # Calculate Operating Cash Flow (CFO)
    financial_data = calculate_cfo(financial_data)

    # Calculate EM1
    em1_results = calculate_em1(financial_data)

    # Save and print results
    save_results(em1_results)

def load_data():
    """
    Load the prepared financial data from the previous step.
    """
    df = pd.read_csv('data/generated/financial_data_prepared.csv')
    return df

def calculate_accruals(df):
    """
    Calculate accruals using the provided formula.
    If a firm does not report information on taxes payable or short-term debt,
    then the change in both variables is assumed to be zero.
    """

    # Group by unique firm (item6105) and calculate diffs within each firm
    df['delta_CA'] = df.groupby('item6105')['item2201'].diff()  # Change in total current assets
    df['delta_Cash'] = df.groupby('item6105')['item2003'].diff()  # Change in cash and cash equivalents
    df['delta_CL'] = df.groupby('item6105')['item3101'].diff()  # Change in total current liabilities
    df['delta_STD'] = df.groupby('item6105')['item3051'].diff().fillna(0)  # Apply fillna only for STD
    df['delta_TP'] = df.groupby('item6105')['item3063'].diff().fillna(0)  # Apply fillna only for TP
    df['Dep'] = df['item1151']  # No fillna applied to Depreciation and amortization expense

    df['Accruals'] = (df['delta_CA'] - df['delta_Cash']) - (df['delta_CL'] - df['delta_STD'] - df['delta_TP']) - df['Dep']

    # Identify rows with NaN in Accruals
    nan_accruals = df[df['Accruals'].isna()]

    # Print the first 10 rows with NaN in Accruals
    print("First 10 rows with NaN in Accruals:")
    print(nan_accruals.head(10))

    # Count and print the number of NaN rows in Accruals
    nan_count = df['Accruals'].isna().sum()
    print(f"Number of rows with NaN in Accruals: {nan_count}")

    # Drop rows where Accruals is NaN
    df = df.dropna(subset=['Accruals'])

    # Print the first few rows to check the calculated accruals
    print(df[['item6105', 'year_', 'Accruals']].head(10))
    
    return df

def calculate_cfo(df):
    """
    Calculate Operating Cash Flow (CFO) by subtracting accruals from operating income.
    """
    df['CFO'] = df['item1250'] - df['Accruals']

    print(df[['item6105', 'year_', 'Accruals', 'CFO']].head(10))
    
    return df

def calculate_em1(df):
    """
    Calculate EM1 for each firm and then take the country-level median.
    """
    df['std_operating_income'] = df.groupby('item6105')['item1250'].transform('std')
    df['std_cfo'] = df.groupby('item6105')['CFO'].transform('std')
    df['EM1'] = df['std_operating_income'] / df['std_cfo']
    df['EM1'] = df.groupby('item6105')['EM1'].transform(lambda x: x / df['item2999'].shift(1))  # Scale by lagged total assets

    country_em1 = df.groupby('item6026')['EM1'].median().reset_index()

    # Round the EM1 results to three decimal places
    country_em1['EM1'] = country_em1['EM1'].round(3)

    # Calculate mean, median, standard deviation, min, max
    summary_stats = country_em1['EM1'].agg(['mean', 'median', 'std', 'min', 'max']).round(3)

    # Add the summary stats to the results
    summary_stats = summary_stats.reset_index()
    summary_stats.columns = ['Statistic', 'EM1']

    country_em1 = pd.concat([country_em1, summary_stats], ignore_index=True)

    return country_em1

def save_results(results):
    """
    Save the EM1 results to a pickle file and print them.
    """
    with open('output/em1_results.pickle', 'wb') as f:
        pickle.dump(results, f)
    
    print("EM1 Results:")
    print(results)

if __name__ == "__main__":
    main()