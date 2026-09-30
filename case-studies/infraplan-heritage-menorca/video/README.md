# 3DT × Infraplan: Heritage Reconstruction, reel da 30 secondi

Video verticale 9:16 (1080×1920, 30 fps) con sottotitoli incisi e musica generata, tratto dal case study *Heritage Reconstruction* (Scanfly EVO, Menorca).

- `out/3DT_Infraplan_Menorca_reel_30s.mp4`: il video finale (H.264 + AAC, -14 LUFS)
- `out/cover.jpg`: fotogramma da usare come cover
- `assets/`: logo, foto reali del rilievo e render delle nuvole di punti (`clouds.js`) estratti dal PDF del case study
- `index.html`: le scene. Le immagini delle nuvole di punti diventano particelle con profondità (parallasse); la mappa del porto di Maó è stilizzata
- `music.py`: colonna sonora a 120 BPM in La minore (Am–F–C–E), con i tagli sulle battute a 4, 10, 18 e 26 s
- `render.mjs`: esporta i fotogrammi con Chromium tramite Playwright e li codifica con ffmpeg

Tutti i dati vengono dal case study: 3 città (Maó, Ciutadella, Es Castell) e 3 isole; acquisizione in meno di 3 giorni, spostamenti in barca inclusi; precisione inferiore a 10 cm rispetto ai punti di controllo; SLAM in SmartProcessing Lidar; GNSS con RINEX da rete CORS.

## Rigenerare
```bash
npm install && pip install numpy scipy imageio-ffmpeg
python3 music.py out/music.wav
node render.mjs out/video_noaudio.mp4                          # oppure --stills 1,5,12 per le anteprime
ffmpeg -i out/video_noaudio.mp4 -i out/music.wav -map 0:v -map 1:a -c:v libx264 -preset slow -crf 21 \
  -maxrate 14M -bufsize 28M -pix_fmt yuv420p -af loudnorm=I=-14:TP=-1.5:LRA=7 -c:a aac -b:a 192k \
  -shortest -movflags +faststart out/3DT_Infraplan_Menorca_reel_30s.mp4
```
