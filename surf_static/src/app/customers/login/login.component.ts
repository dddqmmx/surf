import { Component } from '@angular/core';
import {NgIf} from "@angular/common";
import {encryptData} from "../../util/encryption/encryption_ras";
import { CryptoService } from '../../services/crypto/crypto.service';
import {util} from "node-forge";
import {Base64} from "jsencrypt/lib/lib/asn1js/base64";
import { Router ,NavigationExtras} from '@angular/router';
import {LocalDataService} from "../../services/local_data/local-data.service";
import {SocketManagerService} from "../../services/socket/socket-manager.service";
import {main} from "@angular/compiler-cli/src/main";

@Component({
    selector: 'app-login',
    standalone: true,
    imports: [
        NgIf
    ],
    templateUrl: './login.component.html',
    styleUrl: './login.component.css'
})
export class LoginComponent {

    constructor(private cryptoService: CryptoService,private localDataService:LocalDataService,private socketMassageService:SocketManagerService,private router: Router) {
        this.cryptoService = cryptoService;
        this.localDataService = localDataService;
    }

    socket: WebSocket | undefined;
    fileDropped: boolean = false;
    fileContent: any;
    serverPublicKey: string | undefined;
    isInit:boolean = false;
    onFileDrop(event: any) {
        event.preventDefault();
        this.fileDropped = true;
        this.readFile(event.dataTransfer.files[0]);
    }

    onDragOver(event: any) {
        event.preventDefault();
    }

    onDragLeave(event: any) {
        event.preventDefault();
        this.fileDropped = false;
    }

    onFileSelect(event: any) {
        this.fileDropped = true;
        this.readFile(event.target.files[0]);
    }

    readFile(file: File) {
        const reader = new FileReader();
        reader.onload = () => {
            this.fileContent = reader.result;
        };
        reader.readAsText(file);
    }
    init() {
        const self = this;
        if (this.isJSON(this.fileContent)) {
            const userFile = JSON.parse(this.fileContent)
            const serverAddress = userFile.server_address;
            this.localDataService.serverAddress = serverAddress;
            const publicKey = userFile.public_key;
            const privateKey = atob(userFile.private_key);
            this.cryptoService.setClientPrivateKey(privateKey);
            const socket = new WebSocket('ws://'+serverAddress+'/ws/key_exchange/');
            const requestJson = {
                'command': 'key_exchange',
                'public_key': publicKey
            }
            socket.onopen = function (){
                socket.send(JSON.stringify(requestJson));
            }
            socket.onmessage = function (e: { data: any; }) {
                const json = JSON.parse(e.data)
                const command =    json.command;
                if (command == "key_exchange"){
                    const public_key = json.public_key;
                    self.cryptoService.setServerPublicKey(public_key);
                }
                socket.close();
                self.toLogin()
            };
        }
    }

    login() {
        const self = this;
        if (this.isJSON(this.fileContent)) {
            const userFile = JSON.parse(this.fileContent)
            const toURLSubject = this.socketMassageService.getMessageSubject("user", "to_url").subscribe(
                message => {
                    const data = JSON.parse(message.data).messages;
                    console.log(data)
                    const session_id = data.session_id;
                    self.cryptoService.setSession(session_id);
                    const address = data.address;
                    if (address == 'main'){
                        console.log('main')
                        self.router.navigate(['main/chat']);
                        self.socket?.close();
                    }
                    toURLSubject.unsubscribe()
                })
            this.socketMassageService.send("user", "login", {
                "public_key": userFile.public_key,
            })
        }
    }

    async keyExchange() {
        const self = this;
        if (this.isJSON(this.fileContent)) {
            const userFile = JSON.parse(this.fileContent)
            const serverAddress = userFile.server_address;
            this.socketMassageService.initializeMainConnection(serverAddress)
                .then(async () => {
                    try {
                        // const keyPair = await this.cryptoService.generateKeyPair();
                        // const publicKeyString = await this.cryptoService.exportPublicKey(keyPair.publicKey);
                        // console.log(publicKeyString);
                        // const keyExchangeSubject = this.socketMassageService.getMessageSubject("key", "key_exchange").subscribe(
                        //     message => {
                        //         const data = JSON.parse(message.data).messages;
                        //         const public_key = data.public_key;
                        //         self.cryptoService.setServerPublicKey(public_key);
                        //         keyExchangeSubject.unsubscribe()
                        //     }
                        // )
                        // this.socketMassageService.send("key", "key_exchange", {
                        //     "public_key": publicKeyString
                        // })
                        self.login()
                    } catch (err) {
                        console.error(err);
                    }
                })
                .catch((error) => {
                    // 发生错误时的处理
                    console.error('WebSocket连接出错:', error);
                });

        }
    }

    toLogin(){
        const self = this;
        if (this.isJSON(this.fileContent)) {
            const userFile = JSON.parse(this.fileContent)
            const serverAddress = userFile.server_address;
            this.socket = new WebSocket('ws://'+serverAddress+'/ws/user/');
            this.socket.onopen = function () {
                const requestJson = {
                    'command': 'login',
                    'public_key': userFile.public_key,
                }
                self.send(JSON.stringify(requestJson));
            }
            this.socket.onclose = function (e) {
                console.error('Chat socket closed unexpectedly');
            };
            this.socket.onmessage = function (e: { data: any; }) {
                const json = JSON.parse(e.data)
                console.log(json)
                const command = json.command;
                const data = json.messages;
                if (command == "to_url"){
                    const session_id = data.session_id;
                    self.cryptoService.setSession(session_id);
                    const address = data.address;
                    if (address == 'main'){
                        self.router.navigate(['main/chat']);
                        self.socket?.close();
                    }
                }
            };
        } else {
            console.log('不是 JSON 文件');
        }
    }

    send(message: string){
            if (this.socket != null) {
                this.socket.send(message);
                // const encryptedData = this.cryptoService.encryptData((massage));
                // console.log(encryptedData)
                // if (typeof encryptedData === "string") {
                //     this.socket.send(encryptedData);
                // }
            }
    }

    isJSON(str: any) {
        try {
            JSON.parse(str);
            return true;
        } catch (e) {
            return false;
        }
    }
}
