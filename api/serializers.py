from rest_framework import serializers
from rest_framework.serializers import ValidationError
from hasker.models import Question, Tag, Answer


class QuestionSerializer(serializers.Serializer):

    class TagField(serializers.RelatedField):
        def to_representation(self, value):
            return value.name

        def to_internal_value(self, data):
            if not isinstance(data, unicode):
                raise ValidationError('This must be a string')
            return data

    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=255)
    text = serializers.CharField()
    author = serializers.ReadOnlyField(source='author.username')
    tags = TagField(many=True, queryset=Tag.objects.all())
    rating = serializers.IntegerField(read_only=True)
    creation_date = serializers.DateTimeField(read_only=True)

    def validate_tags(self, tags):
        if len(tags) > 3:
            raise ValidationError('Tags field must not contain more than three strings')
        return tags

    def create(self, validated_data):
        instance = Question.objects.create(
            validated_data['title'],
            validated_data['text'],
            validated_data['author'],
            validated_data.get('tags', [])
        )
        return instance


class AnswerSerializer(serializers.ModelSerializer):

    author = serializers.ReadOnlyField(source='author.username')
    rating = serializers.IntegerField(read_only=True)
    creation_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Answer
        fields = ('id', 'text', 'author', 'rating', 'creation_date')
