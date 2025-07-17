from pathlib import Path
import tempfile
import zipfile

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry,MultiPolygon
import requests

from core.models import State

class Command(BaseCommand):
    help = 'Import USA states to database'


    @transaction.atomic
    def handle(self, *args, **options):
        if State.objects.all().exists():
            return
        # Download US states shapefile from US Census Bureau
        url = "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_state_500k.zip"
        with tempfile.TemporaryDirectory() as td:
            zip_path = Path(td) / "states.zip"
            with requests.get(url, stream=True, timeout=120,verify=False) as r:
                r.raise_for_status()
                with open(zip_path, "wb") as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)

            # Extract and locate the .shp
            with zipfile.ZipFile(zip_path) as zf:
                zf.extractall(td)
            shp_path = next(Path(td).glob("*.shp"))

            # Read with GDAL/OGR
            ds = DataSource(str(shp_path))
            layer = ds[0]

            objs = []
            for feat in layer:
                code = feat.get("STUSPS")   
                name = feat.get("NAME")
                geom = GEOSGeometry(feat.geom.wkt, srid=4326)  # already WGS-84
                
                # Ensure geometry is always a MultiPolygon
                if geom.geom_type == "Polygon":
                    geom = MultiPolygon(geom)
                objs.append(State(state_code=code, name=name, geom=geom))

            State.objects.bulk_create(
                objs,
                update_conflicts=True,
                update_fields=("name", "geom"),
                unique_fields=("state_code",),
            )
            self.stdout.write(
                self.style.SUCCESS(f"Imported/updated {len(objs)} states.")
            )