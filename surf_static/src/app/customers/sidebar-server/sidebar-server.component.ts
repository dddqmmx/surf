import { Component } from '@angular/core';
import {NgForOf} from "@angular/common";

@Component({
  selector: 'app-sidebar-server',
  standalone: true,
    imports: [
        NgForOf
    ],
  templateUrl: './sidebar-server.component.html',
  styleUrl: './sidebar-server.component.css'
})
export class SidebarServerComponent {
    channelInfo =
        {
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
                            "channel_name":"对骂",
                            "channel_type":"text"
                        }
                    ]
                },
                {
                    "channel_class_name":"语音聊天",
                    "channels":[
                        {
                            "channel_name":"语音对骂",
                            "channel_type":"voice"
                        }
                    ]
                }
            ],
        }
}
