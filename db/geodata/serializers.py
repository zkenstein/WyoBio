from rest_framework import serializers
from wq.db.rest.serializers import ModelSerializer

from .models import Point, Observation, Attachment

class AttachmentSerializer(ModelSerializer):
    class Meta:
        model = Attachment
        exclude = ['data']


class ObservationSerializer(ModelSerializer):
    attachments = AttachmentSerializer(many=True)
    class Meta:
        model = Observation

class NestedObservationSerializer(ModelSerializer):
    class Meta:
        model = Observation
        fields = ['id']

class PointSerializer(ModelSerializer):
    observations = NestedObservationSerializer(many=True)
    geometry = serializers.SerializerMethodField()

    def get_geometry(self, instance):
        geom = instance.geometry
        geom.transform(4326)
        import json
        return json.loads(geom.geojson)
        
    class Meta:
        model = Point
