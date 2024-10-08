# -*- coding: utf-8 -*-
"""script-Copy1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1QVwckYiSMtKZ7t25flV5IJ9VaADHrejY

# NOTES
"""





"""# IMPORTS AND SETTINGS"""

import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from linearmodels.panel import PanelOLS, RandomEffects
from statsmodels.api import add_constant
from linearmodels.panel import compare
import numpy as np
import scipy.stats
from linearmodels.panel import FirstDifferenceOLS
from statsmodels.stats.outliers_influence import variance_inflation_factor
# import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 500)
from linearmodels.panel import PanelOLS
# from sklearn.preprocessing import StandardScaler
from statsmodels.stats.diagnostic import het_breuschpagan
import os
import warnings
warnings.filterwarnings('ignore')

project_folder=os.getcwd()
project_folder

"""# SCRIPT

## DATA READING
"""



# data from Excel
filename2 = os.path.join(project_folder, "Regression data", "panel_regression_absolute.csv")
data2 = pd.read_csv(os.path.join(project_folder, filename2))
#'Country' as entity and 'Year' as time
data2 = data2.set_index(['Country', 'Year'])
data2=data2.dropna(axis=1, how="all")
data2.head(20)

data2.info()

# #Standardisation of data
# scaler = StandardScaler()
# numerical_data = data.select_dtypes(include=['float64', 'int64'])
# scaled_data = scaler.fit_transform(numerical_data)
# data_scaled = pd.DataFrame(scaled_data, columns=numerical_data.columns, index=data.index)
# data_scaled

data2.describe().T

#scaling of the data
data2.loc[:, ["GDP/capita", "Tech Advancement CN", "Fixed Asset Investment CN (T-1)", "Avg Wage Difference"]] = data2.loc[:, ["GDP/capita", "Tech Advancement CN", "Fixed Asset Investment CN (T-1)", "Avg Wage Difference"]].div(1000)
data2.loc[:, "Import"] = data2.loc[:, "Import"].div(1000000)
data2.head(20)

data2.describe().T

# dependent, independent and control variables
data2["constant"]=1
dependent_var = data2['Import'].to_frame()
independent_vars = data2.iloc[:,1:]
dependent_var.shape, independent_vars.shape

vif = pd.DataFrame()
vif["VIF Factor"] = [variance_inflation_factor(independent_vars.values, i) for i in range(independent_vars.shape[1])]
vif["features"] = independent_vars.columns
print("Variance Inflation Factors (VIF):")
vif

correlation_matrix = data2.corr()
print(correlation_matrix)

# Verify column names
print(independent_vars.columns)

# Drop the column if it exists
independent_vars = independent_vars.drop(columns=["constant","Fixed Asset Investment CN (T-1)","Avg Wage Difference"], errors='ignore')

# Verify the result
print(independent_vars.columns)

vif = pd.DataFrame()
vif["VIF Factor"] = [variance_inflation_factor(independent_vars.values, i) for i in range(independent_vars.shape[1])]
vif["features"] = independent_vars.columns
print("Variance Inflation Factors (VIF):")
vif

"""## MODELS

### FE MODEL (ENTITY ONE WAY)
"""

print(independent_vars.columns.duplicated())

corr_matrix = independent_vars.corr()
print(corr_matrix)

def matrix_rank_check(df):
    return np.linalg.matrix_rank(df.values)

print(f"Rank of independent variables matrix: {matrix_rank_check(independent_vars)}")
print(f"Number of columns in independent variables: {independent_vars.shape[1]}")

print(corr_matrix)

# Fixed Effects Model
fe_model = PanelOLS(dependent_var, independent_vars, entity_effects=True)
fe_results = fe_model.fit()

print("Fixed Effects Model Results:")
fe_results

"""### FE MODEL (TWO-WAY)"""

#two-way fixed effects model
two_model = PanelOLS(dependent_var, independent_vars, entity_effects=True, time_effects=True,  drop_absorbed = True)
results = two_model.fit()
results

"""### RANDOM EFFECTS"""

# Random Effects Model
re_model = RandomEffects(dependent_var, independent_vars)
re_results = re_model.fit()

print("\nRandom Effects Model Results:")
re_results

#Hausmann Test
comparison = compare({"Fixed": fe_results, "Random": re_results})
comparison

"""### Durbin-Wu-Hausman test"""

import numpy as np
from statsmodels.regression.linear_model import OLS
from scipy.stats import chi2

def durbin_wu_hausman_test(ols_fixed, ols_random):
    """
    Perform the Durbin-Wu-Hausman test for endogeneity.

    Parameters:
    ols_fixed : OLS
        Fixed-effects regression results
    ols_random : OLS
        Random-effects regression results

    Returns:
    chi_squared_stat : float
        The chi-squared test statistic
    p_value : float
        The p-value of the test
    """
    # Residuals from fixed effects model
    u_fe = ols_fixed.resids

    # Residuals from random effects model
    u_re = ols_random.resids

    # Calculate the test statistic
    dw_hausman_stat = np.sum((u_fe - u_re)**2) / np.sum(u_fe**2)

    df = fe_results.df_model - re_results.df_model

    # Compute the p-value
    p_value = 1 - chi2.cdf(dw_hausman_stat, df)

    return dw_hausman_stat, p_value

# Example usage:
# Assuming you have panel data stored in a DataFrame called 'data'
# with columns 'dependent_var', 'independent_var1', 'independent_var2', etc.
# and a variable 'id' for individual identifiers and 'time' for time identifiers.


# Perform the Durbin-Wu-Hausman test
dw_hausman_stat, p_value = durbin_wu_hausman_test(fe_results, re_results)

print("Durbin-Wu-Hausman Test Statistic:", dw_hausman_stat)
print("P-value:", p_value)

fe_results

#Wald Test: H0 is that all the regressors are not associated (no effect) with the dependent variables, H0 model has only the intercept (unconditional average)
wald_result = fe_results.wald_test(formula="Fit=0, `GDP/capita`=0, `Energy Consumption`=0, `Annual Solar Capacity Addition`=0, `Tech Advancement CN`=0, `TechAdvancement `=0, `Trade Policies EU`=0, `Environ. St. Difference`=0")
wald_result

# Perform the Breusch-Pagan test
residuals = fe_results.resids
independent_vars_bp_test = independent_vars.copy()
independent_vars_bp_test["constant"]=1
independent_vars_bp_test

bp_test = het_breuschpagan(resid=residuals, exog_het=independent_vars_bp_test, robust=True)
labels = ['Lagrange multiplier statistic', 'p-value', 'f-value', 'f p-value']
print(dict(zip(labels, bp_test)))

