#%%

import os
os.getcwd()
#%%
os.system("pdftocairo -svg ~/grego/Desktop/target.pdf ./yuukito.svg")
print(" svg in current dir ")
# %%
targetfile="./yuukito.svg"
with open(targetfile) as file:
    source=file.read()
headTag='''<g id="surface1">'''
htIdx=source.find(headTag)+len(headTag)
head=source[:htIdx]
foot="</g>\n</svg>"
lines=source[htIdx:].strip("\n").split("\n")[:-2]
#%%
def create_outdir():
    base_dir = "./output"
    code = 0
    while True:
        output_dir = f"{base_dir}{code}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            return output_dir
        code += 1

output_dir=create_outdir()
def parse_cds(_instr):
    instr=_instr.replace("L ","").strip(" ")
    instr=instr.split(" ")
    for i in range(len(instr)):
        instr[i]=float(instr[i])
    return instr

def snip(instr:str,tag0:str,tag1:str):
    t0=instr.find(tag0)+len(tag0)
    if t0==len(tag0)-1:
        return None
    t1=instr[t0:].find(tag1)+t0
    if tag0=='d="M ':
        return list(parse_cds(instr[t0:t1])), instr[t1:]
    return instr[t0:t1],instr[t1:]

def parse_line(line):
    _line=line
    if line.startswith("<g"):
        return 1,None
    elif line.startswith("</g>"):
        return -1,None
    else:
        cds,_line=snip(_line,'d="M ',' " ')
        return 0,cds

def produce_image(output_list,g):
    outstr="\n".join(output_list)
    if g>0:
        outstr=outstr+"\n</g>"
    outstr=outstr+"\n"+foot
    outnum=str(len(output_list))
    while len(outnum)<6:
        outnum="0"+outnum
    outdirname = output_dir+"/"+\
        outnum+".svg"
    with open(outdirname, 'w') as writer:
        writer.write(outstr)
    defWidth=1404
    defHeight=1872
    w=int(3*defWidth)
    h=int(3*defHeight)
    pngcommand='rsvg-convert -w '+str(w)+' -h '+str(h)+' -b "white" '+outdirname+\
        ' -o "'+output_dir+"/"+outnum+'.png"'
    rmsvg="rm "+outdirname
    os.system(pngcommand)
    os.system(rmsvg)

def detect_discontinuity(cds,current):
    eps=5
    return (abs(current[0]-cds[0])>eps\
             or abs(current[1]-cds[1])>eps)


output_list=[head]

g=0
stride=15
currentX=0
currentY=0
strokePause=2

while len(lines)>0:
    for ii in range(stride):
        if len(lines)==0:
            print("no more lines")
            break
        line=lines[0]
        val,parse=parse_line(line)
        if val!=0:
            g+=val
            lines=lines[1:]
        else:
            """if detect_discontinuity(parse,[currentX,currentY]):
                print(f"currentX{currentX},"\
                      +f" currentY{currentY}\n parse0{parse[0]} parse1{parse[1]}")
                currentX,currentY=parse[:2]
                for j in range(strokePause):
                    
                    output_list.append("<!-- discontinuity -->")
                    produce_image(output_list,g)
                break
            else:
                lines=lines[1:]"""
            lines=lines[1:]
        output_list.append(line)
    produce_image(output_list,g)

output_list.append(foot)
output="\n".join(output_list)
# %%

outname=output_dir.strip("./")
print("outname = "+outname)
os.system('''ffmpeg -framerate 60 -pattern_type glob -i "'''+\
        output_dir +'''/*.png" -r 30 -pix_fmt yuv420p ~/grego'''+\
        '''/Desktop/'yuuki mar2024'/'''+outname+'''.mp4''')