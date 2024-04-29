import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import {error} from "@angular/compiler-cli/src/transformers/util";

@Injectable({
  providedIn: 'root'
})
export class SocketManagerService {
    private sockets: Map<string, WebSocket> = new Map();
    private messageSubjects: Map<string, Subject<MessageEvent>> = new Map();

    public connect(endpoint: string): Observable<MessageEvent>{
        if(!this.sockets.has(endpoint)){
            const socket = new WebSocket(endpoint)
            const messageSubject = new Subject<MessageEvent>();
            this.messageSubjects.set(endpoint, messageSubject);

            socket.onmessage = (event) => {
                messageSubject.next(event);
            };
            socket.close =() =>{
                messageSubject.complete();
                this.sockets.delete(endpoint)
                this.messageSubjects.delete(endpoint)
            }
            socket.onerror = (error) =>{
                messageSubject.error(error)
            }

            this.sockets.set(endpoint, socket)
        }
        return this.messageSubjects.get(endpoint)?.asObservable()!
    }

    public disconnect(endpoint: string){
        if (this.sockets.has(endpoint)){
            this.sockets.get(endpoint)?.close();
            this.sockets.delete(endpoint)
        }
    }
}
