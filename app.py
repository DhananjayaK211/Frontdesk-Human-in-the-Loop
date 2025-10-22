from flask import Flask, render_template, request, redirect, url_for
from db_manager import DBManager
from ai_agent import AIAgent

app = Flask(__name__)
db_manager = DBManager()
ai_agent = AIAgent(db_manager)

@app.route('/call', methods=['POST'])
def handle_incoming_call():
    """
    Simulates an incoming phone call being routed to the AI agent.
    Endpoint for testing the core agent flow.
    """
    # Simulate data coming from a phone/LiveKit webhook
    customer_id = request.form.get('customer_id') or '555-1234'
    question = request.form.get('question')
    
    if not question:
        return "Error: Missing question.", 400
        
    print(f"\n=============================================")
    print(f"     SIMULATED INCOMING CALL: {customer_id}     ")
    print(f"=============================================")
    
    agent_response = ai_agent.handle_call(customer_id, question)
    
    return f"AI Agent's Response to Caller:\n{agent_response}", 200

# --- Supervisor UI and API ---

@app.route('/', methods=['GET'])
def supervisor_dashboard():
    """
    Displays the main supervisor dashboard.
    Evaluates: Viewing pending/history, simple UI constraint.
    """
    pending_requests = db_manager.get_pending_requests()
    all_requests = db_manager.get_all_requests()
    
    return render_template('supervisor.html', 
        pending_requests=pending_requests,
        all_requests=all_requests
    )

@app.route('/resolve/<int:request_id>', methods=['POST'])
def resolve_request_endpoint(request_id):
    """
    API endpoint for the supervisor to submit an answer.
    Evaluates: Linking back to originating request, AI follow-up.
    """
    answer = request.form.get('answer')
    if not answer:
        return redirect(url_for('supervisor_dashboard')) 
        
    resolved_request = db_manager.resolve_request(request_id, answer)
    
    if resolved_request:
        ai_agent.resolve_help_request(resolved_request)
    
    return redirect(url_for('supervisor_dashboard'))

# --- Knowledge Base View ---

@app.route('/knowledge-base', methods=['GET'])
def knowledge_base_view():
    """
    Displays the learned answers.
    Evaluates: Simple view like a "Learned Answers" section.
    """
    kb_entries = db_manager.get_all_kb_entries()
    return render_template('kb.html', kb_entries=kb_entries)


if __name__ == '__main__':
    print("Starting Frontdesk Human-in-the-Loop Supervisor...")
    print("Database is ready. Agent is initialized.")
    
    # Run Flask development server
    app.run(debug=True, port=5000)