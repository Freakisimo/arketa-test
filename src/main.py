from .api_client import ApiClient
from .file_writer import FileWriter

import re
from datetime import datetime, timezone, timedelta

class UserProcessor:
    """Processes user data (Extract & Transform)."""
    def __init__(self, api_client, dependencies=None):
        self.api_client = api_client

    def parser_name(self, name, type):
        remove_chars = ['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.']
        for char in remove_chars:
            name = name.replace(char, '').strip()
        if type == 'first':
            if ',' in name:
                return name.split(',')[0]
            elif ' ' in name:
                return name.split(' ')[0]
            else:
                return 'Unknown'
        elif type == 'last':
            if ',' in name:
                return ' '.join(name.split(',')[1:])
            elif ' ' in name:
                return ' '.join(name.split(' ')[1:])
            else:
                return 'User'

    def validate_email(self, email):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_regex, email):
            return email.lower()
        return None

    def validate_phone(self, phone):
        main_number_part = phone.split(' ')[0]
        digits = re.sub(r'\D', '', main_number_part)
        if len(digits) == 10:
            return f"+1{digits}"
        elif len(digits) == 11 and digits.startswith('1'):
            return f"+{digits}"
        return None

    def parser_address(self, address):
        street = address.get('street', '')
        suite = address.get('suite', '')
        city = address.get('city', '')
        zipcode = address.get('zipcode', '')
        if not any([street, suite, city, zipcode]):
            return None
        return f"{street}, {suite}, {city}, {zipcode}"

    def get_company(self, company):
        company_name = company.get('name', '')
        return company_name if company_name else None

    def process(self):
        print("Processing users...")
        users = self.api_client.get_data("users") or []
        users.sort(key=lambda u: u.get('id', float('inf')))
        accepted = []
        rejected = []

        seen_emails = set()
        seen_phones = set()
        seen_names = set()

        # For this processor, all data is considered "accepted"
        # invalid_email , duplicate_merged , unrecoverable_parse
        for user in users:
            now = datetime.now(timezone.utc)
            data = {
                "externalId": user.get('id', None),
                "name": user.get('name', ''),
                "firstName": self.parser_name(user.get('name', ''), 'first'),
                "lastName": self.parser_name(user.get('name', ''), 'last'),
                "email": self.validate_email(user.get('email', '')),
                "phoneE164": self.validate_phone(user.get('phone', '')),
                "address": self.parser_address(user.get('address', {})),
                "company": self.get_company(user.get('company', {})),
                "createdAt": now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            }
            if data["email"] is None:
                data["reason"] = "invalid_email"
                rejected.append(data)
            elif data["email"] in seen_emails:
                data["reason"] = "duplicate_merged"
                rejected.append(data)
            elif data["phoneE164"] in seen_phones:
                data["reason"] = "duplicate_merged"
                rejected.append(data)
            elif (data["firstName"], data["lastName"]) in seen_names:
                data["reason"] = "duplicate_merged"
                rejected.append(data)
            else:
                del data["name"]
                accepted.append(data)
                seen_emails.add(data["email"])
                if data["phoneE164"]:
                    seen_phones.add(data["phoneE164"])
                seen_names.add((data["firstName"], data["lastName"]))
        print(f"Accepted: {len(accepted)}, Rejected: {len(rejected)}")
        return {"accepted": accepted, "rejected": rejected}

class TodoProcessor:
    """Validates and processes 'todos' (Extract & Transform)."""
    def __init__(self, api_client, dependencies):
        self.api_client = api_client
        self.dependencies = dependencies

    def process(self):
        print("Processing and validating 'todos'...")
        
        user_data = self.dependencies.get('users_result')
        if not user_data:
            print("Error: User data not available. Cannot process todos.")
            todos = self.api_client.get_data("todos") or []
            return {"accepted": [], "rejected": todos}

        valid_user_ids = {user['externalId'] for user in user_data}
        todos = self.api_client.get_data("todos") or []
        
        accepted_todos = []
        rejected_todos = []
        
        for todo in todos:
            id = todo.get('id', None)
            user_id = todo.get('userId', None)
            now = datetime.now(timezone.utc) + timedelta(minutes=id)
            data = {
                "externalId": id,
                "clientExternalId": user_id,
                "type": "todo",
                "title": todo.get('title', ''),
                "status": "completed" if todo.get('completed', False) else "open",
                "occurredAt": now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            }
            if user_id in valid_user_ids:
                accepted_todos.append(data)
            else:
                data["reason"] = "orphan_user"
                rejected_todos.append(data)
        
        print(f"Accepted: {len(accepted_todos)}, Rejected: {len(rejected_todos)}")
        return {"accepted": accepted_todos, "rejected": rejected_todos}

def run_processing_pipeline(api_client):
    """ETL - Extract & Transform Stage."""
    data_registry = {}
    pipeline_steps = [
        {"name": "users_result", "processor": UserProcessor, "deps": {}},
        {"name": "todos_result", "processor": TodoProcessor, "deps": {"users_result": "users_result"}}
    ]

    print("--- Starting ETL (Extract & Transform) ---")
    for step in pipeline_steps:
        name = step["name"]
        ProcessorClass = step["processor"]
        deps_mapping = step["deps"]
        
        dependencies = {
            local_name: data_registry[registry_key]["accepted"]
            for local_name, registry_key in deps_mapping.items()
        }

        processor_instance = ProcessorClass(api_client, dependencies)
        result = processor_instance.process()
        data_registry[name] = result
        print(f"--- Finished E/T for: {name} ---")
    
    print("--- E/T Stage Finished ---\n")
    return data_registry

def save_pipeline_results(data_registry, file_writer):
    """ETL - Load Stage."""
    print("--- Starting ETL (Load) ---")
    
    # --- CUSTOMIZE YOUR LOAD LOGIC HERE ---
    
    # Example: Load 'todos' results
    todos_results = data_registry.get("todos_result")
    if todos_results:
        print("Loading 'todos' data...")
        if todos_results.get("accepted"):
            file_writer.write_to_json(todos_results["accepted"], "todos_accepted")

        if todos_results.get("rejected"):
            header_map_todos = {
                "source_todo_id": "externalId",
                "Motivo": "reason",
                "source_user_id": "clientExternalId",
                "title": "title",
            }
            file_writer.write_to_csv(todos_results["rejected"], "todos_rejected", header_map=header_map_todos)

    # Example: Load 'users' results
    users_results = data_registry.get("users_result")
    if users_results:
        print("Loading 'users' data...")
        if users_results.get("accepted"):
            file_writer.write_to_json(users_results["accepted"], "users_accepted")

        if users_results.get("rejected"):
            header_map_users = {
                "source_user_id": "externalId",
                "reason": "reason",
                "email": "email",
                "phone": "phoneE164",
                "name": "name",
                "address": "address",
            }
            file_writer.write_to_csv(users_results["rejected"], "users_rejected", header_map=header_map_users)

    # --- END OF CUSTOMIZABLE LOAD LOGIC ---
    
    print("--- Load Stage Finished ---")

def main():
    """Orchestrates the ETL process."""
    file_writer = FileWriter()
    api_client = ApiClient("https://jsonplaceholder.typicode.com")

    # 1. Extract & Transform
    final_results = run_processing_pipeline(api_client)

    # 2. Load
    save_pipeline_results(final_results, file_writer)
