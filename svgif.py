#%%
import argparse
import os.path as path
import os
from time import gmtime, strftime

class Svgif():
    def __init__(self, args):
        self.setRenderParams()
        self.infile=args.i
        self.outfile=args.o
        self.Tmp=args.T
        if self.infile is None:
            print("-i infile is a required argument")
            quit()
        self.basename=path.basename(self.infile).rstrip(".pdf").rstrip(".svg")
        self.horizontal=not args.r
        self.pgnm=args.pgnm

        #infile management
        if self.infile.endswith(".pdf"):
            self.pdf_to_svg()
            if self.outfile.endswith(".svg"):
                return
            else:
                self.makenewpngdir()
                self.exportpngs()
        elif self.infile.endswith(".svg"):
            self.svgfile=self.infile
            self.makenewpngdir()
            self.exportpngs()
        else:
            self.pngdir=self.infile

        #outfile management
        if self.outfile.startswith("."):
            self.outfile="."+self.outfile[1:].split(".")[0] #in case of ./
        else:
            self.outfile=self.outfile.split(".")[0]

        self.exportmp4()
        self.exportmov()

    def setRenderParams(self):
        self.keyTol=0.9
        self.keyBlur=0.2
        self.rendRes=int(3*1080)

    def makenewpngdir(self):
        """
        subdirectory under svgif for the .pngs; checks for filename conflicts.
        """
        base_dir = f"./{basename}"
        if self.Tmp:
            base_dir=f"/Tmp/desalabg/pngRenders/{self.basename}"
        code = 0
        while True:
            pngdir = f"{base_dir}{code}"
            if not os.path.exists(pngdir):
                os.makedirs(pngdir)
                return pngdir
            code += 1

    def pdf_to_svg(self):
        pgnm=self.pgnm
        if pgnm is not None:
            pgnmstr=f" -f {pgnm} -l {pgnm}"
        else:
            pgnmstr=""
        if (self.outfile==None or self.outfile.endswith(".mp4")):
            if pgnmstr=="":
                self.svgfile="./"+self.basename+".svg"
            else:
                self.svgfile="./"+self.basename+f"_p{pgnm}.svg"
        else:
            self.svgfile=self.outfile
        os.system("pdftocairo -svg"+ pgnmstr+f" {self.infile} {self.svgfile}")

    def exportpngs(self):
        """
        08-15-2024
        Brutal svg creation method

        This file is very sad because I had to throw out all of my work
        that used path clipping when boox 'updated' to a worse svg convention
        """
        self.pngdir=self.makenewpngdir()
        print("pngdir : "+self.pngdir)
        pngdir=self.pngdir
        with open(self.svgfile) as file:
            source=file.read()
        # important parameters
        stride=30
        strokePause=3
        import os
        os.getcwd()

        # target filename
        g=0
        currentX=0
        currentY=0
        # %%


        headTag='''<g id="surface1">'''
        htIdx=source.find(headTag)+len(headTag)
        head=source[:htIdx]
        foot="</g>\n</svg>"
        lines=source[htIdx:].strip("\n").split("\n")[:-2]
        #%%


        def parse_cds(_instr):
            # parse coordinates
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
            # cut off the svg early
                outstr=outstr+"\n</g>"
            outstr=outstr+"\n"+foot
            # label the associated file
            outnum=str(len(output_list))
            while len(outnum)<6:
                outnum="0"+outnum
            framesvg = pngdir+"/"+\
                outnum+".svg"
            with open(framesvg, 'w') as writer:
                writer.write(outstr)
            defWidth=1404
            defHeight=1872
            
            w=int(3*defWidth)
            h=int(3*defHeight)
            pngcommand='rsvg-convert -w '+str(w)+' -h '+str(h)+' -b "white" '+framesvg+\
                ' -o "'+pngdir+"/"+outnum+'.png"'
            rmsvg="rm "+framesvg
            os.system(pngcommand)
            os.system(rmsvg)
            return outnum

        def detect_discontinuity(cds,current):
            eps=5
            return (abs(current[0]-cds[0])>eps\
                    or abs(current[1]-cds[1])>eps)

        output_list=[head]
        lines0=len(lines)
        poteau=[int(0.75*lines0), int(0.5*lines0), int(0.25*lines0),-1]
        outnum=0
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
            if len(lines)<poteau[0]:
                poteau=poteau[1:]
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
                print(f"lines {lines0-len(lines)}/{lines0}")
            outnum=produce_image(output_list,g)
        self.clonelastframe()

    def clonelastframe(self):
        """
        create copies of the last frame. Otherwise it ends abruptly and risks being trimmed.
        """ 
        lastfile=self.pngdir+"/"+sorted(os.listdir(self.pngdir))[-1]
        for i in range(240):
            unconflicted_name=lastfile.strip("png")[:-1]+"_"+str(i)+".png"
            os.system("cp "+lastfile+" "+unconflicted_name)

    def exportmp4(self):
        outpath=self.outfile+".mp4"
        pngdir=self.pngdir

        print(f"svgif.py: pngdir={pngdir} outpath={outpath}\n")
        resolution=int(3*1080)
        if self.horizontal:
            vfStr=f'-vf "scale=-1:{resolution},transpose=1"'
        else:
            vfStr=f"-vf scale=-1:{resolution}"
        print("output to "+outpath)
        finalcommand="""ffmpeg -framerate 60 -pattern_type glob -i '"""+\
            pngdir +'''/*.png' '''+vfStr+''' -r 30 -pix_fmt yuv420p '''+\
            " -y "+outpath
        #print(finalcommand)
        os.system(finalcommand)

    def exportmov(self):
        outpath=self.outfile+".mov"
        pngdir=self.pngdir

        print(f"svgif.py: pngdir={pngdir} outpath={outpath}\n")
        resolution=self.rendRes
        if self.horizontal:
            vfStr=f'-vf "scale=-1:{resolution},transpose=1,'+\
                f'colorkey=0xFFFFFF:{self.keyTol}:{self.keyBlur}"'
        else:
            vfStr=f"-vf scale=-1:{resolution},colorkey=0xFFFFFF:{self.keyTol}:{self.keyBlur}"
        print("output to "+outpath)
        finalcommand="""ffmpeg -framerate 60 -pattern_type glob -i '"""+\
            pngdir +'''/*.png' '''+vfStr+''' -c:v png -r 30 -pix_fmt rgba '''+\
            " -y "+outpath
        print("\n"+finalcommand+"\n")
        os.system(finalcommand)

    def delete_pngdir(self):
        if self.pngdir is not None:
            os.system("rm -r -f ./"+self.pngdir+"/")

parser = argparse.ArgumentParser()
parser.add_argument("-i", type=str) #input .pdf file
parser.add_argument("-o", type=str) #output .mov file
parser.add_argument("-r", action="store_true", default=False,
    help=" store_true flag; put -r to render a video which is the same orientation as the pngs."+\
        " This is a 90* counterclockwise rotation from the default, and will affect the render (not output metadata).")
parser.add_argument("-T",action="store_true", default=False)
parser.add_argument("--pgnm", type=int)
args=parser.parse_args()

if args.i:
    infile=args.i
else:
    print("args.infile==None; exiting")
    quit()

svgif=Svgif(args)
#svgif.delete_pngdir()
# %%
"""
worked:
ffmpeg -framerate 60 -pattern_type glob -i "output0/*.png" -vf scale=-1:1080 -r 30 -pix_fmt yuv420p ~/grego/Desktop/yuuki2/fusai.mp4
"""
# %%
