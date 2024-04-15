# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 17:33:04 2024

@author: irkat
"""

#set up
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import scipy
from scipy.stats import ttest_rel
###IMPORT
#retrieves folder pathway and datafile names from user
first = input("Hello. Please enter the pathway to your data:\n")
second= input("Thank you. Please enter the name of your data file with disease mortality counts:\n")
third = input("Thank you. Please enter the name of your data file with population counts:\n")
path = first
#import relevant csv data files as pandas data frames. encoding = 'unicode_escape' necessary for non-ACSII characters in files
deaths = pd.read_csv(os.path.join(path, second), encoding = 'unicode_escape')
pops = pd.read_csv(os.path.join(path, third), encoding = 'unicode_escape')

###TEMPORAL INVESTIGATION
##Deaths Wrangling and Consistency Checks
#create datetime type column Date
deaths['Date'] = pd.to_datetime(deaths['Month Code'], format = '%Y%m')
deaths.value_counts('Date')
#excluding 'suppressed' deaths
deaths.loc[deaths['Deaths'] == 'Suppressed', 'Suppressed'] = 'Yes'
suppressed = deaths.loc[deaths['Deaths']=='Supressed']
deaths = deaths.loc[deaths['Suppressed'].isnull()]
deaths['Deaths'] = deaths['Deaths'].astype('int64')
#consistency check int variables - deaths, date, year
deaths.describe()
#frequency checks
deaths.value_counts('State')
deaths.value_counts('Date')
deaths.value_counts('Ten-Year Age Groups Code')
#check for blanks
deaths.isnull().sum()
#check for duplicates
deaths.duplicated().value_counts()

###MERGING POPS AND DEATHS
##Deaths DF Wrangling
##Aggregating Deaths by Year, State, Age Group
deaths = deaths.rename(columns = {'Ten-Year Age Groups Code' : 'age_group'})
group_deaths = deaths.groupby(['Year','age_group','State'], as_index = False).agg(Deaths= ('Deaths','sum'))
#Creating Age Group FLags for Deaths Data (<5, 5-65, 65+)
group_deaths.value_counts('age_group')#there are no under 5
deaths_young = ['5-14','15-24','25-34','35-44', '45-54', '55-64']
deaths_old = ['65-74','75-84','85+']
group_deaths.loc[(group_deaths['age_group'].isin(deaths_young)),'death_young_old']= 'death_young'
group_deaths.loc[(group_deaths['age_group'].inin(deaths_old)),'death_young_old']= 'death_old'
#Aggregate by Year, State
grouped_deaths = group_deaths.groupby(['Year','State'], as_index = False).agg({'death_young':'sum', 'death_old':'sum'})
##Pops DF Wrangling
#Creating State column for pops
pops[['County', 'State']] = pops.County.str.split(",", expand = True)
pops['State'].str.strip()
#Creating combined age group columns for pop date (<5,5-65,65+)
pops.columns
pops['pop_young'] = pops['5 to 9 years'] + pops['10 to 14 years'] + pops['15 to 19 years'] + pops['20 to 24 years'] + pops['25 to 29 years'] + pops['30 to 34 years'] + pops['35 to 39 years'] + pops['40 to 44 years'] + pops['45 to 49 years'] + pops['50 to 54 years'] + pops['55 to 59 years'] + pops['60 to 64 years'] 
pops['pop_young'].sum()
pops['pop_old'] = pops['65 to 69 years'] + pops['70 to 74 years'] + pops['75-79 years'] + pops['80 to 84 years'] + pops['85 years and older']
pops['pop_old'].sum()
#Aggregating Pops by State and Year
group_pops = pops.groupby(['Year','State'], as_index = False).agg({'pop_young' : 'sum', 'pop_old' : 'sum'})
group_pops['pop_young'].sum()
##Merging on State and Year
#strip white space, change case, change type for consistency
group_pops['State'] = group_pops['State'].str.strip()
grouped_deaths['State'] = grouped_deaths['State'].str.strip()
grouped_deaths['State'] = grouped_deaths['State'].str.lower()
group_pops['State'] = group_pops['State'].str.lower()
grouped_deaths['State'] = grouped_deaths['State'].astype('str')
grouped_deaths['Year'] = grouped_deaths['Year'].astype('int64')
#export final grouped data
group_pops.to_csv(os.path.join(path, 'group_pos.csv'))
grouped_deaths.to_csv(os.path.join(path, 'grouped_deaths.csv'))
#merge!
merged = grouped_deaths.merge(group_pops, on = ['Year','State'])
merged.to_csv(os.path.join(path, 'merged_data.csv'))
#export merge
merged['pop_young'].sum()
merged['pop_old'].sum()
print("Files have been merged successfully")
input("Hit enter when ready to continue")

##Data Analysis
#aggregating deaths by month, return month with greatest and least deaths
monthly_deaths = deaths.groupby(deaths['Date'].dt.month).agg({'Deaths' : ['max', 'mean', 'sum']})
monthly_deaths = monthly_deaths.sort_values(('Deaths', 'mean'), ascending= False)
max_month = monthly_deaths.iloc[0]
print("Month with Greatest Number of Deaths\n", max_month)
input("Hit enter when ready to continue")
least_month = monthly_deaths.iloc[11]
print("Month with Least Number of Deaths\n", least_month)
input("Hit enter when ready to continue")
#plotting line graph of deaths over time, saves to folder
line = sns.lineplot(x='Date', y=('Deaths'), data = deaths)
line.figure. savefig(os.path.join(path, 'Death Counts Over Time'))
print("Please review figure: Death Count Over Time")
input("Hit enter when ready to continue")

###VULNERABLE GROUP DETERMINATION
#calculate death rates
merged['rate_old'] = merged['death_old']/merged['pop_old']
merged['rate_young'] = merged['death_young']/merged['pop_old']
avg_young_rate = merged['rate_young'].mean()
avg_old_rate = merged['rate_old'].mean()
print("The average death rate for ages 5-64 is ", avg_young_rate)
print("The average death rate for ages 65+ is ", avg_old_rate)
input("Hit enter when ready to continue")
##t-test
t, p = ttest_rel(merged['death_old'], merged['death_young'])
print(f"T-statistic : {t}")
print(f"P-value: {p}")
alpha = 0.05
if p< alpha:
    print("The difference in death rates is statistically significant. Over 65 is a vulnerable population.")
else:
    print("The difference in death rates is not statistically significant")
    exit()
input("Hit enter when ready to continue")
##Bar graph comparing total death numbers
total_young_deaths = merged['death_young'].sum()
total_old_deaths = merged['death_old'].sum()
fig, ax = plt.subplots(figsize=(6,4))
bar_positions = [0,1]
ax.bar(bar_positions, [total_young_deaths, total_old_deaths], width = 0.4, color = ['sky blue','blue'])
ax.set_xticks(bar_positions)
ax.set_xticklabels(['Young Deaths', 'Old Deaths'])
ax.set_ylabel('Total Deaths')
plt.savefig(os.path.join(path, 'Young vs Old Total Deaths'))
print("Please review figure: Young vs Old Total Deaths")
input("Hit enter when ready to continue")
##Bar graph comparing total population numbers
total_young_pops = merged['pop_young'].sum()
total_old_pops = merged['pop_old'].sum()
fig, ax = plt.subplots(figsize=(6,4))
bar_positions = [0,1]
chart = ax.bar(bar_positions, [total_young_pops, total_old_pops], width = 0.4, color = ['slyblue','blue'])
ax.set_xticks(bar_positions)
ax.set_xticklabels(['Young Population', 'Old Population'])
ax.set_ylabel('Average Death Rate')
plt.savefig(os.path.join(path, 'Young vs Old Average Death Rates'))
print('Please review figure: Young vs Old Average Death Rates. \n Note how seniors (65+) have much higher death rates')
input("Hit ready when ready to continue")
###DETERMINING AREA OF MOST NEED
##List states by 65+ size in most recent year
recent_year = merged['Year'].max()
merged_recent = merged[merged['Year']== recent_year]
merged_sorted = merged_recent.sort_values(by='pop_old', ascending = False)
print("States from highest to lowest senior populations: ")
print(merged_sorted['State'].tolist())
print("States with highest vulnerable populations require the most resources during flu season")
input("Hit enter when ready to continue")
##Bar graph top 10 states
top_states = merged_sorted.head(10)
top_state = merged_sorted['State'].head(1)
plt.figure(figsize = (10,6))
chart = plt.bar(top_states['State'], top_states['pop_old'])
plt.title(f'Vulnerable Population of Top 10 States in {recent_year}')
plt.ylabel('Population')
plt.savefig(os.path.join(path, 'States of Greatest Need'))
print('Please review figure: States of Greatest Need')
input("Hit enter when ready to continue")
print("Greatest need has been determined to be in", max_month, " ", top_state)

