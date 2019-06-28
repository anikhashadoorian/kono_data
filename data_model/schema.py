import graphene
from django.db.models import Q
from graphene import Node
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from data_model import models


class TaskNode(DjangoObjectType):
    class Meta:
        model = models.Task
        interfaces = (Node,)


class DatasetNode(DjangoObjectType):
    class Meta:
        model = models.Dataset
        interfaces = (Node,)
        filter_fields = ['is_public', 'task_type', 'invite_key']


class LabelNode(DjangoObjectType):
    class Meta:
        model = models.Label
        interfaces = (Node,)
        filter_fields = ['user', 'dataset', 'action']

    user = graphene.String()

    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_anonymous:
            return queryset.none()
        return queryset.filter(user=info.context.user)


class Query(graphene.ObjectType):
    dataset = Node.Field(DatasetNode)
    datasets = DjangoFilterConnectionField(DatasetNode)

    label = Node.Field(LabelNode)
    labels = DjangoFilterConnectionField(LabelNode)

    def resolve_datasets(self, info):
        user = info.context.user
        if not user.is_authenticated:
            return models.Dataset.objects.filter(is_public=True)
        else:
            return models.Dataset.objects.exclude(is_public=True).filter(
                Q(user=user) | Q(admins__id=user.id) | Q(contributors__id=user.id)).distinct()

    def resolve_labels(self):
        return models.Label.objects.none()


schema = graphene.Schema(query=Query)
