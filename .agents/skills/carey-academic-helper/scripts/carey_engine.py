import sys
import json
import os
from datetime import datetime

# Path handling for local and agent execution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "references", "carey_calendar.json")

def analyze_calendar_date(query_date_str=None):
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            calendar = json.load(f)
    except FileNotFoundError:
        return {"error": "Calendar data file not found."}

    # Real-time Logic: Default to system current date if "now" or None
    if query_date_str is None or query_date_str.lower() == "now":
        target_date = datetime.now().date()
        is_real_time = True
    else:
        try:
            target_date = datetime.strptime(query_date_str, '%Y-%m-%d').date()
            is_real_time = False
        except ValueError:
            return {"error": "Invalid date format. Please use YYYY-MM-DD."}

    result = {"queried_date": str(target_date)}

    # 1. Check Holidays
    for holiday in calendar['holidays']:
        if holiday['date'] == str(target_date):
            result.update({"type": "Holiday", "name": holiday['name'], "status": "Closed"})
            return result

    # 2. Check Breaks
    for academic_break in calendar['breaks']:
        start = datetime.strptime(academic_break['start'], '%Y-%m-%d').date()
        end = datetime.strptime(academic_break['end'], '%Y-%m-%d').date()
        if start <= target_date <= end:
            result.update({"type": "Break", "name": academic_break['name'], "status": "No Classes"})
            return result

    # 3. Check Terms & Countdown
    current_term = None
    for term in calendar['terms']:
        start = datetime.strptime(term['start'], '%Y-%m-%d').date()
        end = datetime.strptime(term['end'], '%Y-%m-%d').date()
        if start <= target_date <= end:
            current_term = term
            break

    comm_date = datetime.strptime(calendar['milestones']['commencement'], '%Y-%m-%d').date()
    days_to_grad = (comm_date - target_date).days

    if current_term:
        term_end = datetime.strptime(current_term['end'], '%Y-%m-%d').date()
        days_left_in_term = (term_end - target_date).days
        
        status_msg = "In Session"
        # Alert logic for students: finals week approaching
        if is_real_time and 0 <= days_left_in_term <= 7:
            status_msg = "Finals Week approaching / End of Term"

        result.update({
            "type": "Academic Day",
            "term": current_term['name'],
            "days_remaining_in_term": f"{days_left_in_term} days",
            "countdown_to_graduation": f"{days_to_grad} days",
            "status": status_msg
        })
    else:
        result.update({
            "type": "Off-cycle",
            "status": "No Academic Activity",
            "days_to_graduation": f"{days_to_grad} days"
        })

    return result

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            args = json.loads(sys.argv[1])
            date_to_query = args.get("date")
            print(json.dumps(analyze_calendar_date(date_to_query)))
        except Exception as e:
            print(json.dumps({"error": str(e)}))
    else:
        # Support direct execution for quick "now" status
        print(json.dumps(analyze_calendar_date("now")))
        