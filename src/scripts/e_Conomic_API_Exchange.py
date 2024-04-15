import pika

# RabbitMQ connection parameters
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_USERNAME = 'guest'
RABBITMQ_PASSWORD = 'guest'

# Exchange and queue names  (Messages comming into Integration Platfrom starts with in. and outgaoing message queues starts with out.)
EXCHANGE_NAME = 'e_Conomic_API_Accounting_Years_Exchange'
QUEUES = [
    'in.accounting-years',
    'out.accounting-years',
    'in.accountingYear',
    'in.accountingYear.entries',
    'in.accountingYear.totals',
    'in.accountingYear.periods',
    'in.accountingYear.periods',
    'in.periods.accountingYearPeriod',
    'in.accountingYearPeriod.entries',
    'in.accountingYearPeriod.totals'
]

EXCHANGE_NAME = 'e_Conomic_API_Accounts_Exchange'
QUEUES = [
    'in.accounts',
    'in.accountNumber',
    'in.accountingYear',
    'in.accountNumber.accounting-years',
    'in.accounting-years.accountingYear',
    'in.accountingYear.entries',
    'in.accountingYear.totals',
    'in.accountingYear.periods',
    'in.periods.accountingYearPeriod',
    'in.accountingYearPeriod.entries',
    'in.accountingYearPeriod.totals'
]


EXCHANGE_NAME = 'e_Conomic_API_Currencies_Exchange'
QUEUES = [
    'in.currencies',
    'in.currencies.code'
]


EXCHANGE_NAME = 'e_Conomic_API_Customer_Groups_Exchange'
QUEUES = [
    'in.customer-groups',
    'in.customer-groups.customerGroupNumber',
    'in.customerGroupNumber.customers',
    'out.customer-groups',
    'out.customer-groups.customerGroupNumber'
]

EXCHANGE_NAME = 'e_Conomic_API_Customers_Exchange'
QUEUES = [
    'in.customers',
    'in.customers.customerNumber',
    'in.customerNumber.totals',
    'out.customers',
    'out.customers.customerNumber',
    'in.customerNumber.templates',
    'in.templates.invoice',
    'in.templates.invoiceline',
    'in.invoiceline.productNumber',
    'in.customerNumber.contacts',
    'in.contacts.contactNumber',
    'out.customerNumber.contacts',
    'out.contacts.contactNumber',
    'in.delivery-locations.deliveryLocationNumber',
    'out.customerNumber.delivery-locations',
    'out.delivery-locations.deliveryLocationNumber',
    'in.customerNumber.invoices',
    'in.invoices.drafts',
    'in.invoices.booked'
]

EXCHANGE_NAME = 'e_Conomic_API_Invoices_Exchange'
QUEUES = [
    'in.invoices',
    'in.invoices.drafts',
    'in.drafts.draftInvoiceNumber',
    'in.draftInvoiceNumber.pdf',
    'out.invoices.drafts',
    'out.drafts.draftInvoiceNumber',
    'out.draftInvoiceNumber.lines',
    'out.invoices.booked',
    'out.booked.bookWithNumber',
    'in.invoices.booked',
    'in.booked.bookedInvoiceNumber',
    'in.bookedInvoiceNumber.pdf',
    'in.draftInvoiceNumber.templates',
    'in.templates.booking-instructions',
    'in.invoices.totals',
    'in.totals.drafts',
    'in.drafts.customers',
    'in.customers.customerNumber',
    'in.accounting-years.accountingYear',
    'in.periods.accountingPeriod',
    'in.totals.booked',
    'in.booked.paid',
    'in.booked.unpaid',
    'in.unpaid.overdue',
    'in.unpaid.not-overdue',
    'in.invoices.paid',
    'in.invoices.unpaid',
    'in.invoices.overdue',
    'in.invoices.not-due',
    'in.invoices.sent',
    'in.sent.id',
    'in.draftInvoiceNumber.attachment',
    'in.attachment.file',
    'out.attachment.file'
]


def create_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(RABBITMQ_HOST, RABBITMQ_PORT, '/', credentials)
    return pika.BlockingConnection(parameters)

def create_channel(connection):
    return connection.channel()

def create_exchange(channel):
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='direct')

def create_queues(channel):
    for queue_name in QUEUES:
        # Declare the original queue
        channel.queue_declare(queue=queue_name)

        # Bind the original queue to the exchange
        channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key=queue_name)

        # Declare and bind the copy queue
        copy_queue_name = queue_name + '_copy'
        channel.queue_declare(queue=copy_queue_name)
        channel.queue_bind(exchange=EXCHANGE_NAME, queue=copy_queue_name, routing_key=queue_name)

def main():
    # Connect to RabbitMQ
    connection = create_connection()

    try:
        # Create a channel
        channel = create_channel(connection)

        # Create the exchange
        create_exchange(channel)

        # Create queues and bind them to the exchange
        create_queues(channel)

        print("Setup complete: Channels, Exchange, and Queues created.")
    finally:
        # Close the connection
        connection.close()

if __name__ == "__main__":
    main()
