import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import {error} from "@angular/compiler-cli/src/transformers/util";

@Injectable({
  providedIn: 'root'
})
export class SocketManagerService {
    // 这是主连接的 Socket
    private socket: any
    // 存放指定command的订阅
    messageSubjects: Map<string, Subject<MessageEvent>> = new Map();

    //初始化总链接
    public initializeMainConnection(serverAddress:string){
        //判断socket是否存在
        if(!this.socket){
            // 这是主连接的socket
            const endpoint: string = 'ws://' + serverAddress + '/ws/mian/';
            this.socket = new WebSocket(endpoint)
            // 设置 onmessage 事件处理器
            this.socket.onmessage = (event: MessageEvent<any>) => {
                // 解析接收到的消息，假定所有消息都按照规范走
                const jsonMassage = JSON.parse(event.data)
                const command = jsonMassage.command
                let messageSubject: Subject<MessageEvent>;
                // 检查是否已经为该命令创建了一个 Subject
                if (this.messageSubjects.has(command)){
                    // 如果已经存在，直接从 messageSubjects 映射中获取
                    this.messageSubjects.get(command)
                }else {
                    // 如果没有，创建一个新的 Subject 并将其添加到 messageSubjects 映射中
                    // 实际上我感觉没有获取过这个命令的 Subject 甚至可以不处理，return这个方法就好
                     messageSubject = new Subject<MessageEvent>();
                    this.messageSubjects.set(jsonMassage.command,messageSubject);
                }
                // 把消息事件发布到 Subject
                messageSubject!.next(event);
            };
            this.socket.close =() =>{
                // 当连接关闭时，完成所有的 Subject 并清除 messageSubjects 映射
                for (const [command, messageSubject] of this.messageSubjects.entries()) {
                    messageSubject.complete();
                }
                this.messageSubjects.clear();
                // 将 socket 设置为 null，这样下次调用 initializeMainConnection 时，会创建一个新的 WebSocket 连接
                this.socket = null;
            }
        }
    }

    //获取指定command的订阅
    public getMessageSubject(command: string): Subject<MessageEvent> {
        let messageSubject: Subject<MessageEvent>;
        if (this.messageSubjects.has(command)) {
            // 如果已经存在，直接从 messageSubjects 映射中获取
            messageSubject = this.messageSubjects.get(command)!;
        } else {
            // 如果没有，创建一个新的 Subject 并将其添加到 messageSubjects 映射中
            messageSubject = new Subject<MessageEvent>();
            this.messageSubjects.set(command, messageSubject);
        }
        return messageSubject;
    }


    public disconnect(){
        if (this.socket){
            this.socket.close();
        }
    }

    public send(command: string, messages: any){
        const respond_json = {
            "command": command,
            "messages":messages
        }
        this.socket.send(respond_json)
    }
}
