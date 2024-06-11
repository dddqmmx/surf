import { Injectable } from '@angular/core';
import { SocketManagerService } from "../socket/socket-manager.service";
import { CryptoService } from "../crypto/crypto.service";
import { debounceTime, Subject } from "rxjs";

type Channel = {
  id: string;
  name: string;
  type: string;
  description: string;
};

type ChannelGroup = {
  id: string;
  name: string;
  channels: Channel[];
};

type ServerDetailsData = {
  id: string;
  description: string;
  name: string;
  icon_url: string | null;
  channel_groups: ChannelGroup[];
};

@Injectable({
    providedIn: 'root'
})

export class LocalDataService {
    //服务器地址
    serverAddress = ""
    //登录的用户ID
    loggedUserId = ""

    constructor(
        private socketManagerService: SocketManagerService,
        private cryptoService: CryptoService
    ) {}

    /**
     * 存储频道相关
     */
   private channelGroups: ChannelGroup[] = [];

  // 根据ID检索ChannelGroup
  getChannelGroupById(id: string): ChannelGroup | undefined {
    return this.channelGroups.find(group => group.id === id);
  }

  // 根据ID检索Channel
    getChannelById(id: string | null): Channel | undefined {
    for (const group of this.channelGroups) {
      const channel = group.channels.find(channel => channel.id === id);
      if (channel) {
        return channel;
      }
    }
    return undefined;
  }

  // 添加新的ChannelGroups
  addChannelGroups(newChannelGroups: ChannelGroup[] | undefined): void {
    if (newChannelGroups && Array.isArray(newChannelGroups)) {
      this.channelGroups.push(...newChannelGroups);
    } else {
      console.error("Invalid channelGroups data");
    }
  }

    /**
     * 存储用户相关
     */
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
