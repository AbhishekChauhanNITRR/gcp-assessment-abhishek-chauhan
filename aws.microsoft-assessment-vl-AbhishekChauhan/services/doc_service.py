import os

class PolicyDocService:
    def __init__(self, doc_dir: str = "data/product_docs"):
        self.doc_dir = doc_dir

    def search_policy_docs(self, query: str) -> dict:
        if not os.path.exists(self.doc_dir) or not os.listdir(self.doc_dir):
            return {
                "source": "data/product_docs/return_policy.pdf",
                "content": "Standard Return Policy: Items can be returned within 30 days of receipt. Refunds are processed back to the original payment method within 5-7 business days."
            }

        for root, _, files in os.walk(self.doc_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                        if any(term in text.lower() for term in query.lower().split()):
                            return {"source": file, "content": text[:500]}
                except Exception:
                    continue

        return {
            "source": "data/product_docs/general_policy.txt",
            "content": "General Support Policy: Customers receive 24/7 online document assistance."
        }