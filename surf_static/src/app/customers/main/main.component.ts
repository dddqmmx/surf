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
    invitationUserList:any = []
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
                protected localDataService:LocalDataService,
                private socketMangerService: SocketManagerService,
                private router: Router) {
            this.cryptoService = cryptoService;
            this.localDataService = localDataService;
            this.socketMangerService = socketMangerService;
    }

    @ViewChild('sidebarServer')
    public sidebarServer: SidebarServerComponent | undefined

    ngOnInit(): void {
        const self = this;
        const sendAudioSubject = this.socketMangerService.getMessageSubject("chat", "send_audio").subscribe(
            message => {
                const data = JSON.parse(message.data).content;
                self.playAudio(data)
            })
        this.subscriptions.push(sendAudioSubject);
        if (this.cryptoService.session){
            this.getUserData()
            this.getFriends();
        }else {
            alert('你没登录')
            this.router.navigate(['/login'])
        }
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
        const self= this;
        const searchUserSubject = this.socketMangerService.getMessageSubject("user","search_user_result").subscribe(
            message => {
                const data = JSON.parse(message.data).messages;
                self.invitationUserList = data;
                searchUserSubject.unsubscribe()
            })
        this.subscriptions.push(searchUserSubject);
        this.socketMangerService.send('user','search_user', {
            'session_id':this.cryptoService.session,
            'user_id_list': [this.inputUserId]
        })
        // const requestJson = {
        //     'command': 'search_user',
        //     'user_id_list': [this.inputUserId]
        // };
        // this.connectWebSocket(
        //     'ws://' + this.localDataService.serverAddress + '/ws/user/',
        //     requestJson,
        //     (json: { message: any; }) => {
        //         this.invitationList.push(...json.message);
        //     }
        // );
    }
    getUserData() {
        const getUserDataSubject = this.socketMangerService.getMessageSubject("user","get_user_data_result").subscribe(
            message => {
                const data = JSON.parse(message.data).messages;
                console.log(data)
                this.servers.push(...data.user.servers);
                this.localDataService.loggedUserId = data.user.id
                this.localDataService.setUserInfo(data.user.id,data.user)
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
    mediaStream: MediaStream | null = null;
    audioContext: AudioContext | null = null;
    scriptProcessor: ScriptProcessorNode | null = null;
    audioChunks: Float32Array[] = [];
    isRecording: boolean = false;
    sendDataInterval: any;
    mainAudioContext: AudioContext | null = null;

    async startRecording () {
      if (this.isRecording) {
        console.log('已经在录制中...');
        return;
      }
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        if (mediaStream.active) {
          console.log('音频流已经开始传输。');

          this.mediaStream = mediaStream;
          this.audioContext = new AudioContext();

          // Use a smaller buffer size (512) for lower latency
          this.scriptProcessor = this.audioContext.createScriptProcessor(16384, 1, 1);
          this.scriptProcessor.onaudioprocess = (event) => this.handleAudioProcess(event);

          const inputNode = this.audioContext.createMediaStreamSource(mediaStream);
          inputNode.connect(this.scriptProcessor);
          this.scriptProcessor.connect(this.audioContext.destination);

          this.audioChunks = [];
          this.isRecording = true;

          console.log('开始录制音频...');

          // Reduce the interval for data sending
          this.sendDataInterval = setInterval(() => {
            if (this.isRecording && this.audioChunks.length > 0) {
              this.sendAudioData();
            }
          }, 100); // Adjusted for lower latency
        }
      } catch (err) {
        console.error('无法访问麦克风:', err);
      }
    }

    handleAudioProcess(event: AudioProcessingEvent) {
      if (!this.isRecording) return;

      const audioBuffer = event.inputBuffer;
      const inputData = new Float32Array(audioBuffer.getChannelData(0));
      this.audioChunks.push(inputData);
    }
    sendAudioData() {
        const message: Float32Array = this.mergeArrays(this.audioChunks);

        // 打印合并后的音频数据长度
        // console.log('Merged audio data length:', message.length);

        // 将 Float32Array 转换为普通数组
        const regularArray: number[] = Array.from(message);

        // 检查转换后的数组是否包含有效数据
        // console.log('Regular array:', regularArray);

        // 将普通数组转换为 JSON 字符串
        const jsonArray: string = JSON.stringify(regularArray);
        // console.log('JSON array:', jsonArray);

        // 解析 JSON 字符串以检查其内容
        // const data = JSON.parse(jsonArray);
        // console.log('Parsed data length:', data.length);

        // 发送音频数据
        this.socketMangerService.send( "chat", "send_audio",{
            "session_id": this.cryptoService.session,
            "channel_id": '0362e80c-839b-4ee6-9e77-c2cb6668c961',
            "content": jsonArray,
        });
        this.audioChunks = [];
    }

    mergeArrays(arrays: Float32Array[]): Float32Array {
      let totalLength = arrays.reduce((sum, array) => sum + array.length, 0);
      let result = new Float32Array(totalLength);
      let offset = 0;

      arrays.forEach((array) => {
        result.set(array, offset);
        offset += array.length;
      });

      return result;
    }



    stopRecording() {
      if (!this.isRecording) {
        console.log('未在录制中...');
        return;
      }

      this.isRecording = false;
      clearInterval(this.sendDataInterval);

      if (this.scriptProcessor) {
        this.scriptProcessor.disconnect();
      }
      if (this.mediaStream) {
        this.mediaStream.getTracks().forEach((track) => track.stop());
      }
      if (this.audioContext) {
        this.audioContext.close();
      }

      console.log('停止录制音频...');
    }

    playAudio(audioData: Float32Array) {
      if (!this.mainAudioContext) {
        this.mainAudioContext = new AudioContext();
      }

      this.mainAudioContext.resume();

      const channelCount = 1;
      const sampleRate = this.mainAudioContext.sampleRate;
      const totalSamples = audioData.length;

      const audioBuffer = this.mainAudioContext.createBuffer(channelCount, totalSamples, sampleRate);
      const channelData = audioBuffer.getChannelData(0);

      channelData.set(audioData);

      const source = this.mainAudioContext.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(this.mainAudioContext.destination);
      source.start();
    }

    protected readonly console = console;
}
