import {Component, OnInit} from '@angular/core';
import {NgForOf} from "@angular/common";
import {CryptoService} from "../../services/crypto/crypto.service";
import {LocalDataService} from "../../services/local_data/local-data.service";
import {Router, RouterOutlet} from "@angular/router";
import {ChatComponent} from "../chat/chat.component";
import {SidebarServerComponent} from "../sidebar-server/sidebar-server.component";

@Component({
  selector: 'app-main',
  standalone: true,
    imports: [
        NgForOf,
        ChatComponent,
        RouterOutlet,
        SidebarServerComponent
    ],
  templateUrl: './main.component.html',
  styleUrl: './main.component.css'
})
export class MainComponent implements OnInit{
    constructor(private cryptoService: CryptoService,private localDataService:LocalDataService,private router: Router) {
            this.cryptoService = cryptoService;
            this.localDataService = localDataService;
    }
    data = {
        objects: [
            {
                user: {
                    user_nickname: "兎田ぺこら",
                    user_info: {"email": "woshishabi@gmail.com", "phone": "1145141919810"}
                },
            },
            {
                user: {
                    user_nickname: "白上フブキ",
                    user_info: {"email": "woshishabi@gmail.com", "phone": "1145141919810"}
                },
            }
        ]
    };
    getUserData(){
        const self = this;
        const socket = new WebSocket('ws://'+this.localDataService.serverAddress+'/ws/user/');
        socket.onopen = function () {
            const requestJson = {
                'command': 'get_user_data',
                'session_id': self.cryptoService.session,
            }
            socket.send(JSON.stringify(requestJson));
        }
        socket.onclose = function (e) {
            console.error('Chat socket closed unexpectedly');
        };
        socket.onmessage = function (e: { data: any; }) {
            const json = JSON.parse(e.data)
            console.log(json)
            // const command = json.command;
            // if (command == "to_url"){
            //     const url = json.url;
            //     if (url == 'main'){
            //         router.navigate(['/CustomersModule/main']);
            //         self.socket?.close();
            //     }
            // }
        };
    }

    ngOnInit(): void {
        this.getUserData();
    }

}
