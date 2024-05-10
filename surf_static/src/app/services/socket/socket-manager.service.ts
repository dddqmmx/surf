import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
@Injectable({
  providedIn: 'root'
})
export class SocketManagerService {
    // 这是主连接的 Socket
    private socket: any
    // 存放指定command的订阅
    // key是command
    // messageSubjects: Map<string, Subject<MessageEvent>> = new Map();
    // 外层Map，用于根据path存储和查找内层Map
    pathMap = new Map();

// 添加一个新的path和command
    addMessageSubject(path: string, command: string, subject: Subject<MessageEvent>) {
        if (!this.pathMap.has(path)) {
            this.pathMap.set(path, new Map()); // 如果path不存在，创建一个新的Map
        }
        const commandMap = this.pathMap.get(path); // 获取与path关联的Map
        commandMap.set(command, subject); // 在内层Map中添加command和Subject
    }

    public getMessageSubject(path: string,command: string): Subject<MessageEvent> {
        let messageSubject: Subject<MessageEvent>;
        const commandMap = this.pathMap.get(path);
        if (commandMap) {
            messageSubject = commandMap.get(command);
        } else {
            // 如果没有，创建一个新的 Subject 并将其添加到 messageSubjects 映射中
            messageSubject = new Subject<MessageEvent>();
            this.addMessageSubject(path,command, messageSubject);
        }
        return messageSubject;
    }

    existMessageSubject(path: string,command: string) {
        const commandMap = this.pathMap.get(path);
        if (commandMap) {
            return commandMap.has(command); // 如果command存在，返回true
        }
        return false; // 如果path不存在，或者command不存在，返回false
    }

    //初始化总链接
    public initializeMainConnection(serverAddress:string){
        return new Promise<void>((resolve, reject) => {
            //判断socket是否存在
            if(!this.socket){
                // 这是主连接的socket
                const endpoint: string = 'ws://' + serverAddress + '/ws/surf/';
                this.socket = new WebSocket(endpoint)
                // 设置 onopen 事件处理器
                this.socket.onopen = () => {
                    // 连接成功后执行 resolve，表示 WebSocket 已经完全连接
                    resolve();
                };
                // 设置 onmessage 事件处理器
                this.socket.onmessage = (event: MessageEvent<any>) => {
                    console.log(event.data)
                    // 解析接收到的消息，假定所有消息都按照规范走
                    const jsonMassage = JSON.parse(event.data)
                    const path = jsonMassage.path
                    const command = jsonMassage.command
                    let messageSubject = this.getMessageSubject(path,command);
                    // 检查是否已经为该命令创建了一个 Subject
                    if (messageSubject) {
                        // 把消息事件发布到 Subject
                        messageSubject!.next(event);
                    }
                };
                this.socket.close =() =>{
                    // 当连接关闭时，完成所有的 Subject 并清除 pathMap 映射
                    for (const [path, commandMap] of this.pathMap.entries()) {
                        for (const [command, messageSubject] of commandMap.entries()) {
                            messageSubject.complete();
                        }
                        commandMap.clear();
                    }
                    this.pathMap.clear();
                    // 将 socket 设置为 null，这样下次调用 initializeMainConnection 时，会创建一个新的 WebSocket 连接
                    this.socket = null;
                }
                this.socket.onerror = ()=>{
                    this.socket = null;
                }
            } else {
                // 如果 socket 已存在，则直接 resolve，表示 WebSocket 已经完全连接
                resolve();
            }
        });
    }

    public disconnect(){
        if (this.socket){
            for (const [path, commandMap] of this.pathMap.entries()) {
                for (const [command, messageSubject] of commandMap.entries()) {
                    messageSubject.complete();
                }
                commandMap.clear();
            }
            this.pathMap.clear();
            this.socket.close();
            // 将 socket 设置为 null，这样下次调用 initializeMainConnection 时，会创建一个新的 WebSocket 连接
            this.socket = null;
        }
    }

    public send(path: string,command: string, messages: any){
        const respond_json = {
            'path': path,
            "command": command,
            ...messages
        }
        this.socket.send(JSON.stringify(respond_json))
    }
}
