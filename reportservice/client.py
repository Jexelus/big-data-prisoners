import requests
from typing import List, Dict, Optional
from datetime import datetime
CRUD_SERVICE_URL = "http://crudservice:8000"

def get_all_prisoners() -> List[Dict]:
    response = requests.get(f"{CRUD_SERVICE_URL}/")
    if response.status_code == 200:
        return response.json()
    raise Exception("Failed to fetch readers from CRUD service")

def make_report():
    prisoners = get_all_prisoners()
    res = {}
    for prisoner in prisoners:
        res[str(prisoner["id"])] = {
            "name": prisoner["name"],
            "sentence_start": prisoner["sentence_start"],
            "sentence_end": prisoner["sentence_end"],
            "guard_name": prisoner["guard_name"],
            "is_free": True if datetime.now() > prisoner["sentence_end"] else False
        }
    return res

def get_report_data() -> Dict:
    return make_report()