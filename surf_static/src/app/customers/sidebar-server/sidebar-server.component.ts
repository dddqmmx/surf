import {Component, EventEmitter, Output, ViewChild} from '@angular/core';
import {NgForOf, NgIf} from "@angular/common";
import {MainComponent} from "../main/main.component";

@Component({
  selector: 'app-sidebar-server',
  standalone: true,
    imports: [
        NgForOf,
        NgIf
    ],
  templateUrl: './sidebar-server.component.html',
  styleUrl: './sidebar-server.component.css'
})
export class SidebarServerComponent {


    @Output() selectUserPopup = new EventEmitter();

    toggleSelectUserPopup() {
        this.selectUserPopup.emit();
    }

    menuVisible = false;
    toggleMenu(){
        this.menuVisible = !this.menuVisible;
    }
    channelInfo = {
            "server_nane":"桐生可可粉丝频道",
            "server_icon":"",
            "channel_classes":[
                {
                    "channel_class_name":"文字聊天",
                    "channels":[
                        {
                            "channel_name":"闲聊",
                            "channel_type":"text"
                        },
                        {
                            "channel_name":"文字",
                            "channel_type":"text"
                        }
                    ]
                },
                {
                    "channel_class_name":"语音聊天",
                    "channels":[
                        {
                            "channel_name":"语音",
                            "channel_type":"voice"
                        }
                    ]
                }
            ],
        }
}
