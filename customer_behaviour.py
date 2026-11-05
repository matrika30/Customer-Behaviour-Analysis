import os
import re
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL

load_dotenv()

# Read CSV dataset
df = pd.read_csv("customer_shopping_behavior.csv")

# Clean column names for easier SQL queries
df.columns = [
    re.sub(r"_+", "_", re.sub(r"[^a-zA-Z0-9]+", "_", col.strip().lower())).strip("_")
    for col in df.columns
]

print("Dataset loaded successfully!")
print(df.head())

# Create PostgreSQL connection
url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME")
)

engine = create_engine(url)

# Upload dataset to PostgreSQL
df.to_sql(
    "customers",
    engine,
    if_exists="replace",
    index=False
)

print("Dataset imported into PostgreSQL successfully!")

# Check number of records
print("Total records:", len(df))

df = pd.read_csv("customer_shopping_behavior.csv")
#get column details
print(df.head())
#summary statistics of all columns
print(df.describe(include="all"))
#check null values
print(df.isnull().sum())
df['Review Rating'] = df.groupby('Category')['Review Rating'].transform(lambda x: x.fillna(x.median()))
print(df.isnull().sum())
df.columns = df.columns.str.lower() 
df.columns = df.columns.str.replace(' ','_')
df = df.rename(columns= {'purchase_amount_(usd)':'purchase_amount'})
print(df.columns)
#create a column age_group
labels = ['Young Adult','Adult','Middle-aged','Senior']
df['age_group'] = pd.qcut(df['age'],q = 4,labels = labels)
print(df[['age','age_group']].head(10))
#creating column purchase_frequency_days
frequency_mapping = {
    'Fortnightly': 14,
    'Weekly': 7,
    'Monthly': 30,
    'Quarterly': 90,
    'Bi-Weekly': 14,
    'Annually': 365,
    'Every 3 Months': 90
}

df['purchase_frequency_days'] = df['frequency_of_purchases'].map(frequency_mapping)
print(df[['purchase_frequency_days','frequency_of_purchases']].head(10))
print(df[['discount_applied','promo_code_used']].head(10))
print(df['discount_applied'] == df['promo_code_used'].all())
df = df.drop('promo_code_used',axis =1)
print(df.columns)
