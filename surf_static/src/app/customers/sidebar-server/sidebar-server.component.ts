import {Component, EventEmitter, Output, ViewChild} from '@angular/core';
import {NgForOf, NgIf} from "@angular/common";
import {MainComponent} from "../main/main.component";
import {CryptoService} from "../../services/crypto/crypto.service";
import {LocalDataService} from "../../services/local_data/local-data.service";
import {Router} from "@angular/router";
import {SocketManagerService} from "../../services/socket/socket-manager.service";
import {Subscription} from "rxjs";

@Component({
  selector: 'app-sidebar-server',
  standalone: true,
    imports: [
        NgForOf,
        NgIf
    ],
  templateUrl: './sidebar-server.component.html',
  styleUrl: './sidebar-server.component.css'
})
export class SidebarServerComponent {


    @Output() selectUserPopup = new EventEmitter();

    toggleSelectUserPopup() {
        this.selectUserPopup.emit();
    }

    menuVisible = false;
    toggleMenu(){
        this.menuVisible = !this.menuVisible;
    }
    private subscriptions: Subscription[] = [];
    ngOnDestroy(){
        this.subscriptions.forEach(subscription => subscription.unsubscribe());
    }

    constructor(private cryptoService: CryptoService,private localDataService:LocalDataService,private socketManageService:SocketManagerService,private router: Router) {
        this.cryptoService = cryptoService;
        this.localDataService = localDataService;
        this.socketManageService = socketManageService;
    }
    public toChat(id:string){
        this.router.navigate(['main/chat',id]);
    }

    public getServerDetails(serverId:string) {
        const getServerDetailsSubject = this.socketManageService.getMessageSubject("server","get_server_details_result").subscribe(
        message => {
                this.channelInfo = JSON.parse(message.data).messages;
                getServerDetailsSubject.unsubscribe()
            })
        this.subscriptions.push(getServerDetailsSubject)
        this.socketManageService.send('server','get_server_details', {
            'session_id': this.cryptoService.session,
            'server_id': serverId
        })
    }
    channelInfo: {
        id: string
        name: string
        icon_url: string
        channel_groups:[
            {
                "id": string,
                "name": string,
                "channels": [
                    {
                        "id": string,
                        "name": string,
                        "type": string,
                        "description": string
                    }
                ]
            },
        ]
    }|undefined
}
