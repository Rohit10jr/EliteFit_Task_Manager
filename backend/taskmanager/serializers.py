from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username') 
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'due_date', 'priority', 'status', 'author']
        read_only_fields = ['id', 'author']

    def validate_priority(self, value):
        if value not in ['High', 'Medium', 'Low']:
            raise serializers.ValidationError("Priority must be High, Medium, or Low.")
        return value
