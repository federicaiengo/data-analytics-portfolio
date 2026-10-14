import json
from pathlib import Path

ALLOWED_FUNCTIONS = {'GOVERN', 'IDENTIFY', 'PROTECT', 'DETECT', 'RESPOND', 'RECOVER'}

def expected_band(score):
    if score <= 5: return 'low'
    if score <= 9: return 'moderate'
    if score <= 14: return 'elevated'
    return 'high'

def check(document):
    issues=[]
    assets=document.get('assets', [])
    risks=document.get('risks', [])
    ids=[a.get('id') for a in assets]
    risk_ids=[r.get('risk_id') for r in risks]
    if len(assets) != 12 or len(set(ids))!=12 or any(not isinstance(x,str) or not x.startswith('A') for x in ids): issues.append('Invalid asset inventory')
    if len(risks) != 12 or len(set(risk_ids)) != 12: issues.append('Invalid risk identifiers or count')
    for r in risks:
        rid=r.get('risk_id','<unknown>')
        if r.get('asset_id') not in ids: issues.append(f'{rid}: unknown asset')
        l,i=r.get('likelihood'),r.get('impact')
        if any(type(x) is not int or not 1<=x<=5 for x in [l,i]):
            issues.append(f'{rid}: invalid ordinal values')
        elif r.get('inherent_score') != l*i or r.get('local_band') != expected_band(l*i):
            issues.append(f'{rid}: wrong score or band')
        if not set(r.get('csf_2_functions',[])) or not set(r.get('csf_2_functions',[])).issubset(ALLOWED_FUNCTIONS): issues.append(f'{rid}: invalid CSF function')
        if not all(str(r.get(k, '')).strip() for k in ('scenario','proposed_control','evidence_required')): issues.append(f'{rid}: missing rationale or evidence request')
        if r.get('control_status') != 'PROPOSED_NOT_VERIFIED' or r.get('residual_risk') != 'NOT_ASSESSED': issues.append(f'{rid}: unverified controls must not claim effectiveness')
    return issues

if __name__ == '__main__':
    obj=json.loads((Path(__file__).parent/'risk_register.json').read_text(encoding='utf8'))
    errors=check(obj)
    if errors:
        print('FAIL',*errors,sep='\n')
        raise SystemExit(1)
    print('PASS: 12 assets, 12 risk cases, consistent scores, proposed controls only')
