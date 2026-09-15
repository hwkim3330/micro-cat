"""Static tipping margin at HOME: how far the robot can lean before its centre of mass
leaves the two-foot support polygon.

tip angle = atan(horizontal CoM-to-hull-edge reach / CoM height above the soles).
Quasi-static and rigid. No contact model, no friction, no dynamic or walking proof.
Pass extra model paths to compare (e.g. ../micro-x/models/micro_x_14.xml).
"""
import hashlib,json,math,sys
from pathlib import Path
import mujoco,numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'cad'))
def rel(p):
    p=Path(p).resolve()
    return str(p.relative_to(R)) if p.is_relative_to(R) else str(p)
import layout as L
def hull(points):
    points=sorted(set(map(tuple,points)))
    def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    def half(seq):
        r=[]
        for p in seq:
            while len(r)>1 and cross(r[-2],r[-1],p)<=0:r.pop()
            r.append(p)
        return r
    return np.array(half(points)[:-1]+half(points[::-1])[:-1])
def study(path):
    m=mujoco.MjModel.from_xml_path(str(path));d=mujoco.MjData(m)
    d.qpos[:7]=[0,0,.125,1,0,0,0]
    for j in range(m.njnt):
        name=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_JOINT,j)
        if name in L.HOME:d.qpos[m.jnt_qposadr[j]]=L.HOME[name]
    mujoco.mj_forward(m,d)
    pts=[]
    for side in ['left','right']:
        g=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_GEOM,f'{side}_foot_collision')
        c=d.geom_xpos[g];M=d.geom_xmat[g].reshape(3,3);s=m.geom_size[g]
        pts+= [c+M@np.array([sx*s[0],sy*s[1],-s[2]]) for sx in(-1,1) for sy in(-1,1)]
    pts=np.array(pts);zfloor=float(pts[:,2].min())
    poly=hull(pts[pts[:,2]<=zfloor+1e-4][:,:2])
    mass=float(m.body_mass.sum());com=(d.xipos*m.body_mass[:,None]).sum(0)/mass
    h=float(com[2]-zfloor)
    out={'model':rel(path),'mass_g':round(mass*1000,1),'com_height_above_sole_mm':round(h*1000,1)}
    for label,(ux,uy) in [('fwd',(1,0)),('aft',(-1,0)),('lat',(0,1))]:
        r=max(0.,max((p[0]-com[0])*ux+(p[1]-com[1])*uy for p in poly))
        out[label+'_reach_mm']=round(r*1000,1);out['tip_'+label+'_deg']=round(math.degrees(math.atan2(r,h)),1)
    return out
paths=[R/'models/micro_cat_14.xml']+[Path(a) for a in sys.argv[1:]]
res=[study(p) for p in paths]
(R/'artifacts/tip_study.json').write_text(json.dumps(dict(
    scope=' '.join(__doc__.strip().split('\n')[2:5]),pose='policy HOME',
    model_sha256={rel(p):hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths},
    results=res,contact_tested=False,walking_tested=False,physical_validation=False),indent=1)+'\n')
for r in res:print(r)
