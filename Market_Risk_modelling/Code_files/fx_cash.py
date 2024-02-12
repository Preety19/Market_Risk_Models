import math
import pandas as pd
import numpy as np
import scipy
import random
import math ##Importing Math function to use floor function.(Floor function rounds up the value to the nearest integer)
from scipy import stats
from csv import reader

def getData(path, fileext = None):
        if fileext == ".csv":
            df = pd.read_csv(path)
        elif fileext == ".xlsx" or fileext == ".xls":
            df = pd.read_excel(path)

        else:
            df = pd.read_csv(path)
        return df


def get_sim_rates(df):
        simulated_instruments = pd.DataFrame([])

        if len(rates_exchange) != 0:
            rates_exchange["key"] = rates_exchange["currency_from"] + "_"+rates_exchange["currency_to"]
        for i,k in rates_exchange.groupby('key'):
            j = k.filter(["currency_from", "currency_to", "rate", "key"])
            new_row = j.iloc[0].to_dict()
            print(new_row)
            new_row['simulated_rates'] = [0]
            top_row = pd.DataFrame(new_row)
            j = j.reset_index(drop = True)
            j['simulated_rates'] = np.log(j['rate']/j['rate'].shift(-1))
            j = pd.concat([top_row, j]).reset_index(drop = True)
            j["new_rate"] = j['simulated_rates'].apply(lambda x: np.exp(x)*j["rate"].iloc[0])
            simulated_exchange = simulated_exchange.append(j)
            
        se = simulated_exchange.dropna(axis = 0)  
        
        
def get_mtm_bc(idx,tx_df, ex_df):
    
        res_df = list()
        for k, h in tx_eq.groupby('id'):
            h["keyMatch"] = h['currency'] + '_' + h['currency_base']
            keyMatch = h["keyMatch"].iloc[0]
            instrMatch = h["instrument"].iloc[0]
            unitCount = h['unit_count'].iloc[0]

            crss_rate_df = ex_df[ex_df['key']==keyMatch]
            cross_rate = crss_rate_df['new_rate'].iloc[0]

            #equity_rate_df = instr_df[instr_df['instrument'] == instrMatch]
            #equity_rate = equity_rate_df['new_value'].iloc[0]

            mtm_bc = cross_rate  * unitCount
            result = {'idx': idx, "env":k,"instrument": instrMatch, "unit_count":unitCount, "currency":h["currency"].iloc[0],             "mtm_bc":mtm_bc}
            res_df.append(result)

        return res_df        


if __name__ == "__main__":
    
    hs_param_path = str(input("Enter HS_PARAM FILE PATH: "))
    print("Your HS_PARAM Path: ", hs_param_path)
    hs_param = pd.read_csv(hs_param_path)
    
    rates_E_path = str(input("Enter Rates Instrument File Path: "))
    print("Your Rates Instrument File Path: ", rates_E_path)
    rates_E = pd.read_csv(rates_E_path)
    
    rates_exchange_path = str(input("Enter Rates Exchange File Path: "))
    print("Your Rates Exhange File Path: ", rates_exchange_path)
    rates_exchange = pd.read_csv(rates_exchange_path)
    
    tx_eq_path = str(input("Enter Transaction Equity file Path: "))
    print("Your Transaction Equity Path: ", tx_eq_path)
    tx_eq = pd.read_csv(tx_eq_path)
    
    output_path1 = str(input("Enter Output path where you want Excel Sheet for Final Data: "))
    print("Your Output Path: ", output_path1)
    
    output_path2 = str(input("Enter Output path where you want Excel Sheet for Simulated Exchange: "))
    print("Your Output Path: ", output_path2)
    
    output_path3 = str(input("Enter Output path where you want Excel Sheet Simulated Instrument: "))
    print("Your Output Path: ", output_path3)
    
    # Setting up the parameters differently
    decay_factor = hs_param.decay_factor.iloc[0]
    holding_period = hs_param.holding_period.iloc[0]
    confidence_level = hs_param.confidence_level.iloc[0]
    # Number of Days
    n = hs_param['no_of_days'].iloc[0]