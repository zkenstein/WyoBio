from rest_framework import serializers
from wq.db.rest.serializers import ModelSerializer

from .models import Point, Observation, Attachment

class AttachmentSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = Attachment
        exclude = ['data']


class ObservationSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
    
    obsid = serializers.ReadOnlyField(required=False)
    point = serializers.ReadOnlyField()
    attachments = AttachmentSerializer(many=True)
    def create(self, validated_data):
        attachment_data = validated_data.pop('attachments')
        instance = super().create(validated_data)
        for attachment in attachment_data:
            #file = attachment['data']
            file = self.context['request'].FILES['attachments[0][data]']
            attachment = {
                'data': file.read(),
                'att_name': file.name,
                'data_size': file.size,
                'content_type': file.content_type,
                'observation_id': instance.pk,
            }
            Attachment.objects.create(**attachment)
        return instance
    class Meta:
        model = Observation
        exclude = ['obsid', 'point']

class NestedObservationSerializer(ModelSerializer):
    class Meta:
        model = Observation
        fields = ['id']

class PointSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
   
    observations = NestedObservationSerializer(many=True)
    geometry = serializers.SerializerMethodField()

    def get_geometry(self, instance):
        geom = instance.geometry
        if not geom:
            return null
        geom.transform(4326)
        import json
        return json.loads(geom.geojson)
       
    class Meta:
        model = Point
        exclude = ['objectid']
