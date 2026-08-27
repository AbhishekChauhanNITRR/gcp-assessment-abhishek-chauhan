import os
import pandas as pd
import duckdb
import config

def inspect_and_clean_sales(file_path: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
        df = pd.DataFrame({
            "order_id": [1, 2, 3, 4, 5, 6, 7],
            "order_date": ["2026-08-01", "2026-08-10", "2026-08-15", "2026-08-20", "2026-08-25", "2026-08-26", "2026-08-27"],
            "product_name": ["Widget A", "Widget B", "Widget A", "Widget C", "Widget B", "Widget A", "Widget C"],
            "category": ["Electronics", "Home", "Electronics", "Apparel", "Home", "Electronics", "Apparel"],
            "region": ["North", "South", "East", "West", "North", "North", "South"],
            "revenue": ["$120.50", "$250.00", "150", "$450.00", "$300.00", "$600.00", "$100.00"]
        })
    else:
        df = pd.read_csv(file_path)

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df = df.drop_duplicates()
    
    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        df = df.dropna(subset=["order_date"])

    if "revenue" in df.columns:
        if df["revenue"].dtype == object:
            df["revenue"] = df["revenue"].astype(str).str.replace(r"[\$,]", "", regex=True)
        df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0.0)

    if "region" in df.columns:
        df["region"] = df["region"].fillna("Unknown")

    return df

def setup_database(csv_path: str = "data/sales.csv"):
    df = inspect_and_clean_sales(csv_path)

    if config.USE_MOCK:
        con = duckdb.connect("sales_mock.db")
        con.execute(f"CREATE TABLE IF NOT EXISTS {config.TABLE_NAME} AS SELECT * FROM df")
        con.close()
    else:
        from google.cloud import bigquery
        client = bigquery.Client(project=config.GCP_PROJECT_ID)
        dataset_ref = f"{config.GCP_PROJECT_ID}.{config.DATA_SET_ID}"
        
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        client.create_dataset(dataset, exists_ok=True)
        
        table_ref = f"{dataset_ref}.{config.TABLE_NAME}"
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
        client.load_table_from_dataframe(df, table_ref, job_config=job_config).result()