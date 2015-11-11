import positioning,appuifw,time,e32

positioning.select_module(positioning.default_module())
positioning.set_requestors([{"type":"service",
                             "format":"application",
                             "data":"test_app"}])

def getmyposition():
    print 'Reading GPS. Wait...'
    result = positioning.position()
    print 'all gps data: ', result    
    coordinates=result["position"]
    mylatitude = coordinates["latitude"]
    mylongitude = coordinates["longitude"]
    browserApp ='BrowserNG.exe'
    url = 'http://www.marinetraffic.com/ais/m/mob_map.aspx?&zoom=11&centerx='+str(mylongitude)+'&centery='+str(mylatitude)
    e32.start_exe(browserApp, ' "4 %s"' %url, 1)
    appuifw.app.set_exit()

getmyposition()
