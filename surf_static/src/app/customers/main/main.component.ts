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
    servers: any[]=[];
    getUserData(){
        const self = this;
        const socket = new WebSocket('ws://'+this.localDataService.serverAddress+'/ws/user/');
        socket.onopen = function () {
            const requestJson = {
                'command': 'get_user_data',
                'session_id': self.cryptoService.session,
            }
            this.send(JSON.stringify(requestJson));
        }
        socket.onclose = function (e) {
            console.error('Chat socket closed unexpectedly');
        };
        socket.onmessage = function (e: { data: any; }) {
            const json = JSON.parse(e.data)
            const servers = json.message.user.servers;
            for (const server of servers){
                self.servers.push(server)
            }
        };
    }
    getFriends(){
        const self = this;
        const socket = new WebSocket('ws://'+this.localDataService.serverAddress+'/ws/user/');
        socket.onopen = function () {
            const requestJson = {
                'command': 'get_friends',
                'session_id': self.cryptoService.session,
            }
            this.send(JSON.stringify(requestJson));
        }
        socket.onclose = function (e) {
            console.error('Chat socket closed unexpectedly');
        };
        socket.onmessage = function (e: { data: any; }) {
            const json = JSON.parse(e.data)
            console.log("dddd"+json)
        };
    }

    inputUserId = ""

    invitationList:any = []
    searchUser(){
        const self = this;
        const socket = new WebSocket('ws://'+this.localDataService.serverAddress+'/ws/user/');
        socket.onopen = function () {
            const requestJson = {
                'command': 'search_user',
                'user_id_list':[self.inputUserId]
            }
            this.send(JSON.stringify(requestJson));
        }
        socket.onclose = function (e) {
            console.error('Chat socket closed unexpectedly');
        };
        socket.onmessage = function (e: { data: any; }) {
            const json = JSON.parse(e.data)
            console.log(json)
            self.invitationList.slice()
            for (const userInfo of json.message) {
                self.invitationList.push(userInfo)
            }

        };
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
    serverName = ""
    serverDescription = ""

    // 预览图像
    previewImage(file: File) {
        const reader = new FileReader(); // 创建文件读取器
        reader.onload = () => {
            this.previewImageUrl = reader.result as string; // 将图像数据直接赋给图片元素的 src 属性
        };
        reader.readAsDataURL(file); // 读取文件
    }

    createServer() {
        const socket = new WebSocket('ws://'+this.localDataService.serverAddress+'/ws/server/');
        const requestJson = {
            'command': 'create_server',
            'server':{
                'description': this.serverDescription,
                'name': this.serverName,
                'session_id': this.cryptoService.session,
                'is_private': true
            }
        }
        socket.onopen = function (){
            socket.send(JSON.stringify(requestJson));
        }
        socket.onmessage = function (e: { data: any; }) {
            const json = JSON.parse(e.data)
            console.log(json)
            socket.close();
        };
    }
}
