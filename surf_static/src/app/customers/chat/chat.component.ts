import {Component, OnInit} from '@angular/core';
import * as forge from 'node-forge';
import {encryptData} from "../../util/encryption/encryption_ras";
import {CryptoService} from "../../services/crypto/crypto.service";
import {Router} from "@angular/router";
import {NgForOf} from "@angular/common";
import {LocalDataService} from "../../services/local_data/local-data.service";
@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    NgForOf
  ],
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent implements OnInit{
  socket = new WebSocket('ws://'+this.localDataService.serverAddress+'/ws/chat/');
  messageList : any[] = []
  messages = {"command": "get_message_reply'", "type": 1, "messages": [{"chat_uuid": "bfd83b81-e041-4570-a822-65321f63b70b", "message_type": "text", "message_value": "Hello! How are you today?", "user_uuid": "954caf1d-2a63-44c7-8ff6-563430a22f7b", "timestamp": 1712059237.132833}, {"chat_uuid": "bfd83b81-e041-4570-a822-65321f63b70b", "message_type": "text", "message_value": "ur a giant pussy", "user_uuid": "a5fa4363-6710-4621-b745-9a7f6e6d7e89", "timestamp": 1712059618.898636}, {"chat_uuid": "bfd83b81-e041-4570-a822-65321f63b70b", "message_type": "img", "message_value": "idk how stage this fucking image,maybe url or data?", "user_uuid": "954caf1d-2a63-44c7-8ff6-563430a22f7b", "timestamp": 1712060435.746561}, {"chat_uuid": "bfd83b81-e041-4570-a822-65321f63b70b", "message_type": "text", "message_value": "The only pussy I know is your daughter's", "user_uuid": "954caf1d-2a63-44c7-8ff6-563430a22f7b", "timestamp": 1712060614.59922}, {"chat_uuid": "bfd83b81-e041-4570-a822-65321f63b70b", "message_type": "text", "message_value": "if u touch her ill fuckign end u", "user_uuid": "a5fa4363-6710-4621-b745-9a7f6e6d7e89", "timestamp": 1712060706.144846}]}
  constructor(private cryptoService: CryptoService,private localDataService:LocalDataService,private router: Router) {
    this.cryptoService = cryptoService;
    this.localDataService = localDataService;
  }
  ngOnInit(): void {
    if (this.cryptoService.session){
      for (const message of this.messages.messages){
        console.log(message)
        this.messageList.push(message)
      }
      const self = this;
      this.socket.onclose = function (e) {
        console.error('Chat socket closed unexpectedly');
      };
      this.socket.onmessage = function (e: { data: any; }) {
        const json = JSON.parse(e.data)
        const command =  json.command;
        if (command == "new_message"){
          self.messageList.push(json.message)
        }
      };
    }else {
      alert('你没登录')
      this.router.navigate(['/CustomersModule/login'])
    }
  }

  sendMessage(inputMessage: string) {
    const self=this;
    console.log('')
    this.socket.send(JSON.stringify({
      "command":"send_message",
      "session_id": self.cryptoService.session,
      "message":{
        "message_type": "text",
        "message_value": inputMessage
      }
    }))
  }
}
