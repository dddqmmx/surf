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
import {VoiceChatService} from "../../services/service/voice-chat.service";
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
    serverMembers:any= {} ;

    toggleCreatServerPopup() {
      this.creatServerPopupVisible = !this.creatServerPopupVisible;
    }
    toggleSelectUserPopup() {
      this.selectUserPopupVisible = !this.selectUserPopupVisible;

    }
    constructor(private cryptoService: CryptoService,
                protected localDataService:LocalDataService,
                private socketMangerService: SocketManagerService,
                private router: Router,
                protected voiceChatService:VoiceChatService) {
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
        self.enqueueAudioData(data);
      }
    );
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
            this.getServerMembers(serverId);
        });
    }

    getServerMembers(server_id:string){
        const self= this;
        const getServerMembersSubject = this.socketMangerService.getMessageSubject("server","get_server_members_result").subscribe(
            message => {
                const data = JSON.parse(message.data).messages;
                console.log(data)
                const memberUserList:any = []
                //这里的key是角色名称
                Object.keys(data).forEach(key=> {
                    const membersOfRole = data[key].members;
                    membersOfRole.forEach((userId: string)=>{
                        memberUserList.push(userId)
                    })
                })
                self.localDataService.getUserDataFormServer(memberUserList)
                self.serverMembers = data as { [key: string]: { level: number; members: string[] } };
                getServerMembersSubject.unsubscribe()
            })
        this.subscriptions.push(getServerMembersSubject);
        this.socketMangerService.send('server','get_server_members', {
            'session_id':this.cryptoService.session,
            'server_id':server_id
        })
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
                this.servers.push(...data.user.servers);
                this.localDataService.loggedUserId = data.user.id
                this.localDataService.setUserInfo(data.user.id,data.user)
                this.setSidebarServerId(this.servers[0].id)
                this.localDataService.addServers(this.servers)
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

    mediaStream: MediaStream | null = null;
    audioContext: AudioContext | null = null;
    scriptProcessor: ScriptProcessorNode | null = null;
    audioChunks: Float32Array[] = [];
    isRecording: boolean = false;
    sendDataInterval: any;
    mainAudioContext: AudioContext | null = null;
    audioBufferQueue :any[]= [];
    isPlaying = false;
    bufferSize = 4096; // Adjust buffer size if needed

    enqueueAudioData(audioData: any) {
      // Convert incoming audio data to Float32Array if necessary
      const float32Array = new Float32Array(audioData);
      this.audioBufferQueue.push(float32Array);
      if (!this.isPlaying) {
        this.playBufferedAudio();
      }
    }

    async playBufferedAudio() {
      this.isPlaying = true;

      while (this.audioBufferQueue.length > 0) {
        const audioData = this.audioBufferQueue.shift();
        if (audioData) {
          await this.playAudio(audioData);
        }
      }

      this.isPlaying = false;
    }

    playAudio(audioData: Float32Array): Promise<void> {
      return new Promise((resolve, reject) => {
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
        source.onended = () => {
          resolve();
          // Immediately check and play the next audio buffer if available
          if (this.audioBufferQueue.length > 0) {
            this.playBufferedAudio();
          } else {
            this.isPlaying = false;
          }
        };
        source.start();
      });
    }
    protected readonly console = console;
    protected readonly Object = Object;
}
