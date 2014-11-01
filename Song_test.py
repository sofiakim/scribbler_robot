import math
#notes will be in the format <note><pitch><accidental>
#e.g. a4n, e5s, b2f

def freq(note):
    inc=math.pow(2,1.0/12)
    rfreq=16.35159783 #this is the frequency of c0, all other notes will be based on this
    #note that c4 is middle c
    ref={"c":0, "d":2, "e":4, "f":5, "g":7, "a":9, "b":11}
    fraw=rfreq*(math.pow(inc, ref[note[0]]))*(math.pow(2,int(note[1])))
    if note[2]=="s":
        fraw*=inc
    elif note[2]=="f":
        fraw/=inc
    return int(round(fraw))
    
songs = {"fur elise" : ((0.25, "e5n"),(0.25, "e5b"),(0.25, "e5n"),(0.25, "e5b"),(0.25, "e5n"),(0.25, "b4n"),(0.25, "d5n"),(0.25, "c5n"),(1,"c4n","a4n"))}

def playsong(song):
    for a in songs[song]:
        if len(a)==2:
            beep(a[0],freq(a[1]))
        else:
            beep(a[0],freq(a[1]),freq(a[2]))
        

            
def playnote(a):
    if len(a)==2:
        beep(a[0],freq(a[1]))
    else:
        beep(a[0],freq(a[1]),freq(a[2]))
        
playsong("fur elise")

