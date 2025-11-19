import re
import os

HEADER="""<svg xmlns="http://www.w3.org/2000/svg" """+\
    'xmlns:xlink="http://www.w3.org/1999/xlink" width="1404pt"'+\
    """ height="1872pt" viewBox="0 0 1404 1872" version="1.2">\n"""+\
    """<g id="surface1">\n"""+\
    """<use xlink:href="#image6" mask="url(#mask0)"/>"""
LINESTART='<path style=" stroke:none'
FOOTER="""</g>\n</svg>"""

            

class SvgRaster():
   
    def __init__(self,
                svgfile=None,
                pngdir=None,
                outfile=None,
                horizontal=True,
                **kwargs):
        """SVG utility class for svgif2"""
        self.pngdir=pngdir
        self.outfile=outfile
        
        if not self.pngdir.endswith("/"):
            self.pngdir+="/"
        assert outfile is not None
        assert svgfile is not None
        assert self.pngdir is not None
        self.stride=kwargs.get("stride",500)
        self.defWidth=kwargs.get("svgwidth", 1404)
        self.defHeight=kwargs.get("svgheight", 1872)
        self.horizontal=horizontal
        with open(svgfile, "r") as file:
            self.svgtext=file.read()
        self.draw_frames()

    def draw_frames(self):
        from time import gmtime, strftime
        stride=self.stride
        import os
        os.system(f"rm {self.pngdir}*")
        os.getcwd()
        svgtext=self.svgtext
        bodylines=svgtext[svgtext.find(LINESTART):].split("\n")
        write_pieces=[]
        currentline=[]
        _progresspoints=[4/1,4/2,4/3]
        frame=-1
        for line in bodylines:
            if not line.startswith(LINESTART):
                continue
            preamble=line[:line.find('d="')]+'d="'
            currentline=\
                re.split(r'(?=[A-Z])', line[len(preamble):])
                # Take [1:] because first index is ''
            write_pieces.append("\n"+preamble)

            while len(currentline)>0:
                frame+=1
                write_pieces.extend(
                    currentline[:min(stride,len(currentline))])
                currentline=currentline[min(stride,len(currentline)):]
                # assemble outstring and write temp {frame}.svg
                line_end=' "/>'
                if write_pieces[-1].endswith(line_end):
                    line_end=""
                outstring=svgtext[:svgtext.find(LINESTART)]\
                        +''.join(write_pieces)\
                        +line_end+'\n'+FOOTER
                temp_svgpath=f"{self.pngdir}{frame:05}.svg"
                with open(temp_svgpath,"w") as file:
                    file.write(outstring)
                # rasterize from {frame}.svg
                w=int(3*self.defWidth)
                h=int(3*self.defHeight)
                pngcommand=f'rsvg-convert -w {w} -h {h} -b "white" '+\
                    f'{temp_svgpath} -o "{self.pngdir}{frame:05}.png"'
                rmsvg="rm "+temp_svgpath
                os.system(pngcommand)
                os.system(rmsvg)
                
                if len(outstring)*_progresspoints[0]>len(svgtext):
                    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+\
                          f" : {4-len(_progresspoints)}/4")
                    _progresspoints=_progresspoints[1:]
                    if len(_progresspoints)==0:
                        outstring=[0]
                
    
        for i in range(240):
            unconflicted_name=f"{self.pngdir}{frame:05}_{str(i)}.png"
            os.system(\
                f"cp {self.pngdir}{frame:05}.png {unconflicted_name}"\
                    )


        

def main():
    svgrender=SvgRaster(\
        svgfile="./wp2.svg",
        pngdir="./wp2_0/",
        outfile="/mnt/c/Users/grego/Desktop/testout.mp4")
    svgrender.render()

if __name__=="__main__":
    testline=main()

