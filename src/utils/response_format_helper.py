from pydantic import BaseModel, Field

class InvoiceParserFormat(BaseModel):
    invoice_date: str = Field(
        description="The date of the invoice in YYYY-MM-DD format."
    )
    invoice_description: str = Field(
        description="Description of the invoice items, e.g., 'Fuel for vehicle'."
    )
    invoice_amount_total: float = Field(
        description="Total amount of the invoice item including GST."
    )
    invoice_amount_gst: float = Field(
        description="GST tax amount for the invoice item. This is calculated as invoice_amount_total - (invoice_amount_total / 1.15)."
    )
    invoice_amount_excluding_gst: float = Field(
        description="Amount of the invoice item excluding GST tax. If invoice amount excluding GST is not available, it should be the same as (invoice_amount_total - invoice_amount_gst)."
    )

class ExpenseCateogoryFormat(BaseModel):
    expense_category: str = Field(
        description="The category of the expense, e.g., 'Fuel', 'Power', etc."
    )