import pika

# RabbitMQ connection parameters
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_USERNAME = 'guest'
RABBITMQ_PASSWORD = 'guest'

# Exchange name
EXCHANGE_NAME = 'e_Conomic_API'

# Queues to be created
QUEUES = [
    'in.accounting-years',
    'in.invoices',
    'in.invoices.drafts',
    'in.totals.booked',
    'in.booked.paid',
    'in.booked.unpaid'
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
        # Declare the queue
        channel.queue_declare(queue=queue_name)

        # Bind the queue to the exchange
        channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key=queue_name)

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

        print("Setup complete: Exchange and Queues created.")
    finally:
        # Close the connection
        connection.close()

if __name__ == "__main__":
    main()
