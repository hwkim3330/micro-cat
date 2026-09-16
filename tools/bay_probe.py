"""How big a board can the trunk actually take?

Choosing a compute board before measuring the space is how the documents ended up committed
to a Radxa Zero 3W that does not fit. This goes the other way: sweep the deck plane, mark
every point that is inside the trunk shell and clear of the chassis, neck column and servos,
and report the largest axis-aligned rectangle that fits. Shop for a board afterwards.
"""
import json,sys
from pathlib import Path
import numpy as np,trimesh
R=Path(__file__).resolve().parents[1]
CLEAR=1.5   # mm kept between the board outline and anything else
def obstacles():
    rep=json.loads((R/'artifacts/parts.json').read_text())
    keep=('chassis','neck_link','neck_sleeve','tail_cover','torso_shell')
    out=[]
    for p in rep['parts']+rep['purchased']:
        if p['printed'] and p['name'] not in keep:continue
        if not p['printed'] and p['body']!='trunk':continue
        if p['name']=='compute_board':continue
        out.append(trimesh.load_mesh(R/(('models/'+p['name']+'.stl') if p['printed'] else p['stl'])))
    shell=trimesh.load_mesh(R/'models/torso_shell.stl')
    return out,shell
def largest_rect(free):
    """Largest all-true axis-aligned rectangle in a boolean grid (histogram method)."""
    best=(0,None);h=np.zeros(free.shape[1],dtype=int)
    for i in range(free.shape[0]):
        h=np.where(free[i],h+1,0)
        stack=[]
        for j in range(free.shape[1]+1):
            cur=h[j] if j<free.shape[1] else 0
            start=j
            while stack and stack[-1][1]>cur:
                s,hh=stack.pop();area=hh*(j-s)
                if area>best[0]:best=(area,(i-hh+1,s,i,j-1))
                start=s
            stack.append((start,cur))
    return best
def main(z=149.6,step=1.0):
    obs,shell=obstacles()
    lo,hi=shell.bounds
    xs=np.arange(lo[0]+2,hi[0]-2,step);ys=np.arange(lo[1]+2,hi[1]-2,step)
    X,Y=np.meshgrid(xs,ys,indexing='ij')
    pts=np.column_stack([X.ravel(),Y.ravel(),np.full(X.size,z)])
    # Inside the cavity = within the shell's convex hull but not in the wall itself.
    hull=shell.convex_hull
    inside=hull.contains(pts)&~shell.contains(pts)
    blocked=np.zeros(len(pts),bool)
    for m in obs:
        for off in ([0,0,0],[CLEAR,0,0],[-CLEAR,0,0],[0,CLEAR,0],[0,-CLEAR,0]):
            blocked|=m.contains(pts+np.array(off,dtype=float))
    free=(inside&~blocked).reshape(X.shape)
    area,box=largest_rect(free)
    if box is None:print('no free rectangle at z',z);return
    i0,j0,i1,j1=box
    out=dict(scope=' '.join(l.strip() for l in __doc__.strip().split('\n')),deck_z_mm=z,grid_mm=step,clearance_mm=CLEAR,
        largest_bay_mm=[round(float(xs[i1]-xs[i0]),1),round(float(ys[j1]-ys[j0]),1)],
        centre_xy_mm=[round(float((xs[i0]+xs[i1])/2),1),round(float((ys[j0]+ys[j1])/2),1)],
        obstacles=[ 'trunk shell interior','chassis','neck column','trunk servos and battery'],
        connectors_and_wiring_included=False)
    (R/'artifacts/bay_probe.json').write_text(json.dumps(out,indent=1)+'\n')
    print(f"largest free bay at z {z}: {out['largest_bay_mm']} mm centred {out['centre_xy_mm']}")
if __name__=='__main__':main(float(sys.argv[1]) if len(sys.argv)>1 else 149.6)
