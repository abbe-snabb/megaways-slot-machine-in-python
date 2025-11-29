1. Eventuellt lägga till fler partiklar någonstans (osäker var)
2. implementera nya bilder, det ska vara flagor istället för sv, fr, de, en osv. Det ska också vara snyggare pilknappar när man rör sig i informationsrutan.




### UPDATE THE DEMO VERSION ON GITHUB ###
# once
python -m pip install pygame-ce pygbag

# every time you want to rebuild the web version:
python -m pygbag --build .
mkdir -p docs
cp -r build/web/* docs/
git add .
git commit -m "Update web build"
git push