from rest_framework import serializers
from .models import Story, StoryBlock

BlockType = (StoryBlock.TEXT, StoryBlock.IMAGE)

class StorySerializer(serializers.ModelSerializer):
    
    writer_id = serializers.IntegerField(source='writer.id', read_only=True)
    title = serializers.CharField(default='Untitled', allow_blank=True)
    subtitle = serializers.SerializerMethodField()
    updated_at = serializers.DateTimeField(read_only=True)
    published_at = serializers.DateTimeField(allow_null=True, default=None, read_only=True)
    published = serializers.BooleanField(default=False, read_only=True)
    blocks = serializers.SerializerMethodField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta: 
        model = Story
        fields = (
            'id',
            'uid',
            'writer_id',
            'title',
            'subtitle',
            'created_at',
            'updated_at',
            'published_at',
            'published',
            'blocks',
        )
    def validate(self, data):
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['writer'] = user
        story = super(StorySerializer, self).create(validated_data)
        
        if 'blocks' in self.context['request'].data:
            blocks = self.context['request'].data['blocks']
            for i in range(len(blocks)):
                # if blocks[i]['block_type'] not in BlockType:
                #     raise serializers.ValidationError('Only "text" or "image" are allowed for block_type')
                StoryBlock.objects.create(story=story, order=i+1, content=blocks[i]['content'], block_type=blocks[i]['block_type'])
            
        return story

    def update(self, instance, validated_data):
        story = super(StorySerializer, self).update(instance, validated_data)
        blocks = self.context['request'].data['blocks']
        for block in blocks:
            try:
                block_to_update = StoryBlock.objects.get(story=story, order=block['order'])
                if 'content' in block:
                    block_to_update.content = block['content']
                if 'block_type' in block:
                    block_to_update.block_type = block['block_type']
                block_to_update.save()
            except StoryBlock.DoesNotExist:
                StoryBlock.objects.create(story=story, order=block['order'], content=block['content'], block_type=block['block_type'])

        return story

    def get_blocks(self, story):
        return StoryBlockSerializer(story.blocks, context=self.context, many=True).data

    def get_subtitle(self, story):
        data = self.context['request'].data
        if 'subtitle' in data:
            subtitle = data['subtitle']
            if subtitle == '':
                if 'blocks' in data:
                    first_block = story.blocks.filter(block_type='text').first()
                    subtitle = first_block.content # 140자로 잘라야 함
                    story.subtitle = subtitle
                    story.save()
        else:
            subtitle = story.subtitle
        return subtitle

class StoryBlockSerializer(serializers.ModelSerializer):
    order = serializers.IntegerField(required=False)

    class Meta: 
        model = StoryBlock
        fields = '__all__' # story, order, block_type, content