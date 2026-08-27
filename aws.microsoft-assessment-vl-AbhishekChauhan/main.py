import config
from data_pipeline.loader import setup_database
from services.query_service import get_query_service
from services.doc_service import PolicyDocService
from services.ai_service import generate_rag_response

def run_assessment():
    print("==================================================")
    print("  NorthStar Retail Data & AI Query Assistant")
    print(f"  Target Platform: GCP | Mock Mode: {config.USE_MOCK}")
    print("==================================================\n")

    print("[1/4] Preparing Data Warehouse Table...")
    setup_database()
    query_service = get_query_service()
    print("      Table created and loaded successfully.\n")

    print("[2/4] Querying Task 1: Top 5 Products by Total Revenue...")
    top_5 = query_service.get_top_5_products()
    res_1 = generate_rag_response("Top 5 products by revenue", str(top_5))
    print(res_1)
    print("\n" + "-"*50 + "\n")

    print("[3/4] Querying Task 2: Total Revenue by Region...")
    by_region = query_service.get_revenue_by_region()
    res_2 = generate_rag_response("Total revenue by region", str(by_region))
    print(res_2)
    print("\n" + "-"*50 + "\n")

    print("[4/4] Querying Task 3: Best-Selling Category (Recent 7 Days before Max Date)...")
    best_cat = query_service.get_best_category_recent_7_days()
    res_3 = generate_rag_response("Best selling category in last 7 days of dataset", str(best_cat))
    print(res_3)
    print("\n" + "-"*50 + "\n")

    print("[Bonus] Policy Document RAG Search Query...")
    doc_service = PolicyDocService()
    doc_match = doc_service.search_policy_docs("return refund")
    res_policy = generate_rag_response(
        "What is the return policy?", 
        doc_match["content"], 
        source_citation=doc_match["source"]
    )
    print(res_policy)

if __name__ == "__main__":
    run_assessment()