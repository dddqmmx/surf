import {Component, OnDestroy, OnInit} from '@angular/core';
import {appDataDir} from "@tauri-apps/api/path";
import {invoke} from "@tauri-apps/api/core";
import {Router, RouterOutlet} from "@angular/router";
import {NgOptimizedImage} from "@angular/common";
import {CommonDataService} from "../../services/common-data.service";
import {SocketService} from "../../services/socket.service";
import {Subscription} from "rxjs";

@Component({
  selector: 'app-main',
  standalone: true,
    imports: [
        RouterOutlet,
        NgOptimizedImage
    ],
  templateUrl: './main.component.html',
  styleUrl: './main.component.css'
})
export class MainComponent implements OnInit, OnDestroy {
    subscriptions: Subscription[] = [];

    constructor(private router: Router, private socketService: SocketService, private commonDataService: CommonDataService) {
    }

    ngOnDestroy() {
        this.subscriptions.forEach(subscription => subscription.unsubscribe());
    }

    ngOnInit(): void {
        if (this.commonDataService.session == null) {
            this.router.navigate(['/']);
            return
        }
        const getUserDataSubject = this.socketService.getMessageSubject("user", "get_user_data_result").subscribe((message: Record<string, any>) => {
            this.commonDataService.servers = message['user']['servers'];
            this.commonDataService.clientUserId = message['user']['id'];
            console.log(message)
            getUserDataSubject.unsubscribe()
        })
        this.subscriptions.push(getUserDataSubject);
        this.socketService.send('user', 'get_user_data')
    }


}
