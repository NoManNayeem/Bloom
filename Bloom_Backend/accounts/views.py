from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import RegisterSerializer

class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    body: { "username": "...", "password": "..." }
    returns: { "id": ..., "username": "...", "refresh": "...", "access": "..." }
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        # Get the user data from the request
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create the user with the validated data
        user = serializer.save()

        # Create JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Prepare the response data
        data = {
            "id": user.id,
            "username": user.username,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['POST'])
def login(request):
    """
    POST /api/auth/login/
    body: { "username": "...", "password": "..." }
    returns: { "access": "...", "refresh": "..." }
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'detail': 'Username and password are required'}, status=400)

    try:
        # Retrieve the user by username
        user = User.objects.get(username=username)

        # Validate the password
        if user.check_password(password):
            # Create JWT tokens for the user
            refresh = RefreshToken.for_user(user)

            # Return the access and refresh tokens
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })

        return Response({'detail': 'Invalid credentials'}, status=400)

    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=400)
