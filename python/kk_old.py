import positioning,appuifw,time,e32

positioning.select_module(positioning.default_module())
positioning.set_requestors([{"type":"service",
                             "format":"application",
                             "data":"test_app"}])

def getmyposition():
    print 'Reading GPS. Wait...'
    result = positioning.position()
    #print 'all gps data: ', result    
    coordinates=result["position"]
    mylatitude = coordinates["latitude"]
    mylongitude = coordinates["longitude"]
    print 'mylatitude: ', mylatitude
    print 'mylongitude:', mylongitude
    s='<meta HTTP-EQUIV="REFRESH" content="0; url=http://kansalaisen.karttapaikka.fi/kartanhaku/koordinaattihaku.html?srsName=EPSG%3A4258&amp;showSRS=EPSG%3A4258&amp;scale=16000&amp;width=600&amp;heigth=600&amp;y=' + str(mylatitude) + '&amp;x=' + str(mylongitude) + '">'
    f=open('E:\\Activenotes\\goto.html','w')
    f.write(s)
    f.close()
    browserApp ='BrowserNG.exe'
    url = 'file:///E:/Activenotes/goto.html'
    e32.start_exe(browserApp, ' "4 %s"' %url, 1)
    appuifw.app.set_exit()


getmyposition()
