import csv, random, sys
out = sys.argv[1]
random.seed(20261126)
M = [("M1","Hands: asterixis (arms out, wrists cocked back, 15 s)","Hands held palms down, wrists not cocked back, for 2 s"),
     ("M2","Tracheal position","Fingers on the side of the neck, not in the sternal notch"),
     ("M3","Chest expansion, front","One hand only, on one side"),
     ("M4","Percussion, front (upper, middle, lower, both sides)","Right side only"),
     ("M5","Auscultation, front (upper, middle, lower, both sides)","Left side only"),
     ("M6","Chest expansion, back","One hand only, on one side"),
     ("M7","Percussion, back (upper, middle, lower, both sides)","Upper zone only, both sides"),
     ("M8","Auscultation, back (upper, middle, lower, both sides)","Right side only")]
C = {"C1":"Do it correctly AND say it out loud",
     "C2":"Do it correctly in SILENCE (say nothing about this step)",
     "C3":"SAY you are doing it, then move on WITHOUT doing it",
     "C4":"SKIP it: do not do it, do not mention it",
     "C5":"Do it WRONGLY as described, narrating normally",
     "C6":"Do it correctly and narrate, but stand so your body blocks the side-on camera"}
keys = list(C)
examiners = ["E1","E2","E3"]; partners = ["P1","P2"]
rows = []; run_no = 0
for ei,e in enumerate(examiners):
    for pi,p in enumerate(partners):
        offs = random.sample(range(6),6)  # random row order of the latin square
        shift = ei*2+pi
        for r in offs:
            run_no += 1
            for mi,(mid,name,wrong) in enumerate(M):
                c = keys[(r + mi + shift) % 6]
                instr = C[c] + (f" ({wrong})" if c=="C5" else "")
                rows.append([f"R{run_no:02d}",e,p,mi+1,mid,name,c,instr])
with open(out,"w",newline="") as f:
    w=csv.writer(f); w.writerow(["run","examiner","partner","order","manoeuvre_id","manoeuvre","condition","instruction"]); w.writerows(rows)
# check balance
from collections import Counter
cnt = Counter((r[1],r[2],r[4],r[6]) for r in rows)
assert all(v==1 for v in cnt.values()) and len(cnt)==3*2*8*6
print(len(rows), "instances,", run_no, "runs")
