
Setup Instructions:

Clone the Git repository and ensure Docker is installed on your system.
Open PowerShell or CMD and execute the following command to start RabbitMQ container with management plugin:

docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.13-management

Navigate to the project folder and run the provided script to create queues. For example:

(venv) PS C:\code\code\Dealflow\src\scripts> python .\minimal_e_Conomic_API.py

Create a developer account and obtain sandbox access with test data to access the REST API. Refer to the following link for detailed instructions: e-conomic REST API Documentation (Please consult VISMA documentation for further guidance).
Create a folder named "keys" under the project directory. For example: Dealflow\src\workers, and within this folder, create a configuration file named "config.json" containing the credentials received from the e-conomic API. Save the file with the following format:

{
    "X-AppSecretToken": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "X-AgreementGrantToken": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}

In the Dealflow\src\workers\ directory, execute the "scheduler.py" script to initiate the process of fetching data from the API and publishing it to RabbitMQ queues.
Similarly, in the Dealflow\src\workers\ directory, execute the "consumer.py" script to consume messages from the queues and store them into the local SQL database.
