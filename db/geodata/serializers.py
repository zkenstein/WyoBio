from rest_framework import serializers
from wq.db.rest.serializers import ModelSerializer
from django.contrib.gis.geos import Point as GeosPoint
from .models import Point, Observation, Attachment

class AttachmentSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = Attachment
        exclude = ['data']


class ObservationSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()

    # FIXME: Why are these coming through as required?
    obsid = serializers.ReadOnlyField()
    point = serializers.ReadOnlyField()
    
    attachments = AttachmentSerializer(many=True)
    
    def create(self, validated_data):
        request = self.context['request']
        attachment_data = validated_data.pop('attachments')
        
        # FIXME: In theory these should all be set through Fields
        username = request.user.username
        lat = request.POST.get('latitude', None)
        lng = request.POST.get('longitude', None)

        if lat and lng:
            geom = GeosPoint([float(lng), float(lat)], srid=4326)
            geom.transform(3857)
            # FIXME: Check for existing Point at same location
            # (need another PointField hack to make the query work)
            pt = Point.objects.create(
                geometry=geom,
                userid=username
            )
            validated_data['point'] = pt
            

        validated_data['username'] = username
        instance = super().create(validated_data)
        for attachment in attachment_data:
            # file = attachment['data']  # Why is this empty?
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
