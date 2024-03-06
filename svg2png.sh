# Function to prepend zeros to filenames
prepend_zeros() {
    local input="$1"
    local length="$2"
    printf "%0${length}d" "$input"
}

for file in *.svg; do
    # Get the filename without the extension
    filename=$(basename -- "$file")
    filename_no_extension="${filename%.*}"
    # Perform the conversion
    rsvg-convert -w 1024 -h 1024 -b "white" "$file" -o "./out_png/${filename_no_extension}.png"
done
