from pydantic import BaseModel, Field

class InvoiceLineFormat(BaseModel):
    invoice_item_description: str = Field(
        description="Description of the invoice item, e.g., 'Fuel for vehicle'."
    )
    invoice_amount_including_gst: float = Field(
        description="Total amount of the invoice item including GST."
    )
    invoice_amount_gst: float = Field(
        description="GST amount for the invoice item."
    )
    invoice_amount_excluding_gst: float = Field(
        description="Total amount of the invoice item excluding GST."
    )

class InvoiceParserFormat(BaseModel):
    invoice_lines: list[InvoiceLineFormat]
    invoice_date: str = Field(
        description="The date of the invoice in YYYY-MM-DD format."
    )

class ExpenseCateogoryFormat(BaseModel):
    expense_category: str = Field(
        description="The category of the expense, e.g., 'Fuel', 'Power', etc."
    )