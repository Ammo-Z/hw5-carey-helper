import sys
import json
import os
from datetime import datetime

# Path handling for both local and agent execution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "references", "carey_calendar.json")

def analyze_calendar_date(query_date_str):
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            calendar = json.load(f)
    except FileNotFoundError:
        return {"error": "Calendar data file not found."}

    try:
        target_date = datetime.strptime(query_date_str, '%Y-%m-%d').date()
    except ValueError:
        return {"error": "Invalid date format. Please use YYYY-MM-DD."}

    # 1. Check Holidays
    for holiday in calendar['holidays']:
        if holiday['date'] == query_date_str:
            return {"type": "Holiday", "name": holiday['name'], "status": "Closed"}

    # 2. Check Academic Breaks
    for academic_break in calendar['breaks']:
        start = datetime.strptime(academic_break['start'], '%Y-%m-%d').date()
        end = datetime.strptime(academic_break['end'], '%Y-%m-%d').date()
        if start <= target_date <= end:
            return {"type": "Break", "name": academic_break['name'], "status": "No Classes"}

    # 3. Check Terms
    current_term = None
    for term in calendar['terms']:
        start = datetime.strptime(term['start'], '%Y-%m-%d').date()
        end = datetime.strptime(term['end'], '%Y-%m-%d').date()
        if start <= target_date <= end:
            current_term = term['name']
            break

    # 4. Calculate countdown to Graduation
    comm_date = datetime.strptime(calendar['milestones']['commencement'], '%Y-%m-%d').date()
    days_to_grad = (comm_date - target_date).days

    if current_term:
        return {
            "type": "Academic Day",
            "term": current_term,
            "countdown_to_graduation": f"{days_to_grad} days",
            "status": "In Session"
        }

    return {"type": "Off-cycle", "status": "No Academic Activity", "days_to_commencement": f"{days_to_grad} days"}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            args = json.loads(sys.argv[1])
            date_to_query = args.get("date")
            result = analyze_calendar_date(date_to_query)
            print(json.dumps(result))
        except Exception as e:
            print(json.dumps({"error": str(e)}))