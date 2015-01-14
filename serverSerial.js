var http = require("http");
var url = require('url');
var fs = require('fs');
var io = require('/usr/local/lib/node_modules/socket.io');
//var sp = require('/home/pi/node_modules/serialport').SerialPort; 
//var SerialPort  = require('serialport2').SerialPort;
//var SerialPort = sp.SerialPort; 
//var sp = require('/home/pi/node_modules/serialport');
//var SerialPort = sp.SerialPort;
//var port = new SerialPort('/dev/ttyAMA1',{baudRate:57600, dataBits:8, parity:'none', stopBits:1,parser:sp.parsers.raw, buffersize :256}, false);
var i = 0;
var bigData = "";
var readData = '';
var cleanData = '';





var server = http.createServer(function(request, response){
    console.log('Connection');
    var path = url.parse(request.url).pathname;

    switch(path){
        case '/':
            response.writeHead(200, {'Content-Type': 'text/html'});
            response.write('hello world');
	    response.end();
            break;
        case '/stand2.html':
             fs.readFile(__dirname + path, function(error, data){
                if (error){
                    response.writeHead(404);
                    response.write("opps this doesn't exist - 404");
                }
                else{
                    response.writeHead(200, {"Content-Type": "text/html"});
                    response.write(data, "utf8");
                }
		response.end();
            });
             break;
        default:
            response.writeHead(404);
            response.write("opps this doesn't exist - 404");
            break;
    }
   
});

server.listen(8001);
var scktio  = io.listen(server);


var tcpSock = require('net');  
var client  = new tcpSock.Socket;  
var socket  = client.connect(7777);
var buffer = new Buffer(0, 'hex');

// listen for incoming data
socket.on("data", function(data){

    // a custom function for logging more readable binary
    

    // pack incoming data into the buffer
    buffer = Buffer.concat([buffer, new Buffer(data, 'hex')]);

    var dataBuf = new Buffer(data);
    var dataHex = dataBuf.toString('hex');

    scktio.sockets.emit('message', dataHex);
//       console.log('ok frame');  
//    console.log(dataHex);
})


//var sp = new SerialPort();
//sp.open('/dev/ttyAMA0', { // portName is instatiated to be COM3, replace as necessary
//   baudRate: 57600, // this is synced to what was set for the Arduino Code
//   dataBits: 8, // this is the default for Arduino serial communication
//   parity: 'none', // this is the default for Arduino serial communication
//   stopBits: 1 // this is the default for Arduino serial communication
   //flowControl: false // this is the default for Arduino serial communication
//});

// port.open();

// port.on('data', function(data){
//     var dataBuf = new Buffer(data);
//     var dataHex = dataBuf.toString('hex');

//     readData = readData + dataHex ;
//     if ( readData.length > 1600 && readData.indexOf('5a000040')>0) 
//     {
//       cleanData = readData.substring(readData.indexOf('5a000040')+2, readData.lastIndexOf('5a000040')+2);
//       readData = '';
//       scktio.sockets.emit('message', cleanData);
//       console.log('ok frame');  
//     }
// });




// scktio.sockets.on('connection', function(socket){
// 	setInterval(function(){
// 		socket.emit('date',{'date':new Date()});
// 	},1000);
// //	socket.emit('message', {'message':'hello world..'});
// 	console.log('ok socket');
// });







