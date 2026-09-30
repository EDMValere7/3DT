# 3DT × NDAerial: reel da 30 secondi (prototipo)

Video verticale 9:16 (1080×1920, 30 fps) con sottotitoli incisi e musica generata. **Numeri e testi sono segnaposto**: vanno sostituiti con i dati reali del case study Scanfly XT.

- `out/3DT_NDAerial_reel_30s_DEMO.mp4`: il video finale (H.264 + AAC, -14 LUFS)
- `out/cover.jpg`: fotogramma da usare come cover
- `index.html`: tutte le scene (nuvola di punti procedurale, testi, sottotitoli, outro). Il tempo è guidato da `render(t)`
- `music.py`: colonna sonora a 120 BPM in Fa minore, con i tagli sulle battute a 4, 10, 18 e 26 s
- `render.mjs`: esporta i fotogrammi con Chromium tramite Playwright e li codifica con ffmpeg

## Dove modificare
- Sottotitoli: array `CAPS` in `index.html` (inizio, fine, testo)
- Numeri: `150` ettari (`#ha`), statistiche `240 / 3 / 25` in `stats()`
- Titoli: blocchi `#s1`…`#s4`
- Rimuovere il badge "DEMO": `#demo`

## Rigenerare
```bash
npm install && pip install numpy scipy imageio-ffmpeg
python3 music.py out/music.wav
node render.mjs out/video_noaudio.mp4                          # oppure --stills 1,5,12 per le anteprime
ffmpeg -i out/video_noaudio.mp4 -i out/music.wav -map 0:v -map 1:a -c:v libx264 -preset slow -crf 21 \
  -maxrate 14M -bufsize 28M -pix_fmt yuv420p -af loudnorm=I=-14:TP=-1.5:LRA=7 -c:a aac -b:a 192k \
  -shortest -movflags +faststart out/3DT_NDAerial_reel_30s_DEMO.mp4
```
