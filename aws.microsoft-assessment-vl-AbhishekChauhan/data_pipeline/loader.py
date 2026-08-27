import os
import pandas as pd
import duckdb
import config

def inspect_and_clean_sales(file_path: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
        df = pd.DataFrame({
            "order_id": [1, 2, 3, 4, 5, 6, 7],
            "order_date": ["2026-08-01", "2026-08-10", "2026-08-15", "2026-08-20", "2026-08-25", "2026-08-26", "2026-08-27"],
            "store_id": [101, 102, 101, 103, 102, 101, 103],
            "product_id": [10, 11, 10, 12, 11, 10, 12],
            "product_name": ["Widget A", "Widget B", "Widget A", "Widget C", "Widget B", "Widget A", "Widget C"],
            "category": ["Electronics", "Home", "Electronics", "Apparel", "Home", "Electronics", "Apparel"],
            "quantity": [2, 1, 3, 1, 2, 4, 1],
            "unit_price": [60.25, 250.00, 50.00, 450.00, 150.00, 150.00, 100.00],
            "region": ["North", "South", "East", "West", "North", "North", "South"]
        })
    else:
        df = pd.read_csv(file_path)

    # Standardize column header names
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    df = df.drop_duplicates()
    
    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        df = df.dropna(subset=["order_date"])

    # Clean numeric columns
    if "quantity" in df.columns:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)

    if "unit_price" in df.columns:
        if df["unit_price"].dtype == object:
            df["unit_price"] = df["unit_price"].astype(str).str.replace(r"[\$,]", "", regex=True)
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0)

    # Calculate revenue column if missing
    if "revenue" not in df.columns and "quantity" in df.columns and "unit_price" in df.columns:
        df["revenue"] = df["quantity"] * df["unit_price"]

    if "region" in df.columns:
        df["region"] = df["region"].fillna("Unknown")

    return df

def setup_database(csv_path: str = "data/sales.csv"):
    df = inspect_and_clean_sales(csv_path)

    if config.USE_MOCK:
        con = duckdb.connect("sales_mock.db")
        con.execute(f"DROP TABLE IF EXISTS {config.TABLE_NAME}")
        con.execute(f"CREATE TABLE {config.TABLE_NAME} AS SELECT * FROM df")
        con.close()
    else:
        from google.cloud import bigquery

        client = bigquery.Client(project=config.GCP_PROJECT_ID)
        dataset_ref = f"{config.GCP_PROJECT_ID}.{config.DATA_SET_ID}"
        
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        client.create_dataset(dataset, exists_ok=True)
        
        table_ref = f"{dataset_ref}.{config.TABLE_NAME}"
        client.delete_table(table_ref, not_found_ok=True)
        
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",
            autodetect=True
        )
        client.load_table_from_dataframe(df, table_ref, job_config=job_config).result()
