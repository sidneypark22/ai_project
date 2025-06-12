from src.llm.agents.invoice_parser import InvoceParser
from src.llm.utils import OpenAIClientHelper
from src.utils.google_api_helper import GoogleSheetsAPI
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import argparse
load_dotenv()

def get_google_sheet_api_helper() -> GoogleSheetsAPI:
    google_sheet_api = GoogleSheetsAPI(spreadsheet_id=os.getenv("GOOGLE_EXPENSE_SPREADSHEET_ID"))
    google_sheet_api.authenticate_using_credentials_file(credentials_filename=os.getenv("GOOGLE_API_CREDENTIALS_FILE"))
    google_sheet_api.initiate_sheets_service()

    return google_sheet_api

def read_google_sheet(google_sheet_api: GoogleSheetsAPI, sheet_name: str, return_original_output: bool = False):
    return google_sheet_api.read_sheet_range(sheet_name=sheet_name, return_original_output=return_original_output)

def process_invoice(image_path: str) -> str:
    """Get the student information
    Args:
        image_path (str): Path to the invoice image file.
    Returns:
        None"""
    invoice_parser = InvoceParser(openai_client_helper, model)
    response = invoice_parser.parse_invoice(image_path)
    # print(response)

    google_sheet_api = get_google_sheet_api_helper()
    # print(f"Previuos sheet data: {read_google_sheet(google_sheet_api, "Expense")}")
    try:
        for il in response["invoice_lines"]:
            col_date = str(datetime.strftime(datetime.strptime(response["invoice_date"], "%Y-%m-%d"), "%d/%m/%Y"))
            col_expense_description = str(il["expense_category"])
            col_amount = str(il["invoice_amount_excluding_gst"])
            update_res = google_sheet_api.update_sheet(
                sheet_name="Expense",
                values=[[col_date, col_expense_description, col_amount]],
                number_of_cols=3,
                # row_num=len(sheet_data) + 1  # Append to the next row
            )
        # print(f"Updated sheet data: {read_google_sheet(google_sheet_api, "Expense")}")
        return update_res
    except Exception as e:
        print(f"Error updating Google Sheet: {e}")
        return f"Error updating Google Sheet: {e}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "process_invoice",
            "description": "Process an invoice image and update the Google Sheet with the parsed data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Path to the invoice image file."
                    }
                },
                "required": ["image_path"],
                "additionalProperties": False
            },
            "strict": True
        },
    }
]

def main(prompt: str):
    messages = [
        {
            "role": "system",
            "content": """You are a helpful assistant that helps the user with queries. 
If a tool was used to help answer the user query, you must include result from the tool call in your response.
If no tool was used, answer directly.""",
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    response = openai_client_helper.chat_completion_create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    response_message_1 = response.choices[0].message
    if dict(response_message_1).get('tool_calls') is None:
        return response_message_1.content
    else:
        # If the model has called a tool, we need to execute it
        tool_call = response.choices[0].message.tool_calls[0]
        func_name = tool_call.function.name
        kwargs = json.loads(tool_call.function.arguments)
        tool_call_result = globals()[func_name](**kwargs)

        messages.append(response_message_1)  # append model's function call message
        messages.append({                    # append result message
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(tool_call_result)
        })

        return openai_client_helper.chat_completion_create(
            model=model,
            messages=messages,
            tools=tools,
        ).choices[0].message.content

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--prompt", type=str, help="Prompt for the LLM.")
    prompt = argparser.parse_args().prompt

    model = "lmstudio-community/gemma-3-4b-it"
    openai_client_helper = OpenAIClientHelper(
        base_url=os.getenv("OPENAI_API_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
        llm_options={
            "temperature": 0.0,
            "top_p": 0.0,
        },
    )
    print(f"Prompt: {prompt}\n")
    print(f"Response: {main(prompt)}")

# python main.py --prompt "Process the invoice image file 'data/invoice_images/aaaaa_copy.jpg'"