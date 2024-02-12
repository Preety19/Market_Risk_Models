import math
import pandas as pd
import numpy as np

pd.set_option('display.max_rows', 2500)

# Simulated Instrument rates
def sim_instruments(df):
    simulated_instruments = pd.DataFrame([])

    for a, h in df.groupby('instrument'):
        g = h.filter(["instrument", "instrument_type", "value", "key"])
        new_row = g.iloc[0].to_dict()
        new_row['simulated_rates'] = [0]
        top_row = pd.DataFrame(new_row)
        g = g.reset_index(drop = True)
        g['simulated_rates'] = np.log(g["value"]/g["value"].shift(-holding_period, fill_value = g["value"][0]))

        g = pd.concat([top_row, g]).reset_index(drop = True)

        g['new_value'] = g['simulated_rates'].apply(lambda x: np.exp(x)*g["value"].iloc[0])
        simulated_instruments = simulated_instruments.append(g)
    
    return simulated_instruments


def get_sim_exch(df):
    """
    Parameters: df --> rates exchange dataframe
    output: df --> simulated_exchange
    """
    simulated_exchange = pd.DataFrame([])
    for i,k in df.groupby('key'):
        j = k.filter(["currency_from", "currency_to", "rate", "key"])
        new_row = j.iloc[0].to_dict()
        new_row['simulated_rates'] = [0]
        top_row = pd.DataFrame(new_row)

        j = j.reset_index(drop = True)
        j['simulated_rates'] = np.log(j['rate']/j['rate'].shift(-holding_period, fill_value = j["rate"][0]))
        j = pd.concat([top_row, j]).reset_index(drop = True)
        j["new_rate"] = j['simulated_rates'].apply(lambda x: np.exp(x)*j["rate"].iloc[0])
        simulated_exchange = simulated_exchange.append(j)
    
    return simulated_exchange

def get_mtm_bc(idx,tx_df, ex_df, instr_df):
    
    res_df = list()
    for k, h in tx_eq.groupby('id'):
        h["keyMatch"] = h['currency'] + '_' + h['currency_base']
        keyMatch = h["keyMatch"].iloc[0]
        instrMatch = h["instrument"].iloc[0]
        unitCount = h['unit_count'].iloc[0]
        
        crss_rate_df = ex_df[ex_df['key']==keyMatch]
        cross_rate = crss_rate_df['new_rate'].iloc[0]
        
        equity_rate_df = instr_df[instr_df['instrument'] == instrMatch]
        equity_rate = equity_rate_df['new_value'].iloc[0]
        
        mtm_bc = cross_rate * equity_rate * unitCount
        result = {'idx': idx, "env":k,"instrument": instrMatch, "unit_count":unitCount, "accounting_book":h["accounting_book"].iloc[0],
                 "accounting_portfolio": h["accounting_portfolio"].iloc[0], "currency":h["currency"].iloc[0], "mtm_bc":mtm_bc}
        res_df.append(result)

    return res_df

def get_final_result(sim_exch, sim_instr, tx_eq):
    
    final_df = pd.DataFrame()
    for i in range(0, n):
        exch_rates = sim_exch[sim_exch.index == i]
        instr_rates = sim_instr[sim_instr.index == i]
        result = get_mtm_bc(i, tx_eq, exch_rates, instr_rates)
        res = pd.DataFrame(result)

        final_df = final_df.append(res)
        
    final_df.sort_values(by = ['env', 'idx'])
    
    return final_df


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
    
    # Filtering rates instruments based on the equity
    rates_E = rates_E[rates_E["instrument_type"] == 'E']
    rates_E.instrument = rates_E.instrument.astype('str')
    rates_E["key"] = "instru" + '_'+rates_E.instrument
    
    # Making key in rates exchange
    if len(rates_exchange) != 0:
        rates_exchange["key"] = rates_exchange["currency_from"] + "_"+rates_exchange["currency_to"]
        
    simulated_instruments = sim_instruments(df = rates_E)
    simulated_exchange = get_sim_exch(df = rates_exchange)
    
    final_res_output = get_final_result(simulated_exchange, simulated_instruments, tx_eq)
    
    final_res_output.to_csv(output_path1,index = False)
    simulated_exchange.to_csv(output_path2, index=False)
    simulated_instruments.to_csv(output_path3, index = False)