#LEONARDO
#FLANDIA
#SM3201689

import numpy as n
import os
import sys
from PIL import Image
import json
import argparse

#python main.py <palette.json> <scene.json> <tiles.bin> <sprites.bin> <output.png>.
#      0             1              2           3           4           5

#n.set_printoptions(threshold=sys.maxsize) ##niente compressione debug

class blitter:
    def __init__(s, ref, idx):
        s.ref = ref
        s.idx = idx
    def applicaTRASF(s):
        SPRarr =sprites.ritorna()[s.idx]
        SPRarr = n.rot90(SPRarr, k = (s.ref.rot)/90)
        #print(s.ref.rot, s.idx, s.ref.Oflip, s.ref.Vflip, s.ref.x, s.ref.y)
        if s.ref.Oflip:
            SPRarr = n.fliplr(SPRarr)
            #print("oflip eseguito")
        if s.ref.Vflip:
            SPRarr = n.flipud(SPRarr)
        return SPRarr


class virtualVRAM:
    def __init__(s, path, argvn):
        s.path = path
        s.argvn = argvn
        s.pixels = []
    def leggiBIN(s): #legge un file binario
        with open(s.path, "rb") as fil:
            byte2in1 = n.fromfile(fil, dtype=n.uint8)

        pixelvect = n.empty(byte2in1.size * 2, dtype = n.uint8)        
        #scompone i 2 in 1 valori in due valori separati con bitwise >> 4
        pixelvect[0::2] = (byte2in1 >> 4) & 0x0F
        pixelvect[1::2] = byte2in1 & 0x0F
        #resizing ed addattamento
        if s.argvn == 3:
            s.pixels = pixelvect.reshape(8, 32, 8, 32).transpose(0, 2, 1, 3).reshape(64, 32, 32)
        elif s.argvn == 4:
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


class tonic: #sprite tonic, classe che definisce le proprietà di un sprite
    def __init__(s, x):
        s.id = x["id"]
        s.x = x["x"]
        s.y = x["y"]
        s.rot = x["rotation"]
        s.Oflip = x["flip_h"]
        s.Vflip = x["flip_v"]


class SceneParser:
    def __init__(s, path):
        s.path = path
        s.trasp = 0
        s.tile = []
        s.sprites = []
        
    def load(s):
        with open(s.path, "r") as file:
            data = json.load(file)
            
        s.trasp = data.get("transparent_index", 0)
        s.tile = data.get("tile_map", [])
        
        if "sprites" in data:
            for sprite in data["sprites"]:
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
        print(idXtrasp)
        canvARR = n.zeros((s.dim2pix, s.dim1pix, 3), dtype=n.uint8)
        ## sfondo con tiles
        for i in range(20): #20 colonne
            for j in range(15): #15 righe
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
            if xiniz > 575:
                xfinale = 639
            else:
                xfinale = xiniz + 64
            if yiniz > 415:
                yfinale = 479
            else:
                yfinale = yiniz + 64

            """
            print(yiniz, yfinale, xiniz, xfinale, colIDXrgb.shape, sprarr.shape)
            print(colIDXrgb[1, 1], sprarr[1, 1])
            for j in range(yiniz, yfinale):
                for k in range(xiniz, xfinale):
                    #print(sprarr[j-yiniz, k-xiniz], idXtrasp, j, k)
                    if sprarr[j-yiniz, k-xiniz] != idXtrasp:
                        canvARR[j+yiniz, k+xiniz] = colIDXrgb[j-yiniz, k-xiniz]
                        #print("cambio eseguito")\
            """

            for j in range (64): #su X
                for k in range (64): # su y
                    if sprarr[j, k] != idXtrasp:
                        canvARR[j+yiniz, k+xiniz] = colIDXrgb[j, k]
            

            #canvARR[yiniz:yfinale, xiniz:xfinale] = colIDXrgb





        imgfin = Image.fromarray(canvARR, "RGB")
        imgfin.save(s.path)




palette = palett(sys.argv[1])
palette.load()

#print(palette.colori) #DEBUG

canvas = SceneParser(sys.argv[2])
canvas.load()

sprites = virtualVRAM(sys.argv[4], 4)
sprites.leggiBIN()

tiles = virtualVRAM(sys.argv[3], 3)
tiles.leggiBIN()


print(len(sprites.ritorna()[0]))


renderer = RenderingPipeline()
renderer.renderIMG()



#print(n.array2string(tiles.ritorna()[0], separator=", "))     


"""
print(palette.colori)
for i in canvas.sprites:
    print(i.id, i.x, i.y, i.rotation, i.flip_h, i.flip_v)
"""

"""
canvax = Image.new("RGBA", (640, 480), (0,0,0,0))
print(canvax)
canvax.save("t1.png") """


