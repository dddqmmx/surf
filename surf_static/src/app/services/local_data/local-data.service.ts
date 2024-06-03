import { Injectable } from '@angular/core';
import { SocketManagerService } from "../socket/socket-manager.service";
import { CryptoService } from "../crypto/crypto.service";
import { debounceTime, Subject } from "rxjs";

@Injectable({
    providedIn: 'root'
})
export class LocalDataService {
    serverAddress = ""
    loggedUserId = ""

    constructor(
        private socketManagerService: SocketManagerService,
        private cryptoService: CryptoService
    ) {}

    userInfoList = new Map<string, { data: any, timestamp: number }>();

    hasUserInfo(id: string){
        return this.userInfoList.has(id)
    }
    getUserInfo(id: string){
        return this.userInfoList.get(id)?.data
    }
    setUserInfo(id: string,data: any){
        const now = Date.now();
        this.userInfoList.set(id, { data: data, timestamp: now });
    }
    getUserData(ids: string[]): Promise<Map<string, any>> {
        const now = Date.now();
        const result = new Map<string, any>();
        const idsToFetch: string[] = [];

        // 使用 Set 去重
        const uniqueIds = Array.from(new Set(ids));

        uniqueIds.forEach((id: string) => {
            const userInfo = this.userInfoList.get(id);
            if (userInfo && (now - userInfo.timestamp < 30 * 60 * 1000)) {
                // 如果数据存在且未超过30分钟，使用缓存的数据
                result.set(id, userInfo.data);
            } else {
                // 需要重新获取的数据
                idsToFetch.push(id);
            }
        });

        if (idsToFetch.length === 0) {
            // 如果没有需要重新获取的数据，直接返回结果
            return Promise.resolve(result);
        }

        return new Promise((resolve, reject) => {
            // 订阅消息以获取数据
            const subscription = this.socketManagerService.getMessageSubject("user", "search_user_result").subscribe(
                (message) => {
                    const data = JSON.parse(message.data).messages;
                    data.forEach((item: any) => {
                        this.userInfoList.set(item.user_id, { data: item, timestamp: now });
                        result.set(item.user_id, item);
                    });
                    subscription.unsubscribe(); // 取消订阅
                    resolve(result); // 返回结果
                },
                (error) => {
                    subscription.unsubscribe(); // 取消订阅
                    reject(error); // 处理错误
                }
            );

            // 发送请求以获取用户数据
            this.socketManagerService.send('user', 'search_user', {
                'session_id': this.cryptoService.session,
                'user_id_list': idsToFetch
            });
        });
    }

}
