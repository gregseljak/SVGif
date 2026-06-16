#!/bin/bash
#for i in {25..30}; do
i=2
ffmpeg -framerate 60 -pattern_type glob -i "./iranmap_$i/*.png" \
-r 60 \
-vf "scale=1920:-2" \
-c:v libx264 -crf 12 -preset slow \
-pix_fmt yuv420p \
-y ~/grego/Videos/iran/iran_slides_02_1.mp4
#-y ~/grego/Videos/iran/iran_slides_"$i".mp4
#done