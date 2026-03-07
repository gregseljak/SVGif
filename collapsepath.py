import re
import os
import numpy as np
import matplotlib.pyplot as plt
import svgraster
LINESTART=svgraster.LINESTART

class CollapsePath():

    def __init__(self, infile):
        self.infile=infile
        self.filtersize=5
        assert infile.endswith(".svg")
        with open(infile,"r") as file:
            self.svgtext=file.read()
        
    def spatial_filter(self, cds, size=5):
        """Smoothen things a little"""
        size=min(size,len(cds))
        window=np.ones(size)/size
        smooth=np.convolve(cds,window,"same")
        normalization=np.arange(1,size,1)[::-1]
        for i in range(size-1):
            smooth[i]*=normalization[i]
            smooth[-i-1]*=normalization[i]
        return smooth[::4][:-1]

    def collapse_path(self):
        strokewidth=2
        svgtext=self.svgtext
        bodylines=svgtext[svgtext.find(LINESTART):].split("\n")
        
        header=svgtext[:svgtext.find(LINESTART)]
        firstpathtag='<g id="surface1">'
        header=header.replace(firstpathtag,
                       '  <rect width="100%" height="100%"'+\
                        ' fill="white" />\n'+firstpathtag)
        footer="\n</g>\n</svg>"
        newlines=[]
        for line in bodylines:
            coordinates=[]
            if not line.startswith(LINESTART):
                continue
            preamble=line[:line.find('d="')]+'d="'
            preamble=preamble.replace("stroke:none",
                                      f"stroke:black;stroke-width:{strokewidth};fill:none")
             #TODO: sophisticate with regex
            preamble=preamble.replace(\
                ";fill-rule:nonzero;fill:rgb(0%,0%,0%);fill-opacity:1","")
            coordinates=self._coords_from_txt(line[len(preamble):-len('"\>')])
            newlines.append(preamble+"M "\
                            +"L ".join(coordinates[1:])\
                            +'"/>')

            outfile=self.infile.replace(".svg","_flat.svg")
            outstring=header+"\n".join(newlines)+footer
            with open(outfile,"w") as file:
                file.write(outstring)

    def _coords_from_txt(self, looptext):
        """should return ['X1 Y1','X2 Y2',...]"""
        loops=looptext.split("M")
        X=[]
        Y=[]
        for i in range(len(loops)):
            loop=loops[i]
            coords = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?",
                            "L"+loop)
            coords=[float(coord) for coord in coords]
            if len(coords)>=2:
                X.append(np.mean(coords[::2]))
                Y.append(np.mean(coords[1::2]))
        filtersize=self.filtersize
        smoothX=np.round(self.spatial_filter(X,filtersize),6)
        smoothY=np.round(self.spatial_filter(Y,filtersize),6)
        if np.isnan(smoothX).any():
            return [""]
        output=[]
        
        plt.plot(X[1:],-1*np.array(Y[1:]),color="C0")
        plt.plot(smoothX[1:],-1*smoothY[1:],color="C1")
        for i in range(len(smoothX)):
            output.append(str(smoothX[i])+" "+str(smoothY[i]))
        return output




def main():
    collapse=CollapsePath("./grenoble25tunnel.svg")
    collapse.collapse_path()
    plt.show()
if __name__=="__main__":
    main()