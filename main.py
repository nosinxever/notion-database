import os
from pprint import pprint

from notion_client import Client
from notion_client.helpers import get_id


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

    # Add the new entry to the database
    # database_id = new_db["id"]  # Get the ID of the newly created database
    # database_id = "d79c306dd89b4c5aa130eb8c8f6ea933"

  
#    Finding the Page ID
    # entries = query_database_entries(database_id)
    # for entry in entries:
    #     print(entry)

    page_id = "90fef77a0e2e48b59a4b3d0fac9e118a"  # The extracted page ID
    page_content = retrieve_page_content(page_id)
    # print(page_content)

    page_content='hello world'

    add_text_block_to_page(page_id,page_content)


