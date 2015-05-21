from django.contrib.gis.db import models
from django.db.models import Max

class PointField(models.PointField):
    def select_format(self, compiler, sql, params):
        return "%s.STAsText()" % sql, params
    
    def get_placeholder(self, value, compiler, connection):
        return "geometry::STPointFromText(%s, 3857)"

    def get_db_prep_save(self, value, connection):
        return value.wkt

class Point(models.Model):
    id = models.IntegerField(db_column='pntID', primary_key=True)
    objectid = models.IntegerField(db_column='OBJECTID')
    userid = models.CharField(db_column='userID', max_length=50, blank=True, null=True)
    coordcolmethod = models.CharField(db_column='coordColMethod', max_length=50, blank=True, null=True)
    vetted = models.SmallIntegerField(blank=True, null=True)
    geometry = PointField(
        db_column='SHAPE', blank=True, null=True, srid=3857
    )

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = Point.objects.aggregate(Max('id'))['id__max'] + 1
            self.objectid = Point.objects.aggregate(Max('objectid'))['objectid__max'] + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "Point %s" % self.id

    class Meta:
        managed = False
        db_table = 'POINTSWM84'

class Observation(models.Model):
    id = models.IntegerField(db_column='OBJECTID', primary_key=True)
    point = models.ForeignKey(
        Point, db_column='pntID', blank=True, null=True,
        related_name="observations"
    )
    # weather = models.ForeignKey("Weather", db_column='weatherConditions', max_length=250, blank=True, null=True)
    # habdesc = models.CharField(db_column='habDesc', max_length=100, blank=True, null=True)
    obsid = models.IntegerField(db_column='obsID', blank=True, null=True)
    sampdate = models.TextField(db_column='sampDate', blank=True, null=True)
    speciesid = models.CharField(db_column='speciesID', max_length=10, blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    size = models.IntegerField(blank=True, null=True)
    plantphenology = models.CharField(db_column='plantPhenology', max_length=250, blank=True, null=True)
    speciesdescription = models.CharField(db_column='speciesDescription', max_length=250, blank=True, null=True)
    numpeople = models.IntegerField(db_column='numPeople', blank=True, null=True)
    species_guess = models.CharField(max_length=50, blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    town = models.CharField(max_length=100, blank=True, null=True)
    school = models.CharField(max_length=100, blank=True, null=True)
    grade = models.CharField(max_length=100, blank=True, null=True)
    classname = models.CharField(db_column='className', max_length=100, blank=True, null=True)
    comments = models.CharField(max_length=250, blank=True, null=True)
    searchdurationsec = models.IntegerField(db_column='searchDurationSec', blank=True, null=True)
    commonname = models.CharField(db_column='commonName', max_length=50, blank=True, null=True)
    scientificname = models.CharField(db_column='scientificName', max_length=50, blank=True, null=True)
    username = models.CharField(db_column='userName', max_length=50, blank=True, null=True)
    vetted = models.SmallIntegerField(blank=True, null=True)

    def __str__(self):
        return "%s on %s" % (self.commonname, self.sampdate)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = Observation.objects.aggregate(Max('id'))['id__max'] + 1
            maxid = Observation.objects.filter(point=self.point).aggregate(Max('obsid'))['obsid__max']
            self.obsid = maxid + 1 if maxid else 1
        super().save(*args, **kwargs)
        
    class Meta:
        managed = False
        db_table = 'POINTSOBS'
        unique_together = (('point', 'obsid'),)


class Attachment(models.Model):
    id = models.IntegerField(db_column='ATTACHMENTID', primary_key=True)
    observation = models.ForeignKey(Observation, db_column='REL_OBJECTID', related_name='attachments', null=True, blank=True)
    content_type = models.CharField(db_column='CONTENT_TYPE', max_length=150, null=True, blank=True)
    att_name = models.CharField(db_column='ATT_NAME', max_length=250, null=True, blank=True)
    data_size = models.IntegerField(db_column='DATA_SIZE', null=True, blank=True)
    data = models.BinaryField(db_column='DATA', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = Observation.objects.aggregate(Max('id'))['id__max'] + 1
        super().save(*args, **kwargs)

    class Meta:
        managed = False
        db_table = 'POINTSOBS__ATTACH_1'

class Habitat(models.Model):
#    objectid = models.IntegerField(db_column='OBJECTID')  # Field name made lowercase.
 #   id = models.IntegerField(db_column='ID', blank=True, null=True)  # Field name made lowercase.
    desc_field = models.TextField(db_column='DESC_', blank=True, null=True)  # Field name made lowercase. Field renamed because it ended with '_'.

    class Meta:
        managed = False
        db_table = 'POINTSOBS_HABITAT'


class Phenology(models.Model):
  #  objectid = models.IntegerField(db_column='OBJECTID')  # Field name made lowercase.
   # id = models.IntegerField(db_column='ID', blank=True, null=True)  # Field name made lowercase.
    desc_field = models.TextField(db_column='DESC_', blank=True, null=True)  # Field name made lowercase. Field renamed because it ended with '_'.

    class Meta:
        managed = False
        db_table = 'POINTSOBS_PHENOLOGY'


class Weather(models.Model):
    # objectid = models.IntegerField(db_column='OBJECTID')  # Field name made lowercase.
    # id = models.IntegerField(db_column='ID', blank=True, null=True)  # Field name made lowercase.
    id = models.TextField(db_column='DESC_', primary_key=True)  # Field name made lowercase. Field renamed because it ended with '_'.

    def __str__(self):
        return self.id

    class Meta:
        managed = False
        db_table = 'POINTSOBS_WEATHER'