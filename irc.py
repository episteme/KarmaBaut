# currently only works with identds
# currently works with any message length
# future versions should limit to 5(?) chars or more

import socket
import time

# return dictionary key with lowest corresponding value
def oldestKey(dict):
    lowest = dict.keys()[0]
    for key in dict.keys()[1:]:
        if dict[key] < lowest:
            lowest = key
    return lowest

# return identd and number of times message was pasted
def countPoints(dict, oldest_Key):
    oldestMessage = oldest_Key.split(':')[1:]
    oldestIdentd = oldest_Key.split(':')[0]
    pointsAwarded = 0
    del dict[oldest_Key]
    for key in dict.keys():
         checkMessage = key.split(':')[1:]
         if checkMessage == oldestMessage:
             del dict[key]
             pointsAwarded += 1
    return oldestIdentd, pointsAwarded

# returns channel data is from
def dataDest(data):
    return ''.join(data.split(':')[:2]).split(' ')[-2]

# returns nick data is from
def dataNick(data):
    return data.split('!')[0].replace(':', '')

# returns message sent
def dataMsg(data):
    return '' .join(data.split(':')[2:])

def dataIdt(data):
    return ''.join((data.split('@')[0]).split('!')[1])

# connect to quakenet, trash MOTD, respond to first ping
network = 'se.quakenet.org'
port = 6667
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((network,port))
trash = irc.recv(4096)

irc.send('NICK KarmaBaut\r\n')
irc.send('USER KarmaBaut KarmaBaut Debian :KarmaBaut\r\n')
while True:
    data = irc.recv(4096)
    if data.find('PING') != -1:
        irc.send('PONG ' + data.split()[1] + '\r\n')
        break

#
irc.send('JOIN #bigcrew\r\n')

# note: points currently reset every script restart
# future version should save/load score file
dInfo = {}
dPoints = {}

# active loop
while True:
    data = irc.recv(4096)

    # respond to server pings to avoid timeout
    if data.find('PING') != -1:
        irc.send('PONG ' + data.split()[1] + '\r\n')

    # respond to score requests
    elif data.find('!score') != -1:
    # currently responds with all points/identds in dictionary order
    # future version should order scores
        nick = dataNick(data)
        dest = dataDest(data)
        print 'Replying to score request from ' + nick + ' in ' + dest
        if dest == '#bigcrew':
            returnstring = ''
            for key in dPoints.keys():
                returnstring += (key +' has '+ str(dPoints[key]) + ' points. ')
            if returnstring != '':
                irc.send('NOTICE ' + nick + ' : ' + returnstring + '\r\n')
            else:
                irc.send('NOTICE ' + nick + ' :Nobody has any points!\r\n')

    elif data.find('PRIVMSG') != -1:
        nick = dataNick(data)
        dest = dataDest(data)
        message = dataMsg(data)
        identd = dataIdt(data)
        if dest == '#bigcrew':
            dkey = identd + ':' + message
            currenttime = int(time.time())
            dInfo[dkey] = currenttime
            if len(dInfo) > 9:
                AssignPoints = countPoints(dInfo, oldestKey(dInfo))
                if AssignPoints in dPoints:
                    # award (number of times pasted)^2 points
                    dPoints[AssignPoints[0]] += (AssignPoints[1] ** 2)
                else:
                    dPoints[AssignPoints[0]] = (AssignPoints[1] ** 2)
