from django.shortcuts import render
from rest_framework import generics,permissions,mixins,status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Post,Vote
from .serializers import PostSerializer,VoteSerializer
# Create your views here.
class PostListView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def perform_create(self, serializer):
        return serializer.save(poster=self.request.user)

class PostRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def delete(self,request, *args, **kwargs):
        post = Post.objects.filter(pk = kwargs['pk'], poster = self.request.user)
        if post.exists():
            return self.destroy(request,*args, **kwargs)
        else:
            raise ValidationError('You have no authority to destroy another induviduals works...')


class VoteCreateView( generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        post = Post.objects.get(pk=self.kwargs['id'])
        return Vote.objects.filter(voter=user,post=post)

    def perform_create(self,serializer):
        if self.get_queryset().exists():
            raise ValidationError('You have already voted for this post')

        return serializer.save(voter=self.request.user,post = Post.objects.get(pk=self.kwargs['id']))

    def delete(self,request, *args, **kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            raise ValidationError('You did not vote for this post')
