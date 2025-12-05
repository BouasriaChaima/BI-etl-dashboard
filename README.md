# BI-etl-dashboard
pour creer l'entropot des donnees en modele etoile, et le dashboard en utilisons python ,on a besoin de plusieures bibliotheques : pandas openpyxl pyodbc plotly dash dash-bootstrap-components
details des bibliotheques:
- pandas: Manipulation de données
- pyodbc: Connexion aux bases de donnees
- plotly: Graphiques interactifs
- dash: Framework pour le dashboard web
- dash-bootstrap-components: Composants Bootstrap pour Dash
- pickle: manipulation des fichiers
# chemin de connection avec Northwind sous sql server
SQL_SERVER = r"DESKTOP-8TGTEJA\SQLEXPRESS01"s
SQL_DATABASE = "Northwind"
# chemin de connection avec Northwind sous access
ACCESS_PATH = r"C:\Users\user\OneDrive\Documents\Northwind 2012 (1).accdb"
# document ou on veut mettre les fichiers du modele etoile
OUTPUT_FOLDER = "data/star schema"

🎯 Star Schema Structure:

┌─────────────────────┐
│   DIM_Customer      │
│  120 customers      │
└─────────────────────┘
           │
           │ Customer_FK
           ▼
┌─────────────────────┐     ┌─────────────────────┐
│   DIM_Employee      │     │     DIM_Date        │
│  18 employees       │     │   3642 dates        │
└─────────────────────┘     └─────────────────────┘
           │                         │
           │ Employee_FK             │ Date_FK
           ▼                         ▼
        ┌────────────────────────────────┐
        │       FACT_Orders              │
        │      878 orders                │
        │                                │
        │  KPIs:                         │
        │  - Delivered: 848              │
        │  - Not Delivered: 30           │
        └────────────────────────────────┘