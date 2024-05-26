import { Injectable } from '@angular/core';
import { SocketManagerService } from "../socket/socket-manager.service";
import { CryptoService } from "../crypto/crypto.service";
import { debounceTime, Subject } from "rxjs";

@Injectable({
    providedIn: 'root'
})
export class LocalDataService {
    serverAddress = ""

    private requestQueue = new Subject<void>();
    private cache = new Map<string, { timestamp: number, data: any }>();
    private pendingRequests = new Set<string>();

    constructor(
        private socketManagerService: SocketManagerService,
        private cryptoService: CryptoService
    ) {
        this.requestQueue.pipe(
            debounceTime(300)
        ).subscribe(() => {
            this.processBatchRequest();
        });
    }

    getUserData(id: string) {
        const cachedResult = this.cache.get(id);
        const now = Date.now();

        if (cachedResult && (now - cachedResult.timestamp < 60000)) {
            console.log(cachedResult.data);
            return;
        }

        if (!this.pendingRequests.has(id)) {
            this.pendingRequests.add(id);
            this.requestQueue.next();
        }
    }

    private processBatchRequest() {
        const ids = Array.from(this.pendingRequests);
        this.pendingRequests.clear();

        if (ids.length === 0) {
            return;
        }

        this.socketManagerService.getMessageSubject("user", "search_user_result").subscribe(
            (message: { data: string; }) => {
                const data = JSON.parse(message.data).messages;
                data.forEach((item: any) => {
                    this.cache.set(item.id, { timestamp: Date.now(), data: item });
                    console.log(item);
                });
            }
        );

        this.socketManagerService.send('user', 'search_user', {
            'session_id': this.cryptoService.session,
            'user_id_list': ids
        });
    }
}
