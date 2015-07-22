from django.contrib.gis.db import models
from django.db.models import Max
from django.db import connections, transaction
from django.conf import settings


def get_next_id(table):
    cursor = connections['arcgis'].cursor()
    owner = settings.DB_OWNER
    rowid = 0
    owner, table, rowid = cursor.callproc("next_rowid", (owner, table, rowid))
    return rowid


class PointField(models.PointField):
    def select_format(self, compiler, sql, params):
        return "%s.STAsText()" % sql, params
    
    def get_placeholder(self, value, compiler, connection):
        return "geometry::STPointFromText(%s, 3857)"

    def get_db_prep_save(self, value, connection):
        return value.wkt


class IncrementingField(models.IntegerField):
    def get_placeholder(self, value, compiler, connection):
        if value:
            return "%s"
        return "(SELECT MAX({db_column}) + 1 + %s FROM {db_table})".format(
            db_column=self.db_column,
            db_table=self.model._meta.db_table
        )

    def get_db_prep_save(self, value, connection):
        if value:
            return value
        return 0


class ArcGisModel(models.Model):
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = get_next_id(self._meta.db_table)
        super().save(*args, **kwargs)
    class Meta:
        abstract = True


class Point(ArcGisModel):
    id = models.IntegerField(db_column='OBJECTID', primary_key=True)
    pntid = IncrementingField(db_column='pntID', unique=True)
    userid = models.CharField(db_column='userID', max_length=50, blank=True, null=True)
    coordcolmethod = models.CharField(db_column='coordColMethod', max_length=50, blank=True, null=True)
    vetted = models.SmallIntegerField(blank=True, null=True, default=0)
    geometry = PointField(
        db_column='SHAPE', blank=True, null=True, srid=3857
    )

    def __str__(self):
        return "Point %s" % self.id

    class Meta:
        managed = False
        db_table = 'POINTSWM84'


class Observation(ArcGisModel):
    # Row identifiers
    id = models.IntegerField(db_column='OBJECTID', primary_key=True)
    point = models.ForeignKey(
        Point, db_column='pntID', to_field='pntid', blank=True, null=True,
        related_name="observations"
    )
    obsid = IncrementingField(db_column='obsID', blank=True, null=True)

    # Domains
    species = models.ForeignKey(
        "Species", to_field='elcode', db_column='speciesID',
        blank=True, null=True
    )
    weather = models.ForeignKey("Weather", db_column='weatherConditions', max_length=250, blank=True, null=True)
    habitat = models.ForeignKey("Habitat", db_column='habDesc', max_length=100, blank=True, null=True)
    phenology = models.ForeignKey("Phenology", db_column='plantPhenology', max_length=250, blank=True, null=True)
    
    # Other fields
    sampdate = models.DateTimeField(db_column='sampDate', blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    size = models.IntegerField(blank=True, null=True)
    speciesdescription = models.CharField(db_column='speciesDescription', max_length=250, blank=True, null=True)
    numpeople = models.IntegerField(db_column='numPeople', blank=True, null=True)
    species_guess = models.CharField(max_length=200, blank=True, null=True)
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
    vetted = models.SmallIntegerField(db_column='vetted', blank=True, null=True, default=0)
    sensitive = models.CharField(db_column='sensitive', max_length=5, blank=True, null=True, default='N')

    def save(self, *args, **kwargs):
        if self.species_id:
            self.species_guess = None
            self.scientificname = self.species.sname
            if self.species.s_comname:
                self.commonname = self.species.s_comname
            elif self.species.g_comname:
                self.commonname = self.species.g_comname
        elif self.species_guess:
            self.species_guess = self.species_guess[:50]
        super().save(*args, **kwargs)
        
    def __str__(self):
        sampdate = self.sampdate
        if sampdate:
            if isinstance(sampdate, str):
                sampdate = sampdate.split(' ')[0]
            else:
                sampdate = sampdate.date()
        return "%s on %s" % (
            self.species if self.species_id else self.species_guess,
            sampdate or "Unknown",
        )

    class Meta:
        managed = False
        db_table = 'POINTSOBS'
        unique_together = (('point', 'obsid'),)
        ordering = ["-sampdate"]


class Attachment(ArcGisModel):
    id = models.IntegerField(db_column='ATTACHMENTID', primary_key=True)
    observation = models.ForeignKey(Observation, db_column='REL_OBJECTID', related_name='attachments', null=True, blank=True)
    content_type = models.CharField(db_column='CONTENT_TYPE', max_length=150, null=True, blank=True)
    att_name = models.CharField(db_column='ATT_NAME', max_length=250, null=True, blank=True)
    data_size = models.IntegerField(db_column='DATA_SIZE', null=True, blank=True)
    data = models.BinaryField(db_column='DATA', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'POINTSOBS__ATTACH_1'


class Domain(models.Model):
    # objectid = models.IntegerField(db_column='OBJECTID', primary_key=True)
    # code = models.IntegerField(db_column='ID', blank=True, null=True)
    id = models.TextField(db_column='DESC_', primary_key=True)
    def __str__(self):
        return self.id

    class Meta:
        abstract = True
 
class Habitat(Domain):
    class Meta:
        managed = False
        db_table = 'POINTSOBS_HABITAT'


class Phenology(Domain):
    class Meta:
        managed = False
        db_table = 'POINTSOBS_PHENOLOGY'
        verbose_name_plural = "phenology"


class Weather(Domain):
    class Meta:
        managed = False
        db_table = 'POINTSOBS_WEATHER'
        verbose_name_plural = "weather"


class Species(models.Model):
    id = models.IntegerField(db_column='OBJECTID', primary_key=True)
    elcode = models.CharField(
        db_column='ELCODE', max_length=10, unique=True
    )

    parent_elcode = models.CharField(db_column='PARENT_ELCODE', max_length=255, blank=True, null=True)
    grp = models.CharField(db_column='GRP', max_length=255, blank=True, null=True)
    elem_type = models.CharField(db_column='ELEM_TYPE', max_length=255, blank=True, null=True)
    classif_level = models.CharField(db_column='CLASSIF_LEVEL', max_length=255, blank=True, null=True)
    range_map = models.CharField(db_column='RANGE_MAP', max_length=255, blank=True, null=True)
    distributi = models.CharField(db_column='DISTRIBUTI', max_length=255, blank=True, null=True)
    genus_species = models.CharField(db_column='GENUS_SPECIES', max_length=255, blank=True, null=True)
    sname = models.CharField(db_column='SNAME', max_length=255, blank=True, null=True)
    wgfd_sname = models.CharField(db_column='WGFD_SNAME', max_length=255, blank=True, null=True)
    wgfd_comname = models.CharField(db_column='WGFD_COMNAME', max_length=255, blank=True, null=True)
    gname = models.CharField(db_column='GNAME', max_length=255, blank=True, null=True)
    s_comname = models.CharField(db_column='S_COMNAME', max_length=255, blank=True, null=True)
    g_comname = models.CharField(db_column='G_COMNAME', max_length=255, blank=True, null=True)
    num_obs = models.DecimalField(db_column='NUM_OBS', max_digits=15, decimal_places=6, blank=True, null=True)
    s_rank = models.CharField(db_column='S_RANK', max_length=255, blank=True, null=True)
    g_rank = models.CharField(db_column='G_RANK', max_length=255, blank=True, null=True)
    trackstat = models.CharField(db_column='TRACKSTAT', max_length=255, blank=True, null=True)
    usfws_esa = models.CharField(db_column='USFWS_ESA', max_length=255, blank=True, null=True)
    wy_blm = models.CharField(db_column='WY_BLM', max_length=255, blank=True, null=True)
    usfs = models.CharField(db_column='USFS', max_length=255, blank=True, null=True)
    usfsr2 = models.CharField(db_column='USFSR2', max_length=255, blank=True, null=True)
    usfsr4 = models.CharField(db_column='USFSR4', max_length=255, blank=True, null=True)
    wgfd = models.CharField(db_column='WGFD', max_length=255, blank=True, null=True)
    wgfd_nss = models.CharField(db_column='WGFD_NSS', max_length=255, blank=True, null=True)
    wgfd_tier = models.CharField(db_column='WGFD_TIER', max_length=255, blank=True, null=True)
    wy_contrib = models.CharField(db_column='WY_CONTRIB', max_length=255, blank=True, null=True)
    occurences = models.CharField(db_column='OCCURENCES', max_length=255, blank=True, null=True)
    absracts = models.CharField(db_column='ABSRACTS', max_length=255, blank=True, null=True)
    rangemaps = models.CharField(db_column='RANGEMAPS', max_length=255, blank=True, null=True)
    distribmodels = models.CharField(db_column='DISTRIBMODELS', max_length=255, blank=True, null=True)
    esid = models.DecimalField(db_column='ESID', max_digits=15, decimal_places=6, blank=True, null=True)

    def __str__(self):
        if self.s_comname:
            return "%s (%s)" % (self.s_comname, self.sname)
        else:
            return self.sname
    
    class Meta:
        managed = False
        db_table = 'SPECIESLISTCOMPLETE'
        verbose_name_plural = "species"
        ordering = ("sname",)
