import math
import os
import android
import time
import urllib
droid=android.Android()

import termios, sys, os
TERMIOS = termios

def getkey():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] = new[3] & ~TERMIOS.ICANON & ~TERMIOS.ECHO
    new[6][TERMIOS.VMIN] = 1
    new[6][TERMIOS.VTIME] = 0
    termios.tcsetattr(fd, TERMIOS.TCSANOW, new)
    c = None
    try:
        c = os.read(fd, 1)
    finally:
        termios.tcsetattr(fd, TERMIOS.TCSAFLUSH, old)
    return c


#algorithms below are taken from http://www.viestikallio.fi/tools/kkj-wgs84.php#WGS-LALO

#
# Scan iteratively the target area, until find matching
# KKJ coordinate value.  Area is defined with Hayford Ellipsoid.
#
def KKJxy_to_KKJlalo(KKJ, ZoneNumber):
    MinLa = math.radians(59.0)
    MaxLa = math.radians(70.5)
    MinLo = math.radians(18.5)
    MaxLo = math.radians(32.0)

    for i in range(1, 35):
        DeltaLa = MaxLa - MinLa
        DeltaLo = MaxLo - MinLo
        LALO = {'La':MinLa + 0.5 * DeltaLa, 'Lo':MinLo + 0.5 * DeltaLo}

        kkjx,kkjy  = _kkj_latlon_to_kkj_xy((LALO['La'],LALO['Lo']), ZoneNumber)
        KKJt = {'X':kkjx, 'Y':kkjy}

        if KKJt['X'] < KKJ['X']:
            MinLa = MinLa + 0.45 * DeltaLa
        else:
            MaxLa = MinLa + 0.55 * DeltaLa

        if KKJt['Y'] < KKJ['Y']:
            MinLo = MinLo + 0.45 * DeltaLo
        else:
            MaxLo = MinLo + 0.55 * DeltaLo;
    return LALO


def KKJlalo_to_WGSlalo(KKJ):
    La = math.degrees(KKJ['La'])
    Lo = math.degrees(KKJ['Lo'])

    dLa = math.radians(  0.124867E+01       +
                     -0.269982E+00 * La +
                     0.191330E+00 * Lo +
                     0.356119E-02 * La * La +
                     -0.122312E-02 * La * Lo +
                     -0.335514E-03 * Lo * Lo ) / 3600.0
    dLo = math.radians( -0.286111E+02       +
                    0.114183E+01 * La +
                    -0.581428E+00 * Lo +
                    -0.152421E-01 * La * La +
                    0.118177E-01 * La * Lo +
                    0.826646E-03 * Lo * Lo ) / 3600.0

    WGS = {}
    WGS['La'] = KKJ['La'] + dLa
    WGS['Lo'] = KKJ['Lo'] + dLo

    return WGS

def KKJxy_to_WGSlalo(KKJ, zoneNumber):
    """KKJ = (x,y)"""
    x,y = KKJ
    KKJdict = {'X':x, 'Y':y}
    KKJ = KKJxy_to_KKJlalo(KKJdict, zoneNumber)
    WGSdict = KKJlalo_to_WGSlalo(KKJ)
    return WGSdict['La'],WGSdict['Lo']


def _convert_wgs84latlon_to_KKJ(coordinate_latlon):
    lat,lon = coordinate_latlon

    dla = math.radians(-0.124766E+01 + 0.269941E+00 * lat + \
                       -0.191342E+00 * lon + -0.356086E-02 * lat * lat + \
                        0.122353E-02 * lat * lon +
                        0.335456E-03 * lon * lon ) / 3600.0

    dlo = math.radians(0.286008E+02 + -0.114139E+01 * lat + \
                       0.581329E+00 * lon + 0.152376E-01 * lat * lat + \
                      -0.118166E-01 * lat * lon + \
                      -0.826201E-03 * lon * lon ) / 3600.0
    #print dla,dlo
           
    kkj_lat = math.radians(lat) + dla
    kkj_lon = math.radians(lon) + dlo   
    #print 'KKJ lat lon: %f, %f' % (kkj_lat,kkj_lon)
    return _kkj_latlon_to_kkj_xy((kkj_lat,kkj_lon),2)


def _kkj_latlon_to_kkj_xy(kkj_latlon, zone_number):
    kkj_lat, kkj_lon = kkj_latlon
    lon0 = math.radians(zone_number * 3.0 + 18.0)
    #print lon0
    lon = kkj_lon - lon0
    
    a  = 6378388.0            # Hayford ellipsoid
    f  = 1/297.0
    
    b  = (1.0 - f) * a
    bb = b * b   
    c  = (a / b) * a
    ee = (a * a - bb) / bb
    n = (a - b)/(a + b)
    nn = n * n
    
    cosLa = math.cos(kkj_lat)
    NN = ee * cosLa * cosLa
    
    LaF = math.atan(math.tan(kkj_lat) / math.cos(lon * math.sqrt(1 + NN)))
    cosLaF = math.cos(LaF)
    
    t   = (math.tan(lon) * cosLaF) / math.sqrt(1 + ee * cosLaF * cosLaF)

    A   = a / ( 1 + n )

    A1  = A * (1 + nn / 4 + nn * nn / 64)

    A2  = A * 1.5 * n * (1 - nn / 8)

    A3  = A * 0.9375 * nn * (1 - nn / 4)

    A4  = A * 35/48.0 * nn * n
    
    kkj_x = A1 * LaF - A2 * math.sin(2*LaF) + A3 * math.sin(4*LaF) - \
            A4 * math.sin(6*LaF)
    kkj_y = c * math.log(t + math.sqrt(1+t*t)) \
            + 500000.0 + zone_number * 1000000.0
    return kkj_x,kkj_y    
            



class MapCoordinate:
    """Defines coordinate."""

    def __init__(self, coordinate, coordinateSystem):
        """Creates MapCoordinate object.
        Parameters:
            coordinate - (x,y) Must be given in coordinateSystem format
            coordinateSystem - 'KKJ' or 'WGS84'"""
        self._coordinate = coordinate
        self._coordinateSystem = coordinateSystem
        
    def KKJ(self):
        if self._coordinateSystem == 'KKJ':
            return self._coordinate
        else:
            return _convert_wgs84latlon_to_KKJ(self._coordinate)

    def WGS84(self):
        if self._coordinateSystem == 'WGS84':
            return self._coordinate
        else:
            lat,lon = KKJxy_to_WGSlalo(self._coordinate, 2)
            return math.degrees(lat), math.degrees(lon)


class Grid:
    """Rectanle grid"""
    def __init__(self, size):
        """Creates grid. 
        Parameters:
            size - Size of the single tile in grid. Tuple (width,height)
        """
        self.size = size
        
    def getTiles(self, area):
        """Gets tiles from given rectangle area.
        Parameters:
            area - Wanted area. Rectangle.
        Returns:
            Rectangle array [R1,R2...]
        """
        topX = area.topLeftCoordinate().x / self.tileWidth() * self.tileWidth()
        topY= area.topLeftCoordinate().y/ self.tileHeight() * self.tileHeight()+self.tileHeight()
        bottomX = area.bottomRightCoordinate().x / self.tileWidth() * self.tileWidth()
        bottomY = area.bottomRightCoordinate().y/self.tileHeight()*self.tileHeight()
        tiles = []
        for y in range(topY,bottomY, -self.tileHeight()):
            for x in range(topX,bottomX+self.tileWidth(), self.tileWidth()):
                tiles.append(Rectangle((x,y),(x+self.tileWidth(),y-self.tileHeight())))
        return tiles        
            
    def tileWidth(self):
        """Gets the width of the single tile.
        Returns: Width of the tile"""
        return self.size[0]
        
    def tileHeight(self):
        """Gets the height of the single tile.
        Returns: Height of the tile"""
        return self.size[1]
        
class Point:
    """2D point"""
    
    def __init__(self, point=None):
        """Constructs Point.
        Parameters:
            point - (x,y)"""
        if point != None:
            self.x,self.y = int(point[0]),int(point[1])
        else:
            self.x = 0
            self.y = 0
        
    def getX(self):
        return self.x
        
    def setX(self, x):
        self.x = x
    
    def getY(self):
        return self.y

    def setY(self,y):
        self.y = y
        
    def __eq__(self,other):
        if isinstance(other,Point):
            return self.x == other.x and self.y == other.y
        elif isinstance(other, tuple):
            return self.x == other[0] and self.y == other[1]
        else:
            return False
            
    def __str__(self):
        return 'P(%d,%d)' % (self.x, self.y)
    
    x = property(getX,setX,None, 'X coordinate')
    y = property(getY,setY,None, 'Y coordinate')
    
class Rectangle:
    """Rectangle"""

    def __init__(self,topLeft,bottomRight):
        """Creates Rectangle.
        Parameters:
            topLeft - Top left coordinate tuple.
            bottomRight - Bottom right coordinate tuple.
        """
        self.topLeft = Point(topLeft)
        self.bottomRight = Point(bottomRight)
    
    def __eq__(self,other):
        if isinstance(other,Rectangle):
            return other.topLeftCoordinate() == self.topLeftCoordinate() and \
                other.bottomRightCoordinate() == self.bottomRightCoordinate()
        elif isinstance(other,tuple):
            return other == (self.topLeft,self.bottomRight)
        else:
            return False
            
    def topLeftCoordinate(self):
        """Returns top left coordinate Point"""
        return self.topLeft
        
    def bottomRightCoordinate(self):
        """Returns bottom right coordinate Point"""
        return self.bottomRight
        
    def bottomLeftCoordinate(self):
        """Returns bottom left coordinate Point"""
        return Point((self.topLeft.x,self.bottomRight.y))
        
    def topRightCoordinate(self):
        """Returns top right coordinate Point"""
        return Point((self.bottomRight.x,self.topLeft.y))
        
    def center(self):
        """Returns center coordinate Point"""
        centerX = (self.bottomRight.x - self.topLeft.x) / 2
        centerY = (self.bottomRight.y - self.topLeft.y) / 2
        return Point((centerX, centerY))
        
    def overlaps(self,rectangle):
        """Determines if other rectangle overlaps this rectangle.
        Parameters: 
            rectangle - Rectangle
        Returns:
            True: Rectangles overlaps eachother.
            False: Rectangles does not overlap eachother."""
        if rectangle.bottomRightCoordinate().y > self.topLeftCoordinate().y:
            return False
        if rectangle.topLeftCoordinate().x > self.bottomRightCoordinate().x:
            return False
        if rectangle.bottomRightCoordinate().x < self.topLeftCoordinate().x:
            return False
        if rectangle.topLeftCoordinate().y < self.bottomRightCoordinate().y:
            return False
        return True
        
    def move(self, delta):
        """Moves rectangle.
        Parameters:
            delta - (dx,dy)"""
        dx,dy = delta
        self.topLeft.x = self.topLeft.x+dx
        self.bottomRight.x = self.bottomRight.x + dx
        self.topLeft.y = self.topLeft.y + dy
        self.bottomRight.y = self.bottomRight.y + dy
        
    def __str__(self):
        return 'R[%s:%s]' % (self.topLeft,self.bottomRight)

# Coordinates per pixel for each zoom level
_CPP = {800000:200,400000:100,200000:50,80000:20,40001:10,40000:10,16000:4,8000:2,4000:1}

class MapPiece(object):
    
    def __init__(self, rect, screenLocation,zoomLevel):
        bottomY, bottomX, topY, topX = rect.bottomLeftCoordinate().x, \
            rect.bottomLeftCoordinate().y, rect.topRightCoordinate().x, \
            rect.topRightCoordinate().y
        if zoomLevel == 40001:
            nokozoom = 80000
        else:
            nokozoom = zoomLevel
        self.url = 'http://kansalaisen.karttapaikka.fi/image?request=GetMap&bbox=%d,%d,%d,%d&scale=%d&width=600&height=600&srs=NLSFI:kkj&styles=normal&lang=FI&lmid=1179938105236' % (bottomY, bottomX, topY, topX, nokozoom)
        self.image = None

        cpp = _CPP[zoomLevel]
        self.size = (600*cpp,600*cpp)
        self.x,self.y = int(screenLocation[0]), int(screenLocation[1])

class Map(object):

    def __init__(self, rects, center, centerLocationKKJ, size, zoomLevel):
        self.mapPieces = []
        self.center = center
        self.__centerLocation = centerLocationKKJ
        self.__rects = rects
        self._zoomLevel = zoomLevel
        self.size = size
        cpp = _CPP[zoomLevel]
        topNorth, topEast = self.__calculateTopLeftCoordinateOfRequestedMap(size)
        for r in rects:
            mapPieceTopEast = r.topLeftCoordinate().x
            mapPieceTopNorth = r.topLeftCoordinate().y
            x, y = (-(topEast-mapPieceTopEast)/cpp,(topNorth-mapPieceTopNorth)/cpp)
            self.mapPieces.append(MapPiece(r, (x,y), zoomLevel)) 

    def move(self, dx, dy):
        for map in self.mapPieces:
            map.x += dx
            map.y += dy
        xKKJ, yKKJ = self.__centerLocation
        cpp = _CPP[self._zoomLevel]
        xKKJ -= dy * cpp          
        yKKJ += dx * cpp
        self.__centerLocation = (xKKJ,yKKJ)
        self.center = MapCoordinate(self.__centerLocation, 'KKJ').WGS84()

    def toScreenCoordinates(self, position):
        xKKJ,yKKJ = self.__centerLocation
        wantedXKKJ, wantedYKKJ = MapCoordinate(position, 'WGS84').KKJ()
        dxKKJ = wantedXKKJ - xKKJ
        dyKKJ = wantedYKKJ - yKKJ
        cpp = _CPP[self._zoomLevel]
        dx = dxKKJ / cpp
        dy = dyKKJ / cpp
        width,height = self.size
        return dy+width/2, height/2-dx

    def __calculateTopLeftCoordinateOfRequestedMap(self, size):
        cpp = _CPP[self._zoomLevel]
        north,east = self.__centerLocation
        width,height= size
        topNorth = north+height*cpp/2
        topEast = east-width*cpp/2
        return topNorth,topEast  


class Karttapaikka(object):
        
    def __init__(self,zoomi):
#        self.zoomLevel = 40001
        self.zoomLevel = zoomi
        self.name = 'Karttapaikka'

    def getMap(self, centerLocation, size):
        centerKKJ = MapCoordinate(centerLocation, 'WGS84').KKJ()
        rects = self.__calculateMapArea(centerKKJ, size)
        return Map(rects, centerLocation, centerKKJ, size, self.zoomLevel)
    
    def zoomIn(self):
        zoomLevels = _CPP.keys()
        zoomLevels.sort(reverse=True)
        zoomIndex = zoomLevels.index(self.zoomLevel)
        if zoomIndex != len(zoomLevels)-1:
            zoomIndex += 1
        self.zoomLevel = zoomLevels[zoomIndex]
    
    def zoomOut(self):
        zoomLevels = _CPP.keys()
        zoomLevels.sort(reverse=True)
        zoomIndex = zoomLevels.index(self.zoomLevel)
        if zoomIndex != 0:
            zoomIndex -= 1
        self.zoomLevel = zoomLevels[zoomIndex]

    def __calculateMapArea(self, centerLocation, size):
        """Calculates map area.
        Parameters:
            mapSizeInPixels - (width,height)
            centerOfMap - KKJ coordinate tuple (north,east).
        Returns:
            geometry.Rectangle array containing KKJ coordinate rectangles."""
        widthInPixels,heightInPixels = size
        north,east = centerLocation
        cpp = _CPP[self.zoomLevel]
        wantedArea = Rectangle((east-widthInPixels/2*cpp,north+heightInPixels/2*cpp),\
            (east+widthInPixels/2*cpp,north-heightInPixels/2*cpp))
        return Grid((600*cpp,600*cpp)).getTiles(wantedArea)

if __name__ == '__main__':
    la=60
    lo=25
    zoomLevel=40001
    execfile('/mnt/sdcard/karttoja/karttapaikka/asetukset.py')
    g = Karttapaikka(zoomLevel)
    kursori='/mnt/sdcard/karttoja/kursori.png'
    key = '?'
    while key != "q":
	if key == 'g':
	    droid.startLocating()
	    loc = {}
	    while loc == {}:
		loc = droid.readLocation().result
	    try:
		n = loc['gps']
	    except KeyError:
		n = loc['network']
	    la = n['latitude']
	    lo = n['longitude']
	    droid.stopLocating()

        m = g.getMap((la,lo), (600,600))
        f = open('/mnt/sdcard/paskaa.html','w')
        f.write('<html>')
        for map in m.mapPieces:
            jemma='/mnt/sdcard/karttoja/karttapaikka/'+str(int(m._zoomLevel))
            if not os.path.exists(jemma):
                os.makedirs(jemma)
            nimi = jemma+'/'+map.url[len(r'http://'):].replace('/','A').replace('.','B').replace('?','C').replace(':','D').replace('&','E').replace('=','F')+".png"
            if not os.path.exists(nimi):
                print 'urlretrieve'
                urllib.urlretrieve( map.url , nimi )
            f.write('<div style="position: absolute; left:'+str(110+int(map.x))+'; top:'+str(250+int(map.y))+'">')
            f.write('<img src="'+nimi+'">')
            f.write('</div>\n')
        f.write('<div style="position: absolute; left:'+str(360)+'; top:'+str(500)+'">')
        f.write('<img src="'+kursori+'">')
        f.write('</div>\n')
        f.write('</html>\n')
        f.close()
        droid.viewHtml('/mnt/sdcard/paskaa.html')
        os.system('busybox clear')
#        what='la=%f lo=%f zoom=%d' % (round(la,4),(round(lo,4),m._zoomLevel)
        what='la=%f lo=%f zoom=%d' % (la,lo,m._zoomLevel)
        print what                            
	print 'Left Right Up Down Narrow Wider Gps Kp 200000 40001 8000 Quit?'
        key=getkey()
        if key=="k":
            urlu='http://kansalaisen.karttapaikka.fi/kartanhaku/koordinaattihaku.html' +\
                 '?srsName=EPSG:4258&showSRS=EPSG:4258&scale=16000&width=600&heigth=600&y=%f&x=%f'%(la,lo)
            droid.addOptionsMenuItem('Quit','Quit')
            droid.webViewShow(urlu)
            time.sleep(3)
            while  droid.eventPoll().result == []:
                key='q'
            key='q'
        if key=="n":
            g.zoomIn()
        if key=="w":
            g.zoomOut()
        if key=="r":
            lo=lo+(m._zoomLevel/500000.)
        if key=="l":
            lo=lo-(m._zoomLevel/500000.)
        if key=="u":
            la=la+(m._zoomLevel/1000000.)
        if key=="d":
            la=la-(m._zoomLevel/1000000.)
        if key=="2":
            g = Karttapaikka(200000)
        if key=="4":
            g = Karttapaikka(40001)
        if key=="8":
            g = Karttapaikka(8000)
    f=open('/mnt/sdcard/karttoja/karttapaikka/asetukset.py','w')
    f.write('la = '+str(la)+'\n')
    f.write('lo = '+str(lo)+'\n')
    f.write('zoomLevel = '+str(m._zoomLevel)+'\n')
    f.close()
    
