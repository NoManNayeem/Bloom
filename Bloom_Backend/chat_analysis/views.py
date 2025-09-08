from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .agents import conversation_agent, validate_answer, analyze_personality, save_personality_analysis
from .models import ChatConversation, PersonalityTraits
import json

# Store current questions in memory (for demo purposes; consider Redis for production)
user_current_questions = {}

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def chat_api(request):
    user_message = request.data.get('message', '').strip()
    
    if not user_message:
        return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Initialize or retrieve user session
    session_id = f"user_{request.user.id}"
    
    # Get the current question for this user from memory
    current_question = user_current_questions.get(request.user.id)
    
    # Process with conversation agent
    try:
        # Set session state with user info
        conversation_agent.session_state = {'user_id': request.user.id}
        
        # Prepare the input for the agent
        agent_input = f"User: {user_message}"
        if current_question:
            agent_input = f"Current question: {current_question}\nUser response: {user_message}"
        
        response = conversation_agent.run(
            input=agent_input,
            session_id=session_id
        )
        
        # Extract the agent's response
        agent_response = str(response.content) if response.content else "I'm not sure how to respond to that."
        
        # Store conversation in database
        ChatConversation.objects.create(
            user=request.user,
            user_message=user_message,
            agent_message=agent_response,
            is_complete_answer=False  # Set appropriately based on your logic
        )


        # Check if the agent is asking a new question and store it
        if (agent_response.endswith('?') or '?' in agent_response) and not current_question:
            # This is a simple heuristic to detect questions
            user_current_questions[request.user.id] = agent_response
        
        # If we have a current question, validate the user's answer
        analysis_triggered = False
        if current_question:
            validation = validate_answer(current_question, user_message)
            
            if validation.is_answer_complete:
                # Analyze the complete answer
                analysis = analyze_personality(current_question, user_message)
                
                # Save personality analysis with question and full answer
                save_personality_analysis(
                    user_id=request.user.id,
                    question=current_question,
                    full_answer=user_message,
                    analysis_result=analysis
                )
                
                analysis_triggered = True
                # Clear the current question
                user_current_questions.pop(request.user.id, None)
                # Update the agent response to indicate completion
                agent_response = "Thank you for your detailed answer! " + agent_response
            else:
                # Ask follow-up question if validation suggests one
                if validation.follow_up_question:
                    agent_response = validation.follow_up_question
        
        return Response({
            'response': agent_response,
            'analysis_triggered': analysis_triggered
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