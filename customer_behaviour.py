import pandas as pd 
df = pd.read_csv("customer_shopping_behavior.csv")
#get column details
print(df.head())
#summary statistics of all columns
print(df.describe(include="all"))
#check null values
print(df.isnull().sum())