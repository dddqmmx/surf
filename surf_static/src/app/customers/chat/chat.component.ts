import {Component, OnInit} from '@angular/core';
import {CryptoService} from "../../services/crypto/crypto.service";
import {ActivatedRoute, Router} from "@angular/router";
import {NgForOf, NgIf} from "@angular/common";
import {LocalDataService} from "../../services/local_data/local-data.service";
import {FormsModule} from "@angular/forms";
import {SocketManagerService} from "../../services/socket/socket-manager.service";
import {Subscription} from "rxjs";

@Component({
    selector: 'app-chat',
    standalone: true,
    imports: [
        NgForOf,
        FormsModule,
        NgIf
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

    chatName:string | undefined = "";
    messageList : any[] = []
    channelId: string | null = "";
    constructor(private socketManageService:SocketManagerService,private cryptoService: CryptoService,public localDataService:LocalDataService,private route: ActivatedRoute,private router: Router) {
        const self = this;
        this.cryptoService = cryptoService;
        this.localDataService = localDataService;
        this.route.paramMap.subscribe(params => {
            const channelId = params.get('id')
            this.chatName = localDataService.getChannelById(channelId)?.name
            self.channelId = channelId
            const getMessageResultSubject = this.socketManageService.getMessageSubject("chat", "get_message_result").subscribe(
            message => {
                const data = JSON.parse(message.data).messages;
                self.messageList = data
                console.log(self.messageList)
                const userDataList:any = []
                data.forEach((message:any) => {
                    userDataList.push(message.user_id)
                })
                localDataService.getUserDataFormServer(userDataList)
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
                localDataService.getUserDataFormServer(data.id)
                self.messageList.push(data)
            })
            this.subscriptions.push(self.newMassageSubject);
            this.socketManageService.send("chat", "get_message", {
                    "session_id": self.cryptoService.session,
                    "channel_id": channelId,
            })
        });
    }

onScroll(event: any) {
  const element = event.target;
  if (element.scrollTop === 0) {
      const previousHeight = element.scrollHeight;
      this.getMessageFromHistory()
      const newHeight = element.scrollHeight;
      element.scrollTop = newHeight - previousHeight;
  }
}
    getMessageFromHistory(){
        const self = this;
        const oldestMessage = this.messageList[0]
        const getMessageResultSubject = this.socketManageService.getMessageSubject("chat", "get_message_result").subscribe(
            message => {
                const data = JSON.parse(message.data).messages;
                self.messageList = data.concat(this.messageList);
                console.log(self.messageList)
                const userDataList:any = []
                data.forEach((message:any) => {
                    userDataList.push(message.user_id)
                })
                self.localDataService.getUserDataFormServer(userDataList)
                getMessageResultSubject.unsubscribe()
            })
        this.socketManageService.send("chat", "get_message", {
            "session_id": this.cryptoService.session,
            "channel_id": this.channelId,
            "last_msg": [oldestMessage.chat_time,oldestMessage.chat_id]
        })
        console.log(this.messageList.length)
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
