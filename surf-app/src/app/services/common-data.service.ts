import {Injectable} from '@angular/core';
import {SocketService} from "./socket.service";

@Injectable({
    providedIn: 'root'
})
export class CommonDataService {

    constructor() {
    }

    session: string | undefined;
    clientUserId: string = "";
    servers: any[] = []

}
