1. Fixa partiklarna så dem ser lite bättre ut! Eventuellt att lägga til mer när saker och ting händer eller liknande.
2. gör "köp bonus blocket" mer likt resterande design av slotten.
3. implementera nya bilder, det ska vara flagor istället för sv, fr, de, en osv. Det ska också vara snyggare pilknappar när man rör sig i informationsrutan.
4. I fs så ska scatter symbolerna också blinka med partiklar om man får retrigger dvs 2st eller 3 st.
5. Free spins kvar ska gå ner en siffra direkt ner spinnet startar, inte efter spinnet är klart!
6. "s_scatter_hit.wav" should play when the symbol shows, right now it plays after all the reels have stopped.
7. något fortfarande konstigt med wildreel på reel 5. Den beter sig konstigt.
8. spara inte skärmen från fs till när man går tillbaka till base game. Det ska bara vara en random grid, dvs inte det sista spinnet från fs.




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