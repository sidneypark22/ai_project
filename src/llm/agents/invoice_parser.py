import os
from dotenv import load_dotenv
import json
from src.llm.utils import OpenAIClientHelper
from src.utils.response_format_helper import InvoiceParserFormat
from pydantic import BaseModel
from src.utils.response_format_helper import ExpenseCateogoryFormat, InvoiceParserFormat
from src.llm.prompt_engineering.prompt_helper import InvoiceParserPrompts
from openai.types.chat.parsed_chat_completion import ParsedChatCompletion

class InvoceParser:
    def __init__(self, openai_client_helper: OpenAIClientHelper, model: str):
        self.openai_client_helper = openai_client_helper
        self.model = model
        self.expense_categories = [
            'Macbook',
            'Power',
            'Parking',
            'Water',
            'Fuel',
            'Rates',
            'Mortgage Interest',
            'Internet',
            'Vehicle Maintenance',
            'Rego',
            'Vehicle Repair',
            'Gas',
            'Home Maintenance',
            'Office',
            'Entertainment',
            'Depreciation',
            'IPad',
            'IPhone',
            'Transport',
            'Vehicle Purchase',
            'Mobile',
            'ACC',
            'Laptop',
        ]
    def parse_invoice(self, image_path: str) -> ParsedChatCompletion:
        response = self.openai_client_helper.chat_completion_parse(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": InvoiceParserPrompts.parser_system_prompt,
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Please parse the invoice and return the result in the provided response format."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{self.openai_client_helper.get_image_base64(image_path)}"
                            }
                        }
                    ]
                }
            ],
            response_format=InvoiceParserFormat
        )
        response_json = json.loads(response.choices[0].message.content)
        response_json["expense_category"] = self.categorise_expense(response_json["invoice_description"])
        return response_json
    
    def categorise_expense(self, expense_description: str) -> str:
        response = self.openai_client_helper.chat_completion_parse(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": InvoiceParserPrompts.categoriser_system_prompt.format(expense_categories="\n".join(self.expense_categories)),
                },
                {
                    "role": "user",
                    "content": f"Categorise the following expense description: {expense_description}"
                }
            ],
            response_format=ExpenseCateogoryFormat,
        ).choices[0].message.content
        return json.loads(response)["expense_category"]

