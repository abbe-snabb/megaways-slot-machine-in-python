1. Se till så att GUI-logiken fortfarande är 100 % syncad mot min slot_math-fil
2. Lägg till animerade partiklar
3. Lägg till ljud
4. paytable meny knapp som man ska kunna trycka på närsomhelst för att få upp en meny med svart bakgrund typ 50% opacity med all info om vad varje symbol betalar 3way 4way och 5way, samt hur många scatter symboler som behövs för att trigga bonusen, samt maxwin: 5000x.
5. I bonus game fixa en cirkel där det står hur många spins kvar, samt en ruta med hur mycket man har vunnit totalt i bonusen, samt en ruta med det nuvarande spinnets vinst.
6. fixa en liten fotnot till saldo, vinst på spinnet, bet storlek/insats.
7. när saldot inte är tillräckligt för den bet size du vill spinna på i base-game så ska spin-knappen vara disabled.


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