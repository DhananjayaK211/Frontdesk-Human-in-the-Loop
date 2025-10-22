import time
from typing import Dict

def simulate_supervisor_text(question: str, request_id: int):
    """
    Mocks texting the human supervisor with a help request.
    In production, this would be a webhook call or API request to a messaging service.
    """
    print("--- SIMULATION: TEXT TO SUPERVISOR ---")
    print(f"[{time.strftime('%H:%M:%S')}] PENDING REQUEST #{request_id}")
    print(f"Content: 'Hey, I need help answering: \"{question}\". Request ID: {request_id}. Please use the admin panel.'")
    print("------------------------------------------")

def simulate_customer_callback(customer_id: str, answer: str):
    """
    Mocks texting the original customer with the resolved answer.
    This fulfills the requirement: AI should immediately text back the original caller.
    """
    print("--- SIMULATION: TEXT TO CUSTOMER ---")
    print(f"[{time.strftime('%H:%M:%S')}] CUSTOMER ID: {customer_id}")
    print(f"Content: 'Hi! I checked with my supervisor. The answer is: \"{answer}\" Have a great day!'")
    print("---------------------------------------")
