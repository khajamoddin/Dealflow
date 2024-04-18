import os
import logging
from logging.handlers import RotatingFileHandler
import pika
import json
import sqlite3

# Configure logging
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs", "worker_log.txt")

# Create a rotating file handler for logging
file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=1)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)

# Add the file handler to the root logger
logging.root.addHandler(file_handler)
logging.root.setLevel(logging.DEBUG)

# Define SQLite database connection
DB_FILE = 'data.db'

def consume_and_store(queue_name, message):
    try:
        # Parse the JSON message
        data = json.loads(message)

        # Connect to SQLite database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Store the data in the database
        # Example: Insert data into a table named 'messages'
        cursor.execute("INSERT INTO messages (queue_name, data) VALUES (?, ?)", (queue_name, json.dumps(data)))
        conn.commit()

        # Close the database connection
        conn.close()

        logging.info(f"Stored data from queue {queue_name} in the database")
    except Exception as e:
        logging.error(f"Error storing data from queue {queue_name} in the database: {e}")

def process_message(channel, method, properties, body):
    try:
        queue_name = method.routing_key
        message = body.decode('utf-8')
        
        logging.info(f"Received message from queue {queue_name}: {message}")
        consume_and_store(queue_name, message)

        # Acknowledge the message
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logging.error(f"Error processing message from queue {queue_name}: {e}")

def consume_queue(queue_name):
    try:
        # Connect to RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        # Declare the queue
        channel.queue_declare(queue=queue_name, durable=True)

        # Start consuming messages from the queue
        channel.basic_consume(queue=queue_name, on_message_callback=process_message)

        logging.info(f"Consuming messages from queue {queue_name}...")

        # Keep consuming messages until KeyboardInterrupt
        channel.start_consuming()
    except KeyboardInterrupt:
        logging.info("Stopped consuming messages.")
    except Exception as e:
        logging.error(f"Error consuming messages from queue {queue_name}: {e}")

if __name__ == '__main__':
    # Define the queues you want to consume messages from
    queues = ['in.accounting-years', 'in.invoices', 'in.invoices.drafts', 'in.totals.booked', 'in.booked.paid', 'in.booked.unpaid']

    # Start consuming messages from each queue
    for queue_name in queues:
        consume_queue(queue_name)
