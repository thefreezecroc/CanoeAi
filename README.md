

![CanoeAi](https://github.com/user-attachments/assets/a45f8860-4d18-43a5-86e5-a9b523071f4e)

CanoeAI – Smart Technique Feedback System for Canoeing
CanoeAI is an innovative training support tool for sprint canoe athletes. It helps improve paddling technique by collecting movement data, analyzing it with machine learning, and providing real-time feedback using vibration.

📌 Project Summary
CanoeAI is a waterproof, paddle-mounted device that records motion data using a 9-axis IMU sensor embedded in an Arduino Nano 33 BLE. The collected data is used to detect correct and incorrect paddling techniques with a custom-trained machine learning model. When a technical error is detected, the system provides immediate haptic (vibration) feedback.

🧠 Core Features
Real-time motion tracking via 9DOF IMU (accelerometer, gyroscope, magnetometer)

Machine learning classification: stroke types like "correct pull", "push", and "incorrect move"

Instant feedback using vibration motor

Data logging & visualization for training analysis

Waterproof 3D-printed case for paddle mounting

BLE communication (planned) for future mobile integration

⚙️ Hardware Components
Arduino Nano 33 BLE (with integrated IMU)

9-axis IMU (accelerometer, gyroscope, magnetometer)

Vibration motor for feedback

Li-Po battery + charging module

3D-printed waterproof housing

Estimated cost: ~17,900 HUF

💻 Software & Data Processing
Data format: IMU data streamed via BLE in JSON format

Data processing: Python (NumPy, Pandas, Matplotlib), Madgwick filtering

Data storage: CSV format for model training

ML framework: TensorFlow Lite, optimized for microcontroller deployment

Visualization: Blender

🤖 Machine Learning Model
Model detects:

Correct stroke

Push motion

Incorrect technique

Input: Gravity-filtered acceleration data

Output: Real-time label for feedback

Deployed directly on the Arduino via TensorFlow Lite

🛠️ Future Plans
Mobile app with Bluetooth connection

Speed and force sensors

Full statistical analysis of training sessions

🧑‍🔬 Feedback from Experts
“The ability to correct errors immediately during training is essential – CanoeAI does this effectively.”
— György Vas, Canoe Coach

“This tool provides objective, sensor-based feedback, which is a big help especially for beginners.”
— Tamás Krecz, Canoe Coach

“Technical mistakes can cost podium spots – with CanoeAI, you can spot and fix them early.”
— Péter Soltész, World Champion Canoeist

“Even tiny undetectable flaws can ruin a race. CanoeAI could become a regular part of training.”
— Gergely István Lugosi, World Champion Canoeist

🔗 GitHub
Code and model repository:
https://github.com/thefreezecroc/CanoeAi

🇭🇺 README – CanoeAI
CanoeAI – Intelligens technikai visszajelző rendszer kenusportolóknak
A CanoeAI egy innovatív, kenus edzéstámogató eszköz, amely valós idejű visszacsatolással segíti az evezési technika fejlesztését. Szenzoros adatelemzést és gépi tanulást alkalmaz, hogy azonnal jelezze a helyes vagy hibás mozdulatokat a sportolónak.

📌 Projekt összefoglaló
A CanoeAI egy vízálló, kenu lapátra rögzíthető eszköz, amely egy Arduino Nano 33 BLE-be épített 9 tengelyes IMU szenzorral rögzíti a mozgásadatokat. Ezeket egy gépi tanulási modell elemzi, amely megkülönbözteti a helyes és helytelen evezési mozdulatokat. Hibás technika esetén az eszköz azonnali rezgő visszajelzést ad.

🧠 Főbb jellemzők
Valós idejű mozgáskövetés 9DOF IMU segítségével (gyorsulás, giroszkóp, magnetométer)

Gépi tanulási osztályozás: „helyes húzás”, „tolás”, „hibás mozdulat”

Azonnali visszajelzés vibrációs motorral

Adatrögzítés és -megjelenítés az edzések elemzéséhez

3D nyomtatott vízálló tok

BLE kapcsolat (tervezett) mobilos alkalmazáshoz

⚙️ Hardveres összetevők
Arduino Nano 33 BLE (beépített IMU-val)

9 tengelyes IMU szenzor

Vibrációs motor

Li-Po akkumulátor + töltőmodul

3D nyomtatott, vízálló tok

Becsült költség: ~17 900 Ft

💻 Szoftver és adatfeldolgozás
Adatformátum: IMU adatok BLE-n keresztül, JSON formátumban

Adatfeldolgozás: Python (NumPy, Pandas, Matplotlib), Madgwick-szűrés

Tárolás: CSV fájlok gépi tanuláshoz

ML keretrendszer: TensorFlow Lite, mikrokontrollerre optimalizálva

Vizualizáció: Blender

🤖 Mesterséges intelligencia modell
A modell felismeri:

Helyes húzás

Toló mozdulat

Hibás mozdulat

Bemenet: gravitációmentesített gyorsulási adatok

Kimenet: valós idejű visszajelzés

Telepítés: közvetlenül az Arduino-n, TensorFlow Lite segítségével

🛠️ Jövőbeli tervek
Mobilalkalmazás Bluetooth kapcsolattal

Sebesség- és erőmérő szenzorok

Teljes edzésanalízis statisztikákkal

🧑‍🔬 Szakértői visszajelzések
„Nagyon hasznos, ha a tanítvány azonnali visszajelzést kap a hibás mozdulatról.”
— Vas György, edző

„Objektív adatokkal lehet alátámasztani az instrukciókat – ez nagy segítség.”
— Krecz Tamás, edző

„Versenyen az apró hibák is sokba kerülhetnek – a CanoeAI időben segíthet javítani.”
— Soltész Péter, világbajnok kenus

„Akár észrevehetetlen hibák is befolyásolhatják az eredményt – ez az eszköz segíthet ezeket kiszűrni.”
— Lugosi Gergely István, világbajnok kenus

🔗 GitHub
A projekt forráskódja és modellje elérhető:
https://github.com/thefreezecroc/CanoeAi
