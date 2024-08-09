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
    return pd.read_csv('data/generated/financial_data_prepared.csv')

def calculate_accruals(df):
    """
    Calculate accruals using the provided formula.
    """
    df['Accruals'] = (df['item2201'].diff() - df['item2003'].diff()) - (df['item3101'].diff() - df['item3051'].diff() - df['item3063'].diff()) - df['item1151']
    return df

def calculate_cfo(df):
    """
    Calculate Operating Cash Flow (CFO) by subtracting accruals from operating income.
    """
    df['CFO'] = df['item1250'] - df['Accruals']
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