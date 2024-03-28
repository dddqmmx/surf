import {Component, OnInit} from '@angular/core';
import * as forge from 'node-forge';
import {encryptData} from "../../util/encryption/encryption_ras";
@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [],
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent implements OnInit{



  ngOnInit(): void {
    const self = this;
    const socket = new WebSocket('ws://127.0.0.1:8000/ws/chat/');
    socket.onclose = function (e) {
      console.error('Chat socket closed unexpectedly');
    };
    socket.onmessage = function (e: { data: any; }) {
      const json = JSON.parse(e.data)
      const command =  json.command;
      if (command == "init"){
        const public_key = json.public_key;
        const originalData = { 'command': 'sendMessage','message': 'Hello, WebSocket!' };
        const encryptedData = encryptData(JSON.stringify(originalData), public_key);
        if (typeof encryptedData === "string") {
          socket.send(encryptedData);
        } else {
          console.error("Encryption failed.");
        }
      }
    };
  }
}
