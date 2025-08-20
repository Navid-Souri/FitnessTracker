from rest_framework import viewsets, permissions
from .models import Exercise
from .serializers import ExerciseSerializer
from .permissions import IsOwner
from rest_framework.response import Response
from rest_framework.decorators import action

class ExerciseViewSet(viewsets.ModelViewSet):
    serializer_class = ExerciseSerializer
    queryset = Exercise.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        queryset = Exercise.objects.filter(user=self.request.user)
        search_term = self.request.query_params.get("search")
        category = self.request.query_params.get("category")
        
        if search_term:
            queryset = queryset.filter(name__icontains=search_term)
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


    @action (detail=False, methods=['get'])
    def categories(self, request):
        categories = Exercise.objects.filter(user=request.user).values_list('category', flat=True).distinct()
        return Response(categories)
    