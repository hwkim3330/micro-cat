"""How much does the extended paw cost in turning?

The rearward sole extension buys backward-tipping margin. It also enlarges the foot
contact patch, which resists yaw. This sweep edits ONLY the foot collision box in the
generated model - the printed geometry is untouched - so the contact length is the one
thing that changes, and measures commanded-yaw response and forward speed for each.
"""
import json,math,sys,tempfile
import xml.etree.ElementTree as E
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'runtime'))
from compat_env import Environment
SRC=R/'models/micro_cat_14.xml'
def with_rear_limit(rear_mm,tmp):
    """Rebuild the model with each foot collision box trimmed to start at rear_mm."""
    tree=E.parse(SRC);root=tree.getroot()
    for geom in root.iter('geom'):
        if not (geom.get('name') or '').endswith('_foot_collision'):continue
        pos=np.array([float(v) for v in geom.get('pos').split()])
        size=np.array([float(v) for v in geom.get('size').split()])
        lo=pos[0]-size[0];hi=pos[0]+size[0]
        # the sole's front edge is fixed; only the heel moves
        new_lo=max(lo,hi-rear_mm*.001)
        geom.set('pos',' '.join(f'{v:.9g}' for v in [(new_lo+hi)/2,pos[1],pos[2]]))
        geom.set('size',' '.join(f'{v:.9g}' for v in [(hi-new_lo)/2,size[1],size[2]]))
    out=Path(tmp)/f'foot_{rear_mm}.xml';tree.write(out,encoding='unicode');return out
def run(model,cmd,seconds=10.,seed=0):
    env=Environment(model_path=model);env.reset(seed=seed);env.policy.set_vel_cmd(*cmd)
    fell=None
    for _ in range(int(seconds*50)):
        _,fallen,_=env.step(env.policy.infer())
        if fallen and fell is None:fell=float(env.data.time)
    q=env.data.qpos[3:7]
    yaw=math.atan2(2*(q[0]*q[3]+q[1]*q[2]),1-2*(q[2]**2+q[3]**2))
    return dict(yaw_rate_rad_s=yaw/seconds,speed_m_s=float(np.linalg.norm(env.data.qpos[:2]))/seconds,fell_s=fell)
if __name__=='__main__':
    lengths=[int(a) for a in sys.argv[1:]] or [74,66,58,50]
    rows=[]
    with tempfile.TemporaryDirectory() as tmp:
        for L in lengths:
            m=with_rear_limit(L,tmp)
            turn=run(m,(0,0,1.0));fwd=run(m,(0.6,0,0))
            rows.append(dict(sole_length_mm=L,yaw_rate_at_cmd_1_rad_s=round(turn['yaw_rate_rad_s'],4),
                             speed_at_cmd_0p6_m_s=round(fwd['speed_m_s'],4),
                             fell_turning_s=turn['fell_s'],fell_forward_s=fwd['fell_s']))
            print(rows[-1],flush=True)
    (R/'artifacts/foot_length_sweep.json').write_text(json.dumps(dict(
        scope=__doc__.strip().split('\n\n')[1].replace('\n',' '),
        note='Only the foot collision box changes; printed parts, masses and joint limits are identical.',
        command_yaw_rad_s=1.0,command_forward_m_s=0.6,seconds=10,seed=0,results=rows),indent=1)+'\n')
