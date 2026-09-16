"""Original Micro Cat paint masks in assembly mm. Design data: root LICENSE.
Eye, ear and nose graphics are paint / multicolour-finish intent, not loose components.
"""
import numpy as np
EYE=dict(x=44,z=255,face=52.0,r=12.5) # eye button; set by cad/build.py
EAR=[];MUZZLE=(78,0,238)              # ear centreline and muzzle centre; set by cad/build.py
PINK=[244,168,158,255];DARKPINK=[214,124,118,255];IRIS=[18,30,28,255];GLINT=[252,252,246,255]
def paint(mesh,name,color):
 colors=np.tile((np.array(color)*255).astype(np.uint8),(len(mesh.vertices),1))
 if name=='skull':
  x,y,z=mesh.vertices.T;e=EYE
  face=np.abs(y)>e['face']-1.6                            # the button face and its rounded rim
  rad=np.hypot(x-e['x'],z-e['z'])
  colors[face&(rad<e['r']+0.05)]=IRIS
  # No painted glint. The button's flat face is tessellated from its rim only, so a mask that
  # catches part of that rim interpolates its colour across the whole disc: the eye came out
  # as a cream blob with a dark ring. A solid iris is what the surface can actually carry.
  if EAR:
   # Inner ear only: the inboard face of the fin itself. The mask has to be gated on x and y
   # against the ear centreline as well as z, or it spills onto the skull roof between the ears.
   zs=[s[0] for s in EAR];xc=np.interp(z,zs,[s[1] for s in EAR])
   a=np.interp(z,zs,[s[3] for s in EAR]);b=np.interp(z,zs,[s[4] for s in EAR])
   for g in (1,-1):
    yc=np.interp(z,zs,[g*s[2] for s in EAR])
    colors[(z>zs[0]+12)&(np.abs(x-xc)<a*.9)&(np.abs(y-yc)<b*1.6)&(g*(y-yc)<.6)]=PINK
  colors[(x>MUZZLE[0]+4)&(np.hypot(y,z-MUZZLE[2]-1)<10.5)]=DARKPINK  # nose pad on the lens hood only
 if name=='torso_shell':
  x,y,z=mesh.vertices.T
  # Softer belly tone below the equator, painted, not a separate part.
  colors[(z<136)&(np.abs(y)<30)&(x>-40)]=[236,224,196,255]
 mesh.visual.vertex_colors=colors
 return mesh
