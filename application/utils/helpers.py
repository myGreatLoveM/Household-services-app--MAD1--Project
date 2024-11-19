from uuid import uuid4

def generate_uuid():
    return str(uuid4())


def clean_arg(arg: str) -> str:
    return arg.strip().lower()


def paginate(list, page=1, per_page=6):
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    total_pages = (len(list) + per_page - 1) // per_page
    total_items = len(list)
    return (list[start_idx:end_idx], total_items, total_pages, start_idx, end_idx)
