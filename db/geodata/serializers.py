from rest_framework import serializers
from wq.db.rest.serializers import ModelSerializer
from django.contrib.gis.geos import Point as GeosPoint
from .models import Point, Observation, Attachment

class AttachmentSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = Attachment
        exclude = ['data']

class DateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        if isinstance(value, str):
            return value
        return super().to_representation(value)

class ObservationSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
    attachments = AttachmentSerializer(many=True, required=False)
    sampdate = DateTimeField()
    
    def get_fields(self):
        fields = super().get_fields()
        fields.pop('sampdate_label')
        return fields
    
    def to_internal_value(self, data):
        for key in list(data.keys()):
            if data[key] == "":
                del data[key]
        return super().to_internal_value(data)
    
    def create(self, validated_data):
        request = self.context['request']
        attachment_data = validated_data.pop('attachments', [])
        
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
                userid=request.user.id,
            )
            # Reload point to get pntid
            pt = Point.objects.get(pk=pt.pk)
            validated_data['point_id'] = pt.pntid
            

        validated_data['username'] = username
        instance = super().create(validated_data)
        photos = self.context['request'].FILES.getlist('photos')
        for file in photos:
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
        exclude = ['obsid']

class NestedObservationSerializer(ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        fields.pop('sampdate_label')
        return fields
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

class SpeciesSerializer(ModelSerializer):
    class Meta:
        fields = ('elem_type',)
