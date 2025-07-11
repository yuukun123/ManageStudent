def filter_students_by_keyword(students, keyword: str):
    keyword = keyword.strip().lower()
    if not keyword:
        return students
    return [
        s for s in students if keyword in str(s.get("student_id", "")).lower()
        or keyword in str(s.get("full_name", "")).lower()
        or keyword in str(s.get("email", "")).lower()
        or keyword in str(s.get("phone_number", "")).lower()
    ]

def sort_students_by_name(students, order: str):
    return sorted(students, key=lambda x: x.get("full_name", "").lower(), reverse=(order == "sort Z - A"))
