from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .agents import conversation_agent, validate_answer, analyze_personality, save_personality_analysis, PERSONALITY_QUESTIONS
from .models import ChatConversation, PersonalityTraits
import json
from datetime import datetime

# Store conversation state in memory (consider Redis for production)
user_conversation_state = {}

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def chat_api(request):
    user_message = request.data.get('message', '').strip()
    
    if not user_message:
        return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Initialize or retrieve user session state
    user_id = request.user.id
    if user_id not in user_conversation_state:
        user_conversation_state[user_id] = {
            'current_question_index': 0,
            'current_question': None,
            'waiting_for_complete_answer': False,
            'conversation_history': []
        }
    
    state = user_conversation_state[user_id]
    
    # Process with conversation agent
    try:
        # Set session state with user info
        conversation_agent.session_state = {'user_id': user_id}
        
        # Prepare the input for the agent
        context = f"Conversation history: {json.dumps(state['conversation_history'][-5:])}\n" if state['conversation_history'] else ""
        
        if state['waiting_for_complete_answer'] and state['current_question']:
            # We're waiting for a complete answer to the current question
            context += f"Current question: {state['current_question']}\n"
        
        agent_input = f"{context}User: {user_message}"
        
        response = conversation_agent.run(
            input=agent_input,
            session_id=f"user_{user_id}"
        )
        
        # Extract the structured response
        if hasattr(response, 'content') and response.content and hasattr(response.content, 'response'):
            agent_response = response.content.response
            is_question = response.content.is_question
            current_topic = response.content.current_topic
        else:
            agent_response = str(response.content) if response.content else "I'm not sure how to respond to that."
            is_question = '?' in agent_response
            current_topic = None
        
        # Store conversation in database
        ChatConversation.objects.create(
            user=request.user,
            user_message=user_message,
            agent_message=agent_response,
            is_complete_answer=False
        )
        
        # Update conversation history
        state['conversation_history'].append({
            'user': user_message,
            'agent': agent_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # If we have a current question, validate the user's answer
        analysis_triggered = False
        if state['waiting_for_complete_answer'] and state['current_question']:
            validation = validate_answer(state['current_question'], user_message)
            
            if validation.is_answer_complete:
                # Analyze the complete answer
                analysis = analyze_personality(state['current_question'], user_message)
                
                # Save personality analysis with question and full answer
                save_personality_analysis(
                    user_id=user_id,
                    question=state['current_question'],
                    full_answer=user_message,
                    analysis_result=analysis
                )
                
                analysis_triggered = True
                # Move to next question
                state['current_question_index'] += 1
                state['waiting_for_complete_answer'] = False
                state['current_question'] = None
                
                # Update the agent response to indicate completion
                agent_response = f"Thank you for your detailed answer! {agent_response}"
            else:
                # Ask follow-up question if validation suggests one
                if validation.follow_up_question:
                    agent_response = f"{agent_response}\n\n**Follow-up:** {validation.follow_up_question}"
        
        # Check if the agent is asking a new main question
        if is_question and not state['waiting_for_complete_answer']:
            if state['current_question_index'] < len(PERSONALITY_QUESTIONS):
                state['current_question'] = PERSONALITY_QUESTIONS[state['current_question_index']]
                state['waiting_for_complete_answer'] = True
            else:
                # All questions completed
                agent_response = "Thank you for completing the personality assessment! I have enough information now."
        
        return Response({
            'response': agent_response,
            'analysis_triggered': analysis_triggered,
            'progress': f"{state['current_question_index']}/{len(PERSONALITY_QUESTIONS)}"
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def conversation_history(request):
    conversations = ChatConversation.objects.filter(user=request.user)
    data = [{
        'id': c.id,
        'user_message': c.user_message,
        'agent_message': c.agent_message,
        'timestamp': c.timestamp,
        'is_complete': c.is_complete_answer
    } for c in conversations]
    return Response(data)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def analysis_results(request):
    analyses = PersonalityTraits.objects.filter(user=request.user)
    data = [{
        'id': a.id,
        'question': a.question,
        'full_answer': a.full_answer,
        'positive_traits': a.positive,
        'negative_traits': a.negative,
        'quote': a.quote,
        'analyzed_at': a.analyzed_at
    } for a in analyses]
    return Response(data)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def conversation_state(request):
    user_id = request.user.id
    if user_id in user_conversation_state:
        state = user_conversation_state[user_id]
        return Response({
            'current_question_index': state['current_question_index'],
            'total_questions': len(PERSONALITY_QUESTIONS),
            'current_question': state['current_question'],
            'waiting_for_complete_answer': state['waiting_for_complete_answer']
        })
    else:
        return Response({
            'current_question_index': 0,
            'total_questions': len(PERSONALITY_QUESTIONS),
            'current_question': None,
            'waiting_for_complete_answer': False
        })