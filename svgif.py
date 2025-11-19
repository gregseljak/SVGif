import argparse
import os.path as path
import os
import re
from time import gmtime, strftime
from svgraster import SvgRaster


class Svgif():

    def __init__(self,args):
    # parse args and call render()
        if args.i is None:
            print("-i infile is a required argument")
            quit()
        else:
            self.infile=args.i
        self.basename=path.basename(self.infile).split(".")[0]
        if args.o is None:
            self.outfile=self.basename+".mp4"
            self._outfiletype="mp4" # default output filetype
        else:
            self.outfile=args.o
            ext_pattern = r'(?<=\.)[^.\\/:]+$' # file extension 
            self._outfiletype=re.search(ext_pattern, args.o)[0]
            assert self._outfiletype is not None
        self.horizontal=not args.r
        self.pgnm=args.pgnm
        self.stride=args.stride
    
        ### Render logic
        if self.infile.endswith(".pdf"):
            self.svgfile=self.pdf_to_svg()
        elif self.infile.endswith("/"):
            self.pngdir=self.infile
            self.export_mp4()
        else:
            self.svgfile=self.infile
        if self._outfiletype=="svg":
            quit()
        else:
            self.pngdir=None
            self._render()


    def pdf_to_svg(self):
        pgnm=self.pgnm # supports only one page; Use bash for queueing
        if pgnm is not None:
            pgnmstr=f" -f {pgnm} -l {pgnm}"
        else:
            pgnmstr=""
    
        if pgnmstr=="":
            svgfile="./"+self.basename+".svg"
        else:
            svgfile="./"+self.basename+f"_p{pgnm}.svg"
        os.system("pdftocairo -svg"+ pgnmstr+f" {self.infile} {svgfile}")
        return svgfile

    def export_mp4(self):
        outpath=self.outfile
        pngdir=self.pngdir

        print(f"svgrender.py: pngdir={pngdir} outpath={outpath}\n")
        resolution=int(1080*2)
        if self.horizontal:
            vfStr=f'-vf "scale=-1:{resolution},transpose=1"'
        else:
            vfStr=f"-vf scale=-1:{resolution}"
        print("output to "+outpath)
        finalcommand=\
            "ffmpeg -framerate 60 -pattern_type glob -i '"+\
            f"{pngdir}*.png' {vfStr} -r 30 -pix_fmt yuv420p "+\
            " -y "+outpath
        
        print(finalcommand+"\n\n")
        os.system(finalcommand)
        quit()

    def _render(self):
        self.pngdir=self._makenewpngdir()
        print(f" self.pngdir : {self.pngdir}")
        SvgRaster(svgfile=self.svgfile,
                  outfile=self.outfile,
                      pngdir=self.pngdir,
                      stride=self.stride).draw_frames()


    def _makenewpngdir(self):
        """
        subdirectory under svgif for the .pngs; checks for filename conflicts.
        """
        basename=self.basename
        base_dir = f"./{basename}"
        code = 0
        while True:
            pngdir = f"{base_dir}_{code}"
            if not os.path.exists(pngdir):
                os.makedirs(pngdir)
                return pngdir
            code+=1


### -------- -------- ------- ###
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", type=str) #input .pdf file
    parser.add_argument("-o", type=str) #output .mov file
    parser.add_argument("-r", action="store_true", default=False,
        help=" store_true flag; put -r to render a video which is"+\
            "the same orientation as the pngs. This is a 90* counterclockwise"+\
            " rotation from the default, "+\
            "and will affect the render (not output metadata).")
    parser.add_argument("--pgnm", type=int)
    parser.add_argument("--stride", type=int, default=30)
    args=parser.parse_args()

    if args.i:
        infile=args.i
    else:
        print("args.i (infile)==None; exiting")
        quit()

    svgif=Svgif(args)