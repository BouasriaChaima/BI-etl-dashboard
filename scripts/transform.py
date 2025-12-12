import pandas as pd
import pickle

print("TRANSFORMATION - modele en etoile")
print("\nLoading raw data from the file ")

# recuperer les donnees qu'on a extracter
with open('data/raw_data.pkl', 'rb') as f:
    data = pickle.load(f)

customers = data['customers']
employees = data['employees']
orders = data['orders']

# dimension client
dim_customer = customers.copy()
# on va ajouter la cle sequentielle
dim_customer.insert(0, 'Customer_SK', range(1, len(dim_customer) + 1))
# renaming the natural key
dim_customer.rename(columns={'CustomerID': 'Customer_NK'}, inplace=True)
# putting the name of the columns
dim_customer = dim_customer[[
    'Customer_SK', 'Customer_NK', 'CompanyName', 'City', 'Country', 'Source']]
print(f"created dim_customer: {len(dim_customer)} customers")

# dimension employee
dim_employee = employees.copy()
# on va ajouter la cle sequentielle
dim_employee.insert(0, 'Employee_SK', range(1, len(dim_employee) + 1))
# renaming the natural key
dim_employee.rename(columns={'EmployeeID': 'Employee_NK'}, inplace=True)
# putting the name of the columns
dim_employee = dim_employee[[
    'Employee_SK', 'Employee_NK', 'EmployeeName', 'City', 'Country', 'Source']]
print(f"created dim_employee: {len(dim_employee)} employees")

# dimension date
# converting strings into date type
orders['OrderDate'] = pd.to_datetime(orders['OrderDate'], errors='coerce')

# getting the date range
min_date = orders['OrderDate'].min()
max_date = orders['OrderDate'].max()
print(f"date range: {min_date.date()} to {max_date.date()}")

# creating the calender(every date in between)
date_range = pd.date_range(start=min_date, end=max_date, freq='D')
dim_date = pd.DataFrame({
    'Date_SK': range(1, len(date_range) + 1),
    'Date': date_range,
    'Year': date_range.year,
    'Quarter': date_range.quarter,
    'Month': date_range.month,
    'MonthName': date_range.strftime('%B'),
    'Day': date_range.day,
    'DayOfWeek': date_range.dayofweek,
    'DayName': date_range.strftime('%A'),
    'WeekOfYear': date_range.isocalendar().week
})
print(f"created dim_date: {len(dim_date)} dates")

# table des faits
orders['ShippedDate'] = pd.to_datetime(orders['ShippedDate'], errors='coerce')

# Merge to get the sequential keys from dimensions
print("Merging with dimensions to get sequential keys...")

# Merge with dim_customer to get Customer_SK
orders = orders.merge(
    dim_customer[['Customer_NK', 'Source', 'Customer_SK']],
    left_on=['CustomerID', 'Source'],
    right_on=['Customer_NK', 'Source'],
    how='left'
).rename(columns={'Customer_SK': 'Customer_FK'})

# Merge with dim_employee to get Employee_SK
orders = orders.merge(
    dim_employee[['Employee_NK', 'Source', 'Employee_SK']],
    left_on=['EmployeeID', 'Source'],
    right_on=['Employee_NK', 'Source'],
    how='left'
).rename(columns={'Employee_SK': 'Employee_FK'})

# Merge with dim_date to get Date_SK
orders = orders.merge(
    dim_date[['Date', 'Date_SK']],
    left_on='OrderDate',
    right_on='Date',
    how='left'
).rename(columns={'Date_SK': 'Date_FK'})

# calculating KPIs
print("calculating KPIs...")
orders['Delivered'] = orders['ShippedDate'].notna().astype(int)
orders['NotDelivered'] = orders['ShippedDate'].isna().astype(int)

# creating table des faits
fact_orders = orders[['OrderID', 'Customer_FK', 'Employee_FK', 'Date_FK',
                      'Delivered', 'NotDelivered', 'Source']].copy()

# adding the sequentiel key
fact_orders.insert(0, 'Order_SK', range(1, len(fact_orders) + 1))

print(f"created fact table: {len(fact_orders)} orders")
print(f" - Delivered: {fact_orders['Delivered'].sum()}")
print(f" - Not Delivered: {fact_orders['NotDelivered'].sum()}")

# enregistrement du modele
with open('data/star_schema.pkl', 'wb') as f:
    pickle.dump({
        'dim_customer': dim_customer,
        'dim_employee': dim_employee,
        'dim_date': dim_date,
        'fact_orders': fact_orders
    }, f)
