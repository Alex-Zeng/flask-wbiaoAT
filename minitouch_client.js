const WebSocketServer = require('ws').Server
  , http = require('http')
  , express = require('express')
  , path = require('path')
  , net = require('net')
  , app = express()

const PORT = process.env.PORT || 9003

app.use(express.static(path.join(__dirname, '/public')))

const server = http.createServer(app)
const wss = new WebSocketServer({ server: server })

wss.on('connection', function(ws) {
  console.info('Got a client')

  let stream = net.connect({
    port: 1111
  })

  stream.on('error', function() {
    console.error('Be sure to run `adb forward tcp:1111 localabstract:minicap`')
    process.exit(1)
  })



  stream.on('readable', tryRead)

  ws.on('close', function() {
    stream.end()
  })
})

export default server

