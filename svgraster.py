import re
import os


"""
Boox is extremely unpredictable in its output format.
I have to rewrite this from scratch every time there's an update!
"""

LINESTART='<path fill="none"'

FOOTER="</svg>"
class SvgRaster():
   
    def create_idxlist(self, svgstring:str, stride:int):
        """
        Reports the indices of bodylines that should be tied together.
        TODO: make more sophisticated. This is where errors should be caught + handled.
        """
        idxlist=[]
        tags=["<svg"]
        cnt=0
        all_lines=svgstring
        
        recognized_tags=["<g","<defs"]
        for tag in recognized_tags:
            closetag=f"{tag.replace("<","</")}>"
            all_lines=all_lines.replace(f"{closetag}",f"\n{closetag}")\
                .replace(f"\n\n{closetag}",f"\n{closetag}")
        all_lines=all_lines.split("\n")
        for i in range(len(all_lines)-2):
            line=all_lines[i]
            for recognized_tag in recognized_tags:
                if line.startswith(recognized_tag):
                    tags.insert(0,recognized_tag)
                    break
                if line==f'{recognized_tag.replace("<","</")}>':
                    tags.remove(recognized_tag)
                    break
            if line.startswith(LINESTART):
                if all_lines[i-1].startswith(LINESTART) or all_lines[i+1].startswith(LINESTART):
                    cnt+=1
            if cnt%stride==1:
                cnt=2
                idxlist.append({
                    "line_idx":i+1,
                    "frame":len(idxlist),
                    "footer":[tag.replace("<","</")+">" for tag in tags]}
                )
        return idxlist
    

    def __init__(self,
                svgfile=None,
                pngdir=None,
                outfile=None,
                horizontal=True,
                **kwargs):
        """SVG utility class for svgif2"""
        self.pngdir=pngdir
        self.outfile=outfile
        self.header=None
        self.svgfile=svgfile
        if not self.pngdir.endswith("/"):
            self.pngdir+="/"
        assert outfile is not None
        assert svgfile is not None
        assert self.pngdir is not None
        self.stride=kwargs.get("stride",500)
        self.defWidth=kwargs.get("svgwidth", 1404)
        self.defHeight=kwargs.get("svgheight", 1053)
        self.debug=kwargs.get("debug", False)

        self.horizontal=horizontal

        linestarts=[
            "</defs>\n"+LINESTART,
            ' viewBox="0 0 1404 1053">\n'+LINESTART,
            "</g>\n"+LINESTART,
            LINESTART]
        with open(svgfile, "r") as file:
            self.svgtext=file.read()
        for i in range(len(linestarts)):
            if linestarts[i] in self.svgtext:
                self.init_linestart=linestarts[i]
                print(f"Found {self.init_linestart}")
                break
        self.draw_frames()

    def draw_frames(self, idxs:list=None):
        from time import gmtime, strftime
        import os
        os.system(f"rm {self.pngdir}* >/dev/null 2>&1")
        os.getcwd()
        svgtext=self.svgtext
        stride=self.stride
        ### make a preview
        w=int(5*self.defWidth)
        h=int(5*self.defHeight)
        _preview_file=f"{self.pngdir}_preview.png"
        preview_cmd=f'rsvg-convert -w {w} -h {h} -b "white" '+\
                f'{self.svgfile} -o "{_preview_file}"'
        os.system(preview_cmd)
        if self.debug:
            print(preview_cmd)
        if idxs==None:
            idxs=self.create_idxlist(svgtext,stride)
        print(len(idxs))
        all_lines=self.svgtext.split("\n")
        _progresspoints = [int(len(idxs) * p / 8) for p in range(1, 9)]
        if self.debug:
            idxs=idxs[::len(idxs)//40]
        for i in range(len(idxs)):
            idx=idxs[i]
            if i in _progresspoints:
                print(f"SvgRaster.draw_frames: {i:06}/{len(idxs)}")
                print(idx)
            elif self.debug:
                print(idx)
                
            frame=idx["frame"]
            outstring="\n".join(
                all_lines[:idx["line_idx"]]\
                +idx["footer"]
                )
            # output file
            temp_svgpath=f"{self.pngdir}{frame:06}.svg"
            with open(temp_svgpath,"w") as file:
                file.write(outstring)
            # rasterize from {frame}.svg
            pngcommand=f'rsvg-convert -w {w} -h {h} -b "white" '+\
                f'{temp_svgpath} -o "{self.pngdir}{frame:06}.png"'
            rmsvg="rm "+temp_svgpath
            os.system(pngcommand)
            if not self.debug:
                os.system(rmsvg)
            
                
        os.system(f"rm {_preview_file}")
        for i in range(240):
            unconflicted_name=f"{self.pngdir}{frame:06}_{str(i)}.png"
            os.system(\
                f"cp {self.pngdir}{frame:06}.png {unconflicted_name}"\
                    )


        

def main():
    svgrender=SvgRaster(\
        svgfile="./iranmap4.svg",
        pngdir="./iranmap_2/",
        outfile="/mnt/c/Users/grego/Desktop/testout.mp4",
        stride=60,
        debug=False)
    

if __name__=="__main__":
    testline=main()

