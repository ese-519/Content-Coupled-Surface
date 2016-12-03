var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
const dgram = require('dgram');
const server = dgram.createSocket('udp4');
const server_inf = dgram.createSocket('udp4');
// var HOST = '127.0.0.1'
// var PORT = 4560
var message = new Buffer('getdata')
var gotReply = false
var replyFromServer = ''

app.get('/', function(req, res){
  res.sendFile(__dirname + '/index.html');
});

io.on('connection', function(socket) {
	console.log('Got connection')
  	socket.on('getdata', function(msg) {
  		// when the node server receives something from the client
  });
});

server.on('message', function (message, remote) {
	// console.log('Got message from the main server: ', message.toString())
	io.emit('putdata_map', message.toString());
});

server_inf.on('message', function (message, remote) {
	// console.log('Got message from the main server: ', message.toString())
	io.emit('putdata_id', message.toString());
});

http.listen(3000, function(){
  console.log('listening on *:3000');
});

server.bind(4560)
server_inf.bind(4565)





