import {Component, OnInit} from '@angular/core';
import * as forge from 'node-forge';
import {encryptData} from "../../util/encryption/encryption_ras";
import {CryptoService} from "../../services/crypto/crypto.service";
import {ActivatedRoute, Router} from "@angular/router";
import {NgForOf} from "@angular/common";
import {LocalDataService} from "../../services/local_data/local-data.service";
import {FormsModule} from "@angular/forms";
import {SocketManagerService} from "../../services/socket/socket-manager.service";
import {Subscription} from "rxjs";
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
    newMassageSubject :any;

    private subscriptions: Subscription[] = [];
    ngOnDestroy(){
        this.subscriptions.forEach(subscription => subscription.unsubscribe());
    }

    // socket = new WebSocket('ws://'+this.localDataService.serverAddress+'/ws/chat/');
    messageList : any[] = []
    channelId: string | null = "";
    constructor(private socketManageService:SocketManagerService,private cryptoService: CryptoService,private localDataService:LocalDataService,private route: ActivatedRoute,private router: Router) {
        const self = this;
        this.cryptoService = cryptoService;
        this.localDataService = localDataService;
        this.route.paramMap.subscribe(params => {
            const channelId = params.get('id')
            self.channelId = channelId
            const getMessageResultSubject = this.socketManageService.getMessageSubject("chat", "get_message_result").subscribe(
            message => {
                const data = JSON.parse(message.data).messages;
                console.log(data)
                self.messageList = data
                getMessageResultSubject.unsubscribe()
            })
            this.subscriptions.push(getMessageResultSubject);
            if (self.newMassageSubject){
                this.newMassageSubject.unsubscribe();
                this.newMassageSubject = null;
            }
            self.newMassageSubject = this.socketManageService.getMessageSubject("chat", "new_message").subscribe(
            message => {
                const data = JSON.parse(message.data).messages;
                console.log(data)
                self.messageList.push(data)
            })
            this.subscriptions.push(self.newMassageSubject);
            this.socketManageService.send("chat", "get_message", {
                    "session_id": self.cryptoService.session,
                    "channel_id": channelId,
                    "type":0
            })
        });
    }
    ngOnInit(): void {
            // this.socket.onopen = function () {
            //     const requestJson = {
            //         "command":"get_message",
            //         "session_id": self.cryptoService.session,
            //         "channel_id":"aa6cd21b-7080-4e65-9059-8a6a8c303cbb",
            //         "type":0
            //     }
            //     self.socket.send(JSON.stringify(requestJson));
            // }
            // const self = this;
            // this.socket.onclose = function (e) {
            //     console.error('Chat socket closed unexpectedly');
            // };
            // this.socket.onmessage = function (e: { data: any; }) {
            //     const json = JSON.parse(e.data)
            //     const command = json.command;
            //     // console.log(command)
            //     if (command == "new_message"){
            //         self.messageList.push(json.message)
            //     }else if(command == "get_message_result"){
            //         self.messageList = json.messages
            //     }
            // };
    }

    sendMessage() {
        const self=this;
        this.socketManageService.send("chat", "send_message", {
                    "session_id": self.cryptoService.session,
                    "message":{
                        "channel_id": self.channelId,
                        "content":self.massageInputValue,
                    }
            })
        this.massageInputValue = ""
    }
}
