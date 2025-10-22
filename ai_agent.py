from db_manager import DBManager
from simulations import simulate_supervisor_text, simulate_customer_callback
from typing import Dict 

class AIAgent:
    """
    Simulated AI agent logic for call handling, knowledge base lookup, 
    and human-in-the-loop escalation.
    """
    
    # Evaluates: Building good prompts
    SYSTEM_PROMPT = (
        "You are an AI receptionist for 'Frontdesk Salon'. "
        "Your goal is to be helpful and professional. "
        "Your business information is: "
        "Hours: Mon-Fri 9AM-7PM, Sat 10AM-5PM. "
        "Services: Haircuts ($50+), Coloring ($120+), Manicures ($30). "
        "Booking: Appointments are required, call 555-555-5555. "
        "If you **do not know** the answer, you must trigger a 'request help' event."
    )
    
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager
        print(f"AIAgent initialized. System Prompt:\n---\n{self.SYSTEM_PROMPT}\n---")

    def handle_call(self, customer_id: str, question: str) -> str:
        """
        Simulates receiving a call and determining the response path.
        Evaluates: Respond if it knows the answer or trigger "request help"
        """
        print(f"\n[AGENT] Incoming call from {customer_id}. Question: '{question}'")
        
        # 1. Attempt lookup in the Learned Knowledge Base (high-priority)
        kb_answer = self.db_manager.get_kb_answer(question)
        if kb_answer:
            print("[AGENT] Found answer in Learned KB.")
            return f"Hello! Based on our updated information, the answer is: {kb_answer}"

        # 2. Attempt to 'answer' with internal system prompt knowledge (EXPANDED HEURISTIC)
        question_lower = question.lower()
        
        # Check for Hours
        if any(keyword in question_lower for keyword in ['hours', 'open', 'close']):
            print("[AGENT] Responding with hardcoded prompt knowledge (Hours).")
            hours_info = "Mon-Fri 9AM-7PM and Sat 10AM-5PM."
            return f"We are open {hours_info}"
        
        # Check for Services/Pricing
        if any(keyword in question_lower for keyword in ['service', 'price', 'cost', 'haircut', 'manicure', 'coloring']):
            print("[AGENT] Responding with hardcoded prompt knowledge (Services/Pricing).")
            services_info = "We offer Haircuts ($50+), Coloring ($120+), and Manicures ($30)."
            return f"Our main services are: {services_info}"

        # Check for Booking/Appointments
        if any(keyword in question_lower for keyword in ['book', 'appointment', 'schedule']):
            print("[AGENT] Responding with hardcoded prompt knowledge (Booking).")
            booking_info = "Appointments are required. Please call us at 555-555-5555 to book."
            return f"{booking_info}"
            
        # 3. If AI doesn't know (no return yet), escalate
        return self._trigger_help_request(customer_id, question)

    def _trigger_help_request(self, customer_id: str, question: str) -> str:
        """
        Handles the escalation flow.
        Evaluates: Telling the caller, creating request, simulating text to supervisor.
        """
        print("[AGENT] 🚨 Knowledge gap detected. Escalating to supervisor.")
        
        # Create pending help request
        request_id = self.db_manager.create_request(customer_id, question)
        print(f"[AGENT] Created PENDING request ID: {request_id}")
        
        # Simulate texting the supervisor
        simulate_supervisor_text(question, request_id)
        
        # Return response to caller
        return "I apologize, that is not in my current knowledge base. Let me check with my supervisor and get back to you immediately via text message."

    def resolve_help_request(self, resolved_request: Dict):
        """
        Handles the post-supervisor resolution flow.
        Evaluates: AI follow up and knowledge base update.
        """
        request_id = resolved_request['id']
        customer_id = resolved_request['customer_id']
        question = resolved_request['caller_question']
        answer = resolved_request['supervisor_answer']
        
        print(f"\n[AGENT] 🎉 Receiving resolution for request ID: {request_id}")
        
        # 1. AI should update its internal knowledge base
        self.db_manager.save_learned_answer(question, answer, request_id)
        print("[AGENT] Knowledge base updated successfully.")
        
        # 2. AI should immediately text back the original caller
        simulate_customer_callback(customer_id, answer)
        
        print(f"[AGENT] Resolution complete for request ID: {request_id}.")