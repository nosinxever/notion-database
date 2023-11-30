
from notion_client import Client
from notion_client.helpers import get_id

NOTION_TOKEN = "secret_CcumlCK9hiUuJW9Bb7tivCUeb1GaRa9XBHwDS5pqTnz"  # replace yours


notion = Client(auth=NOTION_TOKEN)

users = notion.users.list()

for user in users.get("results"):
    name, user_type = user["name"], user["type"]
    emoji = "😅" if user["type"] == "bot" else "🙋‍♂️"
    print(f"{name} is a {user_type} {emoji}")



def manual_inputs(parent_id="", db_name="") -> tuple:
    """
    Get values from user input
    """
    if parent_id == "":
        is_page_ok = False
        while not is_page_ok:
            input_text = input("\nEnter the parent page ID or URL: ").strip()
            # Checking if the page exists
            try:
                if input_text[:4] == "http":
                    parent_id = get_id(input_text)
                    print(f"\nThe ID of the target page is: {parent_id}")
                else:
                    parent_id = input_text
                notion.pages.retrieve(parent_id)
                is_page_ok = True
                print("Page found")
            except Exception as e:
                print(e)
                continue
    while db_name == "":
        db_name = input("\n\nName of the database that you want to create: ")

    return (parent_id, db_name)


def create_database(parent_id: str, db_name: str) -> dict:
    """
    parent_id(str): ID of the parent page
    db_name(str): Title of the database
    """
    print(f"\n\nCreate database '{db_name}' in page {parent_id}...")
    properties = {
        "Name": {"title": {}},  # This is a required property
        "Description": {"rich_text": {}},
        "In stock": {"checkbox": {}},
        "Food group": {
            "select": {
                "options": [
                    {"name": "🥦 Vegetable", "color": "green"},
                    {"name": "🍎 Fruit", "color": "red"},
                    {"name": "💪 Protein", "color": "yellow"},
                ]
            }
        },
        "Price": {"number": {"format": "dollar"}},
        "Last ordered": {"date": {}},
        "Store availability": {
            "type": "multi_select",
            "multi_select": {
                "options": [
                    {"name": "Duc Loi Market", "color": "blue"},
                    {"name": "Rainbow Grocery", "color": "gray"},
                    {"name": "Nijiya Market", "color": "purple"},
                    {"name": "Gus's Community Market", "color": "yellow"},
                ]
            },
        },
        "+1": {"people": {}},
        "Photo": {"files": {}},
    }
    title = [{"type": "text", "text": {"content": db_name}}]
    icon = {"type": "emoji", "emoji": "🎉"}
    parent = {"type": "page_id", "page_id": parent_id}
    return notion.databases.create(
        parent=parent, title=title, properties=properties, icon=icon
    )




def create_database_entry(database_id: str, entry_data: dict) -> dict:
    """
    Add a new entry to a Notion database.

    :param database_id: The ID of the database where the entry will be added.
    :param entry_data: A dictionary containing the data for the new entry.
    :return: The response from the Notion API.
    """
    new_entry = notion.pages.create(
        parent={"database_id": database_id},
        properties=entry_data
    )
    return new_entry


def update_database_entry(page_id: str, updated_data: dict) -> dict:
    """
    Update an entry in a Notion database.

    :param page_id: The ID of the database entry (page) to update.
    :param updated_data: A dictionary containing the updated data.
    :return: The updated entry.
    """
    updated_entry = notion.pages.update(
        page_id=page_id,
        properties=updated_data
    )
    return updated_entry

def query_database_entries(database_id: str, filter: dict = None) -> list:
    """
    Query entries in a Notion database.

    :param database_id: The ID of the database to query.
    :param filter: A dictionary specifying the filter criteria.
    :return: A list of database entries.
    """
    query_data = {"database_id": database_id}
    if filter:
        query_data["filter"] = filter
    
    response = notion.databases.query(**query_data)
    return response.get("results", [])




if __name__ == "__main__":
    # Create a new database
    # parent_id, db_name = manual_inputs()
    # new_db = create_database(parent_id=parent_id, db_name=db_name)
    # print(f"\n\nDatabase {db_name} created at {new_db['url']}\n")

    # Define the data for the new entry
    entry_data = {
        "Name": {
            "title": [
                {"text": {"content": "Sample Item4"}}
            ]
        },
        "Description": {
            "rich_text": [
                {"text": {"content": "This is a sample description.26"}}
            ]
        },
        "In stock": {
            "checkbox": True
        },
        "Food group": {
            "select": {
                "name": "🥦 Vegetable36"
            }
        },
        "Price": {
            "number": 9
        },
        # "Last ordered" and "Store availability" are omitted for simplicity
        # Include them as needed based on your database structure
    }

    # Add the new entry to the database
    # database_id = new_db["id"]  # Get the ID of the newly created database
    database_id = "9de8bdde58144a1390616d4066c8d51f"

    new_entry = create_database_entry(database_id, entry_data)
    print("New entry added:", new_entry)


    #Finding the Page ID
    entries = query_database_entries(database_id)
    for entry in entries:
        print(f"Entry Name: {entry['properties']['Name']['title'][0]['text']['content']}, Page ID: {entry['id']}")


    # Updating an Entry
    page_id_to_update = "33ce3a46-4528-45d4-88aa-20a4f93f8712"  # Replace with the actual page ID of the entry you want to update

    updated_data = {
        "Name": {
            "title": [
                {"text": {"content": "Updated Item Name"}}
            ]
        },
        "Description": {
            "rich_text": [
                {"text": {"content": "Updated description."}}
            ]
        },
        # Include other properties to update as needed
    }

    updated_entry = update_database_entry(page_id_to_update, updated_data)
    print("Updated entry:", updated_entry)
