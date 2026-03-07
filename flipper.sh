for i in {1..8}; do
    python3 ./svgif.py -i ./quebec.pdf --pgnm "$i" -o ./quebec"$i".svg
    echo "$i"
done
