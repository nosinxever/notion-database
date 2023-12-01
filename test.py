import os
from pprint import pprint

from notion_client import Client

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    print("Could not load .env because python-dotenv not found.")
else:
    load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")

while NOTION_TOKEN == "":
    print("NOTION_TOKEN not found.")
    NOTION_TOKEN = input("Enter your integration token: ").strip()




from notion_client import Client
from notion_client.helpers import get_id


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
    Create a Notion database with a specific structure.

    :param parent_id: ID of the parent page.
    :param db_name: Title of the database.
    :return: The response from the Notion API.
    """
    print(f"Creating database '{db_name}' in page {parent_id}...")

    properties = {
        "password": {"rich_text": {}},
        "icon": {"rich_text": {}},
        "date": {"date": {}},
        "type": {
            "select": {
                "options": [
                    {"name": "Post", "color": "yellow"},
                    {"name": "Page", "color": "yellow"},
                    {"name": "Notice", "color": "yellow"},
                    {"name": "Menu", "color": "yellow"},
                    {"name": "SubMenu", "color": "yellow"},
                    {"name": "CONFIG", "color": "yellow"},
                    # Add more options as needed
                ]
            }
        },
        "category": {"select": {}},
        "slug": {"rich_text": {}},
        "tags": {"multi_select": {}},
        "summary": {"rich_text": {}},
        "title": {"title": {}},  # Title is a required property
        "status": {
            "select": {
                "options": [
                    {"name": "Invisible", "color": "orange"},
                    {"name": "Published", "color": "orange"},
                    {"name": "Draft", "color": "orange"},
                    # Add more options as needed
                ]
            }
        },
        # Add other properties as needed
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



def retrieve_page_content(page_id: str):
    """
    Retrieve the content of a Notion page using its page ID.

    :param page_id: The ID of the page to retrieve.
    :return: The content of the page as a list of strings.
    """
    content = []
    block_children = notion.blocks.children.list(block_id=page_id)

    # print(block_children)

    for block in block_children.get("results", []):
        block_type = block.get("type")
        block_content = block.get(block_type, {})
        # print(block_content)

        if block_type == "paragraph":
            text = ''.join([text.get("plain_text", "") for text in block_content.get("rich_text", [])])
            content.append(text)

        elif block_type in ["heading_1", "heading_2"]:
            heading_text = ''.join([text.get("plain_text", "") for text in block_content.get("rich_text", [])])
            heading_level = "##" if block_type == "heading_1" else "###"
            content.append(f"{heading_level} {heading_text}")

        elif block_type == "quote":
            quote_text = ''.join([text.get("plain_text", "") for text in block_content.get("rich_text", [])])
            content.append(f"> {quote_text}")

        elif block_type == "bulleted_list_item":
            bullets = ''.join([text.get("plain_text", "") for text in block_content.get("rich_text", [])])
            content.append(f"- {bullets}")

        elif block_type == "callout":
            callout_text = ''.join([text.get("plain_text", "") for text in block_content.get("rich_text", [])])
            emoji = block_content.get("icon", {}).get("emoji", "")
            content.append(f"{emoji} {callout_text}")

        # Additional block types can be added here
    return content


def add_text_block_to_page(page_id: str, text_content: str):
    """
    Add a new text block to a Notion page.

    :param page_id: The ID of the page to update.
    :param text_content: The text content to add to the page.
    """
    new_block = {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": text_content
                    }
                }
            ]
        }
    }
    notion.blocks.children.append(block_id=page_id, children=[new_block])


if __name__ == "__main__":
    import random

    def create_fake_data(index):
        """
        Create fake data for a database entry.

        :param index: Index number for the entry.
        :return: A dictionary representing a fake entry.
        """
        types = ["Post", "Page", "Notice", "Menu", "SubMenu", "CONFIG"]
        statuses = ["Invisible", "Published", "Draft"]

        return {
            "title": {"title": [{"text": {"content": f"Fake Entry {index}"}}]},
            "password": {"rich_text": [{"text": {"content": "password123"}}]},
            "icon": {"rich_text": [{"text": {"content": ""}}]},
            "date": {"date": {"start": "2023-01-01"}},
            "type": {"select": {"name": random.choice(types)}},
            "category": {"select": {"name": "Category A"}},
            "slug": {"rich_text": [{"text": {"content": f"/fake-entry-{index}"}}]},
            "tags": {"multi_select": [{"name": "Tag1"}, {"name": "Tag2"}]},
            "summary": {"rich_text": [{"text": {"content": f"Summary for fake entry {index}"}}]},
            "status": {"select": {"name": random.choice(statuses)}},
        }

    database_id = "6c75572b171f4993845f3a2f005f50a1"  # Replace with the ID of the database

    # Add 10 fake entries
    for i in range(1, 11):
        entry_data = create_fake_data(i)
        new_entry = create_database_entry(database_id, entry_data)
        print(f"Entry {i} added: {new_entry['url']}")



    # create_database('77774fc85384416695cae74a3e20018c','mbm')

    # Add the new entry to the database
    # database_id = new_db["id"]  # Get the ID of the newly created database
    # database_id = "d79c306dd89b4c5aa130eb8c8f6ea933"

  
#    Finding the Page ID
    # entries = query_database_entries(database_id)
    # for entry in entries:
    #     print(entry)



