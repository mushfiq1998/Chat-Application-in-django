# Topic - Database
from channels.consumer import SyncConsumer, AsyncConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
import json
from .models import Group, Chat 

class MySyncConsumer(SyncConsumer):

    def websocket_connect(self, event):
        print('websocket connected...........', event)
        # Get default channel layer from a project
        print('Channel layer: ', self.channel_layer)
        # Get channel name
        print('channel name: ', self.channel_name)

        # In this case 'scope' is as like 'request' in method
        self.group_name = self.scope['url_route']['kwargs']['groupkaname']
        print('Group_name: ', self.group_name)

        '''group_add() is a async method. so we have to convert it into 
        sync to use inside SyncConsumer.'''
        # Add a channel to a new or existing group 
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
            )
        # Send request to server to accept connection
        self.send({
            'type': 'websocket.accept'
        })
    
    # It is called when Server receives data from client, 
    def websocket_receive(self, event):
        print('Message received from client......', event['text'])
        # Its type is string
        print('Type of message received from client: ', type(event['text']))
        # Converts json string into Python dict 
        data = json.loads(event['text'])
        print('Data.....', data)
        print('Type of Data.....', type(data))
        print('Chat message.....', data['msg'])
        # Find Group object
        group = Group.objects.get(name = self.group_name)
        # Create new Chat object
        chat = Chat(
            content = data['msg'],
            group = group
        )
        chat.save()

        '''Send message to the group.
        By this action data is not visible in website, to show data in
        frontend server must send data to client as done in the 
        chat_message method/handler, and client must send it to textarea.'''
        async_to_sync(self.channel_layer.group_send)(self.group_name,)
        {
            'type': 'chat.message',
            'message':event['text']
        }
    '''Write handler for the above event chat.message (. is changed to _)
    to send data to client to display data in frontend. When the above
    event is fired, this handler will be called'''
    def chat_message(self, event):
        print('Event.....', event)
        print('Actual data....', event['message'])
        # Its type is string
        print('Type of Actual data....', type(event['message']))
        # Send similar data to client
        self.send({
            'type': 'websocket.send',
            'text': event['message']
        })

    def websocket_disconnect(self, event):
        print('websocket disconnected........', event)
        print('Channel layer: ', self.channel_layer)
        print('channel name: ', self.channel_name)

        '''We have to discard a channel from group when we want to 
        disconnect our ws connection, as we add  a channel to group
        when we want to establish our ws connection.''' 
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
            )
        raise StopConsumer()


class MyAsyncConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print('websocket connected...........', event)
        # Get default channel layer from a project
        print('Channel layer: ', self.channel_layer)
         # Get channel name
        print('channel name: ', self.channel_name)

        self.group_name = self.scope['url_route']['kwargs']['groupkaname']
        
        # Add a channel to a new or existing group 
        await self.channel_layer.group_add(
            self.group_name, self.channel_name
            )
        # Send request to server to accept connection
        await self.send({
            'type': 'websocket.accept'
        })
    
    # It is called when Server receives data from client, 
    async def websocket_receive(self, event):
        print('Message received from client......', event['text'])
        # Its type is string
        print('type of message received from client: ', type(event['text']))
        data = json.loads(event['text'])
        print('Data.....', data)
        print('Type of Data.....', type(data))
        print('Chat message.....', data['msg'])
        # Find Group object
        group = await database_sync_to_async(Group.objects.get)(name = 
        self.group_name)
        # Create new Chat object
        chat = Chat(
            content = data['msg'],
            group = group
        )
        await database_sync_to_async(chat.save)()

        '''Send message to the group programmers.
        # By this action data is not visible in website, to show data in
        # frontend server must send data to client as done in the 
        chat_message method/handler, and client must send it to textarea.'''

        await self.channel_layer.group_send(
            self.group_name,
            {
            'type': 'chat.message',
            'message':event['text']
            }
        )
    '''Write handler for the above event chat.message (. is changed to _)
    to send data to client to display data in frontend. When the above event is fired, 
    this handler will be called'''
    async def chat_message(self, event):
        print('Event.....', event)
        print('Actual data....', event['message'])
        # Its type is sting
        print('Tyoe of Actual data....', type(event['message']))
        # Send similar data to client
        await self.send({
            'type': 'websocket.send',
            'text': event['message']
        })

    async def websocket_disconnect(self, event):
        print('websocket disconnected........', event)
        print('Channel layer: ', self.channel_layer)
        print('channel name: ', self.channel_name)

        '''We have to discard a channel from group when we want to 
        disconnect our ws connection, as we add  a channel to group
        when we want to establish our ws connection.''' 
        await self.channel_layer.group_discard(
            self.group_name, self.channel_name
            )
        raise StopConsumer()
