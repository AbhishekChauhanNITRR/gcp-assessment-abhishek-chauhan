from abc import ABC, abstractmethod
import duckdb
import config

class BaseQueryService(ABC):
    @abstractmethod
    def run_query(self, query: str) -> list[dict]:
        pass

    @abstractmethod
    def get_top_5_products(self) -> list[dict]:
        pass

    @abstractmethod
    def get_revenue_by_region(self) -> list[dict]:
        pass

    @abstractmethod
    def get_best_category_recent_7_days(self) -> list[dict]:
        pass

class LocalDuckDBService(BaseQueryService):
    def run_query(self, query: str) -> list[dict]:
        con = duckdb.connect("sales_mock.db")
        df = con.execute(query).df()
        con.close()
        return df.to_dict(orient="records")

    def get_top_5_products(self) -> list[dict]:
        q = f"""
        SELECT product_name, SUM(revenue) AS total_revenue
        FROM {config.TABLE_NAME}
        GROUP BY product_name
        ORDER BY total_revenue DESC
        LIMIT 5
        """
        return self.run_query(q)

    def get_revenue_by_region(self) -> list[dict]:
        q = f"""
        SELECT region, SUM(revenue) AS total_revenue
        FROM {config.TABLE_NAME}
        GROUP BY region
        ORDER BY total_revenue DESC
        """
        return self.run_query(q)

    def get_best_category_recent_7_days(self) -> list[dict]:
        q = f"""
        WITH MaxDate AS (
            SELECT MAX(order_date) AS max_dt FROM {config.TABLE_NAME}
        )
        SELECT category, SUM(revenue) AS total_revenue
        FROM {config.TABLE_NAME}, MaxDate
        WHERE order_date >= (max_dt - INTERVAL 7 DAY)
        GROUP BY category
        ORDER BY total_revenue DESC
        LIMIT 1
        """
        return self.run_query(q)

class LiveBigQueryService(BaseQueryService):
    def __init__(self):
        from google.cloud import bigquery
        self.client = bigquery.Client(project=config.GCP_PROJECT_ID)
        self.table_path = f"`{config.GCP_PROJECT_ID}.{config.DATA_SET_ID}.{config.TABLE_NAME}`"

    def run_query(self, query: str) -> list[dict]:
        query_job = self.client.query(query)
        results = query_job.result()
        return [dict(row) for row in results]

    def get_top_5_products(self) -> list[dict]:
        q = f"""
        SELECT product_name, SUM(revenue) AS total_revenue
        FROM {self.table_path}
        GROUP BY product_name
        ORDER BY total_revenue DESC
        LIMIT 5
        """
        return self.run_query(q)

    def get_revenue_by_region(self) -> list[dict]:
        q = f"""
        SELECT region, SUM(revenue) AS total_revenue
        FROM {self.table_path}
        GROUP BY region
        ORDER BY total_revenue DESC
        """
        return self.run_query(q)

    def get_best_category_recent_7_days(self) -> list[dict]:
        q = f"""
        WITH MaxDate AS (
            SELECT MAX(order_date) AS max_dt FROM {self.table_path}
        )
        SELECT category, SUM(revenue) AS total_revenue
        FROM {self.table_path}, MaxDate
        WHERE order_date >= DATE_SUB(max_dt, INTERVAL 7 DAY)
        GROUP BY category
        ORDER BY total_revenue DESC
        LIMIT 1
        """
        return self.run_query(q)

def get_query_service() -> BaseQueryService:
    if config.USE_MOCK:
        return LocalDuckDBService()
    return LiveBigQueryService()
