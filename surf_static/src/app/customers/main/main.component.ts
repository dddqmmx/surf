import {Component, input, OnInit, ViewChild} from '@angular/core';
import {NgForOf, NgIf} from "@angular/common";
import {CryptoService} from "../../services/crypto/crypto.service";
import {LocalDataService} from "../../services/local_data/local-data.service";
import {Router, RouterOutlet} from "@angular/router";
import {ChatComponent} from "../chat/chat.component";
import {SidebarServerComponent} from "../sidebar-server/sidebar-server.component";
import {FormsModule} from "@angular/forms";
import {SocketManagerService} from '../../services/socket/socket-manager.service'
import {finalize, Subscription} from "rxjs";
import {SidebarDierctMassagesComponent} from "../sidebar-dierct-massages/sidebar-dierct-massages.component";
@Component({
  selector: 'app-main',
  standalone: true,
    imports: [
        NgForOf,
        ChatComponent,
        RouterOutlet,
        SidebarServerComponent,
        NgIf,
        FormsModule,
        SidebarDierctMassagesComponent
    ],
  templateUrl: './main.component.html',
  styleUrl: './main.component.css'
})
export class MainComponent implements OnInit{

    creatServerPopupVisible = false;
    selectUserPopupVisible = false;
    servers: any[]=[];
    inputUserId = ""
    invitationList:any = []
    serverName = ""
    serverDescription = ""
    messageSubscription : any;
    private subscriptions: Subscription[] = [];
    sidebarType = 0;

    toggleCreatServerPopup() {
      this.creatServerPopupVisible = !this.creatServerPopupVisible;
    }
    toggleSelectUserPopup() {
      this.selectUserPopupVisible = !this.selectUserPopupVisible;

    }
    constructor(private cryptoService: CryptoService,
                private localDataService:LocalDataService,
                private socketMangerService: SocketManagerService,
                private router: Router) {
            this.cryptoService = cryptoService;
            this.localDataService = localDataService;
            this.socketMangerService = socketMangerService;
    }

    @ViewChild('sidebarServer')
    public sidebarServer: SidebarServerComponent | undefined

    ngOnInit(): void {
        if (this.cryptoService.session){
            this.getUserData();
        }else {
            // alert('你没登录')
            // this.router.navigate(['/login'])
        }
        this.getFriends();
    }

    ngOnDestroy(){
        this.subscriptions.forEach(subscription => subscription.unsubscribe());
    }
    previewImageUrl: string = ''; // 存储预览图像的URL
    // 打开文件选择对话框
    openFileInput() {
      document.getElementById('fileInput')?.click();
    }
    // 当文件被选中时触发
    onFileSelected(event: any) {
      const file: File = event.target.files[0]; // 获取选择的文件
      this.previewImage(file); // 调用预览图像方法
    }

    // 预览图像
    previewImage(file: File) {
        const reader = new FileReader(); // 创建文件读取器
        reader.onload = () => {
            this.previewImageUrl = reader.result as string; // 将图像数据直接赋给图片元素的 src 属性
        };
        reader.readAsDataURL(file); // 读取文件
    }

    // Function to handle WebSocket connections and messages
    connectWebSocket(url:any, requestJson:any, messageHandler:any) {
        const socket = new WebSocket(url);
        socket.onopen = function () {
            socket.send(JSON.stringify(requestJson));
        };
        socket.onclose = function (e) {
            console.error('WebSocket closed unexpectedly');
        };
        socket.onmessage = function (e) {
            const json = JSON.parse(e.data);
            messageHandler(json);
        };
    }
    setSidebarDirectMassage(){
        this.sidebarType = 1;
    }
    setSidebarServerId(serverId:string){
        this.sidebarType = 0;
        const waitForSidebarServer = new Promise<void>((resolve) => {
        const intervalId = setInterval(() => {
                if (this.sidebarServer) {
                    clearInterval(intervalId);
                    resolve();
                }
            }, 50); // 每秒检查一次 sidebarServer 是否存在
        });

        // 等待 sidebarServer 存在，然后调用 getServerDetails 方法
        waitForSidebarServer.then(() => {
            this.sidebarServer!.getServerDetails(serverId); // 使用非空断言操作符确保 sidebarServer 存在
        });
    }

    // Reusing WebSocket connection for different functionalities
    searchUser() {
        const requestJson = {
            'command': 'search_user',
            'user_id_list': [this.inputUserId]
        };
        this.connectWebSocket(
            'ws://' + this.localDataService.serverAddress + '/ws/user/',
            requestJson,
            (json: { message: any; }) => {
                this.invitationList.push(...json.message);
            }
        );
    }
    getUserData() {
        const getUserDataSubject = this.socketMangerService.getMessageSubject("user","get_user_data_result").subscribe(
            message => {
                const data = JSON.parse(message.data).messages;
                console.log(data)
                this.servers.push(...data.user.servers);
                this.setSidebarServerId(this.servers[0].id)
                getUserDataSubject.unsubscribe()
            })
        this.subscriptions.push(getUserDataSubject);
        this.socketMangerService.send('user','get_user_data', {
            'session_id':this.cryptoService.session
        })
    }

    createServer() {
        this.socketMangerService.send('server','create_server', {
            'session_id': this.cryptoService.session,
            'server': {
                'description': this.serverDescription,
                'name': this.serverName,
                'is_private': true
            }
        })
    }


    getFriends() {
        this.socketMangerService.send('user','get_friends', {
            'session_id':this.cryptoService.session
        })
    }

    // createServer() {
    //     const requestJson = {
    //         'command': 'create_server',
    //         'server': {
    //             'description': this.serverDescription,
    //             'name': this.serverName,
    //             'session_id': this.cryptoService.session,
    //             'is_private': true
    //         }
    //     };
    //     this.connectWebSocket(
    //         'ws://' + this.localDataService.serverAddress + '/ws/server/',
    //         requestJson,
    //         (json: any) => {
    //             console.log("Server created:", json);
    //         }
    //     );
    // }



}
