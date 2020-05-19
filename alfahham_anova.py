import pandas as pd
import scipy.stats as stats
import researchpy as rp
import statsmodels.api as sm
from statsmodels.formula.api import ols
import matplotlib.pyplot as plt
import os

os.chdir("C:/Users/Alfahham/Desktop/pythonproj/PCA") # point to where the raw input file is on local drive
pwdindex_col = 'True'
df_raw = pd.read_excel("SHC_data_final_04122020.xlsx",  index_col ='ID') #pull in the excel sheet in pandas
df_raw["Depth"] = df_raw["Depth"].map({"ten": "0 - 10",
    "twenty": "10 - 20",
    "thirty": "20 - 30"}) # cleanup of some columns
df_raw["Tillage"] = df_raw["Tillage"].map({"NT": "LT",
                                  "TILL": "T"}) #more cleanup
df_raw = df_raw.rename(columns = {"Treatment_str": "Treatment"}) # rename treatment column

###
## FIRST STEP EVERYTHING ANOVA

all_vars = (df_raw.columns) #all columns in my df
identity_vars = ['PlotID', 'Plot', 'USDA']
explanatory_vars = ['Treatment', 'Tillage', 'Depth']
stupid_vars = ['TrTl','porosity', 'Compaction', 'RockWt_pct','TOT_SAND',
       'CSILT', 'MSILT', 'FSILT', 'TOTSILT', 'CCLAY', 'FCLAY', 'TOT_CLAY']
response_vars = list(set(all_vars)-set(stupid_vars)-set(explanatory_vars)-set(identity_vars))

# 3_way_output - type two ANOVA
diag_dictionary = {"omni":"Omnibus",
                   "omnipv":"Prob_Omnibus",
                   "jb":"Jarque_Bera",
                   "jbpv": "Prob_Jarque_Bera",
                   "condno": "Cond_number",
                   "kurtosis": "Kurtosis"}

def three_way_anova_assumptions(response_var, data):
    '''gives the output of the anova assumptions for a 3 way interaction'''
    anova_model = ols(f'{response_var} ~ C(Treatment)*C(Tillage)*C(Depth)', data=data)
    anova_model_fit = anova_model.fit() # linear model fit
    anova_model_fit.summary()
    diag_dict = anova_model_fit.diagn # diagnosis of linear model
    diag_dict.keys()
    anova_assumptions_test = pd.DataFrame.from_dict(diag_dict, orient='index').rename(columns={0:f"{response_var}__{data.Depth[0]}"})
    anova_output = sm.stats.anova_lm(anova_model_fit, typ=2)
    return anova_assumptions_test

def three_way_anova_results(response_var, data):
    '''runs the ANOVA through a list of response vars and produces a df with ANOVA results'''
    anova_model = ols(f'{response_var} ~ C(Treatment)*C(Tillage)*C(Depth)', data=data)
    anova_model_fit = anova_model.fit() # linear model fit
    anova_output = sm.stats.anova_lm(anova_model_fit, typ=2)
    return anova_output

def two_way_anova_assumptions(response_var, data):
    '''gives the output of the two way anova assumptions'''
    anova_model = ols(f'{response_var} ~ C(Treatment)*C(Tillage)', data=data)
    anova_model_fit = anova_model.fit() # linear model fit
    anova_model_fit.summary()
    diag_dict = anova_model_fit.diagn # diagnosis of linear model
    diag_dict.keys()
    anova_assumptions_test = pd.DataFrame.from_dict(diag_dict, orient='index').rename(columns={0:f"{response_var}__{data.Depth[0]}"})
    return anova_assumptions_test

def one_way_anova_results(response_var, treatment, data):
    '''gives output for one way ANOVA results'''
    anova_model = ols(f'{response_var} ~ C({treatment})', data=data)
    anova_model_fit = anova_model.fit() # linear model fit
    anova_output = sm.stats.anova_lm(anova_model_fit, typ=2)
    return anova_output

df010 = df_raw[df_raw.Depth == '0 - 10']
df010.name = "0-10 cm data"
df1020 = df_raw[df_raw.Depth == '10 - 20']
df1020.name = "10-20 cm data"
df2030 = df_raw[df_raw.Depth == '20 - 30']
df2030.name = "20-30 cm data"

## RUNNING IT TO GET OUTPUT 3 WAY ANOVA ###
final_assumptions_df_3_way_anova = pd.DataFrame(index= ['jb', 'jbpv', 'skew', 'kurtosis', 'omni', 'omnipv', 'condno',
       'mineigval'])
for response_var in response_vars:
    assumptions_df = three_way_anova_assumptions(response_var, data=df_raw)
    final_assumptions_df_3_way_anova = final_assumptions_df_3_way_anova.join(assumptions_df)

final_three_way_anova_df_3_way = pd.DataFrame([])
for response_var in response_vars:
    three_way_output = three_way_anova_results(response_var, data=df_raw)
    three_way_output["response_var"] = response_var
    final_three_way_anova_df_3_way = final_three_way_anova_df_3_way.append(three_way_output)
    final_three_way_anova_df_3_way.loc[
        final_three_way_anova_df_3_way['PR(>F)'] < 0.05, 'sig flag'] = ' * * sig * * '
    final_three_way_anova_df_3_way.loc[(final_three_way_anova_df_3_way['PR(>F)'] <= 0.1)
                               & (final_three_way_anova_df_3_way['PR(>F)'] >= 0.05),
                               'sig flag'] = ' * * near sig * * '

# final_three_way_anova_df_3_way.to_csv("three_way_anova.csv")
##### MAIN PART FOR 2 WAY ANOVA ####
final_assumptions_df_2_way_anova = pd.DataFrame(index= ['jb', 'jbpv', 'skew', 'kurtosis', 'omni', 'omnipv', 'condno',
       'mineigval'])
for dataframes in [df010, df1020, df2030]:
    for response_var in response_vars:
        assumptions_df_2_way_anova = two_way_anova_assumptions(response_var=response_var, data=dataframes)
        final_assumptions_df_2_way_anova = final_assumptions_df_2_way_anova.join(assumptions_df_2_way_anova)

final_two_way_anova_df = pd.DataFrame([])
for dataframes in [df010, df1020, df2030]:
    for response_var in response_vars:
        two_way_output = two_way_anova_results(response_var=response_var, data=dataframes)
        two_way_output["response_var"] = response_var
        two_way_output["depth"] = dataframes.Depth[0]
        final_two_way_anova_df = final_two_way_anova_df.append(two_way_output)
        final_two_way_anova_df.loc[
            final_two_way_anova_df['PR(>F)'] < 0.05, 'sig flag'] = ' * * sig * * '
        final_two_way_anova_df.loc[(final_two_way_anova_df['PR(>F)'] <= 0.1)
                                   & (final_two_way_anova_df['PR(>F)'] >= 0.05),
                                   'sig flag'] = ' * * near sig * * '

# final_two_way_anova_df.to_csv("two_way_anova.csv")

final_one_way_anova_treatment_df = pd.DataFrame([])
for dataframes in [df010, df1020, df2030]:
    for response_var in response_vars:
        output = one_way_anova_results(response_var=response_var, treatment="Treatment" ,data=dataframes)
        output["response_var"] = response_var
        output["depth"] = dataframes.Depth[0]
        final_one_way_anova_treatment_df = final_one_way_anova_treatment_df.append(output)
        final_one_way_anova_treatment_df.loc[
            final_one_way_anova_treatment_df['PR(>F)'] < 0.05, 'sig flag'] = ' * * sig * * '
        final_one_way_anova_treatment_df.loc[(final_one_way_anova_treatment_df['PR(>F)'] <= 0.1)
                                   & (final_one_way_anova_treatment_df['PR(>F)'] >= 0.05),
                                   'sig flag'] = ' * * near sig * * '
final_one_way_anova_treatment_df.to_csv("one_way_anova_treatment.csv")

final_one_way_anova_tillage_df = pd.DataFrame([])
for dataframes in [df010, df1020, df2030]:
    for response_var in response_vars:
        output = one_way_anova_results(response_var=response_var, treatment="Tillage" ,data=dataframes)
        output["response_var"] = response_var
        output["depth"] = dataframes.Depth[0]
        final_one_way_anova_tillage_df = final_one_way_anova_tillage_df.append(output)
        final_one_way_anova_tillage_df.loc[
            final_one_way_anova_tillage_df['PR(>F)'] < 0.05, 'sig flag'] = ' * * sig * * '
        final_one_way_anova_tillage_df.loc[(final_one_way_anova_tillage_df['PR(>F)'] <= 0.1)
                                   & (final_one_way_anova_tillage_df['PR(>F)'] >= 0.05),
                                   'sig flag'] = ' * * near sig * * '
final_one_way_anova_tillage_df.to_csv("one_way_anova_tillage.csv")

#########################################################################
