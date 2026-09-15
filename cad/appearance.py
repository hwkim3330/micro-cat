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
  colors[face&(np.hypot(x-e['x']-4.5,z-e['z']-4.5)<4.0)]=GLINT
  if EAR:                                                 # inner ear: the inboard half above the roof
   zr=EAR[0][0]+4
   for g in (1,-1):
    yc=np.interp(z,[s[0] for s in EAR],[g*s[2] for s in EAR])
    colors[(z>zr)&(g*y>0)&(g*(y-yc)<1.0)]=PINK
  nose=(x>MUZZLE[0]+6)&(np.hypot(y,z-MUZZLE[2]-1)<11.5)   # nose pad around the lens hood
  colors[nose]=DARKPINK
 if name=='torso_shell':
  x,y,z=mesh.vertices.T
  # Softer belly tone below the equator, painted, not a separate part.
  colors[(z<136)&(np.abs(y)<30)&(x>-40)]=[236,224,196,255]
 mesh.visual.vertex_colors=colors
 return mesh
