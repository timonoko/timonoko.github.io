#! /usr/bin/python
import sys,os,csv

def oikea(x):
    d=int(x/100.0)
    f=x-100.0*d
    return(d+f/60)

def towgs(x):
    y=x-0.19
    if int(y)%100>59:
        y=y-40.0
    return(y)

MapName=sys.argv[1]
MapName=os.path.splitext(os.path.basename(MapName))[0]
in8file=MapName+'.in8'
bmpfile=MapName+'.bmp'
jpgfile=MapName+"_ko.jpg"

if os.path.exists(jpgfile):
    print('done')
else:
    f = open(in8file, 'r')
    f.readline()
    f.readline()
    data=f.readline()
    data2=data[12:60]
    data3=data2.split(',')
    
    lelo=float(data3[0])
    dola=float(data3[1])
    rilo=float(data3[2])
    upla=float(data3[3])

    lelo=towgs(lelo)
    rilo=towgs(rilo)
    
    os.system('identify -format "%h" '+bmpfile+' >rapaa')
    f2 = open('rapaa', 'r')
    he=int(f2.readline())
    os.system('identify -format "%w" '+bmpfile+' >rapaa')
    f2 = open('rapaa', 'r')
    wi=int(f2.readline())
    
    jono="convert "+bmpfile
    
    pysty=int(lelo/5.0)*5+5

    if (pysty%100)>59:
        pysty=pysty+40

    while pysty<rilo:
        viiva=wi/(oikea(rilo)-oikea(lelo))*(oikea(pysty)-oikea(lelo))
        print(pysty,viiva)
        jono=jono+' -stroke red -draw "line '+str(int(viiva))+',0'+' '+str(int(viiva))+','+str(he)+'" -font arial -pointsize 72 -stroke red -fill red -draw \'text '+str(int(viiva))+','+str(he-100)+' "'+str(pysty)+'"\''
        pysty=pysty+5
        if (pysty%100)>59:
            pysty=pysty+40
                
    vaaka=int(dola/2)*2+2
    if (vaaka%100)>59:
        vaaka=vaaka+40

    while vaaka<upla:
        viiva=he-he/(oikea(upla)-oikea(dola))*(oikea(vaaka)-oikea(dola))
        print(vaaka,viiva)
        jono=jono+' -stroke red -draw "line 0,'+str(int(viiva))+' '+str(wi)+','+str(int(viiva))+'" -font arial -pointsize 72 -stroke red -fill red -draw \'text '+str(wi-300)+','+str(int(viiva))+' "'+str(vaaka)+'"\''
        vaaka=vaaka+2
        if (vaaka%100)>59:
            vaaka=vaaka+40
                           
    jono= jono+" "+jpgfile
    print(jono)
    os.system(jono)
                        
                            
                            
                            
                            
