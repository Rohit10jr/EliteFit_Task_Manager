from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from .models import Task
from .serializers import TaskSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter
# class TaskListView(APIView):
#     permission_classes = [IsAuthenticated]  

#     def get(self, request):
#         tasks = Task.objects.filter(author=request.user)
#         serializer = TaskSerializer(tasks, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = TaskSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(author=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        

class RegisterView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")

        if not username or not password or not email:
            return Response({"error": "Username, password, and email are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password)  
        )

        return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)


# Search
 
class TaskFilter(filters.FilterSet):
    priority = filters.ChoiceFilter(choices=Task.PRIORITY_CHOICES)
    status = filters.ChoiceFilter(choices=Task.STATUS_CHOICES)
    # due_date = filters.DateFilter(field_name='due_date', lookup_expr='exact')
    # due_date_before = filters.DateFilter(field_name='due_date', lookup_expr='lt')
    # due_date_after = filters.DateFilter(field_name='due_date', lookup_expr='gt') 
    due_date = filters.DateFromToRangeFilter() 

    class Meta:
        model = Task
        fields = ['priority', 'status', 'due_date']
    

# CRUD 

class TaskListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    filter_backends = (filters.DjangoFilterBackend, SearchFilter,OrderingFilter) 
    filterset_class = TaskFilter  
    search_fields = ['title', 'description']  
    ordering_fields = ['due_date', 'title']
    ordering = ['due_date']  

    def get_queryset(self):
        return Task.objects.filter(author=self.request.user)

        # tasks=Task.objects.filter(author=self.request.user) 

        # if tasks is None:
        #     return Response({"message": "No tasks"}, status=status.HTTP_200_OK) 
        # else:
        #     return Task.objects.filter(author=self.request.user) 

    def perform_create(self, serializer):
        try:
            serializer.save(author=self.request.user)
        except ValidationError as e:
            raise ValidationError({"error": e.detail})
        
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except ValidationError:
            return Response({"error": "Invalid data provided"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Task.objects.filter(author=self.request.user)

    def get_object(self):
        try:
            return super().get_object()
        except Task.DoesNotExist:
            raise NotFound({"detail": "Task not found or you do not have permission to access it."})

    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        task.delete()
        return Response({"message": "Task deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
    # def put(self, request, *args, **kwargs):
    #     task = self.get_object()
    #     serializer = self.get_serializer(task, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     try:
    #         self.perform_update(serializer)
    #     except ValidationError:
    #         return Response({"error": "Invalid data for update"}, status=status.HTTP_400_BAD_REQUEST)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    # custom update

    # def update(self, request, *args, **kwargs):
    #     # Custom update logic here, if needed
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_seria lizer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)


