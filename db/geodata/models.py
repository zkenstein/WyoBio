from django.contrib.gis.db import models


class PointField(models.PointField):
    def select_format(self, compiler, sql, params):
        return "%s.STAsText()" % sql, params


class Point(models.Model):
    id = models.IntegerField(db_column='pntID', primary_key=True)
    userid = models.CharField(db_column='userID', max_length=50, blank=True, null=True)
    weatherconditions = models.CharField(db_column='weatherConditions', max_length=250, blank=True, null=True)
    habdesc = models.CharField(db_column='habDesc', max_length=100, blank=True, null=True)
    coordcolmethod = models.CharField(db_column='coordColMethod', max_length=50, blank=True, null=True)
    vetted = models.SmallIntegerField(blank=True, null=True)
    geometry = PointField(
        db_column='SHAPE', blank=True, null=True, srid=3857
    )

    def __str__(self):
        return self.habdesc

    class Meta:
        managed = False
        db_table = 'POINTSWM84'

class Observation(models.Model):
    id = models.IntegerField(db_column='OBJECTID', primary_key=True)
    point = models.ForeignKey(
        Point, db_column='pntID', blank=True, null=True,
        related_name="observations"
    )
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

    class Meta:
        managed = False
        db_table = 'POINTSOBS'
        unique_together = (('point', 'obsid'),)


class Attachment(models.Model):
    id = models.IntegerField(db_column='ATTACHMENTID', primary_key=True)
    observation = models.ForeignKey(Observation, db_column='REL_OBJECTID', related_name='attachments')
    content_type = models.CharField(db_column='CONTENT_TYPE', max_length=150)
    att_name = models.CharField(db_column='ATT_NAME', max_length=250)
    data_size = models.IntegerField(db_column='DATA_SIZE')
    data = models.BinaryField(db_column='DATA', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'POINTSOBS__ATTACH_1'
