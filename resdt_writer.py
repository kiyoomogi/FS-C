"""
Created on Fri Jul 12 16:59:18 2024
 
@author: matthijsnuus
"""
# Define the values
NRES = 3
MDN = 1
RESTIM = [94878, 95200, 94878 + 3600 * 4]
DTM = [1, 30, 60]
 
# Format the header
header = "RESDT----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n"
header += f"{NRES:5d}{MDN:5d}\n"
 
# Format the RESTIM values
restim_lines = ''
for i in range(0, len(RESTIM), 3):
    restim_lines += ''.join([f"{v:10.1f}" for v in RESTIM[i:i+3]]) + '\n'
 
# Format the DTM values
dtm_lines = ''
for i in range(0, len(DTM), 3):
    dtm_lines += ''.join([f"{v:10.1f}" for v in DTM[i:i+3]]) + '\n'
 
# Combine all parts
resdt_block = header + restim_lines + dtm_lines
 
print(resdt_block)