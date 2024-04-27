import {Component, OnInit} from '@angular/core';
import * as forge from 'node-forge';
import {encryptData} from "../../util/encryption/encryption_ras";
import {CryptoService} from "../../services/crypto/crypto.service";
import {Router} from "@angular/router";
import {NgForOf} from "@angular/common";
import {LocalDataService} from "../../services/local_data/local-data.service";
import {FormsModule} from "@angular/forms";
@Component({
    selector: 'app-chat',
    standalone: true,
    imports: [
        NgForOf,
        FormsModule
    ],
    templateUrl: './chat.component.html',
    styleUrls: ['./chat.component.css']
})
export class ChatComponent implements OnInit{
    massageInputValue = "";

    socket = new WebSocket('ws://'+this.localDataService.serverAddress+'/ws/chat/');
    messageList : any[] = []
    constructor(private cryptoService: CryptoService,private localDataService:LocalDataService,private router: Router) {
            this.cryptoService = cryptoService;
            this.localDataService = localDataService;
    }
    ngOnInit(): void {
        if (this.cryptoService.session){
            this.socket.onopen = function () {
                const requestJson = {
                    "command":"get_message",
                    "session_id": self.cryptoService.session,
                    "channel_id":"aa6cd21b-7080-4e65-9059-8a6a8c303cbb",
                    "type":0
                }
                self.socket.send(JSON.stringify(requestJson));
            }
            const self = this;
            this.socket.onclose = function (e) {
                console.error('Chat socket closed unexpectedly');
            };
            this.socket.onmessage = function (e: { data: any; }) {
                const json = JSON.parse(e.data)
                const command = json.command;
                // console.log(command)
                if (command == "new_message"){
                    self.messageList.push(json.message)
                }else if(command == "get_message_result"){
                    self.messageList = json.messages
                }
            };
        }else {
            alert('你没登录')
            this.router.navigate(['/login'])
        }
    }

    sendMessage() {
        const self=this;
        this.socket.send(JSON.stringify({
            "command":"send_message",
            "session_id": self.cryptoService.session,
            "message":{
                "content":self.massageInputValue,
                "channel_id":"aa6cd21b-7080-4e65-9059-8a6a8c303cbb"
            }
        }))
        this.massageInputValue = ""
    }
}
