import requests
import json
import pika
import os
import schedule
import time
import logging
from logging.handlers import RotatingFileHandler


# Configure logging
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs", "log.txt")

# Create a rotating file handler for logging
file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=1)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)

# Add the file handler to the root logger
logging.root.addHandler(file_handler)
logging.root.setLevel(logging.DEBUG)


# Get the directory path of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
keys_dir = os.path.join(current_dir, "keys")
config_file_path = os.path.join(keys_dir, "config.json")

# Load secret tokens from config file
with open(config_file_path, "r") as config_file:
    secret_tokens = json.load(config_file)

# Define RabbitMQ connection parameters
RABBITMQ_USERNAME = 'guest'
RABBITMQ_PASSWORD = 'guest'
RABBITMQ_HOST = 'localhost'  # RabbitMQ server host
RABBITMQ_PORT = 5672  # Default RabbitMQ port

# Define RabbitMQ exchange name
EXCHANGE_NAME = 'e_Conomic_API'

# Define RabbitMQ exchange and queue details
QUEUES = [
    'in.accounting-years',
    'in.invoices',
    'in.invoices.drafts',
    'in.totals.booked',
    'in.booked.paid',
    'in.booked.unpaid'
]

# Define dictionary mapping queue names to their respective API endpoint URLs
queue_api_mapping = {
    'in.accounting-years': "https://restapi.e-conomic.com/accounting-years",
    'in.invoices': "https://restapi.e-conomic.com/invoices",
    'in.invoices.drafts': "https://restapi.e-conomic.com/invoices/drafts",
    'in.totals.booked': "https://restapi.e-conomic.com/invoices/booked",
    'in.booked.paid': "https://restapi.e-conomic.com/invoices/paid",
    'in.booked.unpaid': "https://restapi.e-conomic.com/invoices/unpaid"
}

def send_to_queue(queue_name, data):
    try:
        logging.debug(f"Connecting to RabbitMQ server to send data to queue: {queue_name}")
        # Connect to RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)))
        channel = connection.channel()

        # Declare the queue
        channel.queue_declare(queue=queue_name, durable=True)

        # Publish the message to the queue
        channel.basic_publish(exchange='', routing_key=queue_name, body=data, properties=pika.BasicProperties(delivery_mode=2))

        logging.info(f"Sent data to queue {queue_name}: {data}")

        # Close the connection
        connection.close()
    except Exception as e:
        logging.error(f"Error sending data to queue {queue_name}: {e}")

def fetch_and_send_to_queue(queue_name, api_url):
    try:
        logging.debug(f"Fetching data from API endpoint: {api_url}")
        headers = {
            "Content-Type": "application/json",
            "X-AppSecretToken": secret_tokens["X-AppSecretToken"],
            "X-AgreementGrantToken": secret_tokens["X-AgreementGrantToken"]
        }
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            logging.debug(f"Data fetched successfully from API endpoint: {api_url}")
            send_to_queue(queue_name, json.dumps(data))
        else:
            logging.error(f"Failed to fetch data from {api_url}. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error fetching data from {api_url}: {e}")

# Define periodic task to fetch data from the API and send to queues
def periodic_task():
    logging.debug("Starting periodic task to fetch data from API endpoints and send to queues...")
    for queue_name in QUEUES:
        # Get the API endpoint URL from the mapping
        api_url = queue_api_mapping.get(queue_name)
        if api_url:
            logging.debug(f"Processing queue: {queue_name}")
            fetch_and_send_to_queue(queue_name, api_url)
    logging.debug("Periodic task completed.")

# Schedule the periodic task to run every 5 minutes
schedule.every(5).minutes.do(periodic_task)

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)  # Sleep for 1 second to avoid high CPU usage
