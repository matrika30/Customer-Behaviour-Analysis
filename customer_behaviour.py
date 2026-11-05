import os
import re
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL

load_dotenv()

# Validate environment variables
required_variables = [
    "DB_USER",
    "DB_PASSWORD",
    "DB_HOST",
    "DB_NAME"
]

for variable in required_variables:
    if not os.getenv(variable):
        raise ValueError(
            f"Missing environment variable: {variable}"
        )

print("All environment variables loaded successfully!")
# Read CSV dataset
df = pd.read_csv("customer_shopping_behavior.csv")

# Clean column names for easier SQL queries
df.columns = [
    re.sub(r"_+", "_", re.sub(r"[^a-zA-Z0-9]+", "_", col.strip().lower())).strip("_")
    for col in df.columns
]

print("Dataset loaded successfully!")
print(df.head())

# Check number of records
print("Total records:", len(df))
# Dataset dimensions
print("Shape:", df.shape)

# First five records
print(df.head())

# Dataset information
df.info()

# Statistical summary
print(df.describe(include="all"))

# Missing values
print(df.isnull().sum())

# Duplicate records
print("Duplicates:", df.duplicated().sum())

# Unique values
print(df.nunique())

df['review_rating'] = df.groupby('category')['review_rating'].transform(
    lambda x: x.fillna(x.median())
)

# Handle any remaining missing ratings
df['review_rating'] = df['review_rating'].fillna(
    df['review_rating'].median()
)
print("Missing values before cleaning:")
print(df.isnull().sum())

print("Missing values after cleaning:")
print(df.isnull().sum())

df.rename(
    columns={'purchase_amount_usd': 'purchase_amount'},
    inplace=True
)

#create a column age_group
labels = [
    'Young Adult (18-25)',
    'Adult (26-35)',
    'Middle-aged (36-50)',
    'Senior (51+)'
]

bins = [17, 25, 35, 50, float('inf')]

df['age_group'] = pd.cut(
    df['age'],
    bins=bins,
    labels=labels
)

print(df[['age', 'age_group']].head(15))


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
df['purchase_frequency_days'] = df['frequency_of_purchases'].map(
    frequency_mapping
)
print(df['frequency_of_purchases'].value_counts())

print(
    df[df['purchase_frequency_days'].isnull()]
    ['frequency_of_purchases'].unique()
)

print(df[['purchase_frequency_days','frequency_of_purchases']].head(10))

# Compare both columns
comparison = (
    df['discount_applied'] == df['promo_code_used']
)

print("Matching rows:", comparison.sum())

print("Non-matching rows:", (~comparison).sum())

print(pd.crosstab(
    df['discount_applied'],
    df['promo_code_used']
))

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
