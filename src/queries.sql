-- SELECT * FROM pr_sn AS n 
-- WHERE n.sn_sp = 'neuwiedi' AND
  -- n.pr_acc IN 
  -- (SELECT j.pr_acc FROM pr_sn AS j WHERE j.sn_sp = 'moojeni' OR j.sn_sp = 'jararacussu');
SELECT * FROM pr_sn AS n 
WHERE n.sn_sp = 'jararaca' AND
  n.pr_acc NOT IN 
  (SELECT j.pr_acc FROM pr_sn AS j WHERE j.sn_sp = 'moojeni' OR j.sn_sp = 'jararacussu' OR j.sn_sp = 'neuwiedi' OR j.sn_sp = 'insularis');
