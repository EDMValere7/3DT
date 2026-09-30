# 3DT × Infraplan: Heritage Reconstruction, reel da 45 secondi (IT + EN)

Video verticale 9:16 (1080×1920, 30 fps) con sottotitoli incisi e musica generata, tratto dal case study *Heritage Reconstruction* (Scanfly EVO, Menorca). È disponibile in due versioni, italiana e inglese, con testi scritti in ciascuna lingua (non tradotti riga per riga).

- `out/3DT_Infraplan_Menorca_reel_45s_IT.mp4` e `out/3DT_Infraplan_Menorca_reel_45s_EN.mp4`: i video finali (H.264 + AAC, -14 LUFS)
- `out/cover_IT.jpg` e `out/cover_EN.jpg`: fotogrammi da usare come cover
- `copy.js`: **tutti i testi** delle due lingue (titoli e sottotitoli con i loro tempi)
- `index.html`: le scene; la lingua si sceglie con `?lang=it` oppure `?lang=en`
- `engine.js`: il renderer delle nuvole di punti e la geometria (render reali trasformati in particelle, mappa stilizzata del porto di Maó)
- `music.py`: colonna sonora a 128 BPM (24 battute, 45 s) in La minore (Am–F–C–E); le sezioni iniziano a 7,5 / 18,75 / 30 / 39,4 s
- `render.mjs`, `build.sh`: esportazione dei fotogrammi con Chromium e codifica con ffmpeg

## Regola di leggibilità
Sullo schermo c'è **una sola cosa da leggere per volta**: o un titolo o un sottotitolo, mai entrambi. `render.mjs` si ferma con un errore se in `copy.js` un sottotitolo si sovrappone a un titolo.

## Dati (tutti dal case study)
3 città (Maó, Ciutadella, Es Castell) e 3 isole; acquisizione in meno di 3 giorni, spostamenti in barca inclusi; precisione inferiore a 10 cm rispetto ai punti di controllo; operatore in bici, a piedi e in barca; nessun attrezzo per passare dall'auto allo zaino.

## Rigenerare
```bash
npm install && pip install numpy scipy imageio-ffmpeg
./build.sh                       # entrambe le lingue
node render.mjs en --stills 2,10,20   # anteprime
```
