"""
Search History Manager for persistent storage and retrieval of search analyses.
Allows users to review and reopen past reports.
"""

import os
import json
import time
from typing import List, Dict, Any, Optional

class SearchHistoryManager:
    """
    Manages loading, saving, and listing past patent search reports in JSON format.
    """

    def __init__(self, history_file: str = "data/search_history.json"):
        self.history_file = history_file
        self.history: List[Dict[str, Any]] = []
        self.load_history()

    def load_history(self) -> List[Dict[str, Any]]:
        """
        Loads persistent search history records from JSON file.
        """
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception as e:
                print(f"[SearchHistoryManager] Error loading history ({e}). Resetting.")
                self.history = []
        else:
            self.history = []
        return self.history

    def add_entry(self, report_data: Dict[str, Any]) -> str:
        """
        Saves a new search analysis report into history.
        Returns unique report_id.
        """
        report_id = f"RPT-{int(time.time())}"
        idx_data = report_data.get("novelty_index_data", {})
        novelty_score = idx_data.get("novelty_index", 0.0)
        potential_label = idx_data.get("potential_label", "N/A")

        entry = {
            "report_id": report_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "query": report_data.get("user_idea", ""),
            "novelty_index": novelty_score,
            "novelty_status": potential_label,
            "report_data": report_data
        }
        self.history.insert(0, entry)  # Prepend newest
        self.save_history()
        return report_id

    def get_entry_by_id(self, report_id: str) -> Optional[Dict[str, Any]]:
        """
        Finds specific history item by ID.
        """
        for item in self.history:
            if item.get("report_id") == report_id:
                return item
        return None

    def save_history(self):
        """
        Writes history array to JSON file.
        """
        os.makedirs(os.path.dirname(os.path.abspath(self.history_file)), exist_ok=True)
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"[SearchHistoryManager] Error saving history: {e}")
