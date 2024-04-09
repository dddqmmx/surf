import { Component } from '@angular/core';
import {NgIf} from "@angular/common";
import {encryptData} from "../../util/encryption/encryption_ras";
import { CryptoService } from '../../services/crypto/crypto.service';
import {util} from "node-forge";
import {Base64} from "jsencrypt/lib/lib/asn1js/base64";
import { Router ,NavigationExtras} from '@angular/router';
import {LocalDataService} from "../../services/local_data/local-data.service";

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

  constructor(private cryptoService: CryptoService,private localDataService:LocalDataService,private router: Router) {
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
      console.log(privateKey)
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
        const command =  json.command;
        if (command == "key_exchange"){
          const public_key = json.public_key;
          const session_id = json.session_id;
          console.log(public_key)
          self.cryptoService.setServerPublicKey(public_key);
          console.log(session_id)
          self.cryptoService.setSession(session_id);
        }
        socket.close();
        self.toLogin()
      };
    }
  }

  login() {
    this.init()
  }

  toLogin(){
    const self = this;
    if (this.isJSON(this.fileContent)) {
      const userFile = JSON.parse(this.fileContent)
      const serverAddress = userFile.server_address;
      this.socket = new WebSocket('ws://'+serverAddress+'/ws/login/');
      this.socket.onopen = function () {
        const requestJson = {
          'command': 'login',
          'session_id': self.cryptoService.session,
        }
        self.send(JSON.stringify(requestJson));
      }
      this.socket.onclose = function (e) {
        console.error('Chat socket closed unexpectedly');
      };
      this.socket.onmessage = function (e: { data: any; }) {
        const json = JSON.parse(e.data)
        console.log(json)
        const command =  json.command;
        if (command == "to_url"){
          const url = json.url;
          if (url == 'main'){
            self.router.navigate(['/CustomersModule/chat'])
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
        //   this.socket.send(encryptedData);
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
