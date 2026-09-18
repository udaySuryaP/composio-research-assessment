"""Category access analysis from existing qualified access findings only."""
CLASSIFICATIONS = {
 'Developer-obtainable credential route': [2,3,4,5,7,9,10,11,12,14,15,17,19,20,22,26,27,28,29,32,34,35,36,39,41,43,46,47,48,49,50,51,52,53,54,57,60,61,62,65,66,67,68,70,71,72,73,74,75,76,79,80,81,82,84,85,87,88,91,92,93,95,99],
 'Paid plan / entitlement / usage gate': [1,2,21,35,47,52,53,60,85,87,90,92,94,96,99],
 'Admin / permissions / authorization gate': [1,2,4,10,15,17,20,26,28,36,41,43,44,48,49,53,55,57,61,67,68,73,74,75,76,81,87,88,91,96],
 'App review / provider access approval': [12,14,28,29,31,33,34,35,38,53,72],
 'Partner / sales / credential outreach': [10,29,35,53,56,88,90,92,100],
}
def analyze(rows):
 byid={r['id']:r for r in rows}
 for ids in CLASSIFICATIONS.values():
  assert all(byid[i]['field_status']['access_model']['status']!='unresolved' for i in ids)
 result=[]
 for c in dict.fromkeys(r['category'] for r in rows):
  rs=[r for r in rows if r['category']==c];ids={r['id'] for r in rs}
  classified={i for group in CLASSIFICATIONS.values() for i in group}
  supported={r['id'] for r in rs if r['field_status']['access_model']['status']!='unresolved'}
  result.append({'category':c,'denominator':len(rs),'access_evidence_ids':sorted(supported),'unresolved_ids':sorted(ids-supported),'supported_but_onboarding_unclassified_ids':sorted(supported-classified),'labels':{k:{'count':len(ids&set(v)),'ids':sorted(ids&set(v))} for k,v in CLASSIFICATIONS.items()}})
 return {'categories':result,'rules':'Bounded agent reading of existing access qualification text and attached evidence; overlapping labels, each app counted once per label. Credential route is not proof of free/trial access. Permissions include resource scopes/consent. Review includes provider API-access approval, not ordinary OAuth consent. Named partner/commercial routes can coexist with private self-service routes; outreach can be conditional. Existing misleading gate labels are not counted verbatim. Unclassified access evidence does not establish onboarding. No absence-of-gate claim.','exclusions':{'16':'Facebook-page login does not establish assigned LiveAgent API credential onboarding.','18':'Revocation rights do not establish credential creation.','31':'Token-onboarding detail not accepted as a developer-obtainable route; preserve approval finding only.','33':'Approval is not evidence of a paid plan; ordinary member consent is not public-app review.','38':'Trial approval is not unconditional self-service.','40':'Product trial alone does not establish developer credential access.','55':'Actor permission approval does not establish credential creation.','58':'Local installation does not establish credential creation.','89':'Accounting connection alone does not establish developer credentials.','98':'GitHub registry/Action token is not Mermaid CLI product credential onboarding.'}}
