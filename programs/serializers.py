from rest_framework import serializers
from .models import ProgramExercise , ExerciseProgram
from django.utils import timezone


class ExerciseProgramSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = ExerciseProgram
        fields = ['id', 'name', 'description', 'user', 'created_at', 'updated_at']
        read_only_fields = ['id','user', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['created_at'] = timezone.now()
        validated_data['updated_at'] = timezone.now()
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.updated_at = timezone.now()
        instance.save()
        return instance
    
    
    
class ProgramExerciseReadSerializer(serializers.ModelSerializer):
    
    program_name = serializers.CharField(source='program.name', read_only=True)
    exercise_name = serializers.CharField(source='exercise.name', read_only=True)

    class Meta:
        model = ProgramExercise
        fields = ['program_name', 'order','exercise_name', 'default_sets', 'default_reps', 'default_rest_time']
        read_only_fields = fields
        
        
        
        
class ProgramExerciseWriteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProgramExercise
        fields = ['program', 'exercise', 'default_sets', 'default_reps', 'default_rest_time', 'order']
    
    
    
    def validate(self, attrs): 
        # Validate program-exercise combination doesn't exist already
        if self.instance is None and ProgramExercise.objects.filter(
            program=attrs['program'],
            exercise=attrs['exercise']
        ).exists():
            raise serializers.ValidationError("This exercise is already part of the program.")
        return attrs