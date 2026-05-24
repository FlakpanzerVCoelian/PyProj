#LEONARDO
#FLANDIA
#SM3201689

import numpy as n
import os
import sys
from PIL import Image
import json
import argparse
import pathlib

#python main.py <palette.json> <scene.json> <tiles.bin> <sprites.bin> <output.png>.
#      0             1              2           3           4           5

estFILE = [".py", ".json", ".json", ".bin", ".bin", ".png"]

#n.set_printoptions(threshold=sys.maxsize) ##niente compressione debug

#CLASSI PER LA GESTIONE DEGLI ERRORI


class FileERRATO(Exception):
    def __str__(s):
        return f"File assente o errato"

class FileTYPES(Exception):
    def __init__(s, idx, message):
        s.idx = idx
        super().__init__(message)
    def __str__(s):
        return f"Tipo file ERRATO"

class FileASSENTE(FileTYPES):
    pass

class blitter: #classe blitter, che esegue le operazioni sugli sprite, come rotazione e flip (VR e HL)
    def __init__(s, ref, idx): #inizializzazione
        s.ref = ref
        s.idx = idx
    def applicaTRASF(s): #applica le trasformazioni
        SPRarr =sprites.ritorna()[s.idx]
        SPRarr = n.rot90(SPRarr, k = (s.ref.rot)/90) #ruota
        #print(s.ref.rot, s.idx, s.ref.Oflip, s.ref.Vflip, s.ref.x, s.ref.y)
        if s.ref.Oflip: #flip
            SPRarr = n.fliplr(SPRarr)
            #print("oflip eseguito")
        if s.ref.Vflip:
            SPRarr = n.flipud(SPRarr)
        return SPRarr


class virtualVRAM: #classe virutal VRAM, legge i .bin e li trasforma in un np array
    def __init__(s, path, argvn): #inizializzazione
        s.path = path
        s.argvn = argvn
        s.pixels = []
    def leggiBIN(s): #legge un file binario
        with open(s.path, "rb") as fil:
            byte2in1 = n.fromfile(fil, dtype=n.uint8)

        if byte2in1.size != 32768: #controlla che il file sia di lunghezza corretta 
            raise FileERRATO("Grandezza file non e` uguale a 32768, ma e` {byte2in1.size} (Errore)")
        pixelvect = n.empty(byte2in1.size * 2, dtype = n.uint8)        
        #scompone i 2 in 1 valori in due valori separati con bitwise >> 4
        pixelvect[0::2] = (byte2in1 >> 4) & 0x0F
        pixelvect[1::2] = byte2in1 & 0x0F
        #resizing ed addattamento
        if s.argvn == 3: #se sono tiles li esporta come tiles, 64 di 32x32
            s.pixels = pixelvect.reshape(8, 32, 8, 32).transpose(0, 2, 1, 3).reshape(64, 32, 32)
        elif s.argvn == 4: #se sono sprites li esporta come sprites, 16 di 64x64
            s.pixels =  pixelvect.reshape(4, 64, 4, 64).transpose(0, 2, 1, 3).reshape(16, 64, 64)
    def ritorna(s):
        return s.pixels



class palett: #classe che implementa la color palette
    def __init__(s, path): #inizializza la classe
        s.path = path
        s.colori = []
    def load(s): #metodo che prende i colori definiti dalla scena e li carica in array
        with open(s.path, "r") as fil:
            s.colori = json.load(fil)
            s.colori = n.array(s.colori, dtype=n.uint8)
            if len(s.colori) != 16:
                print(f"Il file {s.path} dovrebbe contenere 16 colori, ma ne contiene {len(s.colori)} (errore)")
                sys.exit()



class tonic: #sprite tonic, classe che definisce le proprietà di un sprite
    def __init__(s, x):
        try:
            s.id = x["id"]
            s.x = x["x"]
            s.y = x["y"]
            s.rot = x["rotation"]
            s.Oflip = x["flip_h"]
            s.Vflip = x["flip_v"]
        except:
            print(f"Impossibile leggere il file {sys.argv[2]} (errore)")
            sys.exit()


class SceneParser:
    def __init__(s, path):
        s.path = path
        s.trasp = 400 #numero impossibile
        s.tile = []
        s.sprites = []
        
    def load(s):
        with open(s.path, "r") as file:
            jsonLETTO = json.load(file)


        try:
            s.trasp = jsonLETTO.get("transparent_index", 400)
            s.tile = jsonLETTO.get("tile_map", [])
        except:
            raise FileERRATO(".json non leggibile (errore)")
            print(f"Il file {s.path} non è leggibile (errore)")
            sys.exit()
        #print(s.trasp, s.tile)
        if s.trasp == 400 or s.tile == []:
            print(f"Il file {s.path} non è leggibile (errore)")
            sys.exit()
        
        if "sprites" in jsonLETTO:
            for sprite in jsonLETTO["sprites"]:
                nuovoOGG = tonic(sprite)
                s.sprites.append(nuovoOGG)
    def ritorna(s, i):
        return s.sprites[i]
        
class RenderingPipeline:
    dim1pix = 640 #20 colonne, LARGHEZZA
    dim2pix = 480 #15 righe, ALTEZZA
    def __init__(s):
        s.path = sys.argv[5]
    def renderIMG(s):
        idXtrasp = canvas.trasp
        #print(idXtrasp) ##debug
        canvARR = n.zeros((s.dim2pix, s.dim1pix, 3), dtype=n.uint8)
        ## sfondo con tiles
        for i in range(20): #20 colonne, X
            for j in range(15): #15 righe, Y
                colIDXv = tiles.ritorna()[canvas.tile[j][i]]
                #print(colIDXv, colIDXv.ndim)
                colIDXrgb = palette.colori[colIDXv]
                xiniz = i * 32
                yiniz = j * 32
                xend = xiniz + 32
                yend = yiniz + 32
                canvARR[yiniz:yend, xiniz:xend] = colIDXrgb
        #aggiunta sprites sopra
        for i in canvas.sprites:
            #print(i.id, i.x, i.y, i.rot, i.Oflip, i.Vflip, i)
            sprarr = blitter(i, i.id).applicaTRASF()
            colIDXv = sprarr
            colIDXrgb = palette.colori[colIDXv]
            #ancore
            xiniz = i.x 
            yiniz = i.y 
            durataLOOPX = 64
            durataLOOPY = 64
            if xiniz > 575:
                xfinale = 639
                durataLOOPX = 639 - xiniz +1
            else:
                xfinale = xiniz + 64
            if yiniz > 415:
                yfinale = 479
                durataLOOPY = 479 - yiniz +1
            else:
                yfinale = yiniz + 64
            print(durataLOOPX, durataLOOPY, xiniz, yiniz, xfinale, yfinale)
            for j in range (durataLOOPY): #su Y
                for k in range (durataLOOPX): # su X
                    if sprarr[j, k] != idXtrasp:
                        canvARR[j+yiniz, k+xiniz, ] = colIDXrgb[j, k]


        try:
            imgfin = Image.fromarray(canvARR, "RGB")
            imgfin.save(s.path)
            print(f"Operazione eseguita con successo!! \nImmagine salvata in {s.path}")
        except:
            print(f"Errore nel salvataggio di {s.path} (errore)")
            sys.exit()
        
def controllafiles():
    for i in range(6):
        try:
            pat = pathlib.Path(sys.argv[i])
            if pat.suffix != estFILE[i]:
                raise FileTYPES(i, "Tipo file ERRATO")
            try:
                f = open(sys.argv[i], "r")
                f.close()
            except:
                print(f"Errore durante la lettura di {sys.argv[i]}")
        except:
            raise FileASSENTE(i, "File assente (errore)")
            print(f"Come argomento {i+1} divrebbe esserci un {estFILE[i]}, ma non è presente nessun argomento")
            sys.exit()
      
try:
    controllafiles()
except FileTYPES as err:
    print(f"{err} (errore)")
    print("In quella posizione ci si aspettava un file di tipo", estFILE[err.idx])
    print("Uso corretto: python main.py <palette.json> <scene.json> <tiles.bin> <sprites.bin> <output.png>")
    sys.exit()

palette = palett(sys.argv[1])
palette.load()

#print(palette.colori) #DEBUG

canvas = SceneParser(sys.argv[2])
canvas.load()

sprites = virtualVRAM(sys.argv[4], 4)
sprites.leggiBIN()

tiles = virtualVRAM(sys.argv[3], 3)
tiles.leggiBIN()


#print(len(sprites.ritorna()[0]))

renderer = RenderingPipeline()
renderer.renderIMG()
