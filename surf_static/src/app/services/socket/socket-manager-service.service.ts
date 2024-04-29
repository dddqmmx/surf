import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class SocketManagerServiceService {
    private sockets: Map<string, WebSocket> = new Map();

    public connect(endpoint: string){
        if (!this.sockets.has(endpoint)) {
            const socket = new WebSocket(endpoint);
            // Set up event handlers for socket here...
            this.sockets.set(endpoint, socket);
        }
        return this.sockets.get(endpoint)!;
    }

    public disconnect(endpoint: string){
        if (this.sockets.has(endpoint)){
            this.sockets.get(endpoint)?.close();
            this.sockets.delete(endpoint)
        }
    }
}
