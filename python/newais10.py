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
    f=open('E:/ais.html','w')
    f.write('<script type="text/javascript">\nwidth=400;\nheight=400;\nborder=0;\nnotation=false;\nshownames=false;\nzoom=10;\nmaptype=0;\ntrackvessel=0;\nfleet="";\nremember=false;\n')
    f.write('latitude=')
    f.write(str(mylatitude))
    f.write('; \nlongitude=')
    f.write(str(mylongitude))
    f.write(';\n</script>\n<script type="text/javascript" src="http://www.marinetraffic.com/ais/embed.js"></script>\n')
    f.close()
    browserApp ='BrowserNG.exe'
    url = 'file:///E:/ais.html'
    e32.start_exe(browserApp, ' "4 %s"' %url, 1)
    appuifw.app.set_exit()

getmyposition()
