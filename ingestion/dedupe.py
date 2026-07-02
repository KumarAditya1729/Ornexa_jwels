import re

class Deduplicator:
    def __init__(self):
        # Maps normalized text -> canonical_id
        self.registry = {}
        # Stores the canonical clusters
        # { "canonical_id": {"primary": product_dict, "aliases": set()} }
        self.clusters = {}
        self.counter = 1

    def normalize(self, text: str) -> str:
        if not text:
            return ""
        # Lowercase and remove punctuation/extra spaces
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def dedupe(self, product_dict: dict) -> dict:
        """Assigns a canonical ID to a product, grouping variants."""
        raw_name = product_dict.get("product_name", "")
        norm_name = self.normalize(raw_name)

        if not norm_name:
            # Cannot dedupe without a name, assign unique ID
            c_id = f"ORNEXA_{self.counter:05d}"
            self.counter += 1
            product_dict["canonical_id"] = c_id
            return product_dict

        if norm_name in self.registry:
            c_id = self.registry[norm_name]
            self.clusters[c_id]["aliases"].add(raw_name)
        else:
            c_id = f"ORNEXA_{self.counter:05d}"
            self.counter += 1
            self.registry[norm_name] = c_id
            self.clusters[c_id] = {
                "primary": product_dict,
                "aliases": {raw_name}
            }

        product_dict["canonical_id"] = c_id
        return product_dict

    def get_canonical_export(self):
        """Returns the canonical clusters for export."""
        export = []
        for c_id, data in self.clusters.items():
            export.append({
                "canonical_id": c_id,
                "primary_product": data["primary"],
                "aliases": list(data["aliases"])
            })
        return export
