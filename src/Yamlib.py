class YammerConnection():

    def open(self):
        from httplib import HTTPSConnection
        connection = HTTPSConnection('www.yammer.com')
        return connection

    def listGroups(self, token):
        #Fetch a list of groups from the authorized Yammer network.

        connection = self.open()

        groups = []

        from simplejson import loads

        count=1
        while 1:
            connection.request('GET', '/api/v1/groups.json?access_token=' + token + '&page=' + str(count))
            raw = connection.getresponse()

            if raw.status == 200:   #error handling
                response = raw.read()
                #print response
                groups.extend(loads(response))
                count+=1

                if len(response) < 50:
                    connection.close()
                    return groups

            else:
                connection.close()
                return 'Error listing groups. HTTP Error ' + str(raw.status) + ': ' + str(raw.reason)

    def listUsers(self, token, pending='false'):
        #Fetch a list of users from the authorized Yammer network.

        from simplejson import loads

        connection = self.open()

        users = []
        
        count = 1       #for pagination
        while 1:
            if pending == 'true':
                connection.request('GET', '/api/v1/users.json?access_token=' + token + '&page=' + str(count) + '&show_pending=true')
            else:
                connection.request('GET', '/api/v1/users.json?access_token=' + token + '&page=' + str(count))

            raw = connection.getresponse()

            if raw.status == 200: #error handling
                response = raw.read()
                users.extend(loads(response))
                count += 1

                if len(response) < 50:      #if the api call hits the last page of users.
                    connection.close()
                    return users
            else:
                connection.close()
                return 'Error listing users. HTTP Error ' + str(raw.status) + ': ' + str(raw.reason)

    def listMessages(self, token):
        #Fetch a list of all messages from the authorized Yammer network.

        from simplejson import loads

        connection = self.open()

        messages = []

        connection.request('GET', '/api/v1/messages.json?access_token=' + token + '&limit=20')

        raw = connection.getresponse()

        if raw.status == 200: #error handling
            response = raw.read()
            messages = loads(response)
            connection.close()
#            messages.extend(loads(response))
            return messages

        else:
            connection.close()
            return 'Error listing users. HTTP Error ' + str(raw.status) + ': ' + str(raw.reason)

    def createGroup(self, token, groupName, private='false', listed='true'):
        #Create a group in Yammer. Pass group name, privacy setting and listing setting.

        from urllib import quote

        connection = self.open()

        groupNameURL = quote(groupName)  #convert group name to acceptable formatting for url

        if (private == 'true') & (listed == 'false'):       #private unlisted group
            connection.request('POST', '/api/v1/groups?access_token=' + token + '&name=' + groupNameURL + '&private=true&show_in_directory=0')
        elif (private == 'true') & (listed == 'true'):     #private listed group
            connection.request('POST', '/api/v1/groups?access_token=' + token + '&name=' + groupNameURL + '&private=true')
        elif (private == 'false') & (listed == 'false'):     #public unlisted group
            connection.request('POST', '/api/v1/groups?access_token=' + token + '&name=' + groupNameURL + '&show_in_directory=0')
        elif (private == 'false') & (listed == 'true'):     #public listed group
            connection.request('POST', '/api/v1/groups?access_token=' + token + '&name=' + groupNameURL)
        else:   #error
            connection.close()
            return 'Error: Invalid arguments for createGroup method'

        raw = connection.getresponse()
        connection.close()

        if raw.status == 201:   #error handling
            return 'Group created.'
        elif raw.status == 404:
            return 'Group already exists in this Yammer network or its parent Yammer network. (HTTP Error: ' + str(raw.status) + ' ' + str(raw.reason) + ')'
        else:
            return 'Error creating group. (HTTP Error ' + str(raw.status) + ' ' + str(raw.reason) + ')'
    
    def renameGroup(self, token, groupId, name):
        #Delete a group.
        
        from urllib import quote
        
        connection = self.open()
        connection.request('PUT', '/api/v1/groups/' + str(groupId) + '.json?access_token=' + token + '&name=' + quote(name))
        raw = connection.getresponse()
        connection.close()
        
        if raw.status == 200:
            return 'Group renamed.'
        else:
            return 'Error renaming group. (HTTP Error: ' + str(raw.status) + ' ' + raw.reason + ')'
    
    def createUser(self, token, email, fullname='', jobtitle='', location='', im_provider='', im_username='', work_telephone='', work_extension='', mobile_telephone='', summary=''):
        #Create a user in the authorized Yammer network. Only email is required for this method.
        #This also possibly adds a user to the community if you specify a community.
        
        from urllib import quote

        connection = self.open()
        connection.request('POST', '/api/v1/users.json?access_token=' + token + '&email=' + quote(email) + '&full_name=' + quote(fullname) + '&job_title=' + quote(jobtitle) + '&location=' + quote(location) + '&im_provider=' + quote(im_provider) + '&im_username=' + quote(im_username) + '&work_telephone=' + quote(work_telephone) + '&work_extension=' + quote(work_extension) + '&mobile_telephone=' + quote(mobile_telephone) + '&summary=' + quote(summary))
        raw = connection.getresponse()
        connection.close()
        
        if raw.status == 201:   #error handling
            return 'User created.'
        else:
            return 'Error creating user. HTTP Error ' + str(raw.status) + ': ' + str(raw.reason)

    def inviteUser(self, token, email):
        #Invite users to the authenticated network.
        
        connection = self.open()
        connection.request('POST', '/api/v1/invitations.json?access_token=' + token + '&email=' + email)
        raw = connection.getresponse()
        connection.close()
        
        if raw.status == 201: #error handling
            return 'Invite sent.'
        else:
            return 'Error inviting user. HTTP Error ' + str(raw.status) + ': ' + str(raw.reason)

    def listGroupsByUser(self, token, email):
        #List all the groups that a user is in.
        
        from simplejson import loads
        
        connection = self.open()

        connection.request('GET', '/api/v1/users/current.json?access_token=' + token + '&include_group_memberships=true')
        raw = connection.getresponse()

        if raw.status == 200: #error handling
            response = raw.read()
            groups = loads(response)
            connection.close()
            return groups
        else:
            connection.close()
            return 'Error listing groups by user. HTTP Error ' + str(raw.status) + ': ' + str(raw.reason)

    def listSubscriptionsByUser(self, token, userId):
        #List all the people that a user is following. Returns a list of user ids
        
        from simplejson import loads
        
        connection = self.open()
        
        subscriptions = []
        
        count = 1
        while 1:
            connection.request('GET', '/api/v1/users/followed_by/' + str(userId) + '.json?access_token=' + token + '&page=' + str(count))
            raw = connection.getresponse()
    
            if raw.status == 200: #error handling
                response = raw.read()
                newIds = loads(response)['meta']['followed_user_ids']
                subscriptions.extend(newIds)
                count+=1

                if len(newIds) < 50:                
                    connection.close()
                    return subscriptions
            else:
                connection.close()
                return 'Error retrieving subscriptions. HTTP Error ' + str(raw.status) + ': ' + str(raw.reason)

    def listFollowersByUser(self, token, userId):
        #List all the followers that a user has.
        #TODO: this doesn't seem to be working correctly. It returns a list that's in the ballpark of the correct quantity, but doesn't match up exactly right with GA

        from simplejson import loads
        
        connection = self.open()
        
        followers = []
        
        count = 1
        while 1:
            connection.request('GET', '/api/v1/users/following/' + str(userId) + '.json?access_token=' + token + '&page=' + str(count))
            raw = connection.getresponse()
    
            if raw.status == 200: #error handling
                response = raw.read()
                newIds = loads(response)['meta']['followed_user_ids']
                followers.extend(newIds)
                count += 1
                
                if len(newIds) < 43:
                    connection.close()
                    return followers
            else:
                connection.close()
                return 'Error retrieving followers. HTTP Error ' + str(raw.status) + ': ' + str(raw.reason)
    
    def groupFeed(self, token, groupId):
        #Show all messages in a group
        
        def getOldestId(messages):  #takes a list of messages and figures out the ID of the oldest one that was retrieved
            messages.reverse()
            lastId = messages[0]['id']
            return lastId
        
        from simplejson import loads
        
        connection = self.open()
        connection.request('GET', '/api/v1/messages/in_group/' + str(groupId) + '.json?access_token=' + token)
        raw = connection.getresponse()
        
        if raw.status != 200:
            connection.close()
            return 'Error retrieving group feed. HTTP Error ' + str(raw.status) + ': ' + str(raw.reason)
        else:
            response = raw.read()
            messages = loads(response)['messages']      #load in the first set of messages 
    
            if len(messages) == 20:                 #are there 20 or more messages?
                lastId = getOldestId(messages)      #if so, the get the ID of the 20th newest message
            
                while 1:            #page through the messages by using the 'older_than' request parameter for each HTTP request
                    connection.request('GET', '/api/v1/messages/in_group/' + str(groupId) + '.json?access_token=' + token + '&older_than=' + str(lastId))
                    raw = connection.getresponse()
                    
                    if raw.status == 200:   #error handling
                        response = raw.read()
                        newMessages = loads(response)['messages']       #here is the next set of older messages
                        messages.extend(newMessages)                    #append these messages to the cumulative list of messages in this group
        
                        if len(newMessages) < 20:                       #are we done yet? If there were less than 20 messages received from the API, then yes
                            connection.close()
                            return messages
                        else:                                           #if we're not done, then get the ID of the oldest message and repeat
                            lastId = getOldestId(newMessages)
                    else:                   #error handling
                        connection.close()
                        return 'Error retrieving group feed. HTTP Error ' + str(raw.status) + ': ' + str(raw.reason)
            else:                           #if there were never more than 20 messages in the group, then just return the original set of messages
                connection.close()
                return messages
        
    def getUserIdfromEmail(self, token, email):
        #Get a user's ID by entering their email
        
        connection = self.open()
        
        from simplejson import loads
        connection.request('GET', '/api/v1/users/by_email.json?access_token=' + token + '&email=' + email)
        raw = connection.getresponse()
        
        if raw.status == 200:   #error handling
            response = raw.read()
            user = loads(response)
            connection.close()
            return user[0]['id']
        else:
            connection.close()
            return 'Error retrieving User ID. HTTP Error ' + str(raw.status) + ': ' + str(raw.reason)

    def getUserfromUserId(self, token, userId):
        #Get a user object by entering a user's ID
        
        connection = self.open()
        
        from simplejson import loads
        
        connection.request('GET', '/api/v1/users/' + str(userId) + '.json?access_token=' + token)
        raw = connection.getresponse()
        
        if raw.status == 200:   #error handling
            response = raw.read()
            user = loads(response)
            connection.close()
            return user
        else:
            connection.close()
            return 'Error retrieving user. HTTP Error ' + str(raw.status) + ': ' + str(raw.reason)
    
    def getOAuth(self, token, userId, cKey):
        #Get a verified OAuth token for a user that will authorize the app that's running
        
        connection = self.open()
        
        from simplejson import loads
        
        connection.request('GET', '/api/v1/oauth/tokens.json?access_token=' + str(token) + '&user_id=' + str(userId) + '&consumer_key=' + cKey)
        raw = connection.getresponse()
        
        if raw.status == 200:       #error handling
            response = raw.read()
            oauths = loads(response)
            connection.close()
            return oauths
        else:
            connection.close()
            return 'Error retrieving oauth tokens. HTTP Error ' + str(raw.status) + ': ' + str(raw.reason)
    
    def createOAuth(self, token, userId, cKey):
        #Get a verified OAuth token for a user that will authorize the app that's running

        connection = self.open()

        from simplejson import loads

        connection.request('POST', '/api/v1/oauth.json?access_token=' + str(token) + '&user_id=' + str(userId) + '&consumer_key=' + cKey)
        raw = connection.getresponse()

        if raw.status == 200:
            response = raw.read()
            oauth = loads(response)
            return oauth
        else:
            connection.close()
            return 'Error creating oauth token. HTTP Error ' + str(raw.status) + ': ' + str(raw.reason)

    def joinGroup(self, token, groupId):
        #Join the user who's token is passed to a group.

        connection = self.open()
        connection.request('POST', '/api/v1/group_memberships.json?access_token=' + token + '&group_id=' + str(groupId))
        raw = connection.getresponse()
        connection.close()

        if raw.status == 201:   #error handling
            return 'Group joined.'
        else:
            return 'Error joining group. HTTP Error ' + str(raw.status) + ': ' + str(raw.reason)

    def postMessage(self, token, body):
        #Post a message to the Yammer feed
        
        from urllib import quote

        connection = self.open()        
        connection.request('POST', '/api/v1/messages.json?access_token=' + str(token) + '&body=' + quote(body))
        raw = connection.getresponse()

        if raw.status == 201:   #error handling
            return 'Message posted.'
        else:
            return 'Error posting message. HTTP Error ' + str(raw.status) + ': ' + str(raw.reason)

    def postGroupMessage(self, token, body, groupId):
        #Post a message to a Yammer group

        from urllib import quote

        connection = self.open()        
        connection.request('POST', '/api/v1/messages.json?access_token=' + str(token) + '&body=' + quote(body) + '&group_id=' + str(groupId))
        raw = connection.getresponse()

        if raw.status == 201:   #error handling
            return 'Message posted.'
        else:
            return 'Error posting group message. HTTP Error ' + str(raw.status) + ': ' + str(raw.reason)

    def postActivityText(self, token, body):
        #Post an activity to the Yammer feed

        from simplejson import dumps
        activity = {'type': 'text', 'text': body}
        activityjson = dumps(activity)

        connection = self.open()
        connection.request('POST', '/api/v1/streams/activities.json?access_token=' + str(token), activityjson, {'Content-Type': 'application/json'})
        raw = connection.getresponse()

        return raw.status

#    def getActivity(self, token):
        #Get the activity stream

#        from simplejson import loads
        