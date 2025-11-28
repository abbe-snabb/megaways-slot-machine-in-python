1. Fixa partiklarna så dem ser lite bättre ut! Eventuellt att lägga til mer när saker och ting händer eller liknande.
2. Lägg till ljud
3. gör "köp bonus blocket" mer likt resterande design av slotten.
4. implementera nya bilder, det ska vara flagor istället för sv, fr, de, en osv. Det ska också vara snyggare pilknappar när man rör sig i informationsrutan.
5. I fs så ska scatter symbolerna också blinka med partiklar om man får retrigger dvs 2st eller 3 st.




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