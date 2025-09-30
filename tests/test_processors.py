
import unittest
from src.main import UserProcessor, TodoProcessor

# -- Test Double (Mock) to simulate the ApiClient --
class MockApiClient:
    """A test double for ApiClient that returns predefined data."""
    def __init__(self, data_map):
        self._data_map = data_map

    def get_data(self, endpoint):
        return self._data_map.get(endpoint, [])

# --- Test Suite ---

class TestUserProcessor(unittest.TestCase):
    """Tests the UserProcessor logic with realistic mock data."""

    def test_user_transformation_and_email_validation(self):
        """
        Tests that users are transformed to the new schema and that
        users with invalid emails are rejected, using realistic data.
        """
        mock_users = [
            {
                "id": 1, "name": "Leanne Graham", "username": "Bret", "email": "sincere@april.biz",
                "address": {"street": "Kulas Light", "suite": "Apt. 556", "city": "Gwenborough", "zipcode": "92998-3874", "geo": {"lat": "-37.3159", "lng": "81.1496"}},
                "phone": "1-770-736-8031 x56442", "website": "hildegard.org",
                "company": {"name": "Romaguera-Crona", "catchPhrase": "Multi-layered client-server neural-net", "bs": "harness real-time e-markets"}
            },
            {
                "id": 2, "name": "Ervin Howell", "username": "Antonette", "email": "invalid-email",
                "address": {"street": "Victor Plains", "suite": "Suite 879", "city": "Wisokyburgh", "zipcode": "90566-7771", "geo": {"lat": "-43.9509", "lng": "-34.4618"}},
                "phone": "010-692-6593 x09125", "website": "anastasia.net",
                "company": {"name": "Deckow-Crist", "catchPhrase": "Proactive didactic contingency", "bs": "synergize scalable supply-chains"}
            }
        ]
        mock_api_client = MockApiClient({"users": mock_users})
        user_processor = UserProcessor(mock_api_client)
        
        result = user_processor.process()
        accepted = result["accepted"]
        rejected = result["rejected"]

        # Assertions
        self.assertEqual(len(accepted), 1, "Should be 1 accepted user.")
        self.assertEqual(len(rejected), 1, "Should be 1 rejected user for invalid email.")
        
        self.assertEqual(rejected[0]["externalId"], 2)
        self.assertEqual(rejected[0]["reason"], "invalid_email")

        accepted_user = accepted[0]
        self.assertEqual(accepted_user["externalId"], 1)
        self.assertEqual(accepted_user["firstName"], "Leanne")
        self.assertEqual(accepted_user["address"], "Kulas Light, Apt. 556, Gwenborough, 92998-3874")

    def test_deduplication_logic_with_realistic_data(self):
        """
        Tests the deduplication logic with realistic data.
        NOTE: This test reflects the current bug where new identifiers are not
        added to the 'seen' sets, resulting in no deduplication.
        """
        mock_users = [
            {
                "id": 1, "name": "Jane Doe", "username": "jane.d", "email": "jane.doe@example.com",
                "address": {"street": "Main St", "suite": "Apt 1", "city": "Anytown", "zipcode": "12345", "geo": {"lat": "0", "lng": "0"}},
                "phone": "1-555-123-4567", "website": "jane.com", "company": {"name": "Doe Inc.", "catchPhrase": "...", "bs": "..."}
            },
            {
                "id": 3, "name": "Jane Doe", "username": "jane.d.clone", "email": "jane.doe@example.com",
                "address": {"street": "Second St", "suite": "Apt 2", "city": "Othertown", "zipcode": "54321", "geo": {"lat": "1", "lng": "1"}},
                "phone": "1-555-111-2222", "website": "janeclone.com", "company": {"name": "Clone Corp", "catchPhrase": "...", "bs": "..."}
            }
        ]
        mock_api_client = MockApiClient({"users": mock_users})
        user_processor = UserProcessor(mock_api_client)
        
        result = user_processor.process()
        accepted = result["accepted"]

        self.assertEqual(len(accepted), 2, "BUG: Deduplication is not working; both users are accepted.")


class TestTodoProcessor(unittest.TestCase):
    """Tests for the TodoProcessor logic and its dependency."""

    def test_reject_todos_with_orphan_user(self):
        """
        Tests that 'todos' are rejected if their 'userId' does not
        correspond to an accepted user's 'externalId'.
        """
        accepted_users_dependency = [
            {"externalId": 1, "firstName": "User", "lastName": "One"},
        ]
        
        mock_todos = [
            {"userId": 1, "id": 101, "title": "A valid todo", "completed": True},
            {"userId": 99, "id": 103, "title": "An orphan todo", "completed": False},
        ]
        
        mock_api_client = MockApiClient({"todos": mock_todos})
        dependencies = {"users_result": accepted_users_dependency}
        
        todo_processor = TodoProcessor(mock_api_client, dependencies)
        
        result = todo_processor.process()
        accepted = result["accepted"]
        rejected = result["rejected"]

        self.assertEqual(len(accepted), 1, "Should be 1 accepted 'todo'.")
        self.assertEqual(len(rejected), 1, "Should be 1 rejected 'todo'.")
        self.assertEqual(rejected[0]['id'], 103)


if __name__ == '__main__':
    unittest.main()
