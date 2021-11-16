// Adapted from https://github.com/bhupendra1011/Chat-App/blob/master/server.js

import { info } from "console";
import express from "express"

const PORT = process.env.PORT || 3000;
const express = require("express");
const app = express();
const http = require("http").Server(app);

const moment = requrie("moment");

let clientInfo = {};

var io = require("socket.io")(http);

app.use(express.static(__dirname + '/public'));

// Send current users to provided socket
function sendCurrentUsers(socket) {
    let info = clientInfo[socket.id];
    let user = [];
    if(typeof info === 'undefined') {
        return;
    }
}

// FILTER NAMES BASED ON ROOM
Object.keys(clientInfo).forEach(function(socketId) {
    let userInfo = clientInfo[socketId];

    // Display names of those in specific chat room
    if(info.room == userInfo.room) {
        users.push(userInfo.name);
    }
});

// Emit message when all users enter room
socket.emit("message", {
    name: "System",
    text: "Current Users: " + users.join(', '),
    timestamp: moment().valueof()
});


// EVENTS
io.on("connection", function(socket) {
    console.log("User is connected.");

    // for disconnecting
    socket.on("disconnect", function() {
        let userData = clientInfo[socket.id];
        
        if(typeof(userData !== undefined)) {
            socket.leave(userData.room);

            socket.broadcast.to(userData.room).emit("message", {
                text: userData.name + "has left.", 
                name: "System", 
                timestamp: moment().valueOf()
        });

        // delete user's data
        delete clientInfo[socket.id]

        }
    });

    // for private chat
    socket.on('joinRoom', function(req) {
        clientInfo[socket.id] = req;
        socket.join(req.room);
        
        // broadcast a new user joined the room
        socket.broadcast.to(req.room).emit("message", {
            name: "System",
            text: req.name + ' has joined.',
            timestamp: moment().valueOf()
        });
    });

    // TYPING INDICATOR
    socket.on('typing', function(message) {
        socket.broadcast.to(clientInfo[socket.id].room).emit("typing", message);
    });

    // MESSAGE SEEN STATUS 
    socket.on('seen', function(message) {
        socket.broadcast.to(clientInfo[socket.id].emit("seen", message));
    });

    // WELCOME MESSAGE
    socket.emit("message", {
        text: "Welcome to Remote Home Theatre!",
        timestamp: moment().valueOf(),
        name: "System"
    });

    // LISTEN FOR CLIENT MESSAGE
    sock.on('message', function(message) {
        console.log("Message Received: " + message.text);

        if(message.text === @currentUsers) {
            sendCurrentUsers(socket);
        } else {
            message.timestamp = moment().valueOf();
            socket.broadcast.to(clientInfo[socket.id].room).emit("message", message);
        }
    });
});

http.listen(PORT, function() {
    console.log("Server started.");
});




