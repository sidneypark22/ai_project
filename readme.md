Language model picks an agent to perform task asked by a user.

- Invoice proess agent:
  - Parse the invoice image file and extract required data
  - Update Google Sheet with the extract data
  - Usage:
    - cmd: python main.py --prompt "Process the invoice image file 'data/invoice_images/aaaaa_copy.jpg'"
    - output:

        Prompt: Process the invoice image file 'data/invoice_images/aaaaa_copy.jpg'

        Response: Okay, the invoice has been processed and the data has been updated in Google Sheet with the following details: 19/05/2024, Fuel, 81.45. The update was made to cells A7:C7 in the Expense sheet.

