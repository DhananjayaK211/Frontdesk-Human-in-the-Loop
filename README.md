# Frontdesk AI Human-in-the-Loop (HILT) Supervisor System

This project implements the foundational architecture for an AI receptionist that can intelligently escalate unknown customer questions to a human supervisor, learn from the resolution, and automatically follow up with the customer.

## 1. Project Goal

The system's core function is to ensure that when the AI encounters a **"knowledge gap,"** it initiates a Human-in-the-Loop workflow: **Escalate → Resolve → Learn → Follow Up.**

## 2.Setup and Installation

Follow these steps to get the system running locally:

### 3. Prerequisites

You must have **Python 3.8+** installed.

### 4. Virtual Environment
.\venv\Scripts\Activate.ps1
### Navigate to the project directory and create a virtual environment 

### 5. Install Dependencies 
pip install Flask livekit-agents

### 6.Run the Application
python -m venv venv