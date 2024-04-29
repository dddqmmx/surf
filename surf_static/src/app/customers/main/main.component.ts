import {Component, input, OnInit} from '@angular/core';
import {NgForOf, NgIf} from "@angular/common";
import {CryptoService} from "../../services/crypto/crypto.service";
import {LocalDataService} from "../../services/local_data/local-data.service";
import {Router, RouterOutlet} from "@angular/router";
import {ChatComponent} from "../chat/chat.component";
import {SidebarServerComponent} from "../sidebar-server/sidebar-server.component";
import {FormsModule} from "@angular/forms";

@Component({
  selector: 'app-main',
  standalone: true,
    imports: [
        NgForOf,
        ChatComponent,
        RouterOutlet,
        SidebarServerComponent,
        NgIf,
        FormsModule
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


    toggleCreatServerPopup() {
      this.creatServerPopupVisible = !this.creatServerPopupVisible;
    }
    toggleSelectUserPopup() {
      this.selectUserPopupVisible = !this.selectUserPopupVisible;

    }
    constructor(private cryptoService: CryptoService,private localDataService:LocalDataService,private router: Router) {
            this.cryptoService = cryptoService;
            this.localDataService = localDataService;
    }


    ngOnInit(): void {
        this.getUserData();
        // this.getFriends();
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
    const requestJson = {
        'command': 'get_user_data',
        'session_id': this.cryptoService.session,
    };
    this.connectWebSocket(
        'ws://' + this.localDataService.serverAddress + '/ws/user/',
        requestJson,
        (json: { message: { user: { servers: any; }; }; }) => {
            this.servers.push(...json.message.user.servers);
        }
    );
}

getFriends() {
    const requestJson = {
        'command': 'get_friends',
        'session_id': this.cryptoService.session,
    };
    this.connectWebSocket(
        'ws://' + this.localDataService.serverAddress + '/ws/user/',
        requestJson,
        (json: any) => {
            console.log("Friends:", json);
        }
    );
}

createServer() {
    const requestJson = {
        'command': 'create_server',
        'server': {
            'description': this.serverDescription,
            'name': this.serverName,
            'session_id': this.cryptoService.session,
            'is_private': true
        }
    };
    this.connectWebSocket(
        'ws://' + this.localDataService.serverAddress + '/ws/server/',
        requestJson,
        (json: any) => {
            console.log("Server created:", json);
        }
    );
}

}
