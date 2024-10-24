import {Injectable} from '@angular/core';
import {Observable, Subject} from 'rxjs';
import {CommonDataService} from "./common-data.service";

@Injectable({
    providedIn: 'root'
})
export class SocketService {

    constructor(private commonDataService: CommonDataService) {
    }

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

    public getMessageSubject(path: string, command: string): Subject<MessageEvent> {
        let messageSubject: Subject<MessageEvent>;
        const commandMap = this.pathMap.get(path);
        if (commandMap && commandMap.get(command)) {
            messageSubject = commandMap.get(command)
        } else {
            // 如果没有，创建一个新的 Subject 并将其添加到 messageSubjects 映射中
            messageSubject = new Subject<MessageEvent>();
            this.addMessageSubject(path, command, messageSubject);
        }
        return messageSubject;
    }

    existMessageSubject(path: string, command: string) {
        const commandMap = this.pathMap.get(path);
        if (commandMap) {
            return commandMap.has(command); // 如果command存在，返回true
        }
        return false; // 如果path不存在，或者command不存在，返回false
    }

    //初始化总链接
    public initializeMainConnection(serverAddress: string): Promise<boolean> {
        return new Promise<boolean>((resolve, reject) => {
            // 如果已经有活跃的连接，检查连接状态
            if (this.socket) {
                if (this.socket.readyState === WebSocket.OPEN) {
                    resolve(true);
                    return;
                }
                // 如果连接不是OPEN状态，关闭现有连接
                this.socket.close();
                this.socket = null;
            }

            try {
                const endpoint: string = 'ws://' + serverAddress + '/ws/surf/';
                this.socket = new WebSocket(endpoint);

                // 设置连接超时
                const timeout = setTimeout(() => {
                    if (this.socket?.readyState !== WebSocket.OPEN) {
                        this.socket?.close();
                        this.socket = null;
                        reject(new Error('Connection timeout'));
                    }
                }, 5000); // 5秒超时

                this.socket.onopen = () => {
                    clearTimeout(timeout);
                    resolve(true);
                };

                this.socket.onmessage = (event: MessageEvent<any>) => {
                    try {
                        const jsonMessage = JSON.parse(event.data);
                        const {path, command} = jsonMessage;

                        console.log(`Received message for path: ${path}, command: ${command}`);

                        const messageSubject = this.getMessageSubject(path, command);
                        if (messageSubject) {
                            messageSubject.next(jsonMessage['messages']);
                        }
                    } catch (error) {
                        console.error('Error processing message:', error);
                    }
                };

                this.socket.onclose = (event: CloseEvent) => {
                    // 清理所有订阅
                    this.pathMap.forEach((commandMap) => {
                        commandMap.forEach((subject: { complete: () => any; }) => subject.complete());
                        commandMap.clear();
                    });
                    this.pathMap.clear();

                    this.socket = null;

                    // 如果不是正常关闭，触发错误处理
                    if (!event.wasClean) {
                        console.error(`WebSocket connection closed abnormally. Code: ${event.code}, Reason: ${event.reason}`);
                    }
                };

                this.socket.onerror = (error: Event) => {
                    clearTimeout(timeout);
                    console.error('WebSocket error:', error);
                    this.socket = null;
                    reject(new Error('WebSocket connection failed'));
                };

            } catch (error) {
                console.error('Error creating WebSocket:', error);
                reject(error);
            }
        });
    }

    public disconnect() {
        if (this.socket) {
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

    public send(path: string, command: string, messages: any = {}) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            throw new Error('WebSocket is not connected');
        }

        // 如果没有提供 messages 则初始化为空对象
        const message = {
            path,
            command,
            ...messages
        };

        // 如果 session 存在，则将其添加到消息中
        if (this.commonDataService.session) {
            message['session_id'] = this.commonDataService.session;
        }

        // 发送消息
        this.socket.send(JSON.stringify(message));
    }

}
