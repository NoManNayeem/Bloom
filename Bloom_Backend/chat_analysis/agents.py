# agents.py
import os
from typing import Dict, Optional, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(override=False)
except ImportError:
    pass

# Ensure OpenAI API key is available
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set in environment variables")

# Agno imports
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.tools import tool
from django.conf import settings

# Configure persistent storage
storage_path = os.path.join(settings.BASE_DIR, 'agno_storage.db')
storage = SqliteAgentStorage(table_name="chat_analysis_sessions", db_file=storage_path)

# Pydantic models for structured output
class PersonalityTraitsModel(BaseModel):
    positive: Dict[str, int] = Field(..., description="Positive personality traits with values from 0 to 100")
    negative: Dict[str, int] = Field(..., description="Negative personality traits with values from 0 to 100")
    quote: str = Field(..., description="A motivational or descriptive quote based on the analysis")

class ValidationResult(BaseModel):
    is_answer_complete: bool = Field(..., description="True if the answer is complete and sufficient for analysis")
    follow_up_question: Optional[str] = Field(None, description="Next question to ask if answer is incomplete")

class ConversationResponse(BaseModel):
    response: str = Field(..., description="The agent's response to the user")
    is_question: bool = Field(..., description="Whether the response is a question")
    current_topic: Optional[str] = Field(None, description="The current topic being discussed")

# Database tool for saving ALL conversations
@tool
def save_conversation_tool(user_id: int, user_message: str, agent_message: str, is_complete: bool = False) -> int:
    """
    Save a conversation to the database.
    """
    from .models import ChatConversation
    from django.contrib.auth.models import User
    
    user = User.objects.get(id=user_id)
    chat = ChatConversation.objects.create(
        user=user,
        user_message=user_message,
        agent_message=agent_message,
        is_complete_answer=is_complete
    )
    return chat.id

# Function to save analysis results
def save_personality_analysis(user_id: int, question: str, full_answer: str, analysis_result: PersonalityTraitsModel):
    """
    Save personality analysis results to the database.
    """
    from .models import PersonalityTraits
    from django.contrib.auth.models import User
    
    user = User.objects.get(id=user_id)
    PersonalityTraits.objects.create(
        user=user,
        question=question,
        full_answer=full_answer,
        positive=analysis_result.positive,
        negative=analysis_result.negative,
        quote=analysis_result.quote
    )

# Personality questions to ask
PERSONALITY_QUESTIONS = [
    "What are your greatest strengths and how have they helped you in your life?",
    "Can you describe a challenging situation you faced and how you handled it?",
    "What are your most important values and how do they guide your decisions?",
    "How do you typically handle stress or pressure?",
    "What kind of activities or environments make you feel most energized?",
]

# Primary Conversation Agent
conversation_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    storage=storage,
    tools=[save_conversation_tool],
    response_model=ConversationResponse,
    instructions="""
    You are a personality assessment interviewer conducting a continuous conversation.
    
    YOUR ROLE:
    1. Ask engaging questions about lifestyle, experiences, preferences, and personality
    2. Request follow-up questions when answers are incomplete or vague
    3. Determine when you have sufficient information for personality analysis
    4. Save ALL conversations using the save_conversation_tool
    5. Maintain natural conversation flow while gathering deep insights
    6. Always ask one question at a time
    7. Be empathetic and encouraging to get detailed responses
    8. Format your responses in markdown with questions in **bold** and emphasize key parts of responses
    
    CONVERSATION FLOW:
    - Start with an introduction and explain you're conducting a personality assessment
    - Ask open-ended questions that require detailed answers
    - If an answer is too short (< 50 words) or vague, ask follow-up questions
    - Only move to the next main question when the current one is fully answered
    - Use the save_conversation_tool with is_complete=True when an answer is complete
    
    STRUCTURED OUTPUT:
    - response: Your markdown-formatted response
    - is_question: Whether your response is a question
    - current_topic: The current topic being discussed
    
    IMPORTANT: You must maintain context of the entire conversation and remember what has been discussed.
    Always use the save_conversation_tool after each exchange to store both your question and the user's response.
    """,
    show_tool_calls=True,
    markdown=True
)

# Validation Agent (to check if answers are complete)
validation_agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    response_model=ValidationResult,
    instructions="""
    Analyze if a user's answer to a question is complete enough for personality analysis.
    
    CRITERIA FOR COMPLETE ANSWER:
    - At least 50 words or 200 characters
    - Contains specific details, examples, or explanations
    - Not vague, generic, or avoiding the question
    - Addresses the core of what was asked
    
    If incomplete, provide a concise follow-up question to elicit more information.
    Output ONLY the structured response with no additional text.
    """
)

# Personality Analysis Agent
analysis_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    response_model=PersonalityTraitsModel,
    instructions="""
    Analyze complete question-answer pairs to identify personality traits.
    
    RETURN FORMAT:
    - positive: Dictionary of 3-5 positive traits with scores (0-100)
    - negative: Dictionary of 3-5 negative traits with scores (0-100)
    - quote: A motivational or insightful quote (max 140 characters)
    
    GUIDELINES:
    - Identify key positive and negative traits based on the response
    - Base scores on the depth and consistency of the response
    - Ensure quotes are relevant to the personality insights
    - Be objective and avoid stereotyping
    - Output ONLY the structured response with no additional text
    """
)

# Helper functions
def validate_answer(question: str, answer: str) -> ValidationResult:
    """Validate if an answer is complete enough for analysis"""
    prompt = f"""
    Question: {question}
    Answer: {answer}
    
    Is this answer complete enough for personality analysis? If not, what follow-up question should be asked?
    """
    
    response: RunResponse = validation_agent.run(prompt)
    if isinstance(response.content, ValidationResult):
        return response.content
    return ValidationResult(is_answer_complete=False, follow_up_question="Could you tell me more about that?")

def analyze_personality(question: str, answer: str) -> PersonalityTraitsModel:
    """Analyze a complete Q&A pair for personality traits"""
    prompt = f"""
    Question: {question}
    Answer: {answer}
    
    Analyze this complete question-answer pair for personality traits.
    """
    
    response: RunResponse = analysis_agent.run(prompt)
    if isinstance(response.content, PersonalityTraitsModel):
        return response.content
    # Fallback if structured output fails
    return PersonalityTraitsModel(
        positive={"Openness": 50},
        negative={"Neuroticism": 50},
        quote="Self-awareness is the first step toward growth."
    )