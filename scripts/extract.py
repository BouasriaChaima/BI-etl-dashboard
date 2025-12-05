import pandas as pd
import pyodbc
import pickle

# chemin de connection avec Northwind sous sql server
SQL_SERVER = r"DESKTOP-8TGTEJA\SQLEXPRESS01"
SQL_DATABASE = "Northwind"
# chemin de connection avec Northwind sous access
ACCESS_PATH = r"C:\Users\user\OneDrive\Documents\Northwind 2012 (1).accdb"

print("==========EXTRACTION :SQL Server + Access===========")

print("==========EXTRACTION :SQL Server===========")
#connection to the database in sql 
sql_conn = pyodbc.connect(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SQL_SERVER};"
    f"DATABASE={SQL_DATABASE};"
    f"Trusted_Connection=yes;"
)
# extraction des clients
sql_customers = pd.read_sql("""
    SELECT CustomerID, CompanyName, City, Country
    FROM Customers
""", sql_conn)
#on ajoute l'attribut source
sql_customers['Source'] = 'SQL'

# extraction des employees
sql_employees = pd.read_sql("""
    SELECT EmployeeID, FirstName + ' ' + LastName as EmployeeName, City, Country
    FROM Employees
""", sql_conn)
#on ajoute l'attribut source
sql_employees['Source'] = 'SQL'

# extraction des commandes
sql_orders = pd.read_sql("""
    SELECT OrderID, CustomerID, EmployeeID, OrderDate, ShippedDate
    FROM Orders
""", sql_conn)
#on ajoute l'attribut source
sql_orders['Source'] = 'SQL'
#on ferme la connection
sql_conn.close()
print("==========EXTRACTION :Access===========")
#on va connecter a la bdd access
access_conn = pyodbc.connect(
    f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};"
    f"DBQ={ACCESS_PATH};"
)
# extraction des clients
access_customers = pd.read_sql("""
    SELECT ID as CustomerID, Company as CompanyName, City, [Country/Region] as Country
    FROM Customers
""", access_conn)
access_customers['Source'] = 'Access'

# extraction des employees
access_employees = pd.read_sql("""
    SELECT ID as EmployeeID, [First Name] & ' ' & [Last Name] as EmployeeName, 
           City, [Country/Region] as Country
    FROM Employees
""", access_conn)
#on ajoute l'attribut source
access_employees['Source'] = 'Access'

# extraction des commandes
access_orders = pd.read_sql("""
    SELECT [Order ID] as OrderID, [Customer ID] as CustomerID, 
           [Employee ID] as EmployeeID, [Order Date] as OrderDate, 
           [Shipped Date] as ShippedDate
    FROM Orders
""", access_conn)
#on ajoute l'attribut source
access_orders['Source'] = 'Access'

access_conn.close()

print("\nconcatination des donnees ")

customers = pd.concat([sql_customers, access_customers], ignore_index=True)
employees = pd.concat([sql_employees, access_employees], ignore_index=True)
orders = pd.concat([sql_orders, access_orders], ignore_index=True)

print(f"Total Customers: {len(customers)}")
print(f"Total Employees: {len(employees)}")
print(f"Total Orders: {len(orders)}")
#saving the data to not repeat the process of extracting when in the following steps
print("\nSaving the data...")
with open('data/raw_data.pkl', 'wb') as f:
    pickle.dump({
        'customers': customers,
        'employees': employees,
        'orders': orders
    }, f)

