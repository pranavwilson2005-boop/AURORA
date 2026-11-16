"""Reproducibly crop and optimize the supplied NASA LOLA south-polar raster.

Usage: python scripts/process_terrain.py [source.tif]
Requires rasterio, numpy, Pillow and pyproj.
"""
from __future__ import annotations
import json, math, sys
from pathlib import Path
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import Window
from rasterio.transform import array_bounds
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'Dataset/LDEM_80S_80MPP_ADJ.tiff'
OUT=ROOT/'public/assets/nasa/terrain'
OUT.mkdir(parents=True,exist_ok=True)
SIZE=256

with rasterio.open(SOURCE) as ds:
    # Coarse evaluation at the source scale: 12 x 12 samples (960 m square).
    # Scan within 61 km of the pole (about 87.8°S at lunar radius) to keep
    # the chosen gameplay patch within the actual polar region and fully covered.
    coarse=ds.read(1,out_shape=(1900,1900),resampling=Resampling.average).astype('float32')
    valid=np.isfinite(coarse)
    gy,gx=np.gradient(np.where(valid,coarse,np.nanmedian(coarse)),80*4)
    slope=np.degrees(np.arctan(np.hypot(gx,gy)))
    step=8; win=12
    best=None
    for row in range(40,1860-step,step):
        for col in range(40,1860-step,step):
            if math.hypot((row+win/2)-950,(col+win/2)-950)>190: continue
            block=slope[row:row+win,col:col+win]
            mask=valid[row:row+win,col:col+win]
            if block.size and mask.mean()>.999:
                score=float(np.mean(block)) + float(np.std(block))*.15
                if best is None or score<best[0]: best=(score,row,col,float(np.mean(block)),float(np.max(block)))
    if best is None: raise RuntimeError('No fully valid candidate landing/construction patch found')
    _,cr,cc,mean_slope,max_slope=best
    # The scene crop is 20.48 km square, centered on the flattest valid ~1 km candidate.
    factor=ds.width/1900
    center_col=(cc+win/2)*factor; center_row=(cr+win/2)*factor
    src_size=SIZE
    left=int(round(center_col-src_size/2)); top=int(round(center_row-src_size/2))
    left=max(0,min(ds.width-src_size,left));top=max(0,min(ds.height-src_size,top))
    window=Window(left,top,src_size,src_size)
    elevation=ds.read(1,window=window).astype('<f4')
    if not np.isfinite(elevation).all(): raise RuntimeError('Selected terrain crop contains NoData')
    transform=ds.window_transform(window)
    lo,bo,ri,to=array_bounds(SIZE,SIZE,transform)
    geographic=transform_bounds(ds.crs,'IAU_2015:30100',lo,bo,ri,to,densify_pts=81) if False else None
    # Convert projected crop corners to the raster's Moon 2015 ocentric geographic CRS.
    geo_crs=ds.crs.geodetic_crs
    from rasterio.warp import transform
    xy=[(lo,bo),(lo,to),(ri,bo),(ri,to)]
    xs,ys=transform(ds.crs,geo_crs,[p[0] for p in xy],[p[1] for p in xy])
    corners=list(zip(xs,ys))
    lons=[p[0] for p in corners];lats=[p[1] for p in corners]
    actual_min=float(np.min(elevation));actual_max=float(np.max(elevation))
    # Raw float32 retains meaningful source values. RGB visualization uses local robust contrast.
    elevation.tofile(OUT/'elevation.f32')
    span=max(actual_max-actual_min,1e-6)
    normalized=np.clip((elevation-actual_min)/span,0,1)
    Image.fromarray(np.round(normalized*65535).astype('uint16')).save(OUT/'heightmap.png')
    # Hillshade + hypsometric tint for an inspectable terrain preview.
    dx,dy=np.gradient(elevation,80,80);s=np.hypot(dx,dy)
    shade=np.clip(0.72-0.35*np.arctan(s)*2,0.32,1.0)
    tint=np.stack([36+normalized*100,46+normalized*110,57+normalized*125],axis=-1)
    rgb=np.uint8(np.clip(tint*shade[...,None],0,255))
    Image.fromarray(rgb,'RGB').save(OUT/'terrain_preview.png',optimize=True)
    # compact 8-bit gameplay grid; source float32 remains available for accurate runtime geometry.
    small=ds.read(1,window=window,out_shape=(SIZE,SIZE),resampling=Resampling.bilinear).astype('<f4')
    small.tofile(OUT/'game_elevation.f32')
    metadata={
      'sourceFilename':SOURCE.name,'sourceBytes':SOURCE.stat().st_size,'driver':ds.driver,
      'dimensions':[ds.width,ds.height],'bands':ds.count,'sourceDtype':ds.dtypes[0],
      'crsWkt':ds.crs.to_wkt(),'crsAuthority':{'projected':'IAU:30135','geographic':'IAU:30100'},'rasterBoundsProjected':list(ds.bounds),
      'pixelSizeMeters':[float(ds.transform.a),float(abs(ds.transform.e))],
      'elevationUnit':'metres (source history states the source grid was multiplied by 1000)',
      'nodata':'NaN','sourceElevationRangeMeters':[-7295.51708984375,7026.3310546875],
      'selectedWindowPixels':[left,top,SIZE,SIZE],'selectedProjectedBoundsMeters':[lo,bo,ri,to],
      'selectedGeographicBoundsDegrees':{'longitude':[min(lons),max(lons)],'latitude':[min(lats),max(lats)]},
      'selectedElevationRangeMeters':[actual_min,actual_max],
      'candidatePatchMeanSlopeDegrees':mean_slope,'candidatePatchMaxSlopeDegrees':max_slope,
      'candidatePatchSizeMeters':[960,960],
      'gameTerrain':{'grid':[SIZE,SIZE],'horizontalExtentMeters':[SIZE*80,SIZE*80],
        'sourceElevationMetersUnmodified':True,'runtimeVerticalScale':'0.012 game units per source metre',
        'runtimeHorizontalScale':'1 game unit per source pixel (80 m)',
        'normalizationMinMeters':actual_min,'normalizationMaxMeters':actual_max,
        'heightmap':'heightmap.png','rawElevation':'elevation.f32','gameElevation':'game_elevation.f32'}
    }
    (OUT/'metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    attribution=f"""AURORA lunar terrain dataset notes

Original file: {SOURCE.name} ({SOURCE.stat().st_size:,} bytes)
Dataset: NASA Lunar Orbiter Laser Altimeter (LOLA), south-polar elevation model.
Raster CRS: {ds.crs.to_authority()} — Moon (2015) Ocentric South Polar Stereographic.
Dimensions: {ds.width} × {ds.height}, {ds.dtypes[0]}, {abs(ds.transform.a):g} m pixel spacing.
Verified projected bounds (m): {tuple(ds.bounds)}.
Selected crop: pixel window {left},{top}, {SIZE} × {SIZE}; geographic corner envelope
lon {min(lons):.5f}…{max(lons):.5f}°, lat {min(lats):.5f}…{max(lats):.5f}°.
Selection: lowest mean slope among fully valid ~960 m windows in a coarse scan;
measured candidate mean slope {mean_slope:.3f}°, max {max_slope:.3f}°. This is a
gameplay convenience only and is not a scientifically safe landing-site assessment.

Processing: crop at native 80 m sampling; reject any crop containing non-finite
NoData; save source elevation as little-endian float32; create a 16-bit normalized
PNG for visualization/inspection. Runtime geometry uses raw elevation.f32 and
retains original metre values. The visual preview is generated hillshade/tint.
The output's fictional buildings, roads, texture and surface dressing are game art,
not NASA measurements. The normalized PNG maps crop min to 0 and max to 65535.

Source metadata reports NaN fill, the z range and history `... 1000.0 MUL`.
Attribution: NASA/GSFC/Arizona State University, Lunar Reconnaissance Orbiter
Lunar Orbiter Laser Altimeter (LOLA). See the original file metadata and NASA PDS
for authoritative dataset provenance and science context.\nNASA PGDA product listing: https://pgda.gsfc.nasa.gov/products/90
"""
    (OUT/'DATASET_INFO.txt').write_text(attribution,encoding='utf-8')
print(json.dumps({'output':str(OUT),'crop':[left,top,SIZE,SIZE],'meanSlopeDegrees':mean_slope,'selectedElevationRange':[actual_min,actual_max],'geographicBounds':metadata['selectedGeographicBoundsDegrees']},indent=2))


