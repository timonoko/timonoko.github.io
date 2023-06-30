f=open("twit.names","r")
for x in f:
    y=x.strip()
    print("<A href=https://twitter.com/%s>%s<A><p>"%(y,y))

