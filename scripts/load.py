import pandas as pd
import pickle
import os

OUTPUT_FOLDER = "data/star schema"
print("LOADING - saving to excel files")

with open('data/star_schema.pkl', 'rb') as f:
    star_schema = pickle.load(f)

dim_customer = star_schema['dim_customer']
dim_employee = star_schema['dim_employee']
dim_date = star_schema['dim_date']
fact_orders = star_schema['fact_orders']

# creation des fichiers excel
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
print(f"Output folder: {OUTPUT_FOLDER}/")

# save dim_customer
filename = f'{OUTPUT_FOLDER}/dim_customer.xlsx'
dim_customer.to_excel(filename, index=False)
print(f"{filename} ({len(dim_customer)} rows)")

# save dim_employee
filename = f'{OUTPUT_FOLDER}/dim_employee.xlsx'
dim_employee.to_excel(filename, index=False)
print(f"{filename} ({len(dim_employee)} rows)")

# save dim_date
filename = f'{OUTPUT_FOLDER}/dim_date.xlsx'
dim_date.to_excel(filename, index=False)
print(f"{filename} ({len(dim_date)} rows)")

# save fact_Orders
filename = f'{OUTPUT_FOLDER}/fact_orders.xlsx'
fact_orders.to_excel(filename, index=False)
print(f"{filename} ({len(fact_orders)} rows)")

print(f"\nFiles saved in '{OUTPUT_FOLDER}/' folder:")
