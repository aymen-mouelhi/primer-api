import json
import os
import hashlib
import braintree
import bcrypt
import logging
import boto3
from base64 import b64decode
import utils.validator as validator
from models.credit_card import CreditCard

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get Stored Encrypted Environment variables
MERCHANT_ID_ENCRYPTED = os.environ["MERCHANT_ID"]
PUBLIC_KEY_ENCRYPTED = os.environ["PUBLIC_KEY"]
PRIVATE_KEY_ENCRYPTED = os.environ["PRIVATE_KEY"]

# Decrypt using master key
MERCHANT_ID = boto3.client('kms').decrypt(CiphertextBlob=b64decode(MERCHANT_ID_ENCRYPTED))['Plaintext'].decode('utf-8')
PUBLIC_KEY = boto3.client('kms').decrypt(CiphertextBlob=b64decode(PUBLIC_KEY_ENCRYPTED))['Plaintext'].decode('utf-8')
PRIVATE_KEY = boto3.client('kms').decrypt(CiphertextBlob=b64decode(PRIVATE_KEY_ENCRYPTED))['Plaintext'].decode('utf-8')

# Init BrainTree API
gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id=MERCHANT_ID,
        public_key=PUBLIC_KEY,
        private_key=PRIVATE_KEY
    )
)


def tokenise(event, context):
    """Tokenise Provided Credit Card and stores the token in BrainTree Vault

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format: Contains number and expiration date

    context: object, required
        Lambda Context runtime methods and attributes

    Returns
    ------
    Response: dict
        Response:
            Contains the created token or an error message
    """

    try:

        payload = json.loads(event["body"])

        if "number" not in payload or "expiration_date" not in payload:
            return {
                "statusCode": 400,
                "headers": {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                "body": json.dumps({
                    "error": "Credit Card information not complete"
                })
            }

        number = payload["number"]
        expiration_date = payload["expiration_date"]
        unique = 0

        logger.info("Tokenise request for {}".format(number[:4]))

        # Extract month and year from expiration_date
        month, year = validator.extract_month_year(expiration_date)

        card = CreditCard(
            number=number,
            month=month,
            year=year
        )

        if not card.is_valid:
            logger.info("Tokenise failed for {}".format(number[:4]))
            return {
                "statusCode": 400,
                "headers": {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                "body": json.dumps({
                    "error": "Invalid Credit Card"
                })
            }

        # Check if we need to have a unique usage of the token or not
        if "unique" in payload:
            unique = payload["unique"]

        logger.info("unique {}".format(unique))

        h = hashlib.sha256()
        if unique == 1:
            # Generate a random Salt
            salt = bcrypt.gensalt()
            h.update(salt + number.encode())
        else:
            h.update(number.encode())

        # Max size accepted by BrainTree = 36
        token = h.hexdigest()[:35]

        logger.info("Token created successfully for {}".format(number[:4]))

        # Store Token in BrainTree Vault for future Transactions
        result = gateway.customer.create({
            "credit_card": {
                "number": number,
                "expiration_date": expiration_date,
                "token": token
            }
        })

        # Check result
        if result.is_success:
            logger.info("Customer created successfully in BrainTree for CC {}".format(number[:4]))
            return {
                "statusCode": 200,
                "headers": {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                "body": json.dumps({
                    "token": token
                })
            }
        else:
            for error in result.errors.deep_errors:
                print(error.attribute)
                print(error.code)
                print(error.message)

            logger.error("Customer couldn't be created due to {}".format(error.message))
            return {
                "statusCode": 401,
                "headers": {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                "body": json.dumps({
                    "error": error.message
                })
            }

    except Exception as e:
        logger.error("An exception occurred while creating customer: {}".format(e))
        return {
            "statusCode": 500,
            "headers": {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            "body": json.dumps({
                "error": str(e)
            })
        }


def sale(event, context):
    """
    Submits a BrainTree Sale Request using the given token
    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        It should contain:
        token: The stored tokenized credit card number
        amount: The amount of the transaction

    context: object, required
        Lambda Context runtime methods and attributes

    Returns
    ------
    transaction: dict
        Response:
            Contains the transaction object if succeeded or an error message
    """
    try:
        payload = json.loads(event["body"])

        if "token" not in payload or "amount" not in payload:
            logger.error("token or amount")
            return {
                "statusCode": 400,
                "headers": {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                "body": json.dumps({
                    "error": "Incomplete transaction information"
                })
            }

        token = payload["token"]
        amount = payload["amount"]

        if not validator.validate_amount(amount):
            logger.error("invalid amount provided")
            return {
                "statusCode": 400,
                "headers": {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                "body": json.dumps({
                    "error": "Bad Amount"
                })
            }
        result = gateway.transaction.sale({
            "amount": amount,
            "payment_method_token": token,
            "options": {
                "submit_for_settlement": True
            }
        })

        if result.is_success:
            return {
                "statusCode": 200,
                "headers": {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                "body": json.dumps({
                    "id": result.transaction.id,
                    "amount": amount,
                    "merchant_account_id": "23jd8ur5",
                    "plan_id": "",
                    "recurring": False,
                    "refund": {},
                    "status": "authorized",
                    "transaction_source": "api",
                    "created_at": result.transaction.created_at.strftime("%d/%m/%Y, %H:%M:%S")
                })
            }
        else:
            for error in result.errors.deep_errors:
                print(error.attribute)
                print(error.code)
                print(error.message)

            logger.error("Transaction couldn't be submitted due to {}".format(error.message))
            return {
                "statusCode": 401,
                "headers": {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                "body": json.dumps({
                    "error": error.message,
                })
            }
    except Exception as e:
        logger.error("An exception occurred while handling Transaction: {}".format(e))
        return {
            "statusCode": 500,
            "headers": {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            "body": json.dumps({
                "error": e
            })
        }
