import asyncio
import os
import re
from datetime import datetime
from typing import AsyncGenerator

from google.adk.agents import BaseAgent, LlmAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types

# --- Configuration ---
MODEL_NAME = 'gemini-2.0-flash-lite'

# --- Step 1: Helper Agents ---

# 1. Classifier
# UPDATED: Added 'GREETING' category so it doesn't force "Hello" into "Civil".
classifier_agent = LlmAgent(
    name="Classifier",
    model=MODEL_NAME,
    instruction="""
    You are a legal intake clerk. 
    Classify the following user query into exactly one of these categories:
    
    User Query: "{current_query}"

    Categories:
    - GREETING (Hi, Hello, Good Morning, Namaste, general pleasantries)
    - CONSTITUTION (Fundamental rights, government power, citizenship)
    - CRIMINAL (Theft, assault, cheating, criminal breach, BNS issues)
    - CIVIL (Property disputes, land boundaries, contracts, divorce, family law, torts)
    - TRAFFIC (Challans, driving licenses, road accidents, Motor Vehicles Act)
    
    Output ONLY the category word (e.g., CIVIL). Do not add punctuation.
    """,
    output_key="law_category" 
)

# --- Step 2: The Expert Agents ---

constitution_agent = LlmAgent(
    name="Constitution_agent",
    model=MODEL_NAME,
    description="Analysis of the Constitution of India.",
    instruction="You are an expert lawyer in the Constitution of India. Analyze the user's problem and cite relevant Articles."
)

bns_agent = LlmAgent(
    name="BNS_agent",
    model=MODEL_NAME,
    description="Analysis of the Bharatiya Nyaya Sanhita (BNS).",
    instruction="You are an expert in the Bharatiya Nyaya Sanhita (BNS). Analyze the user's problem and cite relevant BNS Sections."
)

civil_agent = LlmAgent(
    name="Civil_agent",
    model=MODEL_NAME,
    description="Analysis of Civil Law (CPC, Contracts, Family Law).",
    instruction="You are an expert in Indian Civil Law (Code of Civil Procedure, Contract Act, Family Courts). Analyze the user's problem and suggest legal remedies or relevant sections."
)

traffic_agent = LlmAgent(
    name="Traffic_agent",
    model=MODEL_NAME,
    description="Analysis of Traffic Rules (Motor Vehicles Act).",
    instruction="You are an expert in Indian Traffic Laws (Motor Vehicles Act). Analyze the user's problem regarding challans, accidents, or licenses and cite relevant rules and fines."
)

# --- Step 3: The Custom Orchestrator ---

class IndianLawBot(BaseAgent):
    def __init__(self, name="IndianLawBot"):
        super().__init__(
            name=name,
            sub_agents=[classifier_agent, constitution_agent, bns_agent, civil_agent, traffic_agent]
        )

    def get_sub_agent(self, name):
        for agent in self.sub_agents:
            if agent.name == name:
                return agent
        return None

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        classifier = self.get_sub_agent("Classifier")
        
        # 1. CAPTURE USER QUERY
        last_user_msg = None
        if ctx.session.events:
            for event in reversed(ctx.session.events):
                if event.author == "user":
                    if event.content and event.content.parts:
                        last_user_msg = event.content.parts[0].text
                    break
        
        if not last_user_msg:
            # If no message, we can just yield a default welcome
            yield Event(author="system", content=types.Content(parts=[types.Part(text="Namaste! I am the Indian Law Bot. How can I help you?")]))
            return

        print(f"[DEBUG] User Query Extracted: {last_user_msg[:50]}...")

        # 2. DYNAMIC INSTRUCTION INJECTION
        original_instruction = classifier.instruction
        classifier.instruction = f"""
        You are a legal intake clerk. 
        Classify the following User Query into exactly one of these categories:
        
        User Query: "{last_user_msg}"

        Categories:
        - GREETING
        - CONSTITUTION
        - CRIMINAL
        - CIVIL
        - TRAFFIC
        
        Output ONLY the category word.
        """

        # 3. RUN CLASSIFIER & MANUALLY CAPTURE OUTPUT
        classifier_response_text = ""
        
        print("[DEBUG] Running Classifier...")
        async for event in classifier.run_async(ctx):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        classifier_response_text += part.text
        
        classifier.instruction = original_instruction

        # 4. PROCESS RESULT
        raw_output = classifier_response_text.strip().upper()
        print(f"[DEBUG] Manual Capture: '{raw_output}'")
        
        # UPDATED REGEX to include GREETING
        match = re.search(r"\b(GREETING|CONSTITUTION|CRIMINAL|CIVIL|TRAFFIC)\b", raw_output, re.IGNORECASE)
        
        category = ""
        if match:
            category = match.group(1).upper()
        
        print(f"[DEBUG] Resolved Category: {category}")

        # 5. ROUTING LOGIC (Updated)
        
        if category == "GREETING":
            # Handle Greeting Directly (Do NOT send to an expert agent)
            yield Event(
                author="system",
                content=types.Content(parts=[types.Part(text="Namaste! I am here to help with Indian Legal issues. You can ask me about Constitution, Criminal cases, Civil disputes, or Traffic rules.")])
            )
        
        elif category == "CONSTITUTION":
            target_agent = self.get_sub_agent("Constitution_agent")
            print(f"[DEBUG] Routing to Constitution_agent")
            async for event in target_agent.run_async(ctx):
                yield event

        elif category == "CRIMINAL":
            target_agent = self.get_sub_agent("BNS_agent")
            print(f"[DEBUG] Routing to BNS_agent")
            async for event in target_agent.run_async(ctx):
                yield event

        elif category == "CIVIL":
            target_agent = self.get_sub_agent("Civil_agent")
            print(f"[DEBUG] Routing to Civil_agent")
            async for event in target_agent.run_async(ctx):
                yield event

        elif category == "TRAFFIC":
            target_agent = self.get_sub_agent("Traffic_agent")
            print(f"[DEBUG] Routing to Traffic_agent")
            async for event in target_agent.run_async(ctx):
                yield event

        else:
            yield Event(
                author="system",
                content=types.Content(parts=[types.Part(text=f"I'm having trouble classifying that (Detected: '{raw_output}'). I can help with Constitutional, Criminal, Civil, or Traffic law.")])
            )


# --- Step 4: Expose Root Agent for ADK ---
root_agent = IndianLawBot()