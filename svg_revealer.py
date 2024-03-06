#%%
#%cd ~/nihongo
import os
os.getcwd()
#%%

from IPython.display import SVG, display, HTML
with open("./yuukito_p1.svg") as file:
    svg = file.read()
def show_svg():
    display(SVG("./trial.svg"))
show_svg()

#%%
class SubStroke():
    def __init__(self,x0,x1,width,HexColor):
        self.x0=x0
        self.x1=x1
        self.strokewidth=width
        self.strokeLinecap='round'
        self.strokeLinejoin='round'
        self._matvalues=[1,0,0,-1,0,1872]
        self._HexColor=HexColor
    
    @property
    def HexColor(self):
        return "#"+str(self._HexColor).lstrip("#")


    def CoordString(self):
        return str(self.x0[0])+" "+str(self.x0[1])+" L "+str(self.x1[0])+" "+str(self.x1[1])

    def __str__(self) -> str:
        return '<path transform='\
            +'"matrix('+str(self._matvalues)[1:-1].replace(" ","")+')"'\
            +' stroke-width="'+str(self.strokewidth)+'"'\
            +' stroke-linecap="'+self.strokeLinecap+'"'\
            +' stroke-linejoin="'+self.strokeLinejoin+'"'\
            +' fill="none"'\
            +' stroke="'+self.HexColor+'"'\
            +' d="M'+self.CoordString()+'"/>'

class PenStroke():
    """full stroke; contains substroke"""
    ### TODO update to reflect new svg standards
    #<path style="fill:none;stroke-width:3.30999;stroke-linecap:round;
    #stroke-linejoin:round;stroke:rgb(0%,0%,0%);stroke-opacity:1;
    #stroke-miterlimit:10;" d="M 110.78125 1760.96875 L 110.875 1760.96875 "
    # transform="matrix(1,0,0,-1,0,1872)"/>

    def __init__(self, gString:str, StrokeID:int):
        self.gString = gString
        self.StrokeID=StrokeID
        self.subStrokes=[]
        self.ParseToSubstrokes()

    def PercToHex(self,ColorVals):
        
        rgb=(ColorVals.replace(",","")).split("%")
        for i in range(3):
            rgb[i]=int(rgb[i])
        return '{:02x}{:02x}{:02x}'.format(*rgb)

    def ParseToSubstrokes(self):
        self.subStrokes=[]
        for line in self.gString.split("\n")[1:-1]:
            width0=line.find('stroke-width:')+len('stroke-width:')
            # stroke width
            width1=line[width0:].find(';')+width0
            width = float(line[width0:width1])
            #color
            color0=line.find('stroke:rgb(')+len('stroke:rgb(')
            color1=line[color0:].find(")")+color0
            color=self.PercToHex(line[color0:color1])
            #coordinates
            cds0=line.find('d="M ')+len('d="M ')
            cds1=line[cds0:].find(' "')+cds0
            cds=line[cds0:cds1]
            cds=cds.replace("L ","").strip(" ")
            
            if "V" in cds:
                cds=cds.replace("V"," ")
                x0x,x0y,x1y=cds.split(" ")
                x1x=x0x
            elif "H" in cds:
                cds=cds.replace("H"," ")
                x0x,x0y,x1x=cds.split(" ")
                x1y=x0y
            else:
                x0x,x0y,x1x,x1y=cds.split(" ")
            x0=[float(x0x),float(x0y)]
            x1=[float(x1x),float(x1y)]
            self.subStrokes.append(SubStroke(x0,x1,width,color))
    def gHead(self):
        return '<g clip-path="url(#clip_'+str(self.StrokeID)+'">'
    def gFoot(self):
        return "</g>"
    def RevOrder(self):
        self.subStrokes=self.subStrokes[::-1]
    def __str__(self):
        return ("\n").join([self.gHead()]+self.subStrokes+[self.gFoot()])


class SVGRevealer():
    def __init__(self, SVGdir):
        self.SVGdir = SVGdir
        with open(self.SVGdir) as file:
            self.SVGsource = file.read()
        self.open_tag = """<g clip-path="""
        self.close_tag = """\n</g>"""
        self.StrokeStrings = []
        self.StrokeIdx = []
        self.StartTimes=[]
        self.Delays=[]
        self.Stride=[]
        self.duration=[]
        self.most_recent_frame=None

    def Preamble(self, vbDim=None):
        if vbDim==None:
            vbWidth=self.vbWidth
            vbHeight=self.vbHeight
        else:
            vbWidth,vbHeight=vbDim
        opener = '''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"'''\
             +''' version="1.1" width="'''\
                +self.cdWidth+'''pt" height="'''\
                +self.hdHeight+'''" viewBox="0 0 '''\
                +vbWidth+' '+vbHeight+'''">'''
        return opener
    
    def _last_frameIDX(self, stroke:PenStroke)->int:
        """
        for given stroke, find how many frames were used
        (ex. used for linking frame 1_0 to 0_n); find n
        """
        _lfi=int((len(stroke.subStrokes)-1)//self.Stride[stroke.StrokeID])
        if len(stroke.subStrokes)-1>_lfi*self.Stride[stroke.StrokeID]:
            return _lfi+1
        else:
            return _lfi

    def parse_source(self):
        """
        parse Strokes from SVGsource
        """
        self.PenStrokes=[]
        self.StrokeStrings = []
        self.StrokeIdx = []
        iStart, iStop = -50, 0
        while iStop+len(self.close_tag)+len(self.open_tag)< len(self.SVGsource):
            Start0 = iStop
            iStart = self.SVGsource[Start0:].find(self.open_tag)+Start0
            iStop = self.SVGsource[iStart:].find(self.close_tag)+iStart+len(self.close_tag)
            self.StrokeIdx.append((iStart,iStop))
            self.StrokeStrings.append(self.SVGsource[self.StrokeIdx[-1][0]:self.StrokeIdx[-1][1]])
            
            # (Once the class works)
            self.PenStrokes.append(\
                PenStroke(self.SVGsource[self.StrokeIdx[-1][0]:self.StrokeIdx[-1][1]],\
                    StrokeID=len(self.PenStrokes)))
            
            if len(self.StrokeStrings)>1:
                if self.StrokeIdx[-1][-1] == self.StrokeIdx[-2][-1]:
                    print("gMark loop has bug")
        
        self.SVGheader = self.SVGsource[:self.StrokeIdx[0][0]]
        self.Delays=[0.1 for i in self.PenStrokes]
        self.Stride=[10 for i in self.PenStrokes]
        self.duration=[0.0005 for i in self.PenStrokes]
        self._DimFromHeader()
    def _DimFromHeader(self):
        """
        read svg file header and extract dimensions
        """
        width0t='width="'
        width0 = self.SVGheader.find(width0t)+len(width0t)
        width1 = self.SVGheader[width0:].find('pt"')+width0
        self.cdWidth = int(self.SVGheader[width0:width1])
        height0t='height="'
        height0 = self.SVGheader.find(height0t)+len(height0t)
        height1 = self.SVGheader[height0:].find('pt"')+height0
        self.cdHeight = int(self.SVGheader[height0:height1])  
        vb0=self.SVGheader.find('viewBox="0 0 ')+len('viewBox="0 0 ')
        vb1=self.SVGheader[vb0:].find('"')+vb0
        print(self.SVGheader[vb0:vb1])
        self.vbWidth, self.vbHeight=(self.SVGheader[vb0:vb1]).split(" ")

    def writeHeader(self, WH=None, vbWH=None):
        """
        <svg xmlns="http://www.w3.org/2000/svg" 
        xmlns:xlink="http://www.w3.org/1999/xlink" 
        version="1.1" width="1404pt" height="1872pt" viewBox="0 0 1404 1872">
        """
        if WH is None:
            width, height = self.cdWidth, self.cdHeight
        else:
            width, height = WH
        if vbWH is None:
            vbWidth, vbHeight = self.vbWidth, self.vbHeight
        else:
            vbWidth, vbHeight = vbWH
        headerstring = '''<svg xmlns="http://www.w3.org/2000/svg" '''\
                        +'''xmlns:xlink="http://www.w3.org/1999/xlink" '''\
                        +'''version="1.1" width="'''+str(width)+'pt" '\
                        +'''height="'''+str(height)+'" '\
                        +'viewBox="0 0 '+str(vbWidth)+" "+str(vbHeight)+'">'
        return headerstring

        
    def head_AbsoluteRescale(self, factor):
        width0t='width="'
        width0 = self.SVGheader.find(width0t)+len(width0t)
        width1 = self.SVGheader[width0:].find('pt"')+width0
        width = int(self.SVGheader[width0:width1])
        height0t='height="'
        height0 = self.SVGheader.find(height0t)+len(height0t)
        height1 = self.SVGheader[height0:].find('pt"')+height0
        height = int(self.SVGheader[height0:height1])       
        Nwidth=str(int(factor*width))
        Nheight=str(int(factor*height))
        SVGheader = self.SVGheader[:width0]\
                            +Nwidth\
                            +self.SVGheader[width1:height0]\
                            +Nheight\
                            +self.SVGheader[height1:]
        return SVGheader
    

    def preview(self):
        mysvg = ("\n").join([self.head_AbsoluteRescale(0.1)]+self.StrokeStrings+["</svg>"])
        display(SVG(mysvg))
    
    def stroke_to_frames(self, stroke, trigger:int):
        """
        """
        FrameStrings=[]
        i=0
        strokeID=stroke.StrokeID
        stride=self.Stride[strokeID]
        Nframes=self._last_frameIDX(stroke)
        # TODO: fix next line
        #FrameDuration=int(self.duration[strokeID]/Nframes*10000)/10000*5
        FrameDuration=0.005
        for i in range(Nframes):
            if True:#i==0:
                # new stroke
                if True:#strokeID==0: # start
                    beginline=" "*4+'''begin="0.00s"\n'''
                    self.most_recent_frame="frame0_0"
                elif trigger==-1: # absolute time
                    beginline=" "*4+'''begin="'''+str(self.Delays[strokeID])+'s"\n'''
                    
                else: # pick up from previous
                    #PrevFinal = max(self._last_frameIDX(self.PenStrokes[strokeID-1]),1)
                    beginline=" "*4+'''begin="'''+self.most_recent_frame+'''.end + '''\
                                +str(self.Delays[strokeID])+'s"\n'
                    
            else:
                # continue stroke in progress
                beginline=" "*4+'''begin="'''+self.most_recent_frame+'''.end"\n'''

            self.most_recent_frame="frame"+str(strokeID)+"_"+str(i)
            cptHead = """<g clip-path="url(#clip_"""+str(strokeID)+"_"+str(i)+""")" opacity="0">"""
            animateBody = '''<animate attributeName="opacity"\n'''\
                            +" "*4+'''values="0;1"\n'''\
                            +" "*4+'''dur="'''+str(FrameDuration)+'''s"\n'''\
                            +" "*4+'''repeatCount="1"\n'''\
                            +" "*4+'''fill="freeze"\n'''\
                            +beginline\
                            +" "*4+"""id="frame"""+str(strokeID)+"_"+str(i)+""""/>"""
            FramePieces=[cptHead,animateBody]
            for ii in range(min(stride,int(len(stroke.subStrokes)-i*stride))):
                FramePieces.append(str(stroke.subStrokes[int(stride*i)+ii]))
            FramePieces.append("</g>")
            FrameStrings.append(("\n").join(FramePieces))
            
        return FrameStrings
    
    def Build(self):
        components = [self.writeHeader()]
        for stroke in self.PenStrokes:
            components.extend(self.stroke_to_frames(stroke, stroke.StrokeID-1))
        components.append("</svg>")
        outfile = ("\n").join(components)
        return outfile

#%%

SVR = SVGRevealer("./123.svg") # input

SVR.parse_source()
outdirname = "/mnt/c/Users/grego/Desktop/'SVG animator'/testanim.svg"
with open(outdirname, 'w') as writer:
    writer.write(SVR.Build())
#%%
SVR.preview()
# %%
