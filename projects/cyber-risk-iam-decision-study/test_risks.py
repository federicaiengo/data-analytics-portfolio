import copy
import json
import unittest
from pathlib import Path
from validate_risks import check

FIXTURE=json.loads((Path(__file__).parent/'risk_register.json').read_text(encoding='utf8'))

class RiskRegisterTests(unittest.TestCase):
    def test_baseline_valid(self): self.assertEqual(check(FIXTURE),[])
    def test_duplicate_id_rejected(self):
        d=copy.deepcopy(FIXTURE); d['risks'][1]['risk_id']=d['risks'][0]['risk_id']; self.assertTrue(check(d))
    def test_unknown_asset_rejected(self):
        d=copy.deepcopy(FIXTURE); d['risks'][0]['asset_id']='A99'; self.assertTrue(check(d))
    def test_bad_score_rejected(self):
        d=copy.deepcopy(FIXTURE); d['risks'][0]['inherent_score']=0; self.assertTrue(check(d))
    def test_missing_evidence_rejected(self):
        d=copy.deepcopy(FIXTURE); d['risks'][0]['evidence_required']=''; self.assertTrue(check(d))
    def test_unverified_control_claim_rejected(self):
        d=copy.deepcopy(FIXTURE); d['risks'][0]['control_status']='IMPLEMENTED'; self.assertTrue(check(d))
    def test_residual_claim_rejected(self):
        d=copy.deepcopy(FIXTURE); d['risks'][0]['residual_risk']='LOW'; self.assertTrue(check(d))
    def test_csf_mistyped_rejected(self):
        d=copy.deepcopy(FIXTURE); d['risks'][0]['csf_2_functions']=['AUDIT']; self.assertTrue(check(d))


class VendorChecklistTests(unittest.TestCase):
    def test_vendor_has_twelve_unique_items(self):
        d=json.loads((Path(__file__).parent/'vendor_due_diligence.json').read_text(encoding='utf8'))
        ids=[x['question_id'] for x in d['items']]
        self.assertEqual(len(ids), 12)
        self.assertEqual(len(set(ids)),12)

    def test_vendor_template_is_not_misrepresented_as_checked(self):
        d=json.loads((Path(__file__).parent/'vendor_due_diligence.json').read_text(encoding='utf8'))
        self.assertFalse(d['real_vendor_contacted'])
        self.assertTrue(all(x['evidence_received']=='NOT_REQUESTED' and x['review_decision']=='NOT_ASSESSED' for x in d['items']))

    def test_vendor_questions_and_evidence_requirements_nonempty(self):
        d=json.loads((Path(__file__).parent/'vendor_due_diligence.json').read_text(encoding='utf8'))
        self.assertTrue(all(x['question'].strip() and x['evidence_request'].strip() and x['review_owner_hypothetical'].strip() for x in d['items']))

if __name__ == '__main__': unittest.main()
