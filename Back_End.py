import asyncio
import json
import websockets

clients={}

async def userslist():
  users = []
  for key in clients.keys():
    users.append(key)
  users_message = json.dumps({
    'type': 'users',
    'message': users
  })
  print("Broadcasting:", users_message)
  await broadcast_msg(users_message)

async def enabledname(username,userId):
  accept_message = json.dumps({
    'type': 'accepted',
    'user':username,
    'message':'Username accepted',
    'userId':userId}
  )
  await broadcast_msg(accept_message)

async def disabledname(websocket, username,userId):
  reject_message = json.dumps({
    'type': 'reject',
    'user':username,
    'message':'Username already in use',
    'userId':userId}
  )
  await websocket.send(reject_message)

async def receive_msg(websocket, path):
  async for i in websocket:
    message = json.loads(i)
    if message['type'] == 'signup':
      if not clients.get(message['user']):
        clients[message['user']] = [websocket, message['userId']]
        await enabledname(message['user'], message['userId'])
        await userslist()
      else:
        await disabledname(websocket, message['user'], message['userId'])
    if message['type'] == 'message':
      if message['message'][0] == "~":
        user = message['message'].split()[0][1:]
        print(user)
        await private_msg(user, message)
      elif clients.get(message['user']):
        await broadcast_msg(i)

async def broadcast_msg(message):
  global clients
  disconnectedUsers = []
  for user in clients.keys():
    client = clients.get(user)[0]
    try:
      await client.send(message)
    except:
      disconnectedUsers.append(user)

  for user in disconnectedUsers:
    clients.pop(user)
  if len(disconnectedUsers) > 0:
    await userslist()

async def private_msg(user,message):
  global clients
  if clients.get(user):
    client = clients.get(user)[0]
    realMessage = message['message'].split()
    print(realMessage)
    realMessage = realMessage[1:]
    print(realMessage)
    message['message'] = " ".join(realMessage)
    print("To:",user,"; Message: ", message)
    try:
      await client.send(json.dumps(message))
    except:
      clients.pop(user)
      await userslist()

start_server = websockets.serve(receive_msg, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever() 